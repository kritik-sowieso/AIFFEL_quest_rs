'use strict';
(() => {
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const slides = $$('.slide');
  const data = window.PAPER_DATA;
  let index = 0;
  const escapeHTML = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = n => n == null ? '—' : typeof n === 'number' ? n.toFixed(1) : escapeHTML(n);

  function table(dataset, caption=dataset.source) {
    const max = dataset.columns.map((_,i) => i ? Math.max(...dataset.rows.map(r=>r[i]??-Infinity)) : 0);
    return `<table><caption>${escapeHTML(caption)}</caption><thead><tr>${dataset.columns.map(c=>`<th scope="col">${escapeHTML(c)}</th>`).join('')}</tr></thead><tbody>${dataset.rows.map(row=>`<tr class="${String(row[0]).startsWith('STAMPlus')?'ours':''}">${row.map((v,i)=>i?`<td class="${v!=null&&v===max[i]?'best':''}">${fmt(v)}</td>`:`<th scope="row">${fmt(v)}</th>`).join('')}</tr>`).join('')}</tbody></table>`;
  }

  function go(n, updateHash=true) {
    index=Math.max(0,Math.min(slides.length-1,n));
    slides.forEach((s,i)=>{s.classList.toggle('active',i===index);s.setAttribute('aria-hidden',String(i!==index));});
    $$('video').forEach(v=>v.pause());
    const page=String(index+1).padStart(2,'0');
    $('#current-number').textContent=page;
    $('#current-topic').textContent=slides[index].dataset.topic;
    $('#slide-title').textContent=slides[index].dataset.title;
    $('#page-count').textContent=`${page} / ${slides.length}`;
    $('#progress-fill').style.width=`${(index+1)/slides.length*100}%`;
    $('#prev').disabled=index===0;
    $('#next').disabled=index===slides.length-1;
    $$('#overview-list button').forEach((b,i)=>b.setAttribute('aria-current',String(i===index)));
    $('#announcer').textContent=`${index+1} / ${slides.length}. ${slides[index].dataset.title}`;
    if(updateHash) history.replaceState(null,'',`#${page}`);
    window.scrollTo({top:0,behavior:'instant'});
    // Move focus away from a control that has just become hidden.
    if(document.activeElement?.closest('.slide')&&!document.activeElement.closest('.slide').classList.contains('active')) $('#deck').focus({preventScroll:true});
  }
  function fromHash(){const raw=location.hash.slice(1);if(/^\d+$/.test(raw))go(Number(raw)-1,false);else if(!raw)go(0,false);}
  $('#prev').addEventListener('click',()=>go(index-1));
  $('#next').addEventListener('click',()=>go(index+1));
  $$('[data-go]').forEach(b=>b.addEventListener('click',()=>go(Number(b.dataset.go)-1)));
  window.addEventListener('hashchange',fromHash);
  $('#overview-list').innerHTML=slides.map((s,i)=>`<button data-slide="${i}"><span>${String(i+1).padStart(2,'0')}</span><b>${escapeHTML(s.dataset.title)}</b></button>`).join('');
  $$('#overview-list button').forEach(b=>b.addEventListener('click',()=>{$('#overview').close();go(Number(b.dataset.slide));$('#deck').focus({preventScroll:true});}));
  const openOverview=()=>{$('#overview').showModal();$('#overview-list button[aria-current=true]')?.focus();};
  $('#overview-btn').addEventListener('click',openOverview);
  $$('[data-close]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.close).close()));
  $$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
  $$('[data-zoom]').forEach(b=>b.addEventListener('click',()=>{$('#zoom-image').src=b.dataset.zoom;$('#zoom-image').alt=$('img',b).alt;$('#figure-caption').textContent=b.dataset.caption;$('#figure-dialog').showModal();}));
  function toggleNotes(){const shown=document.body.classList.toggle('show-notes');$('#notes-btn').setAttribute('aria-pressed',String(shown));}
  $('#notes-btn').addEventListener('click',toggleNotes);
  async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{$('#announcer').textContent='이 브라우저에서는 전체 화면을 사용할 수 없습니다.';}}
  $('#fullscreen-btn').addEventListener('click',fullscreen);
  document.addEventListener('keydown',e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||$('dialog[open]')||e.target.closest('input,textarea,select,video,[contenteditable="true"]'))return;
    // Keep native activation keys and arrows available to focused controls.
    const interactive=e.target.closest('button,a,summary');
    if(['Home','End'].includes(e.key)&&interactive)return;
    if(['ArrowRight','PageDown'].includes(e.key)){e.preventDefault();go(index+1);}
    else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(index-1);}
    else if(e.key==='Home'){e.preventDefault();go(0);}
    else if(e.key==='End'){e.preventDefault();go(slides.length-1);}
    else if(e.key.toLowerCase()==='o'){e.preventDefault();openOverview();}
    else if(e.key.toLowerCase()==='n'){e.preventDefault();toggleNotes();}
    else if(e.key.toLowerCase()==='f'){e.preventDefault();fullscreen();}
  });
  let touchStart=null;
  $('#deck').addEventListener('touchstart',e=>{if(!e.target.closest('button,a,video,.table-wrap,details'))touchStart={x:e.changedTouches[0].clientX,y:e.changedTouches[0].clientY};},{passive:true});
  $('#deck').addEventListener('touchend',e=>{if(!touchStart)return;const dx=e.changedTouches[0].clientX-touchStart.x,dy=e.changedTouches[0].clientY-touchStart.y;touchStart=null;if(Math.abs(dx)>90&&Math.abs(dx)>Math.abs(dy)*1.5)go(index+(dx<0?1:-1));},{passive:true});

  function result(kind){
    $$('[data-result]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.result===kind)));
    $('#results-table').innerHTML=table(data[kind]);
    $('#result-insight').innerHTML=kind==='semantic'?'<b>평균과 개별 지표</b><p>STAMPlus-7B의 평균 mIoU는 <strong>63.7</strong>로 이 표에서 가장 높다. PAS-20에서는 <strong>SAN 94.0</strong>이 STAMPlus-7B의 92.1보다 높다.</p>':'<b>함께 읽어야 할 차이</b><p>STAMPlus-7B는 <strong>Test gIoU 65.8 / cIoU 66.9</strong>. 전체 평균은 <strong>63.5</strong>로 Text4Seg++의 <strong>63.8</strong>보다 낮다. 최고 성능의 범위를 지표별로 구분한다.</p>';
  }
  $$('[data-result]').forEach(b=>b.addEventListener('click',()=>result(b.dataset.result)));

  $('#ablation-table').innerHTML='<table><caption>Table X · cIoU (%) / time (s) · 단일 A800 · 행 이름을 선택</caption><thead><tr><th scope="col">설정</th><th scope="col">입력 크기</th><th scope="col">cIoU ↑</th><th scope="col">초 ↓</th></tr></thead><tbody>'+data.ablation.map((r,i)=>`<tr data-ablation-row="${i}"><th scope="row"><button data-ablation="${i}" aria-pressed="false">${escapeHTML(r.name)}</button></th><td>${r.size}</td><td>${r.iou.toFixed(1)}</td><td>${r.time.toFixed(1)}</td></tr>`).join('')+'</tbody></table>';
  function ablation(i){
    const r=data.ablation[i],diff=r.iou-data.ablation[0].iou;
    $$('[data-ablation]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.ablation)===i)));
    $$('[data-ablation-row]').forEach(tr=>tr.classList.toggle('selected',Number(tr.dataset.ablationRow)===i));
    $('#ablation-name').textContent=r.name;
    $('#ablation-delta').textContent=(diff>0?'+':'')+diff.toFixed(1);
    $('#ablation-iou').textContent=r.iou.toFixed(1);
    $('#selected-bar').style.width=r.iou+'%';
    $('#ablation-description').textContent=r.note;
    $('#ablation-time').textContent=r.time.toFixed(1)+' s';
  }
  $$('[data-ablation]').forEach(b=>b.addEventListener('click',()=>ablation(Number(b.dataset.ablation))));
  $('#resolution-table').innerHTML=table(data.resolution);
  function understanding(kind){
    $$('[data-understanding]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.understanding===kind)));
    $('#understanding-table').innerHTML=table(data[kind]);
    $('#understanding-note').textContent=kind==='reasoning'?'Look-twice 조건에서 평균 68.5 → 71.1: Qwen2-VL-2B보다 STAMPlus-2B가 2.6점 높다. STAMPlus 자체의 Direct → Look-twice 차이는 4.2점이다.':'VQA 기준 Qwen2-VL-2B와 비교하면 여러 점수가 유지·개선되지만 TextVQA 70.7 → 70.6, VizWiz 60.3 → 59.2는 하락한다. Mix는 segmentation + visual instruction data 학습이다.';
  }
  $$('[data-understanding]').forEach(b=>b.addEventListener('click',()=>understanding(b.dataset.understanding)));

  const modes={
    target:{entries:[{cls:1,label:'target'}],text:'두 커튼과 침대를 모두 “질문에 해당하는 전경” 하나로 묶습니다.',names:['배경','target']},
    category:{entries:[{cls:1,label:'curtain'},{cls:2,label:'bed'}],text:'두 커튼은 같은 범주 ID를 공유하고, 침대는 별도 ID를 가집니다.',names:['배경','curtain','bed']},
    instance:{entries:[{cls:1,label:'curtain A'},{cls:2,label:'curtain B'},{cls:3,label:'bed'}],text:'커튼 A와 커튼 B를 별도 ID로 구분합니다. 실제 목록은 같은 label과 서로 다른 bbox를 사용할 수 있습니다.',names:['배경','curtain A','curtain B','bed']}
  };
  const colors=['#bcc8c3','#7caff0','#6ad5bf','#e9b961'];
  function mode(kind){
    $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===kind)));
    const m=modes[kind];
    $('#target-json').textContent='[\n'+m.entries.map(e=>'  '+JSON.stringify(e)).join(',\n')+'\n]';
    $('#mode-explanation').textContent=m.text;
    $('#mask-grid').innerHTML=Array.from({length:96},(_,i)=>{
      const r=Math.floor(i/12),c=i%12;
      let id=r<5&&c>=1&&c<=2?1:r<5&&c>=9&&c<=10?2:r>=5&&r<=6&&c>=3&&c<=8?3:0;
      if(kind==='target'&&id)id=1;
      if(kind==='category'&&id)id=id===3?2:1;
      return `<span style="background:${colors[id]}" aria-hidden="true">${id||'·'}</span>`;
    }).join('');
    $('#mask-grid').setAttribute('aria-label',m.text);
    $('#mask-legend').innerHTML=m.names.map((n,i)=>`<span><i style="background:${colors[i]}"></i>${i} ${escapeHTML(n)}</span>`).join('');
  }
  $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>mode(b.dataset.mode)));
  const models={
    vit:['VISUAL REPRESENTATION','이미지를 토큰의 열로 바라보기','ViT는 이미지를 패치로 나눠 Transformer가 처리할 시퀀스로 바꾼다. STAMPlus에서는 이미지 패치와 마스크 토큰의 공간적 대응을 이해하는 출발점이 된다.','패치가 커지면 작은 대상은 어떻게 보일까?','2010.11929'],
    clip:['VISION–LANGUAGE ALIGNMENT','이미지와 언어의 의미를 연결하기','CLIP은 이미지–텍스트 쌍의 대조 학습으로 두 표현을 정렬한다. 열린 어휘를 이해하는 기초이며, 원래의 CLIP 자체가 지시문 기반 픽셀 마스크를 생성하는 모델은 아니다.','“무엇인가”를 아는 것과 “어디까지인가”를 아는 것은 왜 다를까?','2103.00020'],
    llava:['VISUAL INSTRUCTION TUNING','시각 특징을 LLM과 연결하기','LLaVA는 vision encoder와 LLM을 연결하고 시각 instruction tuning을 수행한다. STAMPlus의 Phase 1을 이해하는 연결점이다. 주력 실험은 Qwen2-VL 기반이며 Table II에는 LLaVA 기반 전이 실험도 있다.','이미지를 설명하는 능력을 어떻게 조밀한 분할 출력으로 확장할까?','2304.08485'],
    detr:['SET PREDICTION','객체 집합을 한꺼번에 예측하기','DETR은 learned object query와 bipartite matching을 활용해 객체 집합을 예측한다. 병렬 예측이라는 관점은 연결되지만, STAMPlus의 토큰은 객체 query 대신 이미지 패치에 정렬된다. DETR이 직접 내부 모듈로 쓰인다는 뜻은 아니다.','객체 단위 query와 패치 단위 mask token은 무엇을 하나의 예측 단위로 삼을까?','2005.12872'],
    sam:['PROMPTABLE SEGMENTATION','위치 단서로 마스크를 정교하게 만들기','SAM은 점·box 등의 프롬프트에서 마스크를 만든다. STAMP/STAMPlus의 기본 마스크 생성은 외부 decoder를 요구하지 않지만, 결과를 frozen SAM으로 선택적으로 정제할 수 있다. Table X의 w/o SAM이 그 차이를 보여준다.','decoder-free 생성과 선택적 SAM 후처리는 어떻게 공존할까?','2304.02643']
  };
  function model(kind){const [label,title,text,question,id]=models[kind];$$('[data-model]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.model===kind)));$('#learning-label').textContent=label;$('#learning-title').textContent=title;$('#learning-text').textContent=text;$('#learning-question').textContent=question;$('#learning-link').href='https://arxiv.org/abs/'+id;}
  $$('[data-model]').forEach(b=>b.addEventListener('click',()=>model(b.dataset.model)));
  result('semantic');ablation(2);understanding('reasoning');mode('instance');model('vit');
  document.body.classList.add('js');fromHash();
})();
