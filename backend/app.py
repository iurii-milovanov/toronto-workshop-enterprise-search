import io
import logging
import mimetypes
import os

import aiohttp
import openai
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.search.documents.aio import SearchClient
from azure.storage.blob.aio import BlobServiceClient
from opentelemetry.instrumentation.aiohttp_client import (
    AioHttpClientInstrumentor,
)
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from quart import (
    Blueprint,
    Quart,
    abort,
    current_app,
    jsonify,
    request,
    send_file,
    send_from_directory,
)

from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from approaches.readdecomposeask import ReadDecomposeAsk
from approaches.readretrieveread import ReadRetrieveReadApproach
from approaches.retrievethenread import RetrieveThenReadApproach

# Azure Storage configuration
AZURE_STORAGE_ACCOUNT = os.getenv(
    "AZURE_STORAGE_ACCOUNT", "searchstorageaccstage"
)
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "previews")

# Azure Cognitive Search configuration
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE", "ai-assistant-search")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "ai-assistant-idx")
# UPDATE THE VALUE BELOW TO YOUR COGNITIVE SEARCH ADMIN KEY
COGNITIVE_SEARCH_API_KEY = os.getenv(
    "COGNITIVE_SEARCH_API_KEY",
    "<FILL_IN_YOUR_COGNITIVE_SEARCH_API_KEY>",
)
KB_FIELDS_CONTENT = os.getenv("KB_FIELDS_CONTENT", "Content")
KB_FIELDS_CATEGORY = os.getenv("KB_FIELDS_CATEGORY", "Storage")
KB_FIELDS_SOURCEPAGE = os.getenv("KB_FIELDS_SOURCEPAGE", "LocationURL")

# Azure OpenAI configuration
AZURE_OPENAI_SERVICE = os.getenv(
    "AZURE_OPENAI_SERVICE", "ai-assistant-openai"
)
# UPDATE THE VALUE BELOW TO YOUR OPENAI API KEY
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY", "<FILL_IN_YOUR_OPENAI_API_KEY>"
)
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_CHATGPT_DEPLOYMENT", "ai-assistant-gpt-35-16k"
)
AZURE_OPENAI_CHATGPT_MODEL = os.getenv(
    "AZURE_OPENAI_CHATGPT_MODEL", "gpt-35-turbo-16k"
)
AZURE_OPENAI_GPT4_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_GPT4_DEPLOYMENT", "ai-assistant-gpt-4"
)
AZURE_OPENAI_GPT4_MODEL = os.getenv(
    "AZURE_OPENAI_GPT4_MODEL",
    "gpt-4-32k",
)
AZURE_OPENAI_EMB_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMB_DEPLOYMENT", "ai-assistant-ada"
)
API_VERSION = "2023-05-15"
OPENAI_API_TYPE = "azure"

# Configuration keys
CONFIG_OPENAI_TOKEN = "openai_token"
CONFIG_CREDENTIAL = "azure_credential"
CONFIG_ASK_APPROACHES = "ask_approaches"
CONFIG_CHAT_APPROACHES = "chat_approaches"
CONFIG_BLOB_CLIENT = "blob_client"

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

bp = Blueprint("routes", __name__, static_folder="static")


@bp.route("/")
async def index():
    return await bp.send_static_file("index.html")


@bp.route("/favicon.ico")
async def favicon():
    return await bp.send_static_file("favicon.ico")


@bp.route("/assets/<path:path>")
async def assets(path):
    return await send_from_directory("static/assets", path)


# Serve content files from blob storage from within the app to keep the example self-contained.
# *** NOTE *** this assumes that the content files are public, or at least that all users of the app
# can access all the files. This is also slow and memory hungry.
@bp.route("/content/<path>")
async def content_file(path):
    blob_container = current_app.config[
        CONFIG_BLOB_CLIENT
    ].get_container_client(AZURE_STORAGE_CONTAINER)
    blob = await blob_container.get_blob_client(path).download_blob()
    if not blob.properties or not blob.properties.has_key("content_settings"):
        abort(404)
    mime_type = blob.properties["content_settings"]["content_type"]
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    blob_file = io.BytesIO()
    await blob.readinto(blob_file)
    blob_file.seek(0)
    return await send_file(
        blob_file,
        mimetype=mime_type,
        as_attachment=False,
        attachment_filename=path,
    )


@bp.route("/ask", methods=["POST"])
async def ask():
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    approach = request_json["approach"]
    try:
        impl = current_app.config[CONFIG_ASK_APPROACHES].get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        # Workaround for: https://github.com/openai/openai-python/issues/371
        async with aiohttp.ClientSession() as s:
            openai.aiosession.set(s)
            r = await impl.run(
                request_json["question"], request_json.get("overrides") or {}
            )
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /ask")
        return jsonify({"error": str(e)}), 500


@bp.route("/chat", methods=["POST"])
async def chat():
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    approach = request_json["approach"]
    try:
        impl = current_app.config[CONFIG_CHAT_APPROACHES].get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        # Workaround for: https://github.com/openai/openai-python/issues/371
        async with aiohttp.ClientSession() as s:
            openai.aiosession.set(s)
            r = await impl.run(
                request_json["history"], request_json.get("overrides") or {}
            )
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /chat")
        return jsonify({"error": str(e)}), 500


@bp.before_app_serving
async def setup_clients():
    # Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed,
    # just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the
    # keys for each service
    # If you encounter a blocking error during a DefaultAzureCredential resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
    azure_credential = DefaultAzureCredential(
        exclude_shared_token_cache_credential=True
    )
    azure_cognitive_search_key_credential = AzureKeyCredential(
        COGNITIVE_SEARCH_API_KEY
    )

    # Set up clients for Cognitive Search and Storage
    search_client = SearchClient(
        endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
        index_name=AZURE_SEARCH_INDEX,
        credential=azure_cognitive_search_key_credential,
    )
    blob_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=azure_credential,
    )

    # Used by the OpenAI SDK
    openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
    openai.api_version = API_VERSION
    openai.api_type = OPENAI_API_TYPE
    openai.api_key = OPENAI_API_KEY

    # Store on app.config for later use inside requests
    # current_app.config[CONFIG_OPENAI_TOKEN] = openai_token
    current_app.config[CONFIG_CREDENTIAL] = azure_credential
    current_app.config[CONFIG_BLOB_CLIENT] = blob_client
    # Various approaches to integrate GPT and external knowledge, most applications will use a single one of these patterns
    # or some derivative, here we include several for exploration purposes
    current_app.config[CONFIG_ASK_APPROACHES] = {
        "rtr": RetrieveThenReadApproach(
            search_client,
            AZURE_OPENAI_CHATGPT_DEPLOYMENT,
            AZURE_OPENAI_CHATGPT_MODEL,
            AZURE_OPENAI_EMB_DEPLOYMENT,
            KB_FIELDS_SOURCEPAGE,
            KB_FIELDS_CONTENT,
        ),
        "rrr": ReadRetrieveReadApproach(
            search_client,
            AZURE_OPENAI_CHATGPT_DEPLOYMENT,
            AZURE_OPENAI_EMB_DEPLOYMENT,
            KB_FIELDS_SOURCEPAGE,
            KB_FIELDS_CONTENT,
        ),
        "rda": ReadDecomposeAsk(
            search_client,
            AZURE_OPENAI_CHATGPT_DEPLOYMENT,
            AZURE_OPENAI_EMB_DEPLOYMENT,
            KB_FIELDS_SOURCEPAGE,
            KB_FIELDS_CONTENT,
        ),
    }
    current_app.config[CONFIG_CHAT_APPROACHES] = {
        "rrr": ChatReadRetrieveReadApproach(
            search_client,
            AZURE_OPENAI_CHATGPT_DEPLOYMENT,
            AZURE_OPENAI_CHATGPT_MODEL,
            AZURE_OPENAI_GPT4_DEPLOYMENT,
            AZURE_OPENAI_GPT4_MODEL,
            AZURE_OPENAI_EMB_DEPLOYMENT,
            KB_FIELDS_SOURCEPAGE,
            KB_FIELDS_CONTENT,
        )
    }


def create_app():
    if APPLICATIONINSIGHTS_CONNECTION_STRING:
        configure_azure_monitor()
        AioHttpClientInstrumentor().instrument()
    app = Quart(__name__)
    app.register_blueprint(bp)
    app.asgi_app = OpenTelemetryMiddleware(app.asgi_app)

    return app
