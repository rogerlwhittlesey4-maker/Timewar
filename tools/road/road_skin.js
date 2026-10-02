/* ===================================================================
   THE ROAD — the year 1526 laid over the old engine.
   Nothing below changes a rule, a number or a key: the old world's
   data stays what it was and the save is the same save. This script
   only changes what the eye sees — every name, every place, every
   people — and bridges the Chronicle's grind into the Road's energy.
   =================================================================== */
(function(){
"use strict";
const SK = JSON.parse(document.getElementById("road-skin-data").textContent);
const RE = new RegExp(SK.re, "gi");
const MAP = SK.map;
const INBOX = "timewar_road_inbox_v1";

/* ---- the word-for-word skin ---- */
function fix(s){
  if(!s || !/[A-Za-z]/.test(s)) return s;
  return s.replace(RE, function(m, off){
    const e = MAP[m.toLowerCase()]; if(!e) return m;
    let v = e[0]; const proper = e[1];
    if(v.length > 4 && v.slice(0, 4).toLowerCase() === "the " && off >= 4 && s.slice(off - 4, off).toLowerCase() === "the ") v = v.slice(4);
    const c0 = m.charAt(0), up0 = c0 === c0.toUpperCase() && c0 !== c0.toLowerCase();
    if(proper && !up0){ const sp = m.indexOf(" "); return sp > 0 ? m.slice(0, sp + 1) + fix(m.slice(sp + 1)) : m; }
    if(m.length > 1 && m === m.toUpperCase() && /[A-Z]/.test(m)) return v.toUpperCase();
    if(!proper && up0){ const ws = v.split(" "); return ws.length <= 3 ? ws.map(function(w){ return w ? w.charAt(0).toUpperCase() + w.slice(1) : w; }).join(" ") : v.charAt(0).toUpperCase() + v.slice(1); }
    return v;
  });
}
window.roadFix = fix;

const SKIP = { SCRIPT:1, STYLE:1, TEXTAREA:1, INPUT:1 };
function skinText(n){
  const t = n.nodeValue; if(!t || !/[A-Za-z]/.test(t)) return;
  const p = n.parentNode; if(p && SKIP[p.nodeName]) return;
  const u = fix(t); if(u !== t) n.nodeValue = u;
}
function skinAttrs(el){
  for(const a of ["title","placeholder","aria-label"]){
    if(el.hasAttribute && el.hasAttribute(a)){ const t = el.getAttribute(a), u = fix(t); if(u !== t) el.setAttribute(a, u); }
  }
}
function skinNode(root){
  if(root.nodeType === 3){ skinText(root); return; }
  if(root.nodeType !== 1 && root.nodeType !== 11) return;
  if(root.nodeType === 1){ if(SKIP[root.nodeName]) return; skinAttrs(root); }
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null);
  let n;
  while((n = w.nextNode())){
    if(n.nodeType === 1){ skinAttrs(n); continue; }
    skinText(n);
  }
}
const mo = new MutationObserver(function(muts){
  for(const m of muts){
    if(m.type === "characterData"){ skinText(m.target); continue; }
    if(m.type === "attributes"){ skinAttrs(m.target); continue; }
    for(const n of m.addedNodes) skinNode(n);
  }
});
function startObserver(){
  skinNode(document.body);
  mo.observe(document.body, { childList:true, subtree:true, characterData:true, attributes:true, attributeFilter:["title","placeholder","aria-label"] });
}
document.title = "The Road — Europe, 1526";
if(document.body) startObserver(); else document.addEventListener("DOMContentLoaded", startObserver);

/* dialogs the engine raises */
const _confirm = window.confirm, _prompt = window.prompt, _alert = window.alert;
window.confirm = function(msg){ return _confirm.call(window, fix(String(msg))); };
window.prompt = function(msg, def){ return _prompt.call(window, fix(String(msg)), def); };
window.alert = function(msg){ return _alert.call(window, fix(String(msg))); };

/* ---- the data the eye reads: places, peoples, callings ---- */
function patchData(){
  if(typeof DATA === "undefined" || !DATA || DATA._road) return;
  DATA._road = 1;
  for(const z of DATA.zones){ const p = SK.zones[z.key]; if(p){ z.name = p[0]; z.desc = p[1]; } }
  for(const hb of DATA.hubs){ const t = SK.hubs[hb.key]; if(t) hb.town = t; }
  for(const r in SK.races){ if(DATA.races[r]){ DATA.races[r].name = SK.races[r][0]; DATA.races[r].portrait = SK.races[r][1]; } }
  for(const c in SK.classes){ if(DATA.classes[c]) DATA.classes[c].name = SK.classes[c]; }
  try{
    for(const R of WORLD){ const p = SK.regions[R.name]; if(p){ R.name = p[0]; R.cont = p[1]; R.sub = p[2]; } for(const Z of R.zones){ if(SK.wzones[Z.name]) Z.name = SK.wzones[Z.name]; } }
    for(const k in ZW){ const e = ZW[k]; const p = SK.regions[e.region]; if(p){ e.region = p[0]; e.cont = p[1]; e.sub = p[2]; } if(SK.wzones[e.zone]) e.zone = SK.wzones[e.zone]; }
  }catch(e){}
}

/* ---- money in the coin of 1526: the old copper is a farthing ---- */
coinStr = function(c){
  c = Math.max(0, Math.round(c));
  const d = Math.floor(c / 4), f = c % 4;
  const L = Math.floor(d / 240), s = Math.floor((d % 240) / 12), p = d % 12;
  const fr = ["", "¼", "½", "¾"][f];
  const out = [];
  if(L) out.push('<span class="coin-g">£' + L.toLocaleString() + '</span>');
  if(s || L) out.push('<span class="coin-s">' + s + 's</span>');
  out.push('<span class="coin-c">' + p + fr + 'd</span>');
  return out.join(" ");
};

/* ---- the banner ---- */
function banner(){
  if(document.getElementById("road-banner")) return;
  const w = document.querySelector(".wrap"); if(!w) return;
  const b = document.createElement("div"); b.id = "road-banner";
  b.innerHTML = 'THE ROAD &nbsp;·&nbsp; <b>Europe, Anno Domini 1526</b> &nbsp;·&nbsp; England to the tenth level, then the world';
  w.insertBefore(b, w.firstChild);
}

/* ---- the Chronicle's grind comes in by the inbox ---- */
function ensureExercise(name, e, m){
  if(!S || !S.settings) return false;
  S.settings.exercises = S.settings.exercises || [];
  if(S.settings.exercises.some(x => x.name === name)) return true;
  if(!(e > 0)) return false;
  S.settings.exercises.push({ name:name, e:+e, m:+(m || 0) });
  return true;
}
function drainInbox(why){
  if(typeof S === "undefined" || !S || !S.settings) return 0;
  let list = [];
  try{ list = JSON.parse(localStorage.getItem(INBOX) || "[]") || []; }catch(e){ list = []; }
  if(!list.length) return 0;
  S.roadInboxDone = S.roadInboxDone || [];
  const done = new Set(S.roadInboxDone);
  let n = 0, gained = 0, mins = 0;
  for(const it of list){
    if(!it || !it.id || done.has(it.id)) continue;
    try{
      if(it.kind === "ex" && it.units > 0){ if(ensureExercise(it.name, it.e, it.m)){ gained += logExercise(it.name, it.units) || 0; n++; } }
      else if(it.kind === "study" && it.min > 0){ logStudy(it.cat, it.min); mins += it.min; n++; }
    }catch(e){}
    done.add(it.id);
  }
  if(n){
    S.roadInboxDone = Array.from(done).slice(-600);
    try{ save(); }catch(e){}
    try{ render(); }catch(e){}
    try{ toast("From the Chronicle: " + n + " entr" + (n === 1 ? "y" : "ies") + " — " + (gained ? "+" + gained + " vigour" : "") + (gained && mins ? ", " : "") + (mins ? "+" + mins + " min devotion" : ""), "ding"); }catch(e){}
  }
  return n;
}
window.roadDrainInbox = drainInbox;
window.addEventListener("storage", function(ev){ if(ev.key === INBOX) setTimeout(function(){ drainInbox("storage"); }, 50); });
document.addEventListener("visibilitychange", function(){ if(!document.hidden) drainInbox("visible"); });

/* ---- hooks on the engine ---- */
const _render = render;
let _first = true;
render = function(){
  patchData();
  banner();
  const r = _render.apply(this, arguments);
  if(_first && typeof S !== "undefined" && S){ _first = false; setTimeout(function(){ drainInbox("boot"); }, 0); }
  return r;
};
const _showCreate = showCreate;
showCreate = function(){ patchData(); return _showCreate.apply(this, arguments); };
})();
