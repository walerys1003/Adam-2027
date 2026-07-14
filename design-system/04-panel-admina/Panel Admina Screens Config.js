/* ============================================
   CORE CONFIG SCREENS
   Agenci · Providers · Pipelines · Contexts · Audio Profiles · Tools · MCP
   ============================================ */

/* ------------ AGENTS ------------ */
SCREEN_RENDERERS.agents = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Multi-Agent System · <em>12 aktywnych</em></h1>
      <div class="sub">
        <span>7 PROD · 2 A/B · 3 STAGING</span>
        <span class="sep">·</span><span>Domyślny: <strong style="color:var(--zloto-700);font-family:var(--serif)">welfare-morning v7.4.2</strong></span>
        <span class="sep">·</span><span>Śr. rating: 4.7 ★</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Import YAML</button>
      <button class="btn btn-ghost">Bulk deploy</button>
      <button class="btn btn-accent">+ Nowy agent</button>
    </div>
  </div>

  <!-- Routing analytics -->
  <div class="grid-2" style="margin-bottom:24px">
    <div class="card">
      <div class="card-head"><div><div class="t">Routing Source · <em>skąd przychodzą wywołania</em></div><div class="h-sub">Ostatnie 24h · 2,347 rozmów</div></div></div>
      <div style="padding:20px 24px">
        ${[
          {label:'Scheduled (welfare check)',pct:82,n:1924},
          {label:'Inbound (senior dzwoni)',pct:12,n:281},
          {label:'Family callback',pct:4,n:94},
          {label:'Emergency escalation',pct:2,n:48},
        ].map(r => `
          <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:12.5px">
              <span style="color:var(--granat-900);font-weight:500">${r.label}</span>
              <span style="font-family:var(--mono);color:var(--ink-500)">${r.n} · ${r.pct}%</span>
            </div>
            <div class="prog large" style="color:var(--zloto-500)"><div class="fill" style="width:${r.pct}%"></div></div>
          </div>
        `).join('')}
      </div>
    </div>
    <div class="card">
      <div class="card-head"><div><div class="t">Distribution by Agent · <em>top 5</em></div><div class="h-sub">Ostatnie 24h · 12 agentów</div></div></div>
      <div style="padding:20px 24px">
        ${[
          {name:'adam-med-reminder',pct:100,n:2847,color:'var(--zloto-500)'},
          {name:'adam-welfare-morning',pct:44,n:1247,color:'var(--zloto-500)'},
          {name:'adam-welfare-evening',pct:42,n:1183,color:'var(--zloto-500)'},
          {name:'adam-concierge',pct:11,n:312,color:'var(--zloto-400)'},
          {name:'adam-welfare-B (A/B)',pct:7,n:187,color:'var(--info-blue)'},
        ].map(r => `
          <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:12.5px">
              <span style="font-family:var(--mono);color:var(--granat-900);font-weight:500">${r.name}</span>
              <span style="font-family:var(--mono);color:var(--ink-500)">${r.n.toLocaleString('pl')}</span>
            </div>
            <div class="prog large" style="color:${r.color}"><div class="fill" style="width:${r.pct}%"></div></div>
          </div>
        `).join('')}
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-head"><div><div class="t">Zarządzaj agentami · <em>Manage Agents</em></div><div class="h-sub">CRUD · dialplan snippets · A/B tests</div></div>
      <div class="r"><button class="btn btn-ghost btn-sm">Kopiuj dialplan</button></div>
    </div>
    <div class="table-wrap"><table class="data">
      <thead><tr><th></th><th>Agent</th><th>Wersja</th><th>Model + Voice</th><th>Env</th><th>Rozmowy 24h</th><th>Rating</th><th>p95</th><th>Deploy</th><th></th></tr></thead>
      <tbody>
        ${AGENTS_DATA.map(a => `
          <tr data-drill="agent" data-drill-arg="${a.id}">
            <td style="width:32px">${a.default ? '<span title="Default agent" style="color:var(--zloto-500);font-size:16px">★</span>' : ''}</td>
            <td><div class="row-name"><div class="row-av-wrap"><div class="row-av">${a.initials}</div></div><div><div class="n">${a.name}</div><div class="id">${a.role}</div></div></div></td>
            <td class="num-mono">${a.ver}</td>
            <td class="num-mono">${a.model}<br/><span style="color:var(--zloto-700)">${a.voice}</span></td>
            <td><span class="b ${a.envColor}"><span class="dot"></span>${a.env}</span></td>
            <td class="num-mono">${a.calls}</td>
            <td>${a.rating ? `<span class="num-serif">${a.rating}</span> <span style="color:var(--zloto-500)">★</span>` : '<span style="color:var(--ink-500)">—</span>'}</td>
            <td class="num-mono">${a.p95}</td>
            <td class="num-mono muted">${a.deploy}<br/><span style="font-family:var(--mono);font-size:10px">${a.deployBy}</span></td>
            <td><button class="btn btn-ghost btn-sm">Prompt →</button></td>
          </tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>

  <!-- Dialplan snippet -->
  <div class="section-hd" style="margin-top:32px"><h2>Dialplan · <em>Copy Dialplan Manually</em></h2><span class="link">Wklej do /etc/asterisk/extensions.conf</span></div>
  <div class="card">
    <div style="padding:20px 24px">
      <div class="code" style="max-height:200px">
        <div class="code-line"><span class="code-num">1</span><span class="code-text"><span class="cm">; Adam AI Voice Agent · dialplan</span></span></div>
        <div class="code-line"><span class="code-num">2</span><span class="code-text"><span class="cm">; Auto-generated · v7.4.2 · 2026-07-11</span></span></div>
        <div class="code-line"><span class="code-num">3</span><span class="code-text"></span></div>
        <div class="code-line"><span class="code-num">4</span><span class="code-text"><span class="kw">[ai_agent]</span></span></div>
        <div class="code-line"><span class="code-num">5</span><span class="code-text">exten =&gt; _X.,1,<span class="fn">NoOp</span>(Incoming call to <span class="var">\${EXTEN}</span>)</span></div>
        <div class="code-line"><span class="code-num">6</span><span class="code-text">   same =&gt; n,<span class="fn">Set</span>(<span class="var">AI_AGENT</span>=welfare-morning)</span></div>
        <div class="code-line"><span class="code-num">7</span><span class="code-text">   same =&gt; n,<span class="fn">Set</span>(<span class="var">AI_PROVIDER</span>=openai_realtime)</span></div>
        <div class="code-line"><span class="code-num">8</span><span class="code-text">   same =&gt; n,<span class="fn">Answer</span>()</span></div>
        <div class="code-line"><span class="code-num">9</span><span class="code-text">   same =&gt; n,<span class="fn">Stasis</span>(ai_agent,<span class="var">\${EXTEN}</span>)</span></div>
        <div class="code-line"><span class="code-num">10</span><span class="code-text">   same =&gt; n,<span class="fn">Hangup</span>()</span></div>
      </div>
    </div>
  </div>
</div>`;

const AGENTS_DATA = [
  {id:'welfare-morning',initials:'AW',name:'adam-welfare-morning',role:'Poranny welfare check · 08:00–10:00',ver:'v7.4.2',model:'gpt-4o + claude-3.5',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'1,247',rating:'4.8',p95:'687ms',deploy:'2 dni temu',deployBy:'Krzysztof M.',default:true},
  {id:'welfare-evening',initials:'AE',name:'adam-welfare-evening',role:'Wieczorny welfare check · 19:00–21:00',ver:'v7.4.2',model:'gpt-4o + claude-3.5',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'1,183',rating:'4.7',p95:'712ms',deploy:'2 dni temu',deployBy:'Krzysztof M.'},
  {id:'crisis-triage',initials:'AC',name:'adam-crisis-triage',role:'Kryzysowy · Red/Purple escalation',ver:'v3.1.0',model:'claude-3.5-sonnet',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'47',rating:'4.9',p95:'445ms',deploy:'7 dni temu',deployBy:'Anna W.'},
  {id:'med-reminder',initials:'AM',name:'adam-med-reminder',role:'Przypomnienia leków · schedule',ver:'v2.4.1',model:'gpt-4o-mini',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'2,847',rating:'4.6',p95:'312ms',deploy:'14 dni temu',deployBy:'Krzysztof M.'},
  {id:'concierge',initials:'AK',name:'adam-concierge',role:'Concierge · zamawianie usług',ver:'v1.2.0',model:'gpt-4o',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'312',rating:'4.9',p95:'523ms',deploy:'21 dni temu',deployBy:'Marta L.'},
  {id:'family-callback',initials:'AF',name:'adam-family-callback',role:'Zwrotne od rodziny',ver:'v1.0.2',model:'gpt-4o-mini',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'94',rating:'4.7',p95:'298ms',deploy:'21 dni temu',deployBy:'Marta L.'},
  {id:'onboarding',initials:'AO',name:'adam-onboarding',role:'Pierwsza rozmowa · zapoznawcza',ver:'v0.9.4',model:'gpt-4o',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'8',rating:'4.6',p95:'612ms',deploy:'30 dni temu',deployBy:'Anna W.'},
  {id:'welfare-B',initials:'AB',name:'adam-welfare-B (A/B test)',role:'Nowa persona · warm-empathetic',ver:'v7.5.0-rc1',model:'gpt-4o + claude-3.5',voice:'pl-Adam-M2',env:'A/B 15%',envColor:'yellow',calls:'187',rating:'4.8',p95:'698ms',deploy:'Wczoraj',deployBy:'Krzysztof M.'},
  {id:'familiar-dialects',initials:'AD',name:'adam-familiar-dialects',role:'Experimental · wielkopolskie',ver:'v0.9.0',model:'gpt-4o + fine-tune',voice:'pl-Adam-M',env:'STAGING',envColor:'yellow',calls:'12',rating:null,p95:'834ms',deploy:'Dziś 11:34',deployBy:'Krzysztof M.'},
  {id:'silesian-test',initials:'AS',name:'adam-silesian-test',role:'Experimental · śląskie',ver:'v0.1.0',model:'gpt-4o + fine-tune',voice:'pl-Adam-M',env:'STAGING',envColor:'yellow',calls:'0',rating:null,p95:'—',deploy:'Wczoraj',deployBy:'Anna W.'},
  {id:'medical-report',initials:'MR',name:'adam-medical-report',role:'Rozmowa z lekarzem · FHIR',ver:'v0.5.2',model:'claude-3.5-sonnet',voice:'pl-Adam-F',env:'STAGING',envColor:'yellow',calls:'3',rating:null,p95:'523ms',deploy:'5 dni temu',deployBy:'Marta L.'},
  {id:'demo-showcase',initials:'DM',name:'adam-demo',role:'Demo dla sprzedaży',ver:'v1.0.0',model:'gpt-4o-mini',voice:'pl-Adam-M',env:'PROD',envColor:'green',calls:'2',rating:'5.0',p95:'234ms',deploy:'2 mies. temu',deployBy:'Marta L.'},
];

/* AGENT DETAIL - prompt editor */
DETAIL_RENDERERS.agent = (id) => {
  const a = AGENTS_DATA.find(x => x.id === id) || AGENTS_DATA[0];
  return `
<div class="content-inner">
  <a href="#" class="back-link js-back" data-back="agents">← Wróć do listy agentów</a>

  <div class="detail-head">
    <div class="detail-head-grid">
      <div class="dh-av">${a.initials}</div>
      <div class="dh-info">
        <h1>${a.name}</h1>
        <div class="meta">
          <span><span class="pip ${a.envColor}"><span class="dot"></span>${a.env}</span></span><span class="sep"></span>
          <span>${a.ver}</span><span class="sep"></span>
          <span>${a.role}</span>
        </div>
        <div class="quick-stats">
          <div class="qs"><div class="l">Model</div><div class="v" style="font-size:14px;font-family:var(--sans);font-weight:500">${a.model}</div></div>
          <div class="qs"><div class="l">Voice</div><div class="v" style="font-size:14px;font-family:var(--mono);color:var(--zloto-700)">${a.voice}</div></div>
          <div class="qs"><div class="l">Rozmowy 24h</div><div class="v">${a.calls}</div></div>
          <div class="qs"><div class="l">Rating</div><div class="v">${a.rating||'—'} <span style="font-size:14px;color:var(--zloto-500)">★</span></div></div>
          <div class="qs"><div class="l">Latencja p95</div><div class="v">${a.p95}</div></div>
        </div>
      </div>
      <div class="dh-actions">
        <div class="last-call">Ostatni deploy<strong>${a.deploy}</strong></div>
        <button class="btn btn-primary">▶ Test call</button>
        <button class="btn btn-ghost">Diff · commit</button>
      </div>
    </div>
  </div>

  <div class="subtabs">
    <div class="subtab active" data-tab="prompt">System Prompt</div>
    <div class="subtab" data-tab="tools">Tools <span class="count">8</span></div>
    <div class="subtab" data-tab="voice">Voice & Audio</div>
    <div class="subtab" data-tab="guardrails">Guardrails</div>
    <div class="subtab" data-tab="ab">A/B Testing</div>
    <div class="subtab" data-tab="metrics">Metryki</div>
    <div class="subtab" data-tab="deploy">Deploy History</div>
  </div>

  <div class="subtab-panel active" id="tp-prompt">
    <div class="split-2-1">
      <div class="card">
        <div class="editor-toolbar">
          <button>File</button><button>Edit</button><button>Test</button><button>Diff</button>
          <div class="sep"></div>
          <button>▶ Test call</button><button>💾 Save draft</button>
          <button style="background:var(--zloto-500);color:var(--granat-900);border-color:var(--zloto-500);font-weight:600">Deploy → PROD</button>
          <div style="margin-left:auto">system_prompt.yaml · 42/218 lines</div>
        </div>
        <div class="code" style="border-radius:0;max-height:520px">
          <div class="code-line"><span class="code-num">1</span><span class="code-text"><span class="cm"># ${a.name} · system_prompt ${a.ver}</span></span></div>
          <div class="code-line"><span class="code-num">2</span><span class="code-text"><span class="cm"># Ostatnia zmiana: ${a.deploy} · ${a.deployBy}</span></span></div>
          <div class="code-line"><span class="code-num">3</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">4</span><span class="code-text"><span class="kw">role:</span> <span class="str">"system"</span></span></div>
          <div class="code-line"><span class="code-num">5</span><span class="code-text"><span class="kw">persona:</span></span></div>
          <div class="code-line"><span class="code-num">6</span><span class="code-text">  <span class="kw">name:</span> <span class="str">"Adam"</span></span></div>
          <div class="code-line"><span class="code-num">7</span><span class="code-text">  <span class="kw">voice_id:</span> <span class="str">"${a.voice}"</span></span></div>
          <div class="code-line"><span class="code-num">8</span><span class="code-text">  <span class="kw">tone:</span> <span class="str">"ciepły, spokojny, powolny — jak zaufany sąsiad"</span></span></div>
          <div class="code-line"><span class="code-num">9</span><span class="code-text">  <span class="kw">pace:</span> <span class="num">0.85</span>  <span class="cm"># -15% vs default</span></span></div>
          <div class="code-line"><span class="code-num">10</span><span class="code-text">  <span class="kw">pitch:</span> <span class="num">-2st</span></span></div>
          <div class="code-line"><span class="code-num">11</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">12</span><span class="code-text"><span class="kw">context:</span></span></div>
          <div class="code-line"><span class="code-num">13</span><span class="code-text">  <span class="kw">senior:</span> <span class="var">{{senior.first_name}}</span>, <span class="var">{{senior.age}}</span> lat</span></div>
          <div class="code-line"><span class="code-num">14</span><span class="code-text">  <span class="kw">location:</span> <span class="var">{{senior.district}}</span>, Poznań</span></div>
          <div class="code-line"><span class="code-num">15</span><span class="code-text">  <span class="kw">medications:</span> <span class="var">{{senior.medications}}</span></span></div>
          <div class="code-line"><span class="code-num">16</span><span class="code-text">  <span class="kw">last_call:</span> <span class="var">{{last_call.summary}}</span></span></div>
          <div class="code-line"><span class="code-num">17</span><span class="code-text">  <span class="kw">mood_trend_7d:</span> <span class="var">{{mood_trend}}</span></span></div>
          <div class="code-line"><span class="code-num">18</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">19</span><span class="code-text"><span class="kw">instructions:</span> <span class="str">|</span></span></div>
          <div class="code-line"><span class="code-num">20</span><span class="code-text">  <span class="str">Jesteś Adamem — cyfrowym asystentem opieki nad seniorem.</span></span></div>
          <div class="code-line"><span class="code-num">21</span><span class="code-text">  <span class="str">Dzwonisz do </span><span class="var">{{senior.first_name}}</span><span class="str"> na poranny welfare check.</span></span></div>
          <div class="code-line"><span class="code-num">22</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">23</span><span class="code-text">  <span class="str">ZASADY GŁÓWNE:</span></span></div>
          <div class="code-line"><span class="code-num">24</span><span class="code-text">  <span class="str">1. Zaczynasz od "Dzień dobry Pani/Panie </span><span class="var">{{last_name}}</span><span class="str">"</span></span></div>
          <div class="code-line"><span class="code-num">25</span><span class="code-text">  <span class="str">2. Pytasz o sen, ból, samopoczucie</span></span></div>
          <div class="code-line"><span class="code-num">26</span><span class="code-text">  <span class="str">3. Przypominasz o lekach z </span><span class="var">{{today_meds}}</span></span></div>
          <div class="code-line"><span class="code-num">27</span><span class="code-text">  <span class="str">4. Notujesz mood na skali 0-1 (analiza tonu + treści)</span></span></div>
          <div class="code-line"><span class="code-num">28</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">29</span><span class="code-text">  <span class="str">GUARDRAILS MEDYCZNE:</span></span></div>
          <div class="code-line"><span class="code-num">30</span><span class="code-text">  <span class="str">- NIE diagnozuj. NIE zalecaj leków. NIE zmieniaj dawek.</span></span></div>
          <div class="code-line"><span class="code-num">31</span><span class="code-text">  <span class="str">- Jeśli senior mówi o bólu w klatce piersiowej,</span></span></div>
          <div class="code-line"><span class="code-num">32</span><span class="code-text">  <span class="str">  duszności, "coś dziwnego z sercem" → escalate</span></span></div>
          <div class="code-line"><span class="code-num">33</span><span class="code-text">  <span class="str">  → tool_call: raise_semafor("red", trigger="verbal_cardiac")</span></span></div>
          <div class="code-line"><span class="code-num">34</span><span class="code-text"></span></div>
          <div class="code-line"><span class="code-num">35</span><span class="code-text">  <span class="str">DIALEKT WIELKOPOLSKI:</span></span></div>
          <div class="code-line"><span class="code-num">36</span><span class="code-text">  <span class="str">- "szneka" = drożdżówka</span></span></div>
          <div class="code-line"><span class="code-num">37</span><span class="code-text">  <span class="str">- "bimba" = tramwaj</span></span></div>
          <div class="code-line"><span class="code-num">38</span><span class="code-text">  <span class="str">- "tej" = zawołanie, nie pomijaj kontekstem</span></span></div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-head"><div><div class="t">Zmienne kontekstowe</div><div class="h-sub">Injected przy runtime</div></div></div>
          <div style="padding:16px 24px">
            ${['{{senior.first_name}}','{{senior.age}}','{{senior.district}}','{{senior.medications}}','{{last_call.summary}}','{{mood_trend}}','{{today_meds}}','{{last_name}}'].map(v => `
              <div style="padding:8px 0;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center">
                <code class="num-mono" style="color:var(--info-blue)">${v}</code>
                <span class="pip green"><span class="dot"></span>bound</span>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="card" style="margin-top:16px">
          <div class="card-head"><div><div class="t">Recent changes</div><div class="h-sub">Git log · ostatnie 5</div></div></div>
          <div style="padding:16px 24px">
            ${[
              {sha:'a4f2b8c',msg:'Fix: rozpoznawanie "szneka" i "bimba"',by:'Krzysztof M.',when:'2 dni'},
              {sha:'c8e1d3a',msg:'Add: dialekt wielkopolski (guardrails)',by:'Anna W.',when:'5 dni'},
              {sha:'b1f7e2d',msg:'Tune: pace 0.9 → 0.85 (feedback 30+ seniorów)',by:'Krzysztof M.',when:'7 dni'},
              {sha:'d3a9f4b',msg:'Fix: mood scoring w PL kontekście',by:'Marta L.',when:'12 dni'},
            ].map(c => `
              <div style="padding:10px 0;border-bottom:1px solid var(--line)">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                  <code class="num-mono" style="color:var(--zloto-700)">${c.sha}</code>
                  <span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em">${c.when} temu</span>
                </div>
                <div style="font-size:12.5px;color:var(--granat-900)">${c.msg}</div>
                <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;letter-spacing:0.02em">${c.by}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-tools">
    <div class="card">
      <div class="card-head"><div><div class="t">Tools dostępne dla agenta · <em>8 aktywnych</em></div><div class="h-sub">Function calling · JSON Schema</div></div><button class="btn btn-ghost btn-sm">+ Dołącz tool</button></div>
      <div class="grid-2" style="padding:20px 24px">
        ${[
          {n:'get_medication_schedule',d:'Pobiera harmonogram leków seniora',ph:'in_call',type:'built-in'},
          {n:'submit_medication_compliance',d:'Zapisuje compliance po pytaniu o leki',ph:'in_call',type:'built-in'},
          {n:'raise_semafor',d:'Podnosi poziom semafora (green→yellow→red→purple)',ph:'in_call',type:'built-in'},
          {n:'notify_family',d:'Wysyła SMS/push do opiekunów seniora',ph:'in_call',type:'HTTP'},
          {n:'dial_112',d:'Auto-dial 112 z podaniem adresu i danych medycznych',ph:'in_call',type:'built-in · guarded'},
          {n:'get_wearable_data',d:'Pobiera HR/SpO₂/steps z Xiaomi/Apple/Garmin',ph:'in_call',type:'HTTP'},
          {n:'log_mood',d:'Zapisuje mood score do bazy',ph:'post_call',type:'built-in'},
          {n:'generate_summary',d:'Generuje krótki raport rozmowy dla rodziny',ph:'post_call',type:'built-in'},
        ].map(t => `
          <div class="tool-card">
            <div class="t-head"><div class="t-ic"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg></div><div><div class="t-name">${t.n}()</div><div class="t-kind">${t.ph} · ${t.type}</div></div></div>
            <div class="t-desc">${t.d}</div>
          </div>
        `).join('')}
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-voice">
    <div class="grid-2">
      <div class="card"><div class="card-head"><div><div class="t">Voice · <em>${a.voice}</em></div><div class="h-sub">ElevenLabs TTS v2.5</div></div></div>
        <div style="padding:20px 24px">
          <div class="form-group"><label>Voice ID</label><input type="text" value="${a.voice}"/></div>
          <div class="form-group"><label>Pace (tempo)</label><input type="text" value="0.85 · -15% vs default"/><div class="help">Optymalne dla seniorów: 0.80–0.90</div></div>
          <div class="form-group"><label>Pitch</label><input type="text" value="-2 semitones"/><div class="help">Niższy głos = wyższa wiarygodność dla &gt;70 lat</div></div>
          <div class="form-group"><label>Stability</label><input type="text" value="0.75"/></div>
          <button class="btn btn-ghost">▶ Preview: "Dzień dobry Pani Halino"</button>
        </div>
      </div>
      <div class="card"><div class="card-head"><div><div class="t">Audio · post-processing</div><div class="h-sub">Senior speech optimization (F13)</div></div></div>
        <div style="padding:20px 24px">
          <div class="form-group"><label>EQ boost 2–4 kHz</label><input type="text" value="+3 dB"/><div class="help">Pomaga w niedosłuchu wysokotonowym</div></div>
          <div class="form-group"><label>Dynamic compression</label><input type="text" value="4:1 · -12 dB threshold"/></div>
          <div class="form-group"><label>Codec</label><select><option>OPUS 24kHz</option><option>PCM 16-bit 8kHz (PSTN)</option><option>μ-law 8kHz</option></select></div>
          <div class="form-group"><label>Jitter buffer</label><input type="text" value="80ms adaptive"/></div>
        </div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-guardrails">
    <div class="card"><div class="card-head"><div><div class="t">Guardrails · <em>3 warstwy · v2.1</em></div><div class="h-sub">Medical + Crisis + PII filters</div></div><span class="pip green"><span class="dot"></span>Active</span></div>
      <div style="padding:24px">
        ${[
          {name:'Medical guardrails',desc:'Blokuje diagnozy, rekomendacje leków, zmiany dawek. Fallback: „Zapytaj lekarza."',rules:12,status:'active'},
          {name:'Crisis detection',desc:'40+ triggerów: „ból w klatce", „nie mogę oddychać", „upadłem". Auto-escalate.',rules:47,status:'active'},
          {name:'PII redaction',desc:'Automatyczne maskowanie PESEL, numerów kart, adresów IP w logach.',rules:8,status:'active'},
          {name:'Prompt injection',desc:'Detekcja prób jailbreaku ("ignore previous instructions"). Fallback do skryptu.',rules:15,status:'active'},
        ].map(g => `
          <div style="padding:16px 20px;background:var(--paper-2);border-radius:10px;margin-bottom:12px;display:grid;grid-template-columns:1fr auto auto;gap:16px;align-items:center">
            <div><div style="font-family:var(--serif);font-size:16px;color:var(--granat-900);font-weight:500">${g.name}</div><div style="font-size:12.5px;color:var(--ink-700);margin-top:4px;line-height:1.5">${g.desc}</div></div>
            <div style="font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.04em"><strong style="font-family:var(--serif);font-size:16px;color:var(--granat-900);display:block">${g.rules}</strong>reguł</div>
            <span class="pip green"><span class="dot"></span>${g.status}</span>
          </div>
        `).join('')}
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-ab">
    <div class="card"><div class="card-head"><div><div class="t">A/B Testing · <em>v7.4.2 vs v7.5.0-rc1</em></div><div class="h-sub">85% baseline · 15% experiment · n=187</div></div><span class="pip yellow"><span class="dot"></span>In progress</span></div>
      <div class="grid-2" style="padding:24px">
        <div style="padding:20px;background:var(--paper-2);border-radius:10px">
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.14em;text-transform:uppercase;margin-bottom:8px">Baseline · v7.4.2</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);font-weight:500">4.7</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">RATING</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);font-weight:500">0.71</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">MOOD ŚR.</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);font-weight:500">687ms</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">P95</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--granat-900);font-weight:500">96.4%</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">SUCCESS</div></div>
          </div>
        </div>
        <div style="padding:20px;background:var(--info-blue-bg);border-radius:10px;border:1px solid var(--info-blue)">
          <div style="font-family:var(--mono);font-size:10px;color:var(--info-blue);letter-spacing:0.14em;text-transform:uppercase;margin-bottom:8px">Experiment · v7.5.0-rc1</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--info-blue);font-weight:500">4.8<span style="font-size:14px;color:var(--sem-green)"> ↑0.1</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">RATING</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--info-blue);font-weight:500">0.74<span style="font-size:14px;color:var(--sem-green)"> ↑0.03</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">MOOD ŚR.</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--info-blue);font-weight:500">698ms<span style="font-size:14px;color:var(--sem-yellow)"> ↑11ms</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">P95</div></div>
            <div><div style="font-family:var(--serif);font-size:28px;color:var(--info-blue);font-weight:500">97.1%<span style="font-size:14px;color:var(--sem-green)"> ↑0.7</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em">SUCCESS</div></div>
          </div>
        </div>
      </div>
      <div style="padding:16px 24px;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center">
        <div style="font-size:12px;color:var(--ink-500)">Statistical significance: <strong style="color:var(--granat-900);font-family:var(--mono)">p=0.03</strong> (przekracza 95% CI)</div>
        <div style="display:flex;gap:8px"><button class="btn btn-ghost btn-sm">Zwiększ do 30%</button><button class="btn btn-accent">🎯 Promote to PROD</button></div>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-metrics">
    <div class="card"><div class="card-head"><div><div class="t">Metryki · <em>ostatnie 7 dni</em></div></div></div>
      <div class="chart-area" style="height:280px;padding:24px">
        <svg class="chart-svg" viewBox="0 0 700 240" preserveAspectRatio="none">
          ${[40,80,120,160,200].map(y => `<line class="grid" x1="30" y1="${y}" x2="700" y2="${y}"/>`).join('')}
          <path d="M30,180 L130,160 L230,155 L330,145 L430,150 L530,140 L630,135 L700,130" stroke="var(--zloto-500)" stroke-width="2" fill="none"/>
          <path d="M30,60 L130,72 L230,68 L330,55 L430,60 L530,50 L630,52 L700,48" stroke="var(--sem-green)" stroke-width="2" fill="none"/>
          <path d="M30,120 L130,110 L230,105 L330,115 L430,108 L530,100 L630,95 L700,92" stroke="var(--info-blue)" stroke-width="2" fill="none"/>
        </svg>
      </div>
    </div>
  </div>

  <div class="subtab-panel" id="tp-deploy">
    <div class="card"><div class="card-head"><div><div class="t">Deploy history</div><div class="h-sub">Wszystkie wersje tego agenta</div></div></div>
      <div class="table-wrap"><table class="data compact">
        <thead><tr><th>Wersja</th><th>Deploy</th><th>Author</th><th>Env</th><th>Rozmowy</th><th>Rating</th><th>Rollback</th></tr></thead>
        <tbody>
          <tr class="sel"><td class="num-mono">v7.4.2 <span class="pip green"><span class="dot"></span>current</span></td><td class="num-mono">2 dni temu</td><td>Krzysztof M.</td><td><span class="pip green"><span class="dot"></span>PROD 85%</span></td><td class="num-mono">8,432</td><td>4.7 ★</td><td>—</td></tr>
          <tr><td class="num-mono">v7.4.1</td><td class="num-mono">7 dni temu</td><td>Anna W.</td><td>—</td><td class="num-mono">32,847</td><td>4.6 ★</td><td><button class="btn btn-ghost btn-xs">Rollback</button></td></tr>
          <tr><td class="num-mono">v7.4.0</td><td class="num-mono">14 dni temu</td><td>Krzysztof M.</td><td>—</td><td class="num-mono">44,192</td><td>4.6 ★</td><td><button class="btn btn-ghost btn-xs">Rollback</button></td></tr>
          <tr><td class="num-mono">v7.3.2</td><td class="num-mono">28 dni temu</td><td>Marta L.</td><td>—</td><td class="num-mono">62,314</td><td>4.5 ★</td><td><button class="btn btn-ghost btn-xs">Rollback</button></td></tr>
        </tbody>
      </table></div>
    </div>
  </div>
</div>`;
};

/* ------------ PROVIDERS ------------ */
SCREEN_RENDERERS.providers = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Providers · <em>7 aktywnych</em></h1>
      <div class="sub">
        <span>3 LLM · 2 STT · 2 TTS · 1 Realtime · 1 Backup</span>
        <span class="sep">·</span><span>Health check: co 30s</span>
        <span class="sep">·</span><span>1 provider degraded (Google chirp-2)</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Health check</button>
      <button class="btn btn-ghost">Import config</button>
      <button class="btn btn-accent">+ Dodaj provider</button>
    </div>
  </div>

  <!-- Provider cards grid (11 typów z kodu ProvidersPage.tsx) -->
  <div class="section-hd"><h2>Aktywne providers</h2><span class="link">Kliknij aby edytować konfigurację</span></div>
  <div class="grid-3">
    ${[
      {name:'OpenAI',kind:'Realtime + LLM',logo:'OAI',caps:['gpt-4o-realtime','gpt-4o','gpt-4o-mini'],lat:'687ms',succ:'99.94%',cost:'$0.62',status:'ok'},
      {name:'Anthropic',kind:'LLM · Guardrails',logo:'ANT',caps:['claude-3.5-sonnet','claude-3-haiku'],lat:'892ms',succ:'99.88%',cost:'$0.71',status:'ok'},
      {name:'ElevenLabs',kind:'TTS',logo:'11L',caps:['tts-v2.5','pl-Adam-M','pl-Adam-F','pl-Adam-M2'],lat:'412ms',succ:'99.97%',cost:'$0.34',status:'ok'},
      {name:'Google Live',kind:'STT + Realtime',logo:'GOO',caps:['chirp-2 · pl-PL','gemini-live'],lat:'1.2s',succ:'98.4%',cost:'$0.22',status:'warn'},
      {name:'Deepgram',kind:'STT (backup)',logo:'DPG',caps:['nova-2','whisper-large'],lat:'387ms',succ:'99.9%',cost:'$0.28',status:'ok'},
      {name:'Local Whisper',kind:'STT · self-hosted',logo:'WHS',caps:['large-v3 (CUDA)','fine-tune senior-PL'],lat:'324ms',succ:'100%',cost:'$0.00',status:'ok'},
      {name:'Azure',kind:'TTS (backup)',logo:'AZR',caps:['neural-pl-Marek','neural-pl-Zofia'],lat:'523ms',succ:'99.6%',cost:'$0.24',status:'ok'},
    ].map(p => `
      <div class="prov-card">
        <div class="p-head"><div class="p-logo">${p.logo}</div><div><div class="p-name">${p.name}</div><div class="p-kind">${p.kind}</div></div><span class="pip ${p.status==='ok'?'green':'yellow'}" style="margin-left:auto"><span class="dot"></span>${p.status==='ok'?'OK':'Degraded'}</span></div>
        <div class="p-caps">${p.caps.map(c => `<span class="b neutral" style="font-family:var(--mono);font-size:10px">${c}</span>`).join('')}</div>
        <div class="p-metrics">
          <div><strong>${p.lat}</strong>Lat p95</div>
          <div><strong>${p.succ}</strong>Sukces</div>
          <div><strong>${p.cost}</strong>/ 1k tok</div>
        </div>
      </div>
    `).join('')}

    <!-- Available providers to add (grayed out) -->
    ${[
      {name:'Grok (xAI)',kind:'LLM',logo:'GRX'},
      {name:'Telnyx',kind:'PSTN gateway',logo:'TLN'},
      {name:'Ollama',kind:'LLM · self-hosted',logo:'OLL'},
      {name:'Cerebras',kind:'LLM · low-latency',logo:'CRB'},
    ].map(p => `
      <div class="prov-card" style="border-style:dashed;opacity:0.55">
        <div class="p-head"><div class="p-logo" style="background:var(--paper-2)">${p.logo}</div><div><div class="p-name">${p.name}</div><div class="p-kind">${p.kind}</div></div><button class="btn btn-ghost btn-sm" style="margin-left:auto">+ Add</button></div>
      </div>
    `).join('')}
  </div>

  <!-- Details of one provider (inline edit) -->
  <div class="section-hd" style="margin-top:32px"><h2>Edytuj · <em>OpenAI Realtime</em></h2><span class="link">gpt-4o-realtime · używane przez welfare-morning, welfare-evening</span></div>
  <div class="card">
    <div class="grid-2" style="padding:24px;gap:32px">
      <div>
        <div class="form-group"><label>API Key <span class="tooltip-icon">?</span></label><input type="password" value="sk-proj-8f7a2b••••••••••••••••••••••••••••••••abcd"/><div class="help">Klucz z platform.openai.com</div></div>
        <div class="form-group"><label>Organization ID</label><input type="text" value="org-silvertech-2026"/></div>
        <div class="form-group"><label>Default model</label><select><option>gpt-4o-realtime-preview-2024-12-17</option><option>gpt-4o-2024-11-20</option><option>gpt-4o-mini</option></select></div>
        <div class="form-row">
          <div class="form-group"><label>Temperature</label><input type="text" value="0.8"/></div>
          <div class="form-group"><label>Max tokens / turn</label><input type="text" value="4096"/></div>
        </div>
      </div>
      <div>
        <div class="form-group"><label>Voice (Realtime)</label><select><option>alloy</option><option>echo</option><option>fable</option><option>shimmer</option></select><div class="help">Używamy ElevenLabs zamiast, więc tu bez znaczenia</div></div>
        <div class="form-group"><label>VAD threshold</label><input type="text" value="0.5"/><div class="help">Voice Activity Detection · 0.4–0.6 dla seniorów</div></div>
        <div class="form-row cols-3">
          <div class="form-group"><label>Endpoint region</label><select><option>Frankfurt (EU)</option><option>US East</option></select></div>
          <div class="form-group"><label>Timeout</label><input type="text" value="30s"/></div>
          <div class="form-group"><label>Retries</label><input type="text" value="2"/></div>
        </div>
      </div>
    </div>
    <div style="padding:16px 24px;border-top:1px solid var(--line);display:flex;justify-content:space-between">
      <button class="btn btn-ghost">▶ Test connection</button>
      <div style="display:flex;gap:8px"><button class="btn btn-ghost">Anuluj</button><button class="btn btn-primary">💾 Zapisz</button></div>
    </div>
  </div>
</div>`;

/* ------------ PIPELINES ------------ */
SCREEN_RENDERERS.pipelines = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Pipelines · <em>4 aktywne</em></h1>
      <div class="sub"><span>STT → LLM → TTS routing · fallback logic · A/B routing</span></div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Import YAML</button>
      <button class="btn btn-accent">+ Nowy pipeline</button>
    </div>
  </div>

  ${[
    {name:'welfare-check-primary',desc:'Główny pipeline dla welfare checków porannych/wieczornych',stt:{p:'OpenAI Realtime',m:'gpt-4o-realtime'},llm:{p:'OpenAI',m:'gpt-4o-realtime'},tts:{p:'ElevenLabs',m:'pl-Adam-M'},status:'active',calls:'2,430'},
    {name:'welfare-check-backup',desc:'Fallback gdy OpenAI Realtime jest degraded',stt:{p:'Deepgram',m:'nova-2'},llm:{p:'Anthropic',m:'claude-3.5-sonnet'},tts:{p:'ElevenLabs',m:'pl-Adam-M'},status:'active',calls:'47'},
    {name:'crisis-triage',desc:'Zaostrzony pipeline dla wykrytych kryzysów',stt:{p:'Local Whisper',m:'large-v3'},llm:{p:'Anthropic',m:'claude-3.5-sonnet'},tts:{p:'ElevenLabs',m:'pl-Adam-M'},status:'active',calls:'47'},
    {name:'concierge-services',desc:'Zamawianie usług · pipeline zoptymalizowany kosztowo',stt:{p:'Local Whisper',m:'large-v3'},llm:{p:'OpenAI',m:'gpt-4o-mini'},tts:{p:'Azure',m:'neural-pl-Marek'},status:'active',calls:'312'},
  ].map(p => `
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div><div class="t">${p.name}</div><div class="h-sub">${p.desc}</div></div>
        <div class="r"><span class="pip green"><span class="dot"></span>Active · ${p.calls} rozmów</span><label class="switch"><input type="checkbox" checked/><span class="slider"></span></label></div>
      </div>
      <div style="padding:24px">
        <div class="pipe-stage">
          <div class="pipe-node">
            <div class="n-kind">STT · Speech-to-Text</div>
            <div class="n-name">${p.stt.p}</div>
            <div class="n-prov">${p.stt.m}</div>
          </div>
          <div class="pipe-arrow">→</div>
          <div class="pipe-node">
            <div class="n-kind">LLM · Language Model</div>
            <div class="n-name">${p.llm.p}</div>
            <div class="n-prov">${p.llm.m}</div>
          </div>
          <div class="pipe-arrow">→</div>
          <div class="pipe-node">
            <div class="n-kind">TTS · Text-to-Speech</div>
            <div class="n-name">${p.tts.p}</div>
            <div class="n-prov">${p.tts.m}</div>
          </div>
        </div>
      </div>
      <div style="padding:12px 24px;border-top:1px solid var(--line);display:flex;justify-content:flex-end;gap:6px">
        <button class="btn btn-ghost btn-sm">▶ Test</button>
        <button class="btn btn-ghost btn-sm">Klonuj</button>
        <button class="btn btn-ghost btn-sm">Edytuj</button>
      </div>
    </div>
  `).join('')}
</div>`;

/* ------------ CONTEXTS ------------ */
SCREEN_RENDERERS.contexts = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Contexts <em>(legacy)</em></h1>
      <div class="sub">
        <span class="live" style="color:var(--sem-yellow);background:var(--sem-yellow-bg)">Legacy — zastąpione przez Agents</span>
        <span class="sep">·</span><span>Zachowane dla kompatybilności · 6 kontekstów</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Migruj do Agents</button>
      <button class="btn btn-accent">+ Nowy kontekst</button>
    </div>
  </div>

  <div class="alert-strip warn">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2z"/><path d="M10 8v4M10 15v.5"/></svg></div>
    <div class="info-t">
      <div class="title">Contexts są legacy · przenieś do Multi-Agent System</div>
      <div class="desc">System kontekstów został zastąpiony przez system agentów (v7.0). Zachowany dla kompatybilności — nowe deploye powinny używać Agents. <strong>Migruj automatycznie w 1 kliknięciu.</strong></div>
    </div>
    <div class="cta-group"><button class="btn btn-ghost">Dokumentacja</button><button class="btn btn-danger" style="background:var(--sem-yellow);color:white">Migruj wszystkie</button></div>
  </div>

  <div class="card">
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Namespace</th><th>Opis</th><th>Provider</th><th>Model</th><th>Utworzony</th><th>Ostatnie użycie</th><th></th></tr></thead>
      <tbody>
        ${[
          ['general','Ogólny kontekst · fallback','openai','gpt-3.5-turbo','12 mies. temu','2 dni temu'],
          ['welfare-legacy','Stary welfare check (v6)','openai','gpt-4','8 mies. temu','30 dni temu'],
          ['medical-consult','Konsultacje medyczne','anthropic','claude-2','6 mies. temu','60 dni temu'],
          ['emergency-legacy','Emergency escalation (stary)','openai','gpt-4','8 mies. temu','60 dni temu'],
          ['test-context','Test/dev','openai','gpt-3.5-turbo','3 mies. temu','15 dni temu'],
          ['demo','Demo dla sprzedaży','openai','gpt-4','2 mies. temu','Dziś'],
        ].map(([n,d,p,m,c,l]) => `
          <tr><td class="num-mono" style="color:var(--zloto-700)">${n}</td><td style="font-size:12.5px">${d}</td><td>${p}</td><td class="num-mono">${m}</td><td class="num-mono muted">${c}</td><td class="num-mono muted">${l}</td><td style="display:flex;gap:4px"><button class="btn btn-ghost btn-xs">Migruj</button><button class="btn btn-ghost btn-xs">✕</button></td></tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>
</div>`;

/* ------------ AUDIO PROFILES ------------ */
SCREEN_RENDERERS.profiles = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Audio Profiles · <em>3 profile</em></h1>
      <div class="sub">
        <span>Senior Speech Optimization (F13)</span>
        <span class="sep">·</span><span>WER 3.6% na mowie senioralnej vs 8.2% baseline</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Zaimportuj</button>
      <button class="btn btn-accent">+ Nowy profil</button>
    </div>
  </div>

  <div class="grid-3">
    ${[
      {name:'senior-optimized',default:true,desc:'Domyślny profil dla wszystkich seniorów >65 lat',calls:'1,240',metrics:[['Tempo','-15% (0.85)'],['EQ 2-4kHz','+3 dB'],['Compression','4:1 · -12 dB'],['VAD','sensitivity 0.5'],['Codec','OPUS 24 kHz'],['Jitter buf','80ms adaptive'],['Noise gate','-45 dB threshold'],['De-esser','on · 6-8 kHz']]},
      {name:'default-adult',default:false,desc:'Baseline dla dorosłych <65 lat (rodzina, koordynatorzy)',calls:'87',metrics:[['Tempo','1.0 (normal)'],['EQ','flat'],['Compression','2:1'],['VAD','0.6'],['Codec','OPUS 48 kHz']]},
      {name:'pstn-optimized',default:false,desc:'Zoptymalizowany dla PSTN (stacjonarne telefony)',calls:'167',metrics:[['Tempo','-10% (0.9)'],['EQ 1-3kHz','+2 dB'],['Compression','5:1'],['Codec','G.711 μ-law 8kHz'],['Bandwidth','300-3400 Hz'],['DTMF','on']]},
    ].map(p => `
      <div class="card">
        <div class="card-head">
          <div><div class="t">${p.name} ${p.default?'<span style="color:var(--zloto-500);font-size:14px;margin-left:6px">★</span>':''}</div><div class="h-sub">${p.calls} użyć / 30d</div></div>
          <button class="btn btn-ghost btn-sm">Edytuj</button>
        </div>
        <div style="padding:16px 24px">
          <div style="font-size:12.5px;color:var(--ink-700);line-height:1.5;margin-bottom:16px">${p.desc}</div>
          ${p.metrics.map(([k,v]) => `
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line);font-size:12px">
              <span style="font-family:var(--mono);color:var(--ink-500);letter-spacing:0.04em">${k}</span>
              <span style="font-family:var(--mono);color:var(--granat-900);font-weight:500">${v}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('')}
  </div>

  <!-- Spec impact -->
  <div class="section-hd" style="margin-top:32px"><h2>Skuteczność · <em>senior-optimized vs default</em></h2><span class="link">A/B test na 400 seniorach, 90 dni</span></div>
  <div class="card">
    <div class="grid-4" style="padding:24px">
      <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Word Error Rate</div><div style="font-family:var(--serif);font-size:28px;color:var(--sem-green);margin-top:6px;font-weight:500">3.6<span style="font-size:14px">%</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:4px;letter-spacing:0.04em">vs baseline 8.2% (-56%)</div></div>
      <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Comprehension</div><div style="font-family:var(--serif);font-size:28px;color:var(--sem-green);margin-top:6px;font-weight:500">94<span style="font-size:14px">%</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:4px;letter-spacing:0.04em">vs 71% baseline (+23pp)</div></div>
      <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Success rate</div><div style="font-family:var(--serif);font-size:28px;color:var(--sem-green);margin-top:6px;font-weight:500">96.4<span style="font-size:14px">%</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:4px;letter-spacing:0.04em">vs 82% baseline</div></div>
      <div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Senior satisfaction</div><div style="font-family:var(--serif);font-size:28px;color:var(--sem-green);margin-top:6px;font-weight:500">4.7<span style="font-size:14px">★</span></div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:4px;letter-spacing:0.04em">vs 3.4 baseline</div></div>
    </div>
  </div>
</div>`;

/* ------------ TOOLS ------------ */
SCREEN_RENDERERS.tools = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Tools · <em>4 fazy · 47 narzędzi</em></h1>
      <div class="sub"><span>Function calling · pre_call · in_call · post_call · catalog</span></div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">📚 Katalog HTTP tools</button>
      <button class="btn btn-accent">+ Nowe narzędzie</button>
    </div>
  </div>

  <!-- Phase tabs -->
  <div class="subtabs" style="margin-bottom:20px">
    <div class="subtab active">In-call <span class="count">28</span></div>
    <div class="subtab">Pre-call <span class="count">8</span></div>
    <div class="subtab">Post-call <span class="count">6</span></div>
    <div class="subtab">Catalog · HTTP <span class="count">5</span></div>
  </div>

  <div class="section-hd"><h2>In-call tools · <em>używane podczas rozmowy</em></h2><span class="link">Adam wywołuje je w tle</span></div>

  <div class="grid-3">
    ${[
      {n:'get_medication_schedule',t:'built-in',desc:'Pobiera harmonogram leków seniora z bazy MedGuard',returns:'array[medication] · dose · time · frequency',used:'welfare-morning, welfare-evening, med-reminder'},
      {n:'submit_medication_compliance',t:'built-in',desc:'Zapisuje compliance po pytaniu Adama o wzięcie leków',returns:'{ok, adherence_updated}',used:'welfare-morning, welfare-evening'},
      {n:'raise_semafor',t:'built-in',desc:'Podnosi poziom semafora seniora (green→yellow→red→purple)',returns:'{semafor, escalation_triggered}',used:'crisis-triage, welfare-*'},
      {n:'notify_family',t:'HTTP',desc:'Wysyła SMS + push do opiekunów seniora',returns:'{sent_to: [], message_id}',used:'crisis-triage, welfare-*'},
      {n:'dial_112',t:'built-in · guarded',desc:'Auto-dial 112 z podaniem adresu i danych medycznych',returns:'{call_id, dispatcher_confirmed}',used:'crisis-triage (Purple only)'},
      {n:'get_wearable_data',t:'HTTP',desc:'Pobiera aktualne HR/SpO₂/steps z opaski',returns:'{hr, spo2, steps, sleep, fall_detected}',used:'crisis-triage, welfare-*'},
      {n:'get_mood_history',t:'built-in',desc:'Zwraca trend mood 7/14/30 dni',returns:'array[mood_score] · timestamp',used:'welfare-morning, welfare-evening'},
      {n:'order_service',t:'HTTP',desc:'Zamawia usługę u zaufanego partnera SilverTech',returns:'{order_id, partner, eta}',used:'concierge'},
      {n:'check_calendar',t:'HTTP',desc:'Sprawdza kalendarz Google/Outlook seniora',returns:'array[event] · title · time',used:'welfare-morning, concierge'},
    ].map(t => `
      <div class="tool-card">
        <div class="t-head"><div class="t-ic"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg></div><div><div class="t-name">${t.n}()</div><div class="t-kind">${t.t}</div></div></div>
        <div class="t-desc">${t.desc}</div>
        <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--line);font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em">
          <div style="margin-bottom:4px"><span style="color:var(--zloto-700)">returns:</span> <span style="color:var(--granat-900)">${t.returns}</span></div>
          <div><span style="color:var(--zloto-700)">used_by:</span> ${t.used}</div>
        </div>
      </div>
    `).join('')}
  </div>
</div>`;

/* ------------ MCP SERVERS ------------ */
SCREEN_RENDERERS.mcp = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">MCP Servers · <em>3 aktywne</em></h1>
      <div class="sub"><span>Model Context Protocol (Anthropic) · zewnętrzne konteksty i narzędzia</span></div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">📚 Katalog serwerów MCP</button>
      <button class="btn btn-accent">+ Dodaj serwer MCP</button>
    </div>
  </div>

  <div class="alert-strip info">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10" cy="10" r="8"/><path d="M10 6v4M10 14v.5"/></svg></div>
    <div class="info-t">
      <div class="title">Czym jest MCP?</div>
      <div class="desc">Model Context Protocol (Anthropic) pozwala Adamowi na standardowe łączenie się z zewnętrznymi bazami wiedzy, narzędziami i systemami. Zamiast pisać osobne integracje — używamy MCP.</div>
    </div>
  </div>

  <div class="card" style="margin-bottom:20px">
    <div class="card-head"><div><div class="t">Aktywne serwery MCP</div><div class="h-sub">Podłączone i sprawdzone</div></div></div>
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Nazwa</th><th>Endpoint</th><th>Typ</th><th>Wywołania 24h</th><th>Latencja</th><th>Status</th><th></th></tr></thead>
      <tbody>
        ${[
          {n:'medguard-mcp',url:'mcp://medguard.silvertech.pl',type:'Medications DB',calls:'2,847',lat:'42ms',status:'ok'},
          {n:'wearable-hub-mcp',url:'mcp://wearable.silvertech.pl',type:'Xiaomi/Apple/Garmin',calls:'8,412',lat:'156ms',status:'ok'},
          {n:'112-dispatcher-mcp',url:'mcps://ratunkowy.gov.pl',type:'Emergency dispatch',calls:'1',lat:'324ms',status:'ok'},
        ].map(s => `
          <tr>
            <td class="num-mono" style="color:var(--zloto-700)">${s.n}</td>
            <td class="num-mono muted">${s.url}</td>
            <td>${s.type}</td>
            <td class="num-mono">${s.calls}</td>
            <td class="num-mono">${s.lat}</td>
            <td><span class="pip green"><span class="dot"></span>Connected</span></td>
            <td style="display:flex;gap:4px"><button class="btn btn-ghost btn-xs">Test</button><button class="btn btn-ghost btn-xs">Edytuj</button></td>
          </tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>

  <div class="section-hd"><h2>Katalog dostępnych serwerów MCP</h2><span class="link">Publiczne + custom</span></div>
  <div class="grid-3">
    ${[
      {n:'filesystem',desc:'Dostęp do local filesystem (raporty PDF, transkrypty)',by:'Anthropic'},
      {n:'postgres',desc:'Query PostgreSQL (Adam DB)',by:'Anthropic'},
      {n:'brave-search',desc:'Web search dla concierge (Adam pyta o godziny sklepów)',by:'Anthropic'},
      {n:'google-calendar',desc:'Kalendarz seniora + rodziny',by:'Google'},
      {n:'sentry',desc:'Error tracking i alerts',by:'Sentry'},
      {n:'nfz-drugs',desc:'Baza leków refundowanych NFZ',by:'SilverTech (custom)'},
    ].map(s => `
      <div class="card" style="padding:20px 22px">
        <div style="font-family:var(--serif);font-size:16px;color:var(--granat-900);font-weight:500">${s.n}</div>
        <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em;margin-top:4px">by ${s.by}</div>
        <div style="font-size:12.5px;color:var(--ink-700);margin-top:12px;line-height:1.5">${s.desc}</div>
        <button class="btn btn-ghost btn-sm" style="margin-top:16px;width:100%;justify-content:center">+ Dodaj</button>
      </div>
    `).join('')}
  </div>
</div>`;
