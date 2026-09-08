(function(root){
  'use strict';
  const clean=v=>String(v||'').trim().replace(/\s+/g,' ');
  function brief(d){
    for(const k of ['audience','moment','help','process','proof','channel'])if(!clean(d[k]))throw Error('Complete every field before building the brief.');
    const x=Object.fromEntries(Object.entries(d).map(([k,v])=>[k,clean(v)]));
    return `YOUR CLIENT-ATTRACTION BRIEF\n\nWorking audience\n${x.audience}\n\nWhy they may seek help now\n${x.moment}\n\nWhat you help them work through\n${x.help}\n\nHow you approach the work\n${x.process}\n\nEvidence you can substantiate\n${x.proof}\n\nWhere you can reach them\n${x.channel}\n\nWorking introduction\nI work with ${x.audience}. My focus is ${x.help}.\n\nSupporting explanation\nMy approach: ${x.process}.\n\nBefore you publish\n1. Read the introduction aloud and edit it into your voice.\n2. Ask two people in this audience what they think it means.\n3. Check that the service and evidence match your actual work.\n4. Use your normal firm review process.\n\nThis is a structured draft from your inputs, not a validated market position.\nKeir Dillon | The Positioning Blueprint`;
  }
  const checks=[
    ['audience','A reader can identify the client situation I work with.','Make the client situation specific in your opening sentence.'],
    ['service','My opening explains the kind of help I provide.','Explain the service in plain language before listing credentials.'],
    ['consistency','My profile and homepage tell a consistent story.','Compare the first lines of your profile and homepage; resolve the mismatch.'],
    ['affiliation','My role and firm affiliations are understandable.','Clarify your role alongside required affiliation language.'],
    ['proof','My claims have evidence I can substantiate and use.','Replace an unsupported promise with a specific explanation of your process.'],
    ['questions','My content answers questions my intended clients ask.','Choose one real, general client question and answer it clearly.'],
    ['next','A visitor can understand what happens in a first conversation.','Describe the first conversation and give one working next step.'],
    ['current','My basic details, links, and professional information are current.','Check the contact route, role, links, and dates for accuracy.']
  ];
  function audit(values){
    const allowed=['yes','partly','no'];
    if(values.length!==checks.length||values.some(v=>!allowed.includes(v)))throw Error('Answer all eight questions to see your priorities.');
    const groups={yes:[],partly:[],no:[]};values.forEach((v,i)=>groups[v].push(checks[i]));
    const priorities=[...groups.no,...groups.partly];
    return `THE SNIFF TEST | YOUR SELF-REVIEW\n\n${groups.yes.length} clear / ${groups.partly.length} partial / ${groups.no.length} missing\n\n${priorities.length?'YOUR NEXT IMPROVEMENTS\n'+priorities.slice(0,3).map((c,i)=>`${i+1}. ${c[2]}`).join('\n'):'All eight checks are marked clear. Ask an intended client to explain your website in their own words and compare that with your intention.'}\n\nCOMPLETE REVIEW\n${checks.map((c,i)=>`${c[1]} — ${values[i]}`).join('\n')}\n\nHow priorities were chosen\nMissing items first, then partial items, in the order of the checklist: audience, service, consistency, affiliation, evidence, questions, next step, current details.\n\nThis uses your answers. It does not scan your site or predict inquiries, revenue, or compliance approval.\nKeir Dillon | The Sniff Test`;
  }
  function content(d){
    for(const k of ['audience','question','answer','next'])if(!clean(d[k]))throw Error('Complete the audience, question, answer, and next step.');
    const x=Object.fromEntries(Object.entries(d).map(([k,v])=>[k,clean(v)]));
    return `FOUR WEEKS OF USEFUL CONTENT\n\nAudience: ${x.audience}\nCore question: ${x.question}\nYour factual starting answer: ${x.answer}\n\nWEEK 1 | Explain\nOpening: A question I often hear is: “${x.question}”\nBody: Give your answer in plain language: ${x.answer}\nClose: ${x.next}\n\nWEEK 2 | Clarify\nOpening: What people can misunderstand about “${x.question}”\nBody: Name one misconception you have actually encountered. Explain the accurate distinction using your answer. Do not invent a client story.\nClose: What would make this easier to understand?\n\nWEEK 3 | Prepare\nOpening: Before you make a decision about this, gather these details.\nBody: Write a three-item preparation checklist that genuinely fits your process and the question: ${x.question}\nClose: Save the checklist for your next conversation.\n\nWEEK 4 | Show the process\nOpening: Here is how I help someone work through this question.\nBody: Explain the first two or three steps in your actual process. Use a labeled fictional example if it helps, without promising a financial outcome.\nClose: ${x.next}\n\nONE RECORDING ROUTINE\nSpeak the week's answer for 60 seconds. Use the same idea for a written post. Publish at a pace you can sustain.\n\nREVIEW\nThese are editable outlines, not finished or compliance-approved posts. Check every factual statement, leave client-sensitive information out, and use your firm's review process.\nKeir Dillon | Client-question planner`;
  }
  root.KDTools={brief,audit,content,checks};
  if(typeof module==='object'&&module.exports)module.exports=root.KDTools;
})(typeof window!=='undefined'?window:globalThis);
