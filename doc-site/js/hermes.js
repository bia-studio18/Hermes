document.addEventListener('DOMContentLoaded', () => {
  initMobile();
  initSearch();
  initCopy();
  initToc();
  initSidebarActive();
});

function initMobile() {
  const t = document.querySelector('.d-mobile-toggle');
  const s = document.querySelector('.d-sidebar');
  const o = document.querySelector('.d-sidebar-overlay');
  if (!t) return;
  t.addEventListener('click', () => { s?.classList.toggle('open'); o?.classList.toggle('open'); });
  o?.addEventListener('click', () => { s?.classList.remove('open'); o.classList.remove('open'); });
  document.querySelectorAll('.d-sidebar-link').forEach(l => l.addEventListener('click', () => { s?.classList.remove('open'); o?.classList.remove('open'); }));
}

function initSearch() {
  const ov = document.querySelector('.search-overlay');
  const inp = document.querySelector('.search-modal-input input');
  const res = document.querySelector('.search-modal-results');
  if (!ov) return;
  const idx = [
    { t:'Introduction', s:'Getting Started', u:'docs/introduction/index.html', d:'What is Hermes', k:['introduction','overview','what is'] },
    { t:'Installation', s:'Getting Started', u:'docs/installation/index.html', d:'Install Hermes', k:['install','pip','setup','requirements'] },
    { t:'Quickstart', s:'Getting Started', u:'docs/quickstart/index.html', d:'First Hermes workflow', k:['quickstart','first steps','tutorial'] },
    { t:'Data Acquisition', s:'Core Concepts', u:'docs/concepts/data-acquisition.html', d:'Fetch and acquire data', k:['acquisition','fetch','ingest','data'] },
    { t:'Connectors', s:'Core Concepts', u:'docs/concepts/connectors.html', d:'External data sources', k:['connector','binance','fred','world bank','sec','yfinance'] },
    { t:'Parsing', s:'Core Concepts', u:'docs/concepts/parsing.html', d:'Parse raw data formats', k:['parse','csv','json','xml','parquet'] },
    { t:'Normalization', s:'Core Concepts', u:'docs/concepts/normalization.html', d:'Normalize to canonical form', k:['normalize','standardize','mapping'] },
    { t:'Validation', s:'Core Concepts', u:'docs/concepts/validation.html', d:'Validate data quality', k:['validate','checks','quality'] },
    { t:'Entities', s:'Core Concepts', u:'docs/concepts/entities.html', d:'Entity resolution', k:['entity','resolve','country','company'] },
    { t:'Datasets', s:'Core Concepts', u:'docs/concepts/datasets.html', d:'Dataset abstraction', k:['dataset','data','load','save'] },
    { t:'Schemas', s:'Core Concepts', u:'docs/concepts/schemas.html', d:'Canonical schemas', k:['schema','canonical','field','type'] },
    { t:'Metadata', s:'Core Concepts', u:'docs/concepts/metadata.html', d:'Data metadata', k:['metadata','column','statistics'] },
    { t:'Provenance', s:'Core Concepts', u:'docs/concepts/provenance.html', d:'Data provenance', k:['provenance','source','origin'] },
    { t:'Lineage', s:'Core Concepts', u:'docs/concepts/lineage.html', d:'Data lineage', k:['lineage','operations','history'] },
    { t:'Storage', s:'Core Concepts', u:'docs/concepts/storage.html', d:'Data storage', k:['storage','parquet','duckdb','filesystem'] },
    { t:'Querying', s:'Core Concepts', u:'docs/concepts/querying.html', d:'Query data', k:['query','filter','sql'] },
    { t:'Python API', s:'API Reference', u:'docs/api/index.html', d:'Complete API reference', k:['api','python','function','method'] },
    { t:'CLI Reference', s:'CLI', u:'docs/cli/index.html', d:'Command-line interface', k:['cli','command','terminal'] },
    { t:'Architecture', s:'Architecture', u:'docs/architecture/index.html', d:'System architecture', k:['architecture','structure','design'] },
    { t:'Development', s:'Development', u:'docs/development/index.html', d:'Dev setup and workflow', k:['development','setup','testing'] },
    { t:'Contributing', s:'Contributing', u:'docs/contributing/index.html', d:'Contribution guide', k:['contributing','guidelines','workflow'] },
  ];
  document.querySelectorAll('[data-search]').forEach(el => el.addEventListener('focus', e => { e.target.blur(); openSearch(); }));
  document.addEventListener('keydown', e => { if ((e.metaKey||e.ctrlKey)&&e.key==='k') { e.preventDefault(); openSearch(); } if (e.key==='Escape') closeSearch(); });
  ov.addEventListener('click', e => { if (e.target===ov) closeSearch(); });
  function openSearch() { ov.classList.add('open'); setTimeout(()=>inp?.focus(),50); }
  function closeSearch() { ov.classList.remove('open'); if(inp) inp.value=''; if(res) res.innerHTML=''; }
  if (inp) inp.addEventListener('input', e => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) { res.innerHTML=''; return; }
    const r = idx.filter(p => p.t.toLowerCase().includes(q)||p.d.toLowerCase().includes(q)||p.k.some(k=>k.includes(q))).slice(0,8);
    if (!r.length) { res.innerHTML='<div class="search-empty">No results</div>'; return; }
    res.innerHTML = r.map(x=>`<a href="${x.u}" class="search-result"><div class="search-result-page">${x.s}</div><div>${x.t}</div></a>`).join('');
  });
}

function initCopy() {
  document.querySelectorAll('.codeblock-cp').forEach(b => {
    b.addEventListener('click', () => {
      const pre = b.closest('.codeblock').querySelector('pre');
      if (!pre) return;
      navigator.clipboard.writeText(pre.textContent).then(() => {
        const o = b.textContent; b.textContent = 'copied'; setTimeout(()=>b.textContent=o, 1200);
      });
    });
  });
}

function initToc() {
  const links = document.querySelectorAll('.d-toc-link');
  if (!links.length) return;
  const heads = [];
  links.forEach(l => { const id = l.getAttribute('href')?.replace('#',''); const h = document.getElementById(id); if(h) heads.push({el:h,link:l}); });
  if (!heads.length) return;
  const obs = new IntersectionObserver(es => {
    es.forEach(e => { if(e.isIntersecting) { links.forEach(l=>l.classList.remove('active')); const m=heads.find(h=>h.el===e.target); if(m) m.link.classList.add('active'); } });
  }, { rootMargin: '-60px 0px -70% 0px' });
  heads.forEach(h => obs.observe(h.el));
}

function initSidebarActive() {
  const page = window.location.pathname;
  document.querySelectorAll('.d-sidebar-link').forEach(l => {
    const href = l.getAttribute('href');
    if (href && page.endsWith(href.replace(/^\.\.?\/?/, ''))) l.classList.add('active');
  });
}
