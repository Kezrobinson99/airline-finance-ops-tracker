const API='airline-finance-ops-tracker-production.up.railway.app';
export async function apiGet(p){const r=await fetch(API+p); if(!r.ok)throw new Error(await r.text()); return r.json()}
export async function apiPost(p,b={}){const r=await fetch(API+p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}); if(!r.ok)throw new Error(await r.text()); return r.json()}
export const money=v=>new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',maximumFractionDigits:0}).format(v||0);
