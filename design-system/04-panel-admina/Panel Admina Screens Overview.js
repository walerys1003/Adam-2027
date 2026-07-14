/* ============================================
   OVERVIEW SCREENS
   Dashboard · Seniorzy · Call History · Call Scheduling · Alerty · Wizard
   ============================================ */

/* ------------ DASHBOARD ------------ */
SCREEN_RENDERERS.dashboard = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Operations · <em>Wtorek 12 lipca</em></h1>
      <div class="sub">
        <span class="live">Live · 5s refresh</span>
        <span class="sep">·</span><span>Region: EU-Central-1 · Frankfurt</span>
        <span class="sep">·</span><span>Ostatni deploy: 2 dni temu</span>
        <span class="sep">·</span><span>Koordynator: Krzysztof M.</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Eksport CSV</button>
      <button class="btn btn-ghost">Runbook</button>
      <button class="btn btn-primary">Setup Wizard →</button>
    </div>
  </div>

  <!-- STATUS BAR -->
  <div style="background:var(--paper);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 2px rgba(14,26,46,0.03)">
    <div style="height:3px;background:linear-gradient(90deg,var(--zloto-500),var(--zloto-300),var(--zloto-500))"></div>
    <div style="padding:12px 20px;background:var(--paper-2);border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:center;gap:24px">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:22px;height:22px;border-radius:50%;background:var(--sem-green-bg);display:grid;place-items:center;color:var(--sem-green)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg></div>
        <div style="font-family:var(--serif);font-size:15px;color:var(--sem-green);font-weight:500">System Ready</div>
        <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em;padding:2px 8px;background:white;border:1px solid var(--line);border-radius:4px">14 checks passed</div>
      </div>
      <div style="width:1px;height:24px;background:var(--line-strong)"></div>
      <div style="display:flex;flex-wrap:wrap;gap:20px;align-items:center;font-size:12px">
        ${['OS: ubuntu 24.04','AAVA: 7.4.2','Docker: 27.3.1','Compose: 2.29.7','SSL: Valid · 87d'].map(t => {
          const [k,v] = t.split(': ');
          return `<div style="display:flex;align-items:baseline;gap:6px"><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">${k}:</span><span style="font-family:var(--mono);font-size:11.5px;color:var(--granat-900);font-weight:500">${v}</span></div>`;
        }).join('')}
      </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(5,1fr)">
      ${[
        {icPath:'<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3"/>', color:'blue', lbl:'CPU', val:'34.2%', sub:'16 rdzeni · Xeon E5', bar:34},
        {icPath:'<rect x="2" y="8" width="20" height="8" rx="1"/><path d="M6 8v8M10 8v8M14 8v8M18 8v8"/>', color:'green', lbl:'Memory', val:'58.4%', sub:'37.4 / 64 GB', bar:58},
        {icPath:'<rect x="2" y="14" width="20" height="7" rx="1"/><rect x="2" y="3" width="20" height="7" rx="1"/><path d="M6 6.5h.01M6 17.5h.01"/>', color:'orange', lbl:'Disk', val:'42.1%', sub:'1.16 TB wolne', bar:42},
        {icPath:'<path d="M22 16.9v3a2 2 0 01-2.2 2 20 20 0 01-8.6-3.1 20 20 0 01-6-6 20 20 0 01-3.1-8.7A2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.7a2 2 0 01-.5 2.1L7.9 9.8a16 16 0 006 6l1.2-1.3a2 2 0 012.1-.5c.9.3 1.8.5 2.7.6a2 2 0 011.7 2z"/>', color:'green', lbl:'Asterisk · ARI', val:'Connected', sub:'17 kanałów aktywnych', isText:true},
        {icPath:'<path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/><path d="M9 13l2 2 4-4"/>', color:'green', lbl:'Audio Dirs', val:'Healthy', sub:'3/3 checks passed', isText:true},
      ].map((m,i) => {
        const colors = {blue:{bg:'#dbeafe',fg:'#2563eb'}, green:{bg:'var(--sem-green-bg)',fg:'var(--sem-green)'}, orange:{bg:'rgba(234,88,12,0.1)',fg:'#ea580c'}};
        const c = colors[m.color];
        return `
        <div style="padding:16px 20px;border-right:${i<4?'1px solid var(--line)':'none'};display:flex;align-items:center;gap:14px">
          <div style="width:36px;height:36px;border-radius:8px;background:${c.bg};color:${c.fg};display:grid;place-items:center;flex-shrink:0"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">${m.icPath}</svg></div>
          <div style="flex:1;min-width:0">
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">${m.lbl}</div>
            <div style="font-family:${m.isText?'var(--sans)':'var(--serif)'};font-size:${m.isText?'16':'22'}px;color:${m.isText?c.fg:'var(--granat-900)'};font-weight:${m.isText?'600':'500'};letter-spacing:-0.015em;margin-top:2px;line-height:1">${m.val}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;letter-spacing:0.02em">${m.sub}</div>
            ${m.bar ? `<div style="height:3px;background:var(--line);border-radius:999px;overflow:hidden;margin-top:6px"><div style="height:100%;background:${c.fg};width:${m.bar}%;border-radius:999px"></div></div>` : ''}
          </div>
        </div>
      `;}).join('')}
    </div>
  </div>

  <!-- KPI STRIP -->
  <div class="section-hd"><h2>Wskaźniki biznesowe · <em>ostatnie 24h</em></h2>
    <div class="n-tabs"><button>1h</button><button class="on">24h</button><button>7d</button><button>30d</button></div>
  </div>
  <div class="kpi-strip">
    <div class="kpi"><div class="lbl">Aktywne rozmowy</div><div class="val">17</div><div class="foot pos">↗ +3 vs 15min</div><svg class="spark" viewBox="0 0 56 20" fill="none"><path d="M0 15L9 12L18 14L27 10L36 12L45 8L56 6" stroke="var(--sem-green)" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg></div>
    <div class="kpi"><div class="lbl">Rozmowy dziś</div><div class="val">2,347</div><div class="foot pos">↗ +14%</div><svg class="spark" viewBox="0 0 56 20" fill="none"><path d="M0 18L9 15L18 12L27 14L36 10L45 7L56 5" stroke="var(--zloto-500)" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg></div>
    <div class="kpi"><div class="lbl">Seniorzy aktywni</div><div class="val">1,247</div><div class="foot pos">↗ +8 dzień</div></div>
    <div class="kpi"><div class="lbl">Alerty · 24h</div><div class="val">23</div><div class="foot">14y · 8r · <span style="color:var(--sem-purple)">1p</span></div></div>
    <div class="kpi"><div class="lbl">MTTA średni</div><div class="val">14<sub>s</sub></div><div class="foot pos">↘ -4s (cel 18s)</div></div>
    <div class="kpi"><div class="lbl">Uptime 30d</div><div class="val">99.97<sub>%</sub></div><div class="foot">SLA · 43m budget</div></div>
  </div>

  <!-- LIVE FEED + SENIORS -->
  <div class="split-2-1">
    <div class="card">
      <div class="card-head">
        <div><div class="t">Rozkład dobowy rozmów</div><div class="h-sub">Peak 09:00–11:00 · welfare check poranny</div></div>
        <div class="r"><button class="btn btn-ghost btn-sm">24h</button><button class="btn btn-ghost btn-sm" style="background:var(--granat-700);color:white;border-color:var(--granat-700)">7d</button><button class="btn btn-ghost btn-sm">30d</button></div>
      </div>
      <div class="chart-area">
        <svg class="chart-svg" viewBox="0 0 700 220" preserveAspectRatio="none">
          <line class="grid" x1="30" y1="20" x2="700" y2="20"/><line class="grid" x1="30" y1="70" x2="700" y2="70"/><line class="grid" x1="30" y1="120" x2="700" y2="120"/><line class="grid" x1="30" y1="170" x2="700" y2="170"/>
          <text x="4" y="24">300</text><text x="4" y="74">200</text><text x="4" y="124">100</text><text x="4" y="174">0</text>
          <path d="M30,150 L60,100 L90,70 L120,90 L150,120 L180,135 L210,125 L240,105 L270,75 L300,45 L330,55 L360,90 L390,110 L420,95 L450,75 L480,55 L510,40 L540,70 L570,95 L600,115 L630,90 L660,65 L700,45 L700,200 L30,200 Z" fill="var(--zloto-500)" opacity="0.12"/>
          <path d="M30,150 L60,100 L90,70 L120,90 L150,120 L180,135 L210,125 L240,105 L270,75 L300,45 L330,55 L360,90 L390,110 L420,95 L450,75 L480,55 L510,40 L540,70 L570,95 L600,115 L630,90 L660,65 L700,45" stroke="var(--granat-700)" stroke-width="2" fill="none" stroke-linejoin="round"/>
          <path d="M30,190 L60,185 L90,180 L120,190 L150,192 L180,190 L210,185 L240,180 L270,168 L300,155 L330,170 L360,180 L390,175 L420,172 L450,168 L480,155 L510,140 L540,165 L570,175 L600,185 L630,180 L660,175 L700,168" stroke="var(--sem-red)" stroke-width="1.2" fill="none" stroke-linejoin="round"/>
          <line x1="425" y1="20" x2="425" y2="170" stroke="var(--zloto-500)" stroke-width="1" stroke-dasharray="2 3" opacity="0.6"/>
          <circle cx="425" cy="90" r="5" fill="var(--zloto-500)" stroke="white" stroke-width="2"/>
          <text x="432" y="36" fill="var(--zloto-700)" font-size="10">TERAZ · 217/h</text>
          <text x="30" y="212">00:00</text><text x="130" y="212">04:00</text><text x="230" y="212">08:00</text><text x="330" y="212">12:00</text><text x="430" y="212">16:00</text><text x="530" y="212">20:00</text><text x="640" y="212">24:00</text>
        </svg>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><div><div class="t">Live feed</div><div class="h-sub">SSE · 5s</div></div><span class="pip green"><span class="dot"></span>LIVE</span></div>
      <div class="feed">
        <div class="feed-item critc"><div class="feed-time"><strong>22:15</strong>LIVE</div><div><div class="feed-title"><span class="sem-icon p"></span>Semafor Purple · 112</div><div class="feed-desc">Stanisław Z. · ból w klatce + AFib</div></div></div>
        <div class="feed-item crit"><div class="feed-time"><strong>14:22</strong>3m</div><div><div class="feed-title"><span class="sem-icon r"></span>Red · potencjalny upadek</div><div class="feed-desc">Maria N. · Xiaomi Band 8</div></div></div>
        <div class="feed-item warn"><div class="feed-time"><strong>13:04</strong>1h</div><div><div class="feed-title"><span class="sem-icon y"></span>Yellow · samotność</div><div class="feed-desc">Janusz K. · „wnuki dawno nie dzwoniły"</div></div></div>
        <div class="feed-item"><div class="feed-time"><strong>12:47</strong>1h</div><div><div class="feed-title"><span class="sem-icon g"></span>Welfare check OK · 2m 41s</div><div class="feed-desc">Halina W. · mood 0.72 · leki OK</div></div></div>
        <div class="feed-item"><div class="feed-time"><strong>11:34</strong>3h</div><div><div class="feed-title"><span class="sem-icon info"></span>Deploy · adam v7.4.2</div><div class="feed-desc">Fix: „szneka" recognition · Krzysztof M.</div></div></div>
      </div>
    </div>
  </div>
</div>`;

/* ------------ SENIORS ------------ */
SCREEN_RENDERERS.seniors = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Seniorzy · <em>1247 aktywnych</em></h1>
      <div class="sub">
        <span class="live">Live sync</span>
        <span class="sep">·</span><span>3 alerty aktywne</span>
        <span class="sep">·</span><span>12 nieaktywnych &gt;7d</span>
        <span class="sep">·</span><span>8 pending onboarding</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Import CSV</button>
      <button class="btn btn-ghost">Eksport</button>
      <button class="btn btn-accent">+ Dodaj seniora</button>
    </div>
  </div>

  <!-- Filters -->
  <div class="filter-bar">
    <div class="field"><label>Semafor</label>
      <select><option>Wszystkie stany</option><option>🟢 Green (1198)</option><option>🟡 Yellow (36)</option><option>🔴 Red (12)</option><option>🟣 Purple (1)</option></select>
    </div>
    <div class="field"><label>Pakiet</label>
      <select><option>Wszystkie</option><option>Podstawowy (412)</option><option>Rodzinny (687)</option><option>Premium (148)</option></select>
    </div>
    <div class="field"><label>Dzielnica</label>
      <select><option>Poznań · wszystkie</option><option>Wilda (203)</option><option>Jeżyce (176)</option><option>Grunwald (241)</option><option>Stare Miasto (189)</option><option>Winogrady (154)</option><option>Nowe Miasto (284)</option></select>
    </div>
    <div class="field"><label>Koordynator</label>
      <select><option>Wszyscy</option><option>Krzysztof M. (312)</option><option>Anna W. (287)</option><option>Marta L. (196)</option><option>— auto (452)</option></select>
    </div>
    <div class="field"><label>Wearable</label>
      <select><option>Wszystkie</option><option>Xiaomi Band (587)</option><option>Apple Watch (198)</option><option>Garmin (89)</option><option>Fitbit (67)</option><option>Brak (306)</option></select>
    </div>
    <div style="flex:1"></div>
    <button class="chip-filter on">Aktywni <span class="x">×</span></button>
    <button class="chip-filter">Nieaktywni</button>
    <button class="chip-filter">Pending</button>
  </div>

  <!-- KPI mini -->
  <div class="grid-4" style="margin-bottom:20px">
    <div class="kpi"><div class="lbl">Aktywni</div><div class="val">1,247</div><div class="foot pos">↗ +8 dziś</div></div>
    <div class="kpi"><div class="lbl">Śr. mood</div><div class="val">0.68</div><div class="foot pos">↗ +0.03 vs 7d</div></div>
    <div class="kpi"><div class="lbl">Śr. adherence</div><div class="val">89<sub>%</sub></div><div class="foot pos">↗ +4pp</div></div>
    <div class="kpi"><div class="lbl">Alerty aktywne</div><div class="val">3</div><div class="foot neg">1 purple · 1 red · 1 yellow</div></div>
  </div>

  <div class="card">
    <div class="card-head">
      <div><div class="t">Wszyscy seniorzy · <em>alerty aktywne u góry</em></div><div class="h-sub">Sortowanie: priorytet semafora · ostatnia rozmowa</div></div>
      <div class="r"><span style="color:var(--ink-500)">Pokaż: 25 z 1247</span></div>
    </div>
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr><th>Senior</th><th>Semafor</th><th>Dzielnica</th><th>Pakiet</th><th>Mood 7d</th><th>HR / SpO₂</th><th>Leki</th><th>Ostatnia rozmowa</th><th>Wearable</th><th>Koordynator</th><th></th></tr>
        </thead>
        <tbody>
          ${SENIORS_DATA.map(s => `
            <tr data-drill="senior" data-drill-arg="${s.id}">
              <td><div class="row-name"><div class="row-av-wrap ${s.pulse||''}"><div class="row-av">${s.initials}</div></div><div><div class="n">${s.name}</div><div class="id">${s.age} lat · #${s.id}</div></div></div></td>
              <td><span class="b ${s.semColor}"><span class="dot"></span>${s.semLabel}</span></td>
              <td class="num-mono">${s.district}</td>
              <td><span class="b ${s.pkg==='Premium'?'gold':'neutral'}">${s.pkg}</span></td>
              <td><span class="num-serif ${s.moodColor||''}">${s.mood}</span></td>
              <td><span class="num-mono ${s.hrColor||''}">${s.hr}</span></td>
              <td class="num-mono ${s.medColor||''}">${s.adherence}%</td>
              <td class="num-mono">${s.lastCall}</td>
              <td><span class="num-mono muted">${s.wearable}</span></td>
              <td style="font-family:var(--mono);font-size:11px;color:${s.coord.startsWith('—')?'var(--ink-500)':'var(--granat-900)'}">${s.coord}</td>
              <td><button class="btn btn-ghost btn-sm">Otwórz →</button></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    <div style="padding:16px 24px;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.06em">
      <div>Strona 1 z 50 · pokazano 25 / 1247</div>
      <div style="display:flex;gap:4px">
        <button class="btn btn-ghost btn-sm">← Poprzednia</button>
        <button class="btn btn-primary btn-sm">1</button><button class="btn btn-ghost btn-sm">2</button><button class="btn btn-ghost btn-sm">3</button>
        <span style="padding:6px">…</span>
        <button class="btn btn-ghost btn-sm">50</button>
        <button class="btn btn-ghost btn-sm">Następna →</button>
      </div>
    </div>
  </div>
</div>`;

/* ------------ SENIOR DETAIL (koordynator view) ------------ */
const SENIORS_DATA = [
  {id:'SZ-04127',initials:'SZ',name:'Stanisław Zieliński',age:85,district:'Stare Miasto',pkg:'Premium',semColor:'purple',semLabel:'Purple · LIVE',mood:'0.12',moodColor:'purple',hr:'158/89%',hrColor:'red',adherence:91,medColor:'',lastCall:'22:12 · 3m',wearable:'Apple Watch S9',coord:'Krzysztof M.',pulse:'pulse-purple'},
  {id:'MN-02341',initials:'MN',name:'Maria Nowak',age:74,district:'Grunwald',pkg:'Rodzinny',semColor:'red',semLabel:'Red · Alarm',mood:'0.38',moodColor:'red',hr:'126/95%',hrColor:'red',adherence:88,lastCall:'14:19 · 3m',wearable:'Xiaomi Band 8',coord:'— przydziel',pulse:'pulse-red'},
  {id:'JK-08823',initials:'JK',name:'Janusz Kowalski',age:82,district:'Jeżyce',pkg:'Rodzinny',semColor:'yellow',semLabel:'Yellow · Uważaj',mood:'0.42',moodColor:'yellow',hr:'72/97%',adherence:81,lastCall:'Wcz. 20:03',wearable:'Xiaomi Band 8',coord:'Anna W.'},
  {id:'RT-05612',initials:'RT',name:'Ryszard Tomczak',age:79,district:'Winogrady',pkg:'Podstawowy',semColor:'yellow',semLabel:'Yellow · Leki',mood:'0.61',hr:'78/96%',adherence:68,medColor:'yellow',lastCall:'Dziś 12:15',wearable:'Brak',coord:'Anna W.'},
  {id:'HW-01247',initials:'HW',name:'Halina Wójcik',age:78,district:'Wilda',pkg:'Rodzinny',semColor:'green',semLabel:'Green · Spokojnie',mood:'0.72',hr:'72/97%',adherence:96,lastCall:'Dziś 08:14',wearable:'Xiaomi Band 8',coord:'— auto'},
  {id:'KB-03192',initials:'KB',name:'Krystyna Baran',age:71,district:'Nowe Miasto',pkg:'Podstawowy',semColor:'green',semLabel:'Green',mood:'0.81',hr:'68/98%',adherence:100,lastCall:'Dziś 09:02',wearable:'Fitbit Sense',coord:'— auto'},
  {id:'ZK-06771',initials:'ZK',name:'Zbigniew Krawczyk',age:69,district:'Wilda',pkg:'Rodzinny',semColor:'green',semLabel:'Green',mood:'0.75',hr:'74/97%',adherence:94,lastCall:'Dziś 09:41',wearable:'Garmin Vivosmart',coord:'— auto'},
  {id:'EM-04938',initials:'EM',name:'Ewa Michalska',age:83,district:'Grunwald',pkg:'Premium',semColor:'green',semLabel:'Green',mood:'0.69',hr:'76/96%',adherence:98,lastCall:'Dziś 08:22',wearable:'Apple Watch SE',coord:'Marta L.'},
  {id:'WS-02114',initials:'WS',name:'Wanda Sikora',age:77,district:'Jeżyce',pkg:'Rodzinny',semColor:'green',semLabel:'Green',mood:'0.71',hr:'70/97%',adherence:92,lastCall:'Dziś 09:15',wearable:'Xiaomi Band 8',coord:'— auto'},
  {id:'AS-07823',initials:'AS',name:'Andrzej Szymański',age:73,district:'Stare Miasto',pkg:'Podstawowy',semColor:'green',semLabel:'Green',mood:'0.66',hr:'80/96%',adherence:87,lastCall:'Dziś 08:47',wearable:'Brak',coord:'— auto'},
];

DETAIL_RENDERERS.senior = (id) => {
  const s = SENIORS_DATA.find(x => x.id === id) || SENIORS_DATA[4]; // fallback HW
  const semColor = s.semColor;
  return `
<div class="content-inner">
  <a href="#" class="back-link js-back" data-back="seniors">← Wróć do listy seniorów</a>

  <div class="detail-head ${semColor === 'green' ? '' : semColor}">
    <div class="detail-head-grid">
      <div class="dh-av">${s.initials}</div>
      <div class="dh-info">
        <h1>${s.name}</h1>
        <div class="meta">
          <span>${s.age} lat</span><span class="sep"></span>
          <span>${s.district}, Poznań</span><span class="sep"></span>
          <span>Pakiet <strong>${s.pkg}</strong></span><span class="sep"></span>
          <span>Wearable: ${s.wearable}</span><span class="sep"></span>
          <span class="b ${semColor}"><span class="dot"></span>${s.semLabel}</span>
        </div>
        <div class="quick-stats">
          <div class="qs"><div class="l">Mood</div><div class="v">${s.mood}<sub>/1.0</sub></div></div>
          <div class="qs"><div class="l">Adherence 30d</div><div class="v">${s.adherence}<sub>%</sub></div></div>
          <div class="qs"><div class="l">HR / SpO₂</div><div class="v">${s.hr}</div></div>
          <div class="qs"><div class="l">Rozmowy 7d</div><div class="v">14<sub>/14</sub></div></div>
          <div class="qs"><div class="l">Koordynator</div><div class="v" style="font-size:14px;font-family:var(--sans);font-weight:500">${s.coord}</div></div>
        </div>
      </div>
      <div class="dh-actions">
        <div class="last-call">Ostatnia rozmowa<strong>${s.lastCall}</strong></div>
        <button class="btn btn-primary">▶ Zadzwoń teraz</button>
        <button class="btn btn-ghost">📝 Notatka</button>
        <button class="btn btn-ghost">✉ Kontakt rodziny</button>
      </div>
    </div>
  </div>

  <div class="subtabs">
    <div class="subtab active" data-tab="over">Przegląd</div>
    <div class="subtab" data-tab="calls">Rozmowy <span class="count">147</span></div>
    <div class="subtab" data-tab="meds">Leki <span class="count">4</span></div>
    <div class="subtab" data-tab="alerts">Alerty <span class="count">3</span></div>
    <div class="subtab" data-tab="reports">Raporty</div>
    <div class="subtab" data-tab="wearable">Wearable</div>
    <div class="subtab" data-tab="family">Rodzina · RBAC</div>
    <div class="subtab" data-tab="gdpr">RODO · Zgody</div>
  </div>

  <div class="subtab-panel active" id="tp-over">
    <div class="split-2-1">
      <div>
        <div class="card">
          <div class="card-head"><div><div class="t">Nastrój · 14 dni</div><div class="h-sub">Analiza tonu głosu + treści</div></div><span class="link">7d · 14d · 30d · 90d</span></div>
          <div class="chart-area" style="height:200px">
            <svg class="chart-svg" viewBox="0 0 600 200" preserveAspectRatio="none">
              <line class="grid" x1="0" y1="40" x2="600" y2="40"/><line class="grid" x1="0" y1="100" x2="600" y2="100"/><line class="grid" x1="0" y1="160" x2="600" y2="160"/>
              <rect x="0" y="100" width="600" height="60" fill="var(--sem-yellow-bg)" opacity="0.4"/>
              <path d="M0,85 L43,72 L86,80 L129,60 L172,68 L215,55 L258,88 L301,110 L344,85 L387,68 L430,55 L473,45 L516,38 L559,32 L600,28 L600,200 L0,200 Z" fill="var(--zloto-500)" opacity="0.12"/>
              <path d="M0,85 L43,72 L86,80 L129,60 L172,68 L215,55 L258,88 L301,110 L344,85 L387,68 L430,55 L473,45 L516,38 L559,32 L600,28" stroke="var(--granat-700)" stroke-width="2" fill="none" stroke-linecap="round"/>
              <circle cx="600" cy="28" r="5" fill="var(--zloto-500)" stroke="white" stroke-width="2"/>
              <circle cx="301" cy="110" r="4" fill="var(--sem-yellow)" stroke="white" stroke-width="2"/>
            </svg>
          </div>
        </div>

        <div class="card" style="margin-top:16px">
          <div class="card-head"><div><div class="t">Ostatnie rozmowy</div><div class="h-sub">Welfare check + concierge</div></div><span class="link">Wszystkie 147 →</span></div>
          ${['08:14 · 3m 22s · Poranny welfare · mood 0.72','Wczoraj 19:47 · 4m 15s · Wizyta lekarska','10 lip 19:52 · 5m 08s · Sygnał samotności'].map(x => `
            <div style="padding:14px 24px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center">
              <div><div style="font-family:var(--serif);font-size:14px;color:var(--granat-900);font-weight:500">${x.split(' · ').slice(2).join(' · ')}</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;letter-spacing:0.04em">${x.split(' · ').slice(0,2).join(' · ')}</div></div>
              <div style="display:flex;gap:6px"><button class="btn btn-ghost btn-xs">▶ Play</button><button class="btn btn-ghost btn-xs">📝 Transcript</button></div>
            </div>
          `).join('')}
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-head"><div><div class="t">Leki · adherence 96%</div><div class="h-sub">4 leki · MedGuard sync</div></div></div>
          ${[
            {n:'Metformina 500mg',s:'2×/dzień · 07:15 · 19:15',v:98},
            {n:'Amlodypina 5mg',s:'1×/dzień · 08:00',v:100},
            {n:'Simvastatin 20mg',s:'1×/dzień · wieczór',v:83},
            {n:'Wit. D3 2000 IU',s:'1×/dzień · z posiłkiem',v:96},
          ].map(m => `
            <div style="padding:12px 24px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center">
              <div style="width:32px;height:32px;border-radius:8px;background:var(--paper-2);border:1px solid var(--line);display:grid;place-items:center;color:var(--granat-600)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M9 8V6a3 3 0 016 0v2"/></svg></div>
              <div><div style="font-size:13px;color:var(--granat-900);font-weight:500">${m.n}</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:2px;letter-spacing:0.02em">${m.s}</div></div>
              <div style="text-align:right"><div style="font-family:var(--serif);font-size:18px;color:${m.v<90?'var(--sem-yellow)':'var(--granat-900)'};font-weight:500">${m.v}%</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">30d</div></div>
            </div>
          `).join('')}
        </div>

        <div class="card" style="margin-top:16px">
          <div class="card-head"><div><div class="t">Obserwacje Adama</div><div class="h-sub">AI-generated · tygodniowe</div></div></div>
          <div style="padding:16px 24px">
            <div style="padding:14px;background:var(--paper-2);border-radius:8px;border-left:3px solid var(--zloto-500);margin-bottom:10px">
              <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.12em;text-transform:uppercase">Wzorzec</div>
              <div style="font-family:var(--serif);font-size:14px;color:var(--granat-900);margin-top:6px;line-height:1.35;font-weight:500">Simvastatin pomijany 2× w tygodniu — piątkowe wieczory.</div>
              <div style="font-size:12px;color:var(--ink-700);margin-top:6px;line-height:1.5">Rozważyć przesunięcie dawki na poranek.</div>
            </div>
            <div style="padding:14px;background:var(--paper-2);border-radius:8px;border-left:3px solid var(--sem-yellow)">
              <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.12em;text-transform:uppercase">Trend nastroju</div>
              <div style="font-family:var(--serif);font-size:14px;color:var(--granat-900);margin-top:6px;line-height:1.35;font-weight:500">Środy wieczorem — mood -0.18 pkt.</div>
              <div style="font-size:12px;color:var(--ink-700);margin-top:6px;line-height:1.5">Dzień imieninowy zmarłego męża — telefon rodziny może pomóc.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-calls">
    <div class="card">
      <div class="card-head"><div><div class="t">Historia rozmów · <em>147 wszystkich</em></div><div class="h-sub">Transkrypty + audio · retention 30d</div></div>
        <div class="r"><button class="btn btn-ghost btn-sm">Eksport PDF</button></div>
      </div>
      <div class="table-wrap"><table class="data compact">
        <thead><tr><th>Data / Czas</th><th>Agent</th><th>Kategoria</th><th>Długość</th><th>Mood</th><th>Semafor</th><th>Tools użyte</th><th>Audio</th></tr></thead>
        <tbody>
          ${[
            ['Dziś 08:14','welfare-morning v7.4.2','Welfare check','3m 22s','0.72','green','get_medication_schedule, submit_compliance'],
            ['Wcz. 19:47','welfare-evening v7.4.2','Welfare check','4m 15s','0.68','green','get_medication_schedule'],
            ['10 lip 19:52','welfare-evening','Welfare check','5m 08s','0.42','yellow','raise_semafor("yellow"), notify_family'],
            ['09 lip 08:12','welfare-morning','Welfare check','2m 47s','0.71','green','—'],
            ['08 lip 14:30','concierge','Concierge','1m 55s','—','info','order_service("fryzjer")'],
          ].map(([d,a,c,l,m,sm,t]) => `
            <tr><td class="num-mono">${d}</td><td style="font-family:var(--mono);font-size:11px">${a}</td><td>${c}</td><td class="num-mono">${l}</td><td class="num-serif">${m}</td><td><span class="b ${sm}"><span class="dot"></span>${sm}</span></td><td style="font-family:var(--mono);font-size:10px;color:var(--ink-500)">${t}</td><td><button class="btn btn-ghost btn-xs">▶</button></td></tr>
          `).join('')}
        </tbody>
      </table></div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-meds">
    <div class="grid-2">
      <div class="card"><div class="card-head"><div><div class="t">Harmonogram leków</div><div class="h-sub">Aktywny · MedGuard schedule v2.1</div></div><button class="btn btn-ghost btn-sm">+ Dodaj lek</button></div>
        <div style="padding:20px 24px">
          ${[
            {n:'Metformina 500mg',morning:true,noon:false,evening:true,notes:'Z posiłkiem · min. 30 min przed'},
            {n:'Amlodypina 5mg',morning:true,noon:false,evening:false,notes:'Na czczo'},
            {n:'Simvastatin 20mg',morning:false,noon:false,evening:true,notes:'Wieczorem · po kolacji'},
            {n:'Wit. D3 2000 IU',morning:true,noon:false,evening:false,notes:'Z tłuszczem'},
          ].map(m => `
            <div style="padding:14px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto auto auto;gap:16px;align-items:center">
              <div><div style="font-family:var(--serif);font-size:15px;color:var(--granat-900);font-weight:500">${m.n}</div><div style="font-size:11px;color:var(--ink-500);margin-top:3px;font-style:italic;font-family:var(--serif);font-weight:300">${m.notes}</div></div>
              <div style="width:36px;height:36px;border-radius:50%;background:${m.morning?'var(--sem-green-bg)':'var(--paper-2)'};color:${m.morning?'var(--sem-green)':'var(--ink-400)'};display:grid;place-items:center;font-size:14px" title="Rano">🌅</div>
              <div style="width:36px;height:36px;border-radius:50%;background:${m.noon?'var(--sem-green-bg)':'var(--paper-2)'};color:${m.noon?'var(--sem-green)':'var(--ink-400)'};display:grid;place-items:center;font-size:14px" title="Południe">☀️</div>
              <div style="width:36px;height:36px;border-radius:50%;background:${m.evening?'var(--sem-green-bg)':'var(--paper-2)'};color:${m.evening?'var(--sem-green)':'var(--ink-400)'};display:grid;place-items:center;font-size:14px" title="Wieczór">🌙</div>
            </div>
          `).join('')}
        </div>
      </div>
      <div class="card"><div class="card-head"><div><div class="t">Adherence 30 dni</div><div class="h-sub">Kalendarz compliance</div></div></div>
        <div style="padding:20px 24px">
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:8px">
            ${['P','W','Ś','C','P','S','N'].map(d => `<div style="text-align:center;font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em">${d}</div>`).join('')}
          </div>
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px">
            ${Array.from({length:35},(_,i) => {
              const v = [1,1,1,1,0.6,0.8,1,1,0.9,1,1,1,0.7,1,1,1,1,0.85,1,1,1,1,1,0.9,1,1,1,1,1,1,1,1,1,1,1][i]||1;
              const color = v === 1 ? 'var(--sem-green)' : v >= 0.8 ? 'var(--sem-green-bg)' : v >= 0.6 ? 'var(--sem-yellow-bg)' : 'var(--sem-red-bg)';
              return `<div style="aspect-ratio:1;background:${color};border-radius:4px;display:grid;place-items:center;font-family:var(--mono);font-size:9px;color:var(--granat-700);font-weight:500">${i+1}</div>`;
            }).join('')}
          </div>
          <div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:16px;letter-spacing:0.06em">
            <span>15 CZE</span><span>DZIŚ · 12 LIP</span><span>96% ADHERENCE</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-alerts">
    <div class="card">
      <div class="card-head"><div><div class="t">Historia alertów · <em>3 z 30 dni</em></div></div></div>
      ${[
        {t:'10 lip 19:52',lvl:'yellow',title:'Sygnał samotności',desc:'"Wnuki dawno nie dzwoniły" · mood 0.42',resp:'Rodzina powiadomiona · SMS'},
        {t:'02 lip 21:03',lvl:'yellow',title:'Ból głowy',desc:'"Boli mnie od rana" · powtórzono 3×',resp:'Sugestia wizyty lekarskiej'},
        {t:'22 cze 14:47',lvl:'red',title:'Wykrycie upadku',desc:'Xiaomi Band 8 · fałszywy alarm (spadł pilot)',resp:'Rozwiązane po rozmowie · 22s'},
      ].map(a => `
        <div style="padding:16px 24px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:80px 1fr auto;gap:16px;align-items:start">
          <div style="font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.04em">${a.t}</div>
          <div><div style="font-family:var(--serif);font-size:16px;color:var(--granat-900);font-weight:500">${a.title}</div><div style="font-size:13px;color:var(--ink-700);margin-top:3px">${a.desc}</div><div style="font-family:var(--mono);font-size:11px;color:var(--sem-green);margin-top:6px;letter-spacing:0.04em">→ ${a.resp}</div></div>
          <span class="b ${a.lvl}"><span class="dot"></span>${a.lvl}</span>
        </div>
      `).join('')}
    </div>
  </div>

  <div class="subtab-panel" id="tp-reports">
    <div class="card"><div class="card-head"><div><div class="t">Raporty tygodniowe i miesięczne</div><div class="h-sub">PDF · HL7 FHIR export</div></div></div>
      <div class="grid-2" style="padding:20px 24px">
        ${['Raport tygodniowy · 05–12 lip','Raport tygodniowy · 28 cze–05 lip','Raport miesięczny · Czerwiec 2026','Raport miesięczny · Maj 2026'].map(r => `
          <div style="padding:20px;background:var(--paper-2);border-radius:10px;border:1px solid var(--line)">
            <div style="font-family:var(--serif);font-size:16px;color:var(--granat-900);font-weight:500">${r}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:6px;letter-spacing:0.06em">14 rozmów · mood 0.71 · adherence 96%</div>
            <div style="display:flex;gap:6px;margin-top:12px"><button class="btn btn-ghost btn-sm">📄 PDF</button><button class="btn btn-ghost btn-sm">FHIR</button><button class="btn btn-ghost btn-sm">Wyślij lekarzowi</button></div>
          </div>
        `).join('')}
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-wearable">
    <div class="card"><div class="card-head"><div><div class="t">${s.wearable}</div><div class="h-sub">Sparowane · sync co 5 min</div></div><span class="pip green"><span class="dot"></span>Connected</span></div>
      <div class="grid-4" style="padding:20px 24px">
        <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">HR (24h)</div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);margin-top:6px;font-weight:500;letter-spacing:-0.015em">72<span style="font-size:14px;color:var(--zloto-700)">bpm</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--sem-green);margin-top:4px;letter-spacing:0.04em">Norma · min 62 · max 92</div></div>
        <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">SpO₂</div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);margin-top:6px;font-weight:500">97<span style="font-size:14px;color:var(--zloto-700)">%</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--sem-green);margin-top:4px;letter-spacing:0.04em">Norma &gt;95%</div></div>
        <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Kroki dziś</div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);margin-top:6px;font-weight:500">3,247</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:4px;letter-spacing:0.04em">Cel 5000</div></div>
        <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Sen (noc)</div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);margin-top:6px;font-weight:500">7h 12m</div><div style="font-family:var(--mono);font-size:10px;color:var(--sem-green);margin-top:4px;letter-spacing:0.04em">Deep 22% · REM 18%</div></div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-family">
    <div class="card"><div class="card-head"><div><div class="t">Rodzina i RBAC</div><div class="h-sub">Kontakty alarmowe + kolejność powiadamiania</div></div><button class="btn btn-ghost btn-sm">+ Zaproś opiekuna</button></div>
      ${[
        {n:1,name:'Anna Chmielewska',rel:'Córka',role:'Opiekun Główny',phone:'+48 606 123 456',perm:'Pełne + zarządzanie'},
        {n:2,name:'Piotr Wójcik',rel:'Syn',role:'Opiekun',phone:'+48 601 987 654',perm:'Read-only'},
        {n:3,name:'Dr Katarzyna Chmielewska',rel:'Lekarz POZ',role:'Lekarz',phone:'+48 618 771 200',perm:'Raporty medyczne'},
        {n:4,name:'Ratunkowe',rel:'Auto',role:'112',phone:'112',perm:'Auto-dial przy Purple'},
      ].map(f => `
        <div style="padding:14px 24px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:32px 1fr auto auto;gap:16px;align-items:center">
          <div style="width:28px;height:28px;border-radius:50%;background:var(--paper-2);display:grid;place-items:center;font-family:var(--serif);font-size:12px;color:var(--granat-700);font-weight:500">${f.n}</div>
          <div><div style="font-size:14px;color:var(--granat-900);font-weight:500">${f.name}</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:2px;letter-spacing:0.06em">${f.rel} · ${f.role}</div></div>
          <div class="num-mono">${f.phone}</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.06em">${f.perm}</div>
        </div>
      `).join('')}
    </div>
  </div>

  <div class="subtab-panel" id="tp-gdpr">
    <div class="card"><div class="card-head"><div><div class="t">RODO · Zgody i przetwarzanie danych</div><div class="h-sub">GDPR Compliance Toolkit · Faza F12</div></div></div>
      <div style="padding:20px 24px">
        ${[
          {name:'Zgoda na nagrywanie rozmów',status:'Wyrażona',date:'12 mar 2026',retention:'30 dni'},
          {name:'Zgoda na przetwarzanie danych medycznych',status:'Wyrażona',date:'12 mar 2026',retention:'Aktywna umowa'},
          {name:'Zgoda na udostępnianie rodzinie',status:'Wyrażona',date:'12 mar 2026',retention:'Aktywna umowa'},
          {name:'Zgoda na udostępnianie lekarzowi',status:'Wyrażona',date:'02 kwi 2026',retention:'Aktywna umowa'},
          {name:'Zgoda na wywoływanie 112',status:'Wyrażona',date:'12 mar 2026',retention:'Aktywna umowa'},
          {name:'Marketing i badania',status:'Odmówiona',date:'12 mar 2026',retention:'—'},
        ].map(c => `
          <div style="padding:12px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto auto auto;gap:16px;align-items:center">
            <div style="font-size:13px;color:var(--granat-900);font-weight:500">${c.name}</div>
            <span class="pip ${c.status==='Wyrażona'?'green':'red'}"><span class="dot"></span>${c.status}</span>
            <div class="num-mono muted">${c.date}</div>
            <div class="num-mono muted">${c.retention}</div>
          </div>
        `).join('')}
        <div style="margin-top:20px;padding:16px;background:var(--info-blue-bg);border-radius:8px;font-size:12px;color:var(--info-blue);line-height:1.5">
          <strong>Prawo do usunięcia:</strong> Senior lub opiekun główny może w każdej chwili poprosić o usunięcie wszystkich danych. Zgodnie z RODO art. 17.
        </div>
      </div>
    </div>
  </div>
</div>`;
};

/* ------------ CALL HISTORY ------------ */
SCREEN_RENDERERS.calls = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Call History · <em>18,432 rozmów</em></h1>
      <div class="sub">
        <span class="live">Live sync</span>
        <span class="sep">·</span><span>7d: 14,208 · 24h: 2,347 · Teraz: 17 aktywnych</span>
        <span class="sep">·</span><span>Śr. długość: 3m 42s · Sukces: 96.4%</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">📊 Analytics</button>
      <button class="btn btn-ghost">Eksport CSV</button>
      <button class="btn btn-primary">🗑 Bulk delete</button>
    </div>
  </div>

  <!-- Filters (z FilterOptions w CallHistoryPage.tsx) -->
  <div class="filter-bar">
    <div class="field"><label>Agent</label><select><option>Wszystkie 12</option><option>welfare-morning</option><option>welfare-evening</option><option>crisis-triage</option><option>med-reminder</option><option>concierge</option></select></div>
    <div class="field"><label>Metoda</label><select><option>Wszystkie</option><option>Inbound</option><option>Outbound</option><option>Scheduled</option></select></div>
    <div class="field"><label>Status</label><select><option>Wszystkie</option><option>Completed</option><option>Failed</option><option>No answer</option><option>Busy</option></select></div>
    <div class="field"><label>Semafor</label><select><option>Wszystkie</option><option>🟢 Green</option><option>🟡 Yellow</option><option>🔴 Red</option><option>🟣 Purple</option></select></div>
    <div class="field"><label>Od</label><input type="date" value="2026-07-05"/></div>
    <div class="field"><label>Do</label><input type="date" value="2026-07-12"/></div>
    <div style="flex:1"></div>
    <button class="chip-filter on">Ma transkrypt <span class="x">×</span></button>
    <button class="chip-filter">Ma audio</button>
    <button class="chip-filter">Ma alert</button>
  </div>

  <!-- Transcript search -->
  <div style="margin-bottom:20px;padding:14px 16px;background:var(--paper);border:1px solid var(--line);border-radius:10px;display:flex;gap:12px;align-items:center">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--ink-500)" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
    <input type="text" placeholder="Przeszukuj transkrypty (regex ok): np. „ból w klatce" OR „upadek" OR /leki/i" style="flex:1;border:none;background:transparent;font-family:var(--mono);font-size:12px;color:var(--ink-900);outline:none"/>
    <span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em">4 rezultaty w 147 rozmowach</span>
  </div>

  <!-- KPI -->
  <div class="grid-4" style="margin-bottom:20px">
    <div class="kpi"><div class="lbl">Rozmowy w oknie</div><div class="val">14,208</div><div class="foot">7 dni · sr. 2029/dzień</div></div>
    <div class="kpi"><div class="lbl">Sukces</div><div class="val">96.4<sub>%</sub></div><div class="foot pos">↗ +0.3pp</div></div>
    <div class="kpi"><div class="lbl">Śr. długość</div><div class="val">3<sub>m 42s</sub></div><div class="foot">Cel: 3–5min</div></div>
    <div class="kpi"><div class="lbl">Alerty wywołane</div><div class="val">187</div><div class="foot neg">14 red · 8 purple</div></div>
  </div>

  <div class="card">
    <div class="card-head">
      <div><div class="t">Wszystkie rozmowy</div><div class="h-sub">Ostatnie 24h · sortowanie: newest</div></div>
      <div class="r"><span style="color:var(--ink-500)">Pokazano 30 z 2347</span></div>
    </div>
    <div class="table-wrap"><table class="data compact">
      <thead><tr><th>Call ID</th><th>Senior</th><th>Kierunek</th><th>Agent</th><th>Długość</th><th>Mood</th><th>Semafor</th><th>Status</th><th>Tools</th><th></th></tr></thead>
      <tbody>
        ${[
          {id:'C-847291',sn:'Stanisław Z.',dir:'Outbound',agent:'crisis-triage v3.1',len:'0m 42s',mood:'—',sem:'purple',status:'LIVE',tools:'raise_semafor, dial_112'},
          {id:'C-847290',sn:'Maria N.',dir:'Outbound',agent:'welfare-evening',len:'0m 15s',mood:'—',sem:'red',status:'No answer',tools:'—'},
          {id:'C-847289',sn:'Janusz K.',dir:'Outbound',agent:'welfare-evening',len:'3m 47s',mood:'0.42',sem:'yellow',status:'Completed',tools:'raise_semafor("yellow")'},
          {id:'C-847288',sn:'Halina W.',dir:'Outbound',agent:'welfare-morning',len:'3m 22s',mood:'0.72',sem:'green',status:'Completed',tools:'get_med, submit_compliance'},
          {id:'C-847287',sn:'Krystyna B.',dir:'Outbound',agent:'welfare-morning',len:'2m 55s',mood:'0.81',sem:'green',status:'Completed',tools:'get_med, submit_compliance'},
          {id:'C-847286',sn:'Zbigniew K.',dir:'Outbound',agent:'welfare-morning',len:'4m 08s',mood:'0.75',sem:'green',status:'Completed',tools:'get_med, submit_compliance'},
          {id:'C-847285',sn:'Ewa M.',dir:'Outbound',agent:'welfare-morning',len:'2m 47s',mood:'0.69',sem:'green',status:'Completed',tools:'get_med, submit_compliance'},
          {id:'C-847284',sn:'Wanda S.',dir:'Outbound',agent:'welfare-morning',len:'3m 12s',mood:'0.71',sem:'green',status:'Completed',tools:'get_med, submit_compliance'},
          {id:'C-847283',sn:'Andrzej Sz.',dir:'Outbound',agent:'welfare-morning',len:'3m 55s',mood:'0.66',sem:'green',status:'Completed',tools:'get_med'},
          {id:'C-847282',sn:'Krystyna B.',dir:'Inbound',agent:'concierge',len:'1m 22s',mood:'—',sem:'info',status:'Completed',tools:'order_service("fryzjer")'},
        ].map(c => `
          <tr>
            <td class="num-mono" style="color:var(--zloto-700)">${c.id}</td>
            <td><div class="a-pill"><div class="a-av">${c.sn.match(/[A-Z]/g).slice(0,2).join('')}</div><span class="a-name">${c.sn}</span></div></td>
            <td class="num-mono">${c.dir}</td>
            <td style="font-family:var(--mono);font-size:11px">${c.agent}</td>
            <td class="num-mono">${c.len}</td>
            <td class="num-serif ${c.sem==='red'||c.sem==='purple'?c.sem:''}">${c.mood}</td>
            <td><span class="b ${c.sem}"><span class="dot"></span>${c.sem}</span></td>
            <td><span class="pip ${c.status==='Completed'?'green':c.status==='LIVE'?'purple':'yellow'}"><span class="dot"></span>${c.status}</span></td>
            <td style="font-family:var(--mono);font-size:10px;color:var(--ink-500);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.tools}</td>
            <td style="display:flex;gap:4px"><button class="btn btn-ghost btn-xs">▶</button><button class="btn btn-ghost btn-xs">📝</button></td>
          </tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>
</div>`;

/* ------------ CALL SCHEDULING ------------ */
SCREEN_RENDERERS.scheduling = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Call Scheduling · <em>2 aktywne kampanie</em></h1>
      <div class="sub">
        <span>Welfare check: 2×/dzień · 1247 seniorów</span>
        <span class="sep">·</span><span>Medication reminders: on-demand · 4,847/dzień</span>
        <span class="sep">·</span><span>Family callbacks: 12 zaplanowanych</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Historia kampanii</button>
      <button class="btn btn-accent">+ Nowa kampania</button>
    </div>
  </div>

  <!-- Active campaigns -->
  <div class="section-hd"><h2>Aktywne kampanie</h2><span class="link">Cron syntax · consent gate · retry logic</span></div>
  <div class="grid-2">
    ${[
      {name:'Welfare Check Poranny',cron:'0 8 * * *',seniors:1247,agent:'welfare-morning v7.4.2',last:'Dziś 08:00 · 100% completed',next:'Jutro 08:00',color:'green'},
      {name:'Welfare Check Wieczorny',cron:'0 19 * * *',seniors:1247,agent:'welfare-evening v7.4.2',last:'Wcz. 19:00 · 96% completed',next:'Dziś 19:00',color:'green'},
      {name:'Medication Reminders',cron:'Per-schedule',seniors:1198,agent:'med-reminder v2.4.1',last:'2 min temu',next:'Ciągły',color:'green'},
      {name:'Weekly Family Report',cron:'0 18 * * 0',seniors:1247,agent:'system (email)',last:'Nd. 18:00',next:'Niedziela 18:00',color:'green'},
    ].map(c => `
      <div class="card" style="border-left:3px solid var(--sem-${c.color})">
        <div class="card-head"><div><div class="t">${c.name}</div><div class="h-sub">${c.agent}</div></div><label class="switch"><input type="checkbox" checked/><span class="slider"></span></label></div>
        <div style="padding:16px 24px">
          <div style="display:grid;grid-template-columns:auto 1fr;gap:12px 16px;font-size:12.5px;color:var(--ink-700)">
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Cron</div><div class="num-mono">${c.cron}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Seniorów</div><div class="num-serif">${c.seniors.toLocaleString('pl')}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Ostatnie</div><div>${c.last}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Następne</div><div>${c.next}</div>
          </div>
          <div style="display:flex;gap:6px;margin-top:16px;padding-top:12px;border-top:1px solid var(--line)">
            <button class="btn btn-ghost btn-sm">Edytuj cron</button>
            <button class="btn btn-ghost btn-sm">Zobacz retry rules</button>
            <button class="btn btn-ghost btn-sm">▶ Test call</button>
          </div>
        </div>
      </div>
    `).join('')}
  </div>

  <!-- Heatmap -->
  <div class="section-hd" style="margin-top:32px"><h2>Rozkład rozmów · <em>tydzień</em></h2><span class="link">Intensywność / godzinę · natężenie welfare check</span></div>
  <div class="card">
    <div class="heatmap">
      <div class="hm-lbl"></div>
      ${Array.from({length:24},(_,i)=>`<div class="hm-hour">${String(i).padStart(2,'0')}</div>`).join('')}
      ${['Pon','Wt','Śr','Cz','Pt','Sob','Nd'].map(day => `
        <div class="hm-lbl">${day}</div>
        ${Array.from({length:24},(_,h)=>{
          let level = 0;
          if (h >= 8 && h <= 10) level = 4;
          else if (h >= 19 && h <= 21) level = 3;
          else if (h >= 11 && h <= 18) level = 2;
          else if (h >= 6 && h <= 22) level = 1;
          return `<div class="hm-cell l${level}" title="${day} ${String(h).padStart(2,'0')}:00 · ${level*80} rozmów"></div>`;
        }).join('')}
      `).join('')}
    </div>
    <div style="padding:16px 24px;border-top:1px solid var(--line);display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.06em">
      <span>PEAK · pon-sob 08–10 · welfare check poranny (~250/h)</span>
      <div style="display:flex;gap:6px;align-items:center">
        <span>MNIEJ</span>
        <span style="width:16px;height:12px;background:var(--paper-2);border-radius:2px"></span>
        <span style="width:16px;height:12px;background:rgba(200,150,62,0.15);border-radius:2px"></span>
        <span style="width:16px;height:12px;background:rgba(200,150,62,0.35);border-radius:2px"></span>
        <span style="width:16px;height:12px;background:rgba(200,150,62,0.6);border-radius:2px"></span>
        <span style="width:16px;height:12px;background:var(--zloto-500);border-radius:2px"></span>
        <span>WIĘCEJ</span>
      </div>
    </div>
  </div>

  <!-- Consent Gate -->
  <div class="section-hd" style="margin-top:32px"><h2>Consent Gate · <em>zgody na wychodzące</em></h2><span class="link">RODO Art. 6 · legitimate interest audit trail</span></div>
  <div class="card">
    <div style="padding:20px 24px">
      <div style="display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line)">
        <div style="width:36px;height:36px;border-radius:50%;background:var(--sem-green-bg);color:var(--sem-green);display:grid;place-items:center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg></div>
        <div><div style="font-family:var(--serif);font-size:15px;color:var(--granat-900);font-weight:500">Welfare Check Poranny/Wieczorny</div><div style="font-size:12px;color:var(--ink-700);margin-top:3px">Zgoda na cykliczny welfare check w umowie · art. 6 ust. 1 lit. a (zgoda)</div></div>
        <div style="text-align:right"><div class="num-serif">1247</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em">SENIORÓW · 100%</div></div>
      </div>
      <div style="display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line)">
        <div style="width:36px;height:36px;border-radius:50%;background:var(--sem-green-bg);color:var(--sem-green);display:grid;place-items:center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg></div>
        <div><div style="font-family:var(--serif);font-size:15px;color:var(--granat-900);font-weight:500">Medication Reminders</div><div style="font-size:12px;color:var(--ink-700);margin-top:3px">Zgoda na przetwarzanie danych medycznych · art. 9 ust. 2 lit. h</div></div>
        <div style="text-align:right"><div class="num-serif">1198</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em">SENIORÓW · 96%</div></div>
      </div>
      <div style="display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:14px 0">
        <div style="width:36px;height:36px;border-radius:50%;background:var(--sem-yellow-bg);color:var(--sem-yellow);display:grid;place-items:center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L1 21h22L12 2z"/><path d="M12 9v6M12 18v.5"/></svg></div>
        <div><div style="font-family:var(--serif);font-size:15px;color:var(--granat-900);font-weight:500">Emergency 112 Auto-Dial</div><div style="font-size:12px;color:var(--ink-700);margin-top:3px">Zgoda + żywotny interes · art. 6 ust. 1 lit. d (życie i zdrowie)</div></div>
        <div style="text-align:right"><div class="num-serif">1247</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em">SENIORÓW · 100%</div></div>
      </div>
    </div>
  </div>
</div>`;

/* ------------ ALERTS ------------ */
SCREEN_RENDERERS.alerts = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Alerty · <em>3 aktywne</em></h1>
      <div class="sub">
        <span>30 dni: 187 alertów · 14 red · 8 purple · rozwiązane: 176 · średni MTTA: 14s</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Escalation policy</button>
      <button class="btn btn-ghost">Runbook</button>
      <button class="btn btn-danger">🚨 Trigger test alert</button>
    </div>
  </div>

  <!-- Active alerts -->
  <div class="section-hd"><h2>Aktywne alerty</h2><span class="link">Sortowanie: waga · czas</span></div>

  <div class="alert-strip">
    <div class="icon-wrap" style="background:var(--sem-purple-bg);color:var(--sem-purple)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2zm0 6v4m0 2v.5" stroke-linecap="round"/></svg></div>
    <div class="info-t">
      <div class="title" style="color:var(--sem-purple)">🟣 PURPLE · 112 wezwane · Stanisław Zieliński</div>
      <div class="desc">Ból w klatce + AFib · Apple Watch S9 · <strong>Karetka ETA 8 min</strong> · Koordynator: Krzysztof M. · LIVE 00:42</div>
    </div>
    <div class="cta-group">
      <button class="btn btn-ghost">Śledź</button>
      <button class="btn btn-primary" style="background:var(--sem-purple)">Otwórz LIVE</button>
    </div>
  </div>

  <div class="alert-strip">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2zm0 6v4m0 2v.5" stroke-linecap="round"/></svg></div>
    <div class="info-t">
      <div class="title">🔴 RED · Potencjalny upadek · Maria Nowak</div>
      <div class="desc">Xiaomi Band 8 · gwałtowne przemieszczenie + HR skok +34 · brak odpowiedzi na 3 próby · <strong>3 min temu</strong> · Koordynator: —</div>
    </div>
    <div class="cta-group">
      <button class="btn btn-ghost">Otwórz</button>
      <button class="btn btn-danger">Przejmij</button>
    </div>
  </div>

  <div class="alert-strip warn">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2zm0 6v4m0 2v.5" stroke-linecap="round"/></svg></div>
    <div class="info-t">
      <div class="title" style="color:var(--sem-yellow)">🟡 YELLOW · Samotność · Janusz Kowalski</div>
      <div class="desc">"Wnuki dawno nie dzwoniły" · mood 0.42 · Sugestia: powiadomić rodzinę · Koordynator: Anna W.</div>
    </div>
    <div class="cta-group">
      <button class="btn btn-ghost">Otwórz</button>
      <button class="btn btn-ghost" style="background:var(--sem-yellow);color:white;border:none">Wyślij SMS rodzinie</button>
    </div>
  </div>

  <!-- Escalation policy -->
  <div class="section-hd" style="margin-top:32px"><h2>Ścieżka eskalacji · <em>4 poziomy</em></h2><span class="link">Semafor progresywny · zapobiega alarm fatigue</span></div>
  <div class="card">
    <div style="padding:24px">
      ${[
        {lvl:'L1',col:'green',name:'Green · Spokojnie',trig:'Wszystko w normie · mood ≥0.6 · leki OK',resp:'Log · aktualizacja panelu opiekuna',mtta:'—',time:'—'},
        {lvl:'L2',col:'yellow',name:'Yellow · Uważaj',trig:'Mood <0.5 · samotność · pominięta dawka',resp:'SMS rodzinie · sugestia telefonu',mtta:'2 min',time:'W ciągu doby'},
        {lvl:'L3',col:'red',name:'Red · Alarm',trig:'Upadek · HR>140 · ból w klatce (werbalny)',resp:'Push + SMS rodzina + koordynator · Adam dzwoni 3× · retry 20s',mtta:'18s',time:'Natychmiast'},
        {lvl:'L4',col:'purple',name:'Purple · Krytyczne',trig:'Zagrożenie życia · kryzys werbalny + wearable · utrata kontaktu',resp:'112 auto-dial + rodzina + koordynator + LIVE feed',mtta:'42s',time:'Natychmiast · overrideń DND'},
      ].map(l => `
        <div style="display:grid;grid-template-columns:60px 1fr 1fr 1fr 90px 130px;gap:16px;padding:16px 0;border-bottom:1px solid var(--line);align-items:center">
          <div style="width:44px;height:44px;border-radius:50%;background:var(--sem-${l.col});color:white;display:grid;place-items:center;font-family:var(--serif);font-size:14px;font-weight:600">${l.lvl}</div>
          <div><div style="font-family:var(--serif);font-size:16px;color:var(--granat-900);font-weight:500">${l.name}</div></div>
          <div style="font-size:12.5px;color:var(--ink-700);line-height:1.5"><strong style="color:var(--granat-900)">Trigger:</strong> ${l.trig}</div>
          <div style="font-size:12.5px;color:var(--ink-700);line-height:1.5"><strong style="color:var(--granat-900)">Response:</strong> ${l.resp}</div>
          <div style="text-align:center"><div class="num-serif">${l.mtta}</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em">MTTA</div></div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em">${l.time}</div>
        </div>
      `).join('')}
    </div>
  </div>

  <!-- History -->
  <div class="section-hd" style="margin-top:32px"><h2>Historia alertów · <em>30 dni</em></h2>
    <div class="n-tabs"><button>24h</button><button class="on">7d</button><button>30d</button></div>
  </div>
  <div class="card">
    <div class="table-wrap"><table class="data compact">
      <thead><tr><th>Data</th><th>Senior</th><th>Poziom</th><th>Trigger</th><th>Koordynator</th><th>MTTA</th><th>Rozwiązanie</th><th>Status</th></tr></thead>
      <tbody>
        ${[
          ['Dziś 22:15','Stanisław Z.','purple','Ból w klatce + AFib','Krzysztof M.','LIVE','—','LIVE'],
          ['Dziś 14:22','Maria N.','red','Wykrycie upadku (Xiaomi)','— przydziel','—','—','Aktywny'],
          ['Dziś 13:04','Janusz K.','yellow','Samotność werbalna','Anna W.','—','—','Aktywny'],
          ['10 lip 22:03','Stanisława W.','red','HR>140 + duszność','Krzysztof M.','16s','Fałszywy alarm (aktywność fizyczna)','Zamknięty'],
          ['08 lip 03:47','Jan Nowicki','purple','Utrata przytomności','Anna W.','21s','Karetka · hospitalizacja','Zamknięty'],
          ['07 lip 19:12','Ryszard T.','yellow','Adherence <70%','Anna W.','—','Rozmowa z rodziną','Zamknięty'],
        ].map(([d,s,l,t,c,m,r,st]) => `
          <tr><td class="num-mono">${d}</td><td>${s}</td><td><span class="b ${l}"><span class="dot"></span>${l}</span></td><td style="font-size:12.5px">${t}</td><td style="font-family:var(--mono);font-size:11px">${c}</td><td class="num-mono">${m}</td><td style="font-size:12px;color:var(--ink-500)">${r}</td><td><span class="pip ${st==='Zamknięty'?'green':st==='LIVE'?'purple':'red'}"><span class="dot"></span>${st}</span></td></tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>
</div>`;

/* ------------ WIZARD ------------ */
SCREEN_RENDERERS.wizard = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Setup Wizard · <em>Krok 3 z 5</em></h1>
      <div class="sub">
        <span>Kreator pierwszego uruchomienia AVA + Adam</span>
        <span class="sep">·</span><span>Zajmuje ~15 minut</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Zapisz i wróć później</button>
      <button class="btn btn-ghost">Pomiń kreator</button>
    </div>
  </div>

  <div class="card" style="padding:32px 40px">
    <div class="wizard-steps">
      <div class="step done"><div class="num">✓</div><div class="lbl">Providers</div></div>
      <div class="step done"><div class="num">✓</div><div class="lbl">Local AI</div></div>
      <div class="step active"><div class="num">3</div><div class="lbl">Asterisk</div></div>
      <div class="step"><div class="num">4</div><div class="lbl">Test call</div></div>
      <div class="step"><div class="num">5</div><div class="lbl">Gotowe</div></div>
    </div>

    <div style="max-width:820px;margin:0 auto">
      <h2 style="font-family:var(--serif);font-size:32px;color:var(--granat-900);font-weight:500;letter-spacing:-0.02em;line-height:1.1">Skonfiguruj <em style="color:var(--zloto-700);font-style:italic">Asterisk PBX</em></h2>
      <p style="font-size:15px;color:var(--ink-700);line-height:1.6;margin-top:12px">Adam używa Asterisk PBX do wykonywania połączeń przez PSTN/SIP. Podłącz swoją instancję Asterisk przez ARI (Asterisk REST Interface).</p>

      <div style="margin-top:32px;padding:20px 24px;background:var(--sem-green-bg);border-radius:12px;border:1px solid var(--sem-green);display:flex;align-items:center;gap:14px">
        <div style="width:32px;height:32px;border-radius:50%;background:var(--sem-green);color:white;display:grid;place-items:center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg></div>
        <div style="flex:1"><div style="font-family:var(--serif);font-size:15px;color:var(--sem-green);font-weight:500">Asterisk wykryty w sieci</div><div style="font-size:12px;color:var(--ink-700);margin-top:2px">Instancja PBX odpowiada pod adresem <code style="font-family:var(--mono);background:white;padding:1px 6px;border-radius:3px;font-size:11px">asterisk.local:5060</code></div></div>
      </div>

      <div class="form-row" style="margin-top:24px">
        <div class="form-group"><label>Adres ARI</label><input type="text" value="http://asterisk.local:8088/ari"/><div class="help">HTTP endpoint dla Asterisk REST Interface</div></div>
        <div class="form-group"><label>Nazwa aplikacji</label><input type="text" value="ai_agent"/><div class="help">Nazwa Stasis application (dialplan)</div></div>
      </div>

      <div class="form-row">
        <div class="form-group"><label>ARI Username</label><input type="text" value="AIAgent"/></div>
        <div class="form-group"><label>ARI Password</label><input type="password" value="••••••••••••"/></div>
      </div>

      <div class="form-group"><label>Extension / Route</label><input type="text" value="from-internal / _X."/><div class="help">Dialplan route dla przychodzących połączeń do Adama</div></div>

      <div style="margin-top:24px;padding:16px 20px;background:var(--paper-2);border-radius:8px;border-left:3px solid var(--zloto-500)">
        <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">Wymagane moduły Asterisk</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12.5px">
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">res_ari.so</code></div>
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">res_ari_events.so</code></div>
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">res_ari_channels.so</code></div>
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">res_ari_recordings.so</code></div>
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">res_http_websocket.so</code></div>
          <div style="display:flex;align-items:center;gap:6px"><span style="color:var(--sem-green)">✓</span><code style="font-family:var(--mono);font-size:11px">app_stasis.so</code></div>
        </div>
      </div>

      <div style="display:flex;justify-content:space-between;gap:12px;margin-top:32px;padding-top:24px;border-top:1px solid var(--line)">
        <button class="btn btn-ghost">← Wstecz (Local AI)</button>
        <div style="display:flex;gap:8px">
          <button class="btn btn-ghost">Test connection</button>
          <button class="btn btn-primary">Zapisz i dalej →</button>
        </div>
      </div>
    </div>
  </div>
</div>`;
