import{r as n,b5 as e}from"./vendor-7aeae076.js";import{A as a,R as r,S as se,Q as oe,E as ne,a as ae,b as u,c as re,d as ie,e as le}from"./index-c3174742.js";import{g as ce,d as pe,D as he,h as de,T as m,e as ue,C as E,f as me}from"./fluentui-react-b7bb3823.js";import"./fluentui-icons-09adad71.js";const Se="_oneshotContainer_p6613_1",ge="_oneshotTopSection_p6613_8",xe="_oneshotBottomSection_p6613_15",Ce="_oneshotTitle_p6613_25",ve="_oneshotQuestionInput_p6613_39",Te="_oneshotAnswerContainer_p6613_46",fe="_oneshotAnalysisPanel_p6613_53",Re="_oneshotSettingsSeparator_p6613_58",ye="_settingsButton_p6613_62",o={oneshotContainer:Se,oneshotTopSection:ge,oneshotBottomSection:xe,oneshotTitle:Ce,oneshotQuestionInput:ve,oneshotAnswerContainer:Te,oneshotAnalysisPanel:fe,oneshotSettingsSeparator:Re,settingsButton:ye};function _e(){const[_,S]=n.useState(!1),[i,H]=n.useState(a.RetrieveThenRead),[g,D]=n.useState(""),[x,I]=n.useState(""),[C,V]=n.useState(""),[c,O]=n.useState(r.Hybrid),[A,Q]=n.useState(3),[v,U]=n.useState(!0),[b,F]=n.useState(!1),[j,L]=n.useState(""),T=n.useRef(""),[f,k]=n.useState(!1),[p,P]=n.useState(),[h,M]=n.useState(),[N,w]=n.useState(),[d,l]=n.useState(void 0),R=async t=>{T.current=t,p&&P(void 0),k(!0),w(void 0),l(void 0);try{const s={question:t,approach:i,overrides:{promptTemplate:g.length===0?void 0:g,promptTemplatePrefix:x.length===0?void 0:x,promptTemplateSuffix:C.length===0?void 0:C,excludeCategory:j.length===0?void 0:j,top:A,retrievalMode:c,semanticRanker:v,semanticCaptions:b}},B=await le(s);M(B)}catch(s){P(s)}finally{k(!1)}},q=(t,s)=>{D(s||"")},G=(t,s)=>{I(s||"")},K=(t,s)=>{V(s||"")},z=(t,s)=>{Q(parseInt(s||"3"))},J=(t,s,B)=>{O((s==null?void 0:s.data)||r.Hybrid)},W=(t,s)=>{H((s==null?void 0:s.key)||a.RetrieveThenRead)},X=(t,s)=>{U(!!s)},Y=(t,s)=>{F(!!s)},Z=(t,s)=>{L(s||"")},$=t=>{R(t)},ee=t=>{N===t&&d===u.CitationTab?l(void 0):(w(t),l(u.CitationTab))},y=t=>{l(d===t?void 0:t)},te=[{key:a.RetrieveThenRead,text:"Retrieve-Then-Read"},{key:a.ReadRetrieveRead,text:"Read-Retrieve-Read"},{key:a.ReadDecomposeAsk,text:"Read-Decompose-Ask"}];return e.jsxs("div",{className:o.oneshotContainer,children:[e.jsxs("div",{className:o.oneshotTopSection,children:[e.jsx(se,{className:o.settingsButton,onClick:()=>S(!_)}),e.jsx("h1",{className:o.oneshotTitle,children:"Ask your data"}),e.jsx("div",{className:o.oneshotQuestionInput,children:e.jsx(oe,{placeholder:"Example: Does my plan cover annual eye exams?",disabled:f,onSend:t=>R(t)})})]}),e.jsxs("div",{className:o.oneshotBottomSection,children:[f&&e.jsx(ce,{label:"Generating answer"}),!T.current&&e.jsx(ne,{onExampleClicked:$}),!f&&h&&!p&&e.jsx("div",{className:o.oneshotAnswerContainer,children:e.jsx(ae,{answer:h,onCitationClicked:t=>ee(t),onThoughtProcessClicked:()=>y(u.ThoughtProcessTab),onSupportingContentClicked:()=>y(u.SupportingContentTab)})}),p?e.jsx("div",{className:o.oneshotAnswerContainer,children:e.jsx(re,{error:p.toString(),onRetry:()=>R(T.current)})}):null,d&&h&&e.jsx(ie,{className:o.oneshotAnalysisPanel,activeCitation:N,onActiveTabChanged:t=>y(t),citationHeight:"600px",answer:h,activeTab:d})]}),e.jsxs(pe,{headerText:"Configure answer generation",isOpen:_,isBlocking:!1,onDismiss:()=>S(!1),closeButtonAriaLabel:"Close",onRenderFooterContent:()=>e.jsx(he,{onClick:()=>S(!1),children:"Close"}),isFooterAtBottom:!0,children:[e.jsx(de,{className:o.oneshotSettingsSeparator,label:"Approach",options:te,defaultSelectedKey:i,onChange:W}),(i===a.RetrieveThenRead||i===a.ReadDecomposeAsk)&&e.jsx(m,{className:o.oneshotSettingsSeparator,defaultValue:g,label:"Override prompt template",multiline:!0,autoAdjustHeight:!0,onChange:q}),i===a.ReadRetrieveRead&&e.jsxs(e.Fragment,{children:[e.jsx(m,{className:o.oneshotSettingsSeparator,defaultValue:x,label:"Override prompt prefix template",multiline:!0,autoAdjustHeight:!0,onChange:G}),e.jsx(m,{className:o.oneshotSettingsSeparator,defaultValue:C,label:"Override prompt suffix template",multiline:!0,autoAdjustHeight:!0,onChange:K})]}),e.jsx(ue,{className:o.oneshotSettingsSeparator,label:"Retrieve this many documents from search:",min:1,max:50,defaultValue:A.toString(),onChange:z}),e.jsx(m,{className:o.oneshotSettingsSeparator,label:"Exclude category",onChange:Z}),e.jsx(E,{className:o.oneshotSettingsSeparator,checked:v,label:"Use semantic ranker for retrieval",onChange:X}),e.jsx(E,{className:o.oneshotSettingsSeparator,checked:b,label:"Use query-contextual summaries instead of whole documents",onChange:Y,disabled:!v}),e.jsx(me,{className:o.oneshotSettingsSeparator,label:"Retrieval mode",options:[{key:"hybrid",text:"Vectors + Text (Hybrid)",selected:c==r.Hybrid,data:r.Hybrid},{key:"vectors",text:"Vectors",selected:c==r.Vectors,data:r.Vectors},{key:"text",text:"Text",selected:c==r.Text,data:r.Text}],required:!0,onChange:J})]})]})}_e.displayName="OneShot";export{_e as Component};
//# sourceMappingURL=OneShot-7404dd6b.js.map