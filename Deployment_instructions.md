# Deployment Instructions

## Login to Azure
```bash
az login
```

## Set the default subscription
```bash
az account set --subscription <subscriptionID>
```

## Create a resource group and a managed identity
```bash
export RESOURCE_GROUP=ai-assistant-rg
export LOCATION=eastus

az group create --name $RESOURCE_GROUP --location $LOCATION
az identity create --name ai-assistant-id --resource-group $RESOURCE_GROUP
```

## Create a Cognitive Search service
```bash
az search service create --name ai-assistant-search --resource-group $RESOURCE_GROUP --sku Standard --location $LOCATION
```

## Enable semantic search at the service level
https://learn.microsoft.com/en-us/azure/search/semantic-how-to-enable-disable?tabs=enable-portal

## Create an OpenAI service
```bash
export AZURE_OPENAI_SERVICE=ai-assistant-openai1
az cognitiveservices account create \
--name $AZURE_OPENAI_SERVICE \
--custom-domain $AZURE_OPENAI_SERVICE \
--resource-group $RESOURCE_GROUP \
--location canadaeast \
--kind OpenAI \
--sku s0 
```

## Deploy the OpenAI models
```bash
az cognitiveservices account deployment create \
--name $AZURE_OPENAI_SERVICE \
--resource-group $RESOURCE_GROUP \
--deployment-name ai-assistant-ada \
--model-name text-embedding-ada-002 \
--model-version "2"  \
--model-format OpenAI \
--sku-capacity "120" \
--sku-name "Standard"

az cognitiveservices account deployment create \
--name $AZURE_OPENAI_SERVICE \
--resource-group $RESOURCE_GROUP \
--deployment-name ai-assistant-gpt-35-16k \
--model-name gpt-35-turbo-16k \
--model-version "0613"  \
--model-format OpenAI \
--sku-capacity "120" \
--sku-name "Standard"

az cognitiveservices account deployment create \
--name $AZURE_OPENAI_SERVICE \
--resource-group $RESOURCE_GROUP \
--deployment-name ai-assistant-gpt-4 \
--model-name gpt-4-32k \
--model-version "0613"  \
--model-format OpenAI \
--sku-capacity "30" \
--sku-name "Standard"
```
## Retrieve the OpenAI and Cognitive Search service keys
Use the Azure portal to retrieve the keys for the OpenAI and Cognitive Search services.


![Search Key](images/search_key.png?raw=true "Search Key")
![OpenAI Key](images/openai_key.png?raw=true "OpenAI Key")


Update the `COGNITIVE_SEARCH_API_KEY` and `OPENAI_API_KEY` variables in the [app.py](backend/app.py) notebook.


## Ingest workshop data into Azure Cognitive Search
Follow the instructions in the [Data_preparation.ipynb](notebooks/Data_preparation.ipynb) notebook.


Don't forget to update the `COGNITIVE_SEARCH_API_KEY` and `OPENAI_API_KEY` variables.

## Build the Docker image
```bash
export IMAGE_NAME=ss-ai-assistant-custom-image
docker build --tag $IMAGE_NAME .
```

## [OPTIONAL] Test the Docker image locally
```bash
docker run -it -p 8000:8000 $IMAGE_NAME
```
Open http://localhost:8000 in your browser. You should see the app running.

## Create container registry
```bash
az acr create --name aiassistantrepo --resource-group $RESOURCE_GROUP --sku Basic --admin-enabled true
```

## Retrieve the administrative credentials
```bash
az acr credential show --resource-group $RESOURCE_GROUP --name aiassistantrepo
```
The JSON output of this command provides two passwords along with the registry's user name.

## Sign in to the container registry
```bash
docker login aiassistantrepo.azurecr.io --username aiassistantrepo
```

## Push the image to the registry
```bash
docker tag $IMAGE_NAME aiassistantrepo.azurecr.io/$IMAGE_NAME:latest
docker push aiassistantrepo.azurecr.io/$IMAGE_NAME:latest
```

## Authorize the managed identity for your registry
```bash
principalId=$(az identity show --resource-group $RESOURCE_GROUP --name ss-ai-assistant-id --query principalId --output tsv)
registryId=$(az acr show --resource-group $RESOURCE_GROUP --name aiassistantrepo --query id --output tsv)
az role assignment create --assignee $principalId --scope $registryId --role "AcrPull"
```

## Create the App Service app
```bash
az appservice plan create --name AIassistantServicePlan --resource-group $RESOURCE_GROUP --is-linux
az webapp create --resource-group $RESOURCE_GROUP --plan AIassistantServicePlan --name ai-assistant-app --deployment-container-image-name aiassistantrepo.azurecr.io/$IMAGE_NAME:latest
```

## Configure the web app
```bash
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name ai-assistant-app --settings WEBSITES_PORT=8000
```

```bash
id=$(az identity show --resource-group $RESOURCE_GROUP --name ss-ai-assistant-id --query id --output tsv)
az webapp identity assign --resource-group $RESOURCE_GROUP --name ai-assistant-app --identities $id
```

```bash
appConfig=$(az webapp config show --resource-group $RESOURCE_GROUP --name ai-assistant-app --query id --output tsv)
az resource update --ids $appConfig --set properties.acrUseManagedIdentityCreds=True
```

```bash
clientId=$(az identity show --resource-group $RESOURCE_GROUP --name ai-assistant-id --query clientId --output tsv)
az resource update --ids $appConfig --set properties.AcrUserManagedIdentityID=$clientId
```

## Enable CI/CD in App Service
```bash
cicdUrl=$(az webapp deployment container config --enable-cd true --name ai-assistant-app --resource-group $RESOURCE_GROUP --query CI_CD_URL --output tsv)
az acr webhook create --name appserviceCD --registry aiassistantrepo --uri $cicdUrl --actions push --scope $IMAGE_NAME:latest
```
