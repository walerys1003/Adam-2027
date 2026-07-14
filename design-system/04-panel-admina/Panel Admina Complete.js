/* ============================================
   Panel Admina Complete — Router
   ============================================ */

const SCREENS = {
  dashboard:  { label: 'Dashboard',       crumb: 'Dashboard',         cta: '+ Nowy agent' },
  seniors:    { label: 'Seniorzy',        crumb: 'Seniorzy',          cta: '+ Dodaj seniora' },
  calls:      { label: 'Call History',    crumb: 'Call History',      cta: 'Eksport CSV' },
  scheduling: { label: 'Call Scheduling', crumb: 'Call Scheduling',   cta: '+ Nowa kampania' },
  alerts:     { label: 'Alerty',          crumb: 'Alerty',            cta: 'Assign koordynator' },
  marketplace:{ label: 'Marketplace',     crumb: 'Marketplace · Concierge', cta: '+ Nowe zamówienie' },
  wizard:     { label: 'Setup Wizard',    crumb: 'Setup Wizard',      cta: 'Uruchom kreator' },
  agents:     { label: 'Agenci',          crumb: 'Agenci · Multi-Agent', cta: '+ Nowy agent' },
  providers:  { label: 'Providers',       crumb: 'Providers',         cta: '+ Dodaj provider' },
  pipelines:  { label: 'Pipelines',       crumb: 'Pipelines',         cta: '+ Nowy pipeline' },
  contexts:   { label: 'Contexts',        crumb: 'Contexts (legacy)', cta: '+ Nowy kontekst' },
  profiles:   { label: 'Audio Profiles',  crumb: 'Audio Profiles',    cta: '+ Nowy profil' },
  tools:      { label: 'Tools',           crumb: 'Tools · 4 phases',  cta: '+ Nowe narzędzie' },
  mcp:        { label: 'MCP Servers',     crumb: 'MCP Servers',       cta: '+ Dodaj serwer MCP' },
  wearables:  { label: 'Wearables Fleet', crumb: 'Wearables Fleet',   cta: 'Force sync all' },
  env:        { label: 'Environment',     crumb: 'Environment',       cta: 'Zapisz zmiany' },
  docker:     { label: 'Docker Services', crumb: 'Docker Services',   cta: 'Restart all' },
  asterisk:   { label: 'Asterisk',        crumb: 'Asterisk · ARI',    cta: 'Test connection' },
  models:     { label: 'Models',          crumb: 'Models catalog',    cta: '+ Dodaj model' },
  logs:       { label: 'Live Logs',       crumb: 'Live Logs',         cta: 'Pobierz logs' },
  terminal:   { label: 'Terminal',        crumb: 'Web Terminal',      cta: 'Wyczyść' },
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function switchScreen(id) {
  if (!SCREENS[id]) id = 'dashboard';
  const meta = SCREENS[id];

  // Sidebar active state
  $$('.side-nav a').forEach(a => a.classList.toggle('active', a.dataset.screen === id));

  // Breadcrumb + CTA
  $('#crumb-cur').textContent = meta.crumb;
  $('#primary-cta').textContent = meta.cta;

  // Persist to localStorage
  try { localStorage.setItem('adam-admin-screen', id); } catch(_) {}

  // Render screen
  const container = $('#content');
  container.innerHTML = SCREEN_RENDERERS[id] ? SCREEN_RENDERERS[id]() : `
    <div class="content-inner">
      <div class="page-head"><div><h1 class="h">${meta.label}</h1></div></div>
      <div class="empty"><div class="icon">🧱</div><h3>W budowie</h3><p>Ten ekran zostanie dodany w kolejnej iteracji.</p></div>
    </div>`;

  // Wire up subtabs inside
  $$('.subtab', container).forEach(tab => {
    tab.addEventListener('click', () => {
      const parent = tab.parentElement;
      $$('.subtab', parent).forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetId = tab.dataset.tab;
      const wrap = parent.parentElement;
      $$('.subtab-panel', wrap).forEach(p => p.classList.toggle('active', p.id === 'tp-' + targetId));
    });
  });

  // Detail-view back links
  $$('.js-back', container).forEach(el => {
    el.addEventListener('click', (e) => { e.preventDefault(); switchScreen(el.dataset.back || 'dashboard'); });
  });

  // Row-click drill-down (senior/agent/provider details)
  $$('[data-drill]', container).forEach(el => {
    el.addEventListener('click', () => {
      const target = el.dataset.drill;
      const rendered = DETAIL_RENDERERS[target];
      if (rendered) {
        container.innerHTML = rendered(el.dataset.drillArg || '');
        // re-bind
        $$('.subtab', container).forEach(tab => {
          tab.addEventListener('click', () => {
            const parent = tab.parentElement;
            $$('.subtab', parent).forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.dataset.tab;
            const wrap = parent.parentElement;
            $$('.subtab-panel', wrap).forEach(p => p.classList.toggle('active', p.id === 'tp-' + targetId));
          });
        });
        $$('.js-back', container).forEach(elBack => {
          elBack.addEventListener('click', (e) => { e.preventDefault(); switchScreen(elBack.dataset.back || 'dashboard'); });
        });
        // reset scroll
        window.scrollTo({ top: 0, behavior: 'instant' });
      }
    });
  });

  // Reset scroll on screen switch
  window.scrollTo({ top: 0, behavior: 'instant' });
}

// Wire up sidebar clicks (immediate, since scripts are at end of body)
function initAdminPanel() {
  $$('.side-nav a').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const id = a.dataset.screen;
      if (id) switchScreen(id);
    });
  });

  // Restore
  let initial = 'dashboard';
  try {
    const saved = localStorage.getItem('adam-admin-screen');
    if (saved && SCREENS[saved]) initial = saved;
  } catch(_) {}
  switchScreen(initial);
}

/* ============================================
   SCREEN RENDERERS (stubs — real impl below)
   Each returns HTML string
   ============================================ */
const SCREEN_RENDERERS = {};
const DETAIL_RENDERERS = {};
