// tiny in-memory stand-in for the Firebase compat SDK, for tests only
(function(){const DEL={__del:1},ST={__st:1},D=window.__DB=window.__DB||{};const col=n=>D[n]=D[n]||{};
const fix=o=>{const r={};for(const k in o){const v=o[k];if(v===ST)r[k]=new Date();else if(v&&typeof v==='object'&&!(v instanceof Date)&&!Array.isArray(v)&&v!==DEL)r[k]=fix(v);else r[k]=v}return r};
const merge=(a,b)=>{for(const k in b){if(b[k]&&typeof b[k]==='object'&&!(b[k] instanceof Date)&&!Array.isArray(b[k])){a[k]=merge(a[k]&&typeof a[k]==='object'?a[k]:{},b[k])}else a[k]=b[k]}return a};
const snap=(n,id)=>({id,exists:id in col(n),data:()=>col(n)[id],ref:{delete:()=>{delete col(n)[id];return Promise.resolve()},update:o=>{Object.assign(col(n)[id],o);return Promise.resolve()}}});
const Q=(n,fs=[],lim=1e9,ord=null)=>({where:(k,op,v)=>Q(n,[...fs,[k,op,v]],lim,ord),orderBy:(k,d)=>Q(n,fs,lim,[k,d]),limit:l=>Q(n,fs,l,ord),
 _run(){const val=x=>x instanceof Date?x.getTime():x;let ids=Object.keys(col(n)).filter(id=>fs.every(([k,op,v])=>{const a=val(col(n)[id][k]),b=val(v);return op==='=='?a===b:op==='>'?a>b:op==='>='?a>=b:op==='<='?a<=b:a<b}));
  if(ord)ids.sort((x,y)=>(val(col(n)[x][ord[0]])-val(col(n)[y][ord[0]]))*(ord[1]==='desc'?-1:1));return ids.slice(0,lim)},
 get(){window.__READS=(window.__READS||0)+1;const ids=this._run();return Promise.resolve({size:ids.length,docs:ids.map(id=>snap(n,id))})},count(){const self=this;return{get:()=>Promise.resolve({data:()=>({count:self._run().length})})}},
 doc:id=>({get:()=>Promise.resolve(snap(n,id)),set:(o,opt)=>{col(n)[id]=opt&&opt.merge?merge(col(n)[id]||{},fix(o)):fix(o);return Promise.resolve()},
  update:o=>{for(const k in o){const p=k.split('.');let t=col(n)[id]=col(n)[id]||{};while(p.length>1){const q=p.shift();t=t[q]=t[q]||{}}if(o[k]===DEL)delete t[p[0]];else t[p[0]]=o[k]}return Promise.resolve()},delete:()=>{delete col(n)[id];return Promise.resolve()}}),
 add:o=>{const id='id'+Math.random().toString(36).slice(2,10);col(n)[id]=fix(o);return Promise.resolve({id})}});
let user=window.__USER||null,cbs=[];const auth={get currentUser(){return user},onAuthStateChanged(cb){cbs.push(cb);setTimeout(()=>cb(user),0);return()=>{}},signInWithPopup(){user=window.__USER2||{uid:'owner',email:'owner@example.com'};cbs.forEach(c=>c(user));return Promise.resolve({user})},signOut(){user=null;cbs.forEach(c=>c(null));return Promise.resolve()}};
const fsf=()=>({collection:n=>{if(window.__DENY&&window.__DENY.includes(n)){const e=()=>Promise.reject({code:'permission-denied'});return{limit:()=>({get:e}),get:e,orderBy:()=>({limit:()=>({get:e})}),doc:()=>({get:e,set:e})}}return Q(n)}});
fsf.FieldValue={serverTimestamp:()=>ST,delete:()=>DEL};const dbf=()=>({});
window.firebase={apps:[],initializeApp(){this.apps.push(1)},auth:Object.assign(()=>auth,{GoogleAuthProvider:function(){}}),firestore:fsf,database:dbf}})();
