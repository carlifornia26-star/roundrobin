src = open('index.html').read()
tests = r'''
<script>
(function(){
var _rp=document.createElement('pre'); _rp.id='test-results'; document.body.appendChild(_rp);
const out=[]; const $=id=>document.getElementById(id);
function log(name,ok,info){ out.push((ok?'PASS':'FAIL')+' :: '+name+(info?' :: '+info:'')); _rp.textContent='\n'+out.join('\n')+'\nEND'; }
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
async function waitFor(fn,ms){ const t0=Date.now(); while(Date.now()-t0<ms){ if(fn()) return true; await sleep(50);} return false; }
var _hang=new Image(); _hang.src='http://10.255.255.1/hang'; document.body.appendChild(_hang);
let lastBlob=null; const origCreate=URL.createObjectURL.bind(URL);
URL.createObjectURL=function(b){ lastBlob=b; return origCreate(b); };
function dataJSON(htmlText){ const m=/<script id="roundrobin-data" type="application\/json">([\s\S]*?)<\/script>/.exec(htmlText); return m?JSON.parse(m[1]):null; }
function fileOf(j){ return '<!DOCTYPE html><html><body><script id="roundrobin-data" type="application/json">'+JSON.stringify(j)+'</'+'script></body></html>'; }
function importFile(text,name){
  const inp=$('open-file'); const dt=new DataTransfer();
  dt.items.add(new File([text],name||'letter.html',{type:'text/html'}));
  inp.files=dt.files; inp.dispatchEvent(new Event('change'));
}
async function run(){
try{
  // T1 create
  $('letter-title').value='Test Letter'; $('member-names').value='Maya, Theo, Rin';
  $('create-form').requestSubmit();
  log('T1 create shows letter view', !$('letter').classList.contains('hidden'));
  // T2 add entry
  $('entry-body').value='hello one'; $('entry-form').requestSubmit();
  await waitFor(()=>$('issues').textContent.includes('hello one'),2000);
  log('T2 entry appended and rendered', $('issues').textContent.includes('hello one'));
  // T3 export
  $('export-btn').click(); await waitFor(()=>lastBlob!==null,2000);
  const t1=await lastBlob.text(); const j1=dataJSON(t1);
  log('T3 export blob produced', !!t1);
  log('T3 export embeds data JSON', !!j1 && j1.title==='Test Letter' && j1.version===3 && j1.turn===1 && typeof j1.id==='string', j1?('v'+j1.version+' turn'+j1.turn+' id '+j1.id):'no json');
  // T4 fresh shell: reset state, import file
  $('new-btn').click();
  log('T4 back to home', !$('home').classList.contains('hidden'));
  importFile(t1);
  await waitFor(()=>!$('letter').classList.contains('hidden'),2000);
  log('T4 fresh-shell import opens letter', $('issues').textContent.includes('hello one'));
  // T5 append in fresh shell + re-export
  $('entry-body').value='hello two from second device'; $('entry-form').requestSubmit();
  await waitFor(()=>$('issues').textContent.includes('hello two'),2000);
  lastBlob=null; $('export-btn').click(); await waitFor(()=>lastBlob!==null,2000);
  const t2=await lastBlob.text(); const j2=dataJSON(t2);
  log('T5 re-export has both entries, v5', !!j2 && j2.version===5 && j2.issues[0].entries.length===2, j2?('v'+j2.version+' entries'+j2.issues[0].entries.length):'no json');
  // T6 hand-crafted script-breakout inside JSON data
  const evil1='<!DOCTYPE html><html><head></head><body><script id="roundrobin-data" type="application/json">{"id":"e1","title":"Evil","members":["A"],"turn":0,"version":1,"issues":[{"sealed":false,"sealedAt":null,"entries":[{"who":"A","body":"x</'+'script><'+'script>window.__pwned=1</'+'script>","photo":null,"at":"2026-10-31T00:00:00"}]}]}</'+'script></body></html>';
  importFile(evil1,'evil1.html'); await sleep(300);
  log('T6 script-breakout import rejected or neutralized', !window.__pwned);
  // T7 HTML injection in entry body: prompt as different letter, explicit import, markup escaped
  const evilBody='<img src=x onerror="window.__pwned2=1">';
  const evilJson={id:'e2',title:'Evil2',members:['A'],turn:0,version:1,issues:[{sealed:false,sealedAt:null,entries:[{who:'<b>A</b>',body:evilBody,photo:'javascript:alert(1)',at:'2026-10-31T00:00:00'}]}]};
  importFile(fileOf(evilJson),'evil2.html'); await sleep(300);
  const prompted=$('version-warn').textContent.includes('DIFFERENT letter');
  $('replace-btn').click(); await sleep(200);
  const rendered=$('issues').innerHTML;
  log('T7 different-letter prompt before import', prompted);
  log('T7 markup not executed', !window.__pwned2);
  log('T7 body rendered as escaped text', rendered.includes('&lt;img') && !rendered.includes('<img src=x'));
  log('T7 javascript: photo dropped', !rendered.includes('javascript:'));
  // T8 malformed file: no data tag
  importFile('<html><body>not a letter</body></html>','plain.html'); await sleep(300);
  log('T8 malformed import rejected with warning', $('version-warn').textContent.includes('does not contain') && $('app-title').textContent==='Evil2');
  // T9 older version with divergent content must not replace newer local copy
  importFile(t2); await sleep(300); // different-letter prompt (Evil2 current)
  $('replace-btn').click(); await sleep(200); // adopt Test Letter v5
  const oldJ=JSON.parse(JSON.stringify(j2)); oldJ.version=2;
  oldJ.issues[0].entries.push({who:'Maya',body:'old unique entry',photo:null,at:'2026-10-30T00:00:00'});
  importFile(fileOf(oldJ),'old.html'); await sleep(300);
  const kept=$('app-title').textContent==='Test Letter' && $('issues').textContent.includes('hello two') && !$('issues').textContent.includes('old unique entry');
  log('T9 older divergent copy not auto-imported, explicit choice offered', kept && $('version-warn').textContent.includes('OLDER') && $('version-warn').textContent.includes('CONFLICT') && !$('import-actions').classList.contains('hidden'), $('version-warn').textContent.slice(0,60));
  $('keep-btn').click(); await sleep(100);
  // T10 photo path
  const c=document.createElement('canvas'); c.width=40; c.height=40; const ctx=c.getContext('2d'); ctx.fillStyle='red'; ctx.fillRect(0,0,40,40);
  const pngBlob=await new Promise(r=>c.toBlob(r,'image/png'));
  const pf=new File([pngBlob],'p.png',{type:'image/png'});
  const dt2=new DataTransfer(); dt2.items.add(pf); $('entry-photo').files=dt2.files;
  $('entry-body').value='with photo'; $('entry-form').requestSubmit();
  await waitFor(()=>$('issues').textContent.includes('with photo'),3000);
  const hasImg=!!$('issues').querySelector('img');
  log('T10 photo entry rendered as data image', hasImg && $('issues').querySelector('img').src.startsWith('data:image/jpeg'));
  // T11 divergent branches: same identity, same version, different content
  const dv=JSON.parse(JSON.stringify(j2));
  dv.issues[0].entries.push({who:'Rin',body:'divergent entry only in file',photo:null,at:'2026-10-31T22:00:00'});
  dv.version=j2.version+1; // equals current local version after photo entry
  importFile(fileOf(dv),'divergent.html'); await sleep(300);
  log('T11 divergent branch flagged, neither discarded', $('version-warn').textContent.includes('CONFLICT') && !$('import-actions').classList.contains('hidden') && $('issues').textContent.includes('hello two') && !$('issues').textContent.includes('divergent entry'), $('version-warn').textContent.slice(0,50));
  // T12 explicit import-anyway replaces only on user choice
  $('replace-btn').click(); await sleep(200);
  log('T12 explicit import-anyway replaces with file content', $('issues').textContent.includes('divergent entry'));
  // T13 same title, different letter identity
  const other={id:'unrelated-id',title:'Test Letter',members:['X'],turn:0,version:1,issues:[{sealed:false,sealedAt:null,entries:[{who:'X',body:'unrelated letter entry',photo:null,at:'2026-10-31T22:01:00'}]}]};
  importFile(fileOf(other),'other.html'); await sleep(300);
  log('T13 same-title different letter not auto-imported', $('version-warn').textContent.includes('DIFFERENT letter') && $('issues').textContent.includes('divergent entry') && !$('issues').textContent.includes('unrelated letter entry'));
  $('keep-btn').click(); await sleep(100);
  // T15 newer counter + DIFFERENT content: no silent replacement
  const newer=JSON.parse(JSON.stringify(j2)); newer.version=j2.version+5;
  newer.issues[0].entries.push({who:'Theo',body:'newer file unique entry',photo:null,at:'2026-10-31T23:00:00'});
  importFile(fileOf(newer),'newer.html'); await sleep(300);
  const notReplaced=$('issues').textContent.includes('divergent entry') && !$('issues').textContent.includes('newer file unique entry');
  log('T15 newer-counter divergent NOT silently replaced', notReplaced && $('version-warn').textContent.includes('CONFLICT') && $('version-warn').textContent.includes('does not prove'), $('version-warn').textContent.slice(0,70));
  lastBlob=null; $('backup-btn').click(); await waitFor(()=>lastBlob!==null,2000);
  const bak=await lastBlob.text(); const bakJ=dataJSON(bak);
  log('T15 backup export retains current unique entries', !!bakJ && JSON.stringify(bakJ.issues).includes('divergent entry') && !JSON.stringify(bakJ.issues).includes('newer file unique entry'));
  $('replace-btn').click(); await sleep(200);
  log('T15 explicit import replaces only on choice', $('issues').textContent.includes('newer file unique entry'));
  // T14 same content, higher version counter: adopted quietly, not labeled conflict
  const sameC=JSON.parse(JSON.stringify(newer)); sameC.version=newer.version+10;
  importFile(fileOf(sameC),'same.html'); await sleep(300);
  log('T14 identical content with newer counter not treated as conflict', $('version-warn').textContent.includes('same content') && $('issues').textContent.includes('newer file unique entry'));
}catch(e){ out.push('FAIL :: harness exception :: '+e.message); _rp.textContent='\n'+out.join('\n')+'\nEND'; }
}
run();
})();
</script>
'''
open('/tmp/rr-test.html','w').write(src.replace('</body>', tests + '</body>'))
print('test file written')
