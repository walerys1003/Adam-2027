/* ============================================
   SYSTEM SCREENS
   Environment · Docker · Asterisk · Models · Logs · Terminal
   ============================================ */

/* ------------ ENVIRONMENT ------------ */
SCREEN_RENDERERS.env = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Environment Variables · <em>.env</em></h1>
      <div class="sub">
        <span>78 zmiennych · 12 wymaganych · 3 secrets</span>
        <span class="sep">·</span><span>Zmiany wymagają restartu: ai_engine, admin_ui</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Backup .env</button>
      <button class="btn btn-ghost">Import .env</button>
      <button class="btn btn-primary" style="background:var(--sem-red)">Restart services</button>
    </div>
  </div>

  <div class="alert-strip warn">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2z"/></svg></div>
    <div class="info-t">
      <div class="title">Zmiany zapisane — wymagany restart</div>
      <div class="desc"><strong>2 zmiany</strong> oczekują na restart: <code style="font-family:var(--mono);font-size:11px;background:white;padding:1px 6px;border-radius:3px">OPENAI_API_KEY</code>, <code style="font-family:var(--mono);font-size:11px;background:white;padding:1px 6px;border-radius:3px">ELEVENLABS_VOICE_ID</code></div>
    </div>
    <div class="cta-group"><button class="btn btn-ghost">Zobacz diff</button><button class="btn btn-primary" style="background:var(--sem-yellow);color:white">Restart ai_engine</button></div>
  </div>

  <!-- Categories -->
  <div class="subtabs">
    <div class="subtab active">Wszystkie <span class="count">78</span></div>
    <div class="subtab">Core</div>
    <div class="subtab">Providers</div>
    <div class="subtab">Asterisk</div>
    <div class="subtab">Adam-specific</div>
    <div class="subtab">Secrets <span class="count">3</span></div>
    <div class="subtab">Advanced</div>
  </div>

  <!-- Env vars -->
  <div class="card">
    ${[
      {section:'Core',vars:[
        {k:'NODE_ENV',v:'production',type:'string',help:'Environment mode'},
        {k:'LOG_LEVEL',v:'info',type:'enum',help:'error, warn, info, debug'},
        {k:'ADMIN_UI_PORT',v:'3003',type:'number',help:'Port admin panelu'},
        {k:'AI_ENGINE_PORT',v:'8000',type:'number',help:''},
        {k:'DATABASE_URL',v:'postgres://silvertech:••••@db.frankfurt.silvertech.pl:5432/adam',type:'secret',help:'PostgreSQL connection'},
      ]},
      {section:'Adam-specific · SilverTech',vars:[
        {k:'ADAM_DEFAULT_VOICE',v:'pl-Adam-M',type:'string',help:'Domyślny voice ID (ElevenLabs)'},
        {k:'ADAM_WELFARE_MORNING_TIME',v:'08:00',type:'string',help:'Godzina porannego welfare check'},
        {k:'ADAM_WELFARE_EVENING_TIME',v:'19:00',type:'string',help:'Godzina wieczornego welfare check'},
        {k:'ADAM_SEMAFOR_ESCALATION_TIMEOUT',v:'60s',type:'string',help:'Timeout przed eskalacją Red→Purple'},
        {k:'ADAM_112_ENABLED',v:'true',type:'boolean',help:'⚠ Auto-dial 112 przy Purple'},
        {k:'ADAM_SMS_PROVIDER',v:'twilio',type:'enum',help:'twilio, textmagic, smsapi'},
      ]},
      {section:'Providers',vars:[
        {k:'OPENAI_API_KEY',v:'sk-proj-8f7a2b••••••••••••abcd',type:'secret',help:'OpenAI API key',modified:true},
        {k:'ANTHROPIC_API_KEY',v:'sk-ant-api03••••••••••••1234',type:'secret',help:'Anthropic API key'},
        {k:'ELEVENLABS_API_KEY',v:'••••••••••••••••',type:'secret',help:'ElevenLabs API key'},
        {k:'ELEVENLABS_VOICE_ID',v:'pl-Adam-M-v2.5',type:'string',help:'Voice ID',modified:true},
        {k:'DEEPGRAM_API_KEY',v:'••••••••••••••••',type:'secret',help:''},
      ]},
      {section:'Asterisk · ARI',vars:[
        {k:'ARI_URL',v:'http://asterisk.local:8088/ari',type:'string',help:''},
        {k:'ARI_USER',v:'AIAgent',type:'string',help:''},
        {k:'ARI_PASSWORD',v:'••••••••••••',type:'secret',help:''},
        {k:'ARI_APP_NAME',v:'ai_agent',type:'string',help:'Stasis application name'},
      ]},
    ].map(section => `
      <div style="border-bottom:1px solid var(--line)">
        <div style="padding:12px 24px;background:var(--paper-2);font-family:var(--mono);font-size:11px;color:var(--zloto-700);letter-spacing:0.14em;text-transform:uppercase;font-weight:500">${section.section}</div>
        ${section.vars.map(v => `
          <div style="padding:12px 24px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:260px 1fr auto;gap:16px;align-items:center${v.modified?';background:var(--sem-yellow-bg)':''}">
            <div>
              <code class="num-mono" style="color:var(--granat-900);font-weight:500">${v.k}${v.modified?' <span style="color:var(--sem-yellow);font-family:var(--sans);font-size:10px;background:white;padding:1px 5px;border-radius:3px;letter-spacing:0.06em">MODIFIED</span>':''}</code>
              <div style="font-size:11px;color:var(--ink-500);font-style:italic;margin-top:3px">${v.help}</div>
            </div>
            <div>
              <input type="${v.type==='secret'?'password':'text'}" value="${v.v}" style="width:100%;padding:6px 10px;border:1px solid var(--line-strong);border-radius:6px;font-family:var(--mono);font-size:12px;background:white;color:var(--ink-900)"/>
            </div>
            <div style="display:flex;gap:4px">
              <span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;background:var(--paper-2);border-radius:4px">${v.type}</span>
              <button class="btn btn-ghost btn-xs" title="Kopiuj">📋</button>
            </div>
          </div>
        `).join('')}
      </div>
    `).join('')}
  </div>
</div>`;

/* ------------ DOCKER ------------ */
SCREEN_RENDERERS.docker = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Docker Services · <em>4 kontenery</em></h1>
      <div class="sub">
        <span>Compose project: asterisk-ai-voice-agent</span>
        <span class="sep">·</span><span>Wszystkie healthy</span>
        <span class="sep">·</span><span>Zajętość images: 8.4 GB · volumes: 2.1 GB</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">docker-compose logs</button>
      <button class="btn btn-ghost">Prune unused</button>
      <button class="btn btn-primary" style="background:var(--sem-yellow);color:white">Restart all</button>
    </div>
  </div>

  <!-- Container tiles -->
  <div class="section-hd"><h2>Kontenery · <em>4 usługi</em></h2><span class="link">Live status · odświeżanie 10s</span></div>

  <div style="display:grid;gap:12px;margin-bottom:24px">
    ${[
      {name:'ai_engine',status:'ok',up:'48d 12h',cpu:'34.2%',ram:'2.4/4 GB',ports:'8000, 8001',image:'silvertech/adam-engine:7.4.2',health:'healthy'},
      {name:'admin_ui',status:'ok',up:'48d 12h',cpu:'2.1%',ram:'184/512 MB',ports:'3003',image:'silvertech/adam-ui:7.4.2',health:'healthy'},
      {name:'local_ai_server',status:'ok',up:'48d 12h',cpu:'67% GPU',ram:'12/24 GB',ports:'9000, 9001',image:'silvertech/whisper-server:1.2.0',health:'healthy'},
      {name:'asterisk',status:'ok',up:'48d 12h',cpu:'8.3%',ram:'380/1024 MB',ports:'5060, 5061, 8088, 8089',image:'asterisk:20-alpine',health:'healthy'},
    ].map(c => `
      <div class="container-tile ${c.status==='ok'?'':'err'}">
        <div class="c-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg></div>
        <div>
          <div class="c-name">${c.name}</div>
          <div class="c-meta">
            <span>Image: <code style="font-family:var(--mono)">${c.image}</code></span>
            <span>Uptime: ${c.up}</span>
            <span>Ports: ${c.ports}</span>
          </div>
        </div>
        <div style="display:flex;gap:16px;font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.04em">
          <div><strong style="font-family:var(--serif);font-size:14px;color:var(--granat-900);display:block">${c.cpu}</strong>CPU</div>
          <div><strong style="font-family:var(--serif);font-size:14px;color:var(--granat-900);display:block">${c.ram}</strong>RAM</div>
        </div>
        <div style="display:flex;gap:6px">
          <span class="c-status">● ${c.health}</span>
          <button class="btn btn-ghost btn-xs" title="Logs">📄</button>
          <button class="btn btn-ghost btn-xs" title="Terminal">⌨</button>
          <button class="btn btn-ghost btn-xs" title="Restart" style="color:var(--sem-yellow)">↻</button>
          <button class="btn btn-ghost btn-xs" title="Stop" style="color:var(--sem-red)">⏹</button>
        </div>
      </div>
    `).join('')}
  </div>

  <!-- Images + volumes -->
  <div class="grid-2">
    <div class="card">
      <div class="card-head"><div><div class="t">Images · <em>8.4 GB</em></div><div class="h-sub">docker images</div></div><button class="btn btn-ghost btn-sm">Prune</button></div>
      <div class="table-wrap"><table class="data compact">
        <thead><tr><th>Repository</th><th>Tag</th><th>Size</th><th>Created</th></tr></thead>
        <tbody>
          ${[
            ['silvertech/adam-engine','7.4.2','2.1 GB','2 dni'],
            ['silvertech/whisper-server','1.2.0','3.8 GB','30 dni'],
            ['silvertech/adam-ui','7.4.2','412 MB','2 dni'],
            ['asterisk','20-alpine','198 MB','2 mies.'],
            ['postgres','16-alpine','247 MB','2 mies.'],
            ['redis','7-alpine','42 MB','2 mies.'],
            ['silvertech/adam-engine','7.4.1 <span style="color:var(--sem-yellow);font-family:var(--mono);font-size:9px;padding:1px 4px;background:var(--sem-yellow-bg);border-radius:3px">unused</span>','2.1 GB','9 dni'],
          ].map(([r,t,s,c]) => `<tr><td class="num-mono">${r}</td><td class="num-mono" style="color:var(--zloto-700)">${t}</td><td class="num-mono">${s}</td><td class="num-mono muted">${c}</td></tr>`).join('')}
        </tbody>
      </table></div>
    </div>
    <div class="card">
      <div class="card-head"><div><div class="t">Volumes · <em>2.1 GB</em></div><div class="h-sub">Persistent storage</div></div></div>
      <div class="table-wrap"><table class="data compact">
        <thead><tr><th>Volume</th><th>Mount</th><th>Size</th><th>Driver</th></tr></thead>
        <tbody>
          ${[
            ['adam_postgres_data','/var/lib/postgresql/data','1.8 GB','local'],
            ['adam_media','/var/spool/asterisk/media','412 MB','local · bind'],
            ['adam_logs','/var/log/adam','67 MB','local'],
            ['adam_whisper_models','/models','—','local · shared'],
          ].map(([v,m,s,d]) => `<tr><td class="num-mono">${v}</td><td class="num-mono muted" style="font-size:11px">${m}</td><td class="num-mono">${s}</td><td>${d}</td></tr>`).join('')}
        </tbody>
      </table></div>
    </div>
  </div>
</div>`;

/* ------------ ASTERISK ------------ */
SCREEN_RENDERERS.asterisk = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Asterisk Setup · <em>ARI</em></h1>
      <div class="sub">
        <span>Live connection: <strong style="color:var(--sem-green)">Connected</strong></span>
        <span class="sep">·</span><span>Asterisk 20.5.0</span>
        <span class="sep">·</span><span>ARI: asterisk.local:8088</span>
        <span class="sep">·</span><span>17 aktywnych kanałów</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Kopiuj dialplan</button>
      <button class="btn btn-ghost">Reload asterisk</button>
      <button class="btn btn-primary">▶ Test connection</button>
    </div>
  </div>

  <div class="grid-2" style="margin-bottom:24px">
    <div class="card">
      <div class="card-head"><div><div class="t">ARI Connection</div><div class="h-sub">Live connection status to Asterisk REST Interface</div></div><span class="pip green"><span class="dot"></span>Connected</span></div>
      <div style="padding:20px 24px">
        <div style="display:grid;grid-template-columns:auto 1fr;gap:12px 20px;font-size:12.5px">
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">URL</div>
          <div class="num-mono">http://asterisk.local:8088/ari</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">User</div>
          <div class="num-mono">AIAgent</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">App name</div>
          <div class="num-mono">ai_agent</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">WebSocket</div>
          <div><span class="pip green"><span class="dot"></span>Connected · ws://asterisk.local:8088/ari/events</span></div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Uptime</div>
          <div class="num-mono">48d 12h 47m</div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><div><div class="t">Application Registration</div><div class="h-sub">Whether ai_agent app is registered</div></div><span class="pip green"><span class="dot"></span>Registered</span></div>
      <div style="padding:20px 24px">
        <div style="display:grid;grid-template-columns:auto 1fr;gap:12px 20px;font-size:12.5px">
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Stasis app</div>
          <div class="num-mono">ai_agent</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Extension</div>
          <div class="num-mono">_X. → Stasis(ai_agent,\${EXTEN})</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Kanały aktywne</div>
          <div><span class="num-serif">17</span> <span style="font-family:var(--mono);font-size:11px;color:var(--ink-500)">/ max 200</span></div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.08em;text-transform:uppercase">Rozmowy total</div>
          <div class="num-mono">18,432 (od uruchomienia)</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Required modules -->
  <div class="card" style="margin-bottom:24px">
    <div class="card-head"><div><div class="t">Required Modules</div><div class="h-sub">Asterisk modules needed for AI Voice Agent</div></div><span class="pip green"><span class="dot"></span>6/6 loaded</span></div>
    <div class="table-wrap"><table class="data compact">
      <thead><tr><th>Moduł</th><th>Nazwa</th><th>Wersja</th><th>Status</th><th>Fix hint</th></tr></thead>
      <tbody>
        ${[
          {mod:'res_ari.so',desc:'Asterisk REST Interface',ver:'20.5.0',status:'loaded'},
          {mod:'res_ari_events.so',desc:'ARI Events (WebSocket)',ver:'20.5.0',status:'loaded'},
          {mod:'res_ari_channels.so',desc:'Channel management',ver:'20.5.0',status:'loaded'},
          {mod:'res_ari_recordings.so',desc:'Recording API',ver:'20.5.0',status:'loaded'},
          {mod:'res_http_websocket.so',desc:'HTTP WebSocket support',ver:'20.5.0',status:'loaded'},
          {mod:'app_stasis.so',desc:'Stasis dialplan application',ver:'20.5.0',status:'loaded'},
        ].map(m => `
          <tr><td class="num-mono" style="color:var(--zloto-700)">${m.mod}</td><td style="font-size:12.5px">${m.desc}</td><td class="num-mono">${m.ver}</td><td><span class="pip green"><span class="dot"></span>${m.status}</span></td><td style="color:var(--ink-500);font-size:11px">—</td></tr>
        `).join('')}
      </tbody>
    </table></div>
  </div>

  <!-- ARI User config -->
  <div class="card">
    <div class="card-head"><div><div class="t">ARI User Configuration</div><div class="h-sub">/etc/asterisk/ari_additional_custom.conf</div></div><button class="btn btn-ghost btn-sm">Kopiuj</button></div>
    <div style="padding:20px 24px">
      <div class="code" style="max-height:200px">
        <div class="code-line"><span class="code-num">1</span><span class="code-text"><span class="cm">; ARI user block · required by Adam</span></span></div>
        <div class="code-line"><span class="code-num">2</span><span class="code-text"><span class="cm">; /etc/asterisk/ari_additional_custom.conf</span></span></div>
        <div class="code-line"><span class="code-num">3</span><span class="code-text"></span></div>
        <div class="code-line"><span class="code-num">4</span><span class="code-text"><span class="kw">[AIAgent]</span></span></div>
        <div class="code-line"><span class="code-num">5</span><span class="code-text">type=user</span></div>
        <div class="code-line"><span class="code-num">6</span><span class="code-text">password=<span class="var">\${ARI_PASSWORD}</span></span></div>
        <div class="code-line"><span class="code-num">7</span><span class="code-text">read_only=no</span></div>
        <div class="code-line"><span class="code-num">8</span><span class="code-text">allowed_origins=http://adam.silvertech.pl,https://adam.silvertech.pl</span></div>
      </div>
    </div>
  </div>
</div>`;

/* ------------ MODELS ------------ */
SCREEN_RENDERERS.models = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Models · <em>catalog & installed</em></h1>
      <div class="sub">
        <span>18 modeli w katalogu · 8 zainstalowanych · 3 aktywne</span>
        <span class="sep">·</span><span>Disk: 12.4 GB / 1.16 TB</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Odśwież katalog</button>
      <button class="btn btn-accent">+ Custom model</button>
    </div>
  </div>

  <div class="subtabs">
    <div class="subtab active">STT <span class="count">3 installed</span></div>
    <div class="subtab">TTS <span class="count">2 installed</span></div>
    <div class="subtab">LLM <span class="count">3 installed</span></div>
    <div class="subtab">Custom <span class="count">2</span></div>
  </div>

  <!-- Active -->
  <div class="section-hd"><h2>Aktywne modele</h2><span class="link">Wybrane w default pipeline</span></div>
  <div class="grid-3" style="margin-bottom:32px">
    ${[
      {kind:'STT',name:'Whisper large-v3',prov:'Local (self-hosted)',size:'3.8 GB',latency:'324ms',status:'active',wer:'3.6%'},
      {kind:'TTS',name:'pl-Adam-M v2.5',prov:'ElevenLabs',size:'API',latency:'412ms',status:'active',wer:'—'},
      {kind:'LLM',name:'gpt-4o-realtime',prov:'OpenAI',size:'API',latency:'687ms',status:'active',wer:'—'},
    ].map(m => `
      <div class="card" style="border:1px solid var(--zloto-400);background:linear-gradient(180deg,var(--zloto-50),white)">
        <div style="padding:20px 22px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <span class="b gold">${m.kind} · Active</span>
            <span style="color:var(--zloto-500);font-size:14px">★</span>
          </div>
          <div style="font-family:var(--serif);font-size:20px;color:var(--granat-900);font-weight:500;letter-spacing:-0.01em">${m.name}</div>
          <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em;margin-top:4px">${m.prov}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px;padding-top:12px;border-top:1px solid var(--line)">
            <div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Size</div><div class="num-mono" style="margin-top:2px">${m.size}</div></div>
            <div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase">Latency p95</div><div class="num-mono" style="margin-top:2px">${m.latency}</div></div>
          </div>
        </div>
      </div>
    `).join('')}
  </div>

  <!-- STT catalog -->
  <div class="section-hd"><h2>STT · <em>Speech-to-Text</em></h2><span class="link">Whisper · Deepgram · Google Chirp</span></div>
  <div class="grid-4">
    ${[
      {name:'Whisper large-v3',prov:'OpenAI (open)',size:'3.8 GB',status:'installed',selected:true},
      {name:'Whisper large-v3 · senior-fine-tune',prov:'SilverTech custom',size:'3.9 GB',status:'installed',selected:false,custom:true},
      {name:'Whisper medium',prov:'OpenAI (open)',size:'1.5 GB',status:'installed',selected:false},
      {name:'Nova-2 (Deepgram)',prov:'Deepgram · API',size:'—',status:'available',selected:false},
      {name:'Chirp-2 pl-PL',prov:'Google · API',size:'—',status:'available',selected:false},
      {name:'Distil-Whisper large',prov:'HuggingFace (auto-DL)',size:'756 MB',status:'available',selected:false},
      {name:'Whisper large-v2',prov:'OpenAI (open)',size:'2.9 GB',status:'available',selected:false},
      {name:'Wav2Vec2 pl (allegro)',prov:'HuggingFace (auto-DL)',size:'1.2 GB',status:'available',selected:false},
    ].map(m => `
      <div class="model-card${m.selected?' style="border:1px solid var(--zloto-400)"':''}">
        <div style="display:flex;justify-content:space-between;align-items:start;gap:8px">
          <div style="flex:1">
            <div class="m-name">${m.name}${m.custom?' <span class="b gold" style="font-size:9px">custom</span>':''}</div>
            <div class="m-kind">STT</div>
          </div>
          ${m.selected ? '<span style="color:var(--zloto-500);font-size:14px">★</span>' : ''}
        </div>
        <div class="m-size">${m.prov} · ${m.size}</div>
        <div class="m-actions">
          ${m.status === 'installed'
            ? `<span class="pip green" style="flex:1;justify-content:center"><span class="dot"></span>Installed</span>${!m.selected?'<button class="btn btn-ghost btn-xs">Aktywuj</button>':''}<button class="btn btn-ghost btn-xs" title="Delete">🗑</button>`
            : `<button class="btn btn-ghost btn-sm" style="flex:1;justify-content:center">⬇ Download</button>`
          }
        </div>
      </div>
    `).join('')}
  </div>
</div>`;

/* ------------ LOGS ------------ */
SCREEN_RENDERERS.logs = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Live Logs · <em>streaming</em></h1>
      <div class="sub">
        <span class="live">Live · WebSocket</span>
        <span class="sep">·</span><span>Buforowanie: 10 000 wpisów · retention: 30 dni</span>
        <span class="sep">·</span><span>Dziś: 42 847 wpisów</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">📥 Pobierz ostatnie 1h</button>
      <button class="btn btn-ghost">🔍 Elasticsearch</button>
      <button class="btn btn-primary">Pauza</button>
    </div>
  </div>

  <!-- Mode toggle + filters -->
  <div class="subtabs" style="margin-bottom:16px">
    <div class="subtab active">Troubleshoot · structured</div>
    <div class="subtab">Raw · tail -f</div>
  </div>

  <div class="filter-bar">
    <div style="display:flex;gap:6px">
      <button class="chip-filter on">ERROR</button>
      <button class="chip-filter on">WARNING</button>
      <button class="chip-filter on">INFO</button>
      <button class="chip-filter">DEBUG</button>
    </div>
    <div style="width:1px;height:24px;background:var(--line-strong)"></div>
    <div style="display:flex;gap:6px">
      <button class="chip-filter on">call</button>
      <button class="chip-filter on">provider</button>
      <button class="chip-filter on">audio</button>
      <button class="chip-filter">transport</button>
      <button class="chip-filter">vad</button>
      <button class="chip-filter">tools</button>
      <button class="chip-filter">config</button>
    </div>
    <div style="flex:1"></div>
    <div class="field"><label>Search regex</label><input type="text" placeholder="Filter…" style="min-width:200px"/></div>
  </div>

  <!-- Log stream -->
  <div class="card" style="padding:0">
    <div style="max-height:600px;overflow-y:auto;background:var(--paper)">
      ${[
        {t:'14:22:07.234',lvl:'error',cat:'call',msg:'Failed to complete call C-847290 · No answer after 3 retries · target=+48606123456 (Maria N.)'},
        {t:'14:22:07.201',lvl:'warning',cat:'call',msg:'Retry attempt 3/3 for call C-847290 · gap=20s · reason=no_answer'},
        {t:'14:22:03.891',lvl:'info',cat:'call',msg:'ARI channel PJSIP/trunk-00001a2f created · call C-847291 (Stanisław Z. · Purple escalation)'},
        {t:'14:22:03.782',lvl:'warning',cat:'tools',msg:'raise_semafor("purple") invoked · trigger=verbal_cardiac+afib · senior_id=SZ-04127'},
        {t:'14:22:03.512',lvl:'info',cat:'provider',msg:'openai_realtime · session.created · session_id=sess_abc123 · agent=crisis-triage v3.1'},
        {t:'14:22:00.001',lvl:'info',cat:'vad',msg:'VAD threshold triggered · pitch_shift=+34Hz · speech_detected=true · confidence=0.94'},
        {t:'14:21:58.412',lvl:'info',cat:'audio',msg:'Audio profile applied: senior-optimized · EQ+3dB@2-4kHz · pace=0.85'},
        {t:'14:21:56.234',lvl:'warning',cat:'audio',msg:'Wearable HR spike detected: 158 bpm · senior=SZ-04127 · source=apple_watch_s9 · timestamp=2026-07-12T14:21:56Z'},
        {t:'14:21:52.008',lvl:'info',cat:'call',msg:'Outbound call initiated · target=+48604552312 (Stanisław Z.) · agent=welfare-evening'},
        {t:'14:21:44.891',lvl:'info',cat:'tools',msg:'get_wearable_data() returned: {hr: 158, spo2: 89, fall: false, afib: true}'},
        {t:'14:21:33.234',lvl:'debug',cat:'transport',msg:'RTP jitter buffer resized: 80ms → 120ms (adaptive · noise level 0.032)'},
        {t:'14:20:32.128',lvl:'info',cat:'call',msg:'Adam v7.4.2 · initiated welfare check call to +48601239876 (Maria N.)'},
        {t:'14:20:32.001',lvl:'info',cat:'provider',msg:'ElevenLabs TTS · voice pl-Adam-M · generation started · 143 chars'},
        {t:'14:19:47.234',lvl:'info',cat:'call',msg:'Call C-847289 completed · duration=3m 47s · mood=0.42 · semafor_raised=yellow'},
        {t:'14:19:20.891',lvl:'info',cat:'tools',msg:'raise_semafor("yellow") · reason=loneliness_verbal · pattern="wnuki dawno nie dzwoniły"'},
        {t:'14:18:43.234',lvl:'warning',cat:'audio',msg:'Xiaomi Band 8 · fall detected · senior=MN-02341 · accel=8.7G · followed by 3s silence'},
      ].map(l => `
        <div class="log-line">
          <span class="lt">${l.t}</span>
          <span class="ll ${l.lvl}">${l.lvl}</span>
          <span class="lc">${l.cat}</span>
          <span class="lm">${l.msg}</span>
        </div>
      `).join('')}
    </div>
  </div>

  <div style="margin-top:12px;padding:12px 20px;background:var(--paper);border:1px solid var(--line);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-family:var(--mono);font-size:11px;color:var(--ink-500);letter-spacing:0.06em">
    <span>Auto-scroll: <strong style="color:var(--sem-green)">ON</strong> · Buffer: <strong style="color:var(--granat-900)">2,847 / 10,000</strong></span>
    <span>Last event: <strong style="color:var(--granat-900)">2s ago</strong></span>
  </div>
</div>`;

/* ------------ TERMINAL ------------ */
SCREEN_RENDERERS.terminal = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Web Terminal · <em>admin CLI</em></h1>
      <div class="sub">
        <span>Podłączony jako: <strong style="color:var(--granat-900)">krzysztof.m@adam-prod</strong></span>
        <span class="sep">·</span><span>2FA active</span>
        <span class="sep">·</span><span>Sesja: 47min pozostało</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Historia sesji</button>
      <button class="btn btn-ghost">Runbook</button>
      <button class="btn btn-ghost" style="background:var(--sem-red);color:white;border-color:var(--sem-red)">Wyloguj</button>
    </div>
  </div>

  <div class="alert-strip warn">
    <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 2L1 18h18L10 2z"/></svg></div>
    <div class="info-t">
      <div class="title">Terminal ma pełen dostęp do systemu · wszystkie komendy są logowane</div>
      <div class="desc">Wpisz <code style="font-family:var(--mono);background:white;padding:1px 6px;border-radius:3px">help</code> aby zobaczyć dostępne komendy · <code style="font-family:var(--mono);background:white;padding:1px 6px;border-radius:3px">runbook</code> aby otworzyć procedury incident response</div>
    </div>
  </div>

  <div class="card" style="padding:0;overflow:hidden">
    <div class="editor-toolbar">
      <span style="color:var(--granat-900);font-weight:600">bash</span>
      <div class="sep"></div>
      <button>Clear</button><button>Copy all</button><button>📥 Export</button>
      <div style="margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink-500)">bash 5.2.15 · pty · UTF-8</div>
    </div>

    <div class="terminal-pane">
      <div class="term-line term-out" style="color:#6ee7b7">Welcome to Adam Ops Terminal · SilverTech Poznań</div>
      <div class="term-line term-out">Type "help" for available commands · "runbook" for incident procedures</div>
      <div class="term-line term-out" style="color:#5a6a8a">Session started: 2026-07-12 14:15:23 · 2FA verified · role=coordinator</div>
      <div class="term-line term-out" style="color:#5a6a8a">—</div>

      <div class="term-line"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input">docker compose -p asterisk-ai-voice-agent ps</span></div>
      <div class="term-line term-out">NAME              IMAGE                              STATUS         PORTS</div>
      <div class="term-line term-out" style="color:#6ee7b7">ai_engine         silvertech/adam-engine:7.4.2       Up 48 days     0.0.0.0:8000-8001-&gt;8000-8001/tcp</div>
      <div class="term-line term-out" style="color:#6ee7b7">admin_ui          silvertech/adam-ui:7.4.2           Up 48 days     0.0.0.0:3003-&gt;3003/tcp</div>
      <div class="term-line term-out" style="color:#6ee7b7">asterisk          asterisk:20-alpine                 Up 48 days     0.0.0.0:5060,8088-&gt;5060,8088</div>
      <div class="term-line term-out" style="color:#6ee7b7">local_ai_server   silvertech/whisper-server:1.2.0    Up 48 days     0.0.0.0:9000-9001-&gt;9000-9001/tcp</div>

      <div class="term-line" style="margin-top:12px"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input">adam agents list --env=prod</span></div>
      <div class="term-line term-out">NAME                       VERSION    ENV      CALLS_24H   RATING   LAST_DEPLOY</div>
      <div class="term-line term-out">adam-welfare-morning       v7.4.2     PROD     1,247       4.8      2 days ago</div>
      <div class="term-line term-out">adam-welfare-evening       v7.4.2     PROD     1,183       4.7      2 days ago</div>
      <div class="term-line term-out">adam-crisis-triage         v3.1.0     PROD     47          4.9      7 days ago</div>
      <div class="term-line term-out">adam-med-reminder          v2.4.1     PROD     2,847       4.6      14 days ago</div>
      <div class="term-line term-out">adam-concierge             v1.2.0     PROD     312         4.9      21 days ago</div>

      <div class="term-line" style="margin-top:12px"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input">adam alerts active</span></div>
      <div class="term-line term-out" style="color:#fca5a5">🟣 PURPLE · SZ-04127 (Stanisław Zieliński) · Ból w klatce + AFib · 112 dispatched · ETA 8min</div>
      <div class="term-line term-out" style="color:#fca5a5">🔴 RED    · MN-02341 (Maria Nowak)         · Fall detected · No answer 3/3 · 3 min ago</div>
      <div class="term-line term-out" style="color:#fbbf24">🟡 YELLOW · JK-08823 (Janusz Kowalski)     · Verbal loneliness signal · Family notified</div>

      <div class="term-line" style="margin-top:12px"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input">adam senior show SZ-04127 --live</span></div>
      <div class="term-line term-out">Senior:      Stanisław Zieliński (85, Stare Miasto)</div>
      <div class="term-line term-out">Package:     Premium</div>
      <div class="term-line term-out" style="color:#fca5a5">Semafor:     🟣 PURPLE · escalation started 42s ago</div>
      <div class="term-line term-out">HR / SpO₂:   158 bpm / 89% · Apple Watch S9</div>
      <div class="term-line term-out">EKG event:   AFib detected 22:12</div>
      <div class="term-line term-out">Call:        In progress · agent=crisis-triage v3.1 · 00:42 elapsed</div>
      <div class="term-line term-out">Emergency:   112 dispatched · unit #47-12 · ETA 8 min</div>
      <div class="term-line term-out">Family:      Notified via SMS (córka Magdalena C.) · replied "jadę"</div>

      <div class="term-line" style="margin-top:12px"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input">tail -f /var/log/adam/crisis.log | grep SZ-04127</span></div>
      <div class="term-line term-out">[22:15:34] [SZ-04127] Ambulance en route · #47-12 · ETA 8min</div>
      <div class="term-line term-out">[22:14:52] [SZ-04127] 112 auto-dial · dispatcher answered in 5s</div>
      <div class="term-line term-out">[22:14:20] [SZ-04127] Family notified · SMS delivered · magdalena.c@gmail.com</div>
      <div class="term-line term-out">[22:13:47] [SZ-04127] Coordinator online · krzysztof.m · picked up</div>
      <div class="term-line term-out">[22:13:12] [SZ-04127] Semafor RAISED: red → purple · trigger=verbal_cardiac+afib</div>
      <div class="term-line term-out" style="color:#5a6a8a">Following log (Ctrl+C to stop) ...</div>

      <div class="term-line" style="margin-top:12px"><span class="term-prompt">krzysztof.m@adam-prod:~$</span><span class="term-input"><span class="cursor"></span></span></div>
    </div>
  </div>

  <!-- Quick commands -->
  <div class="section-hd" style="margin-top:24px"><h2>Szybkie komendy</h2><span class="link">Kliknij aby wkleić</span></div>
  <div class="grid-3">
    ${[
      ['adam agents list','Wszystkie agenty i ich status'],
      ['adam alerts active','Aktywne alerty na wszystkich seniorach'],
      ['adam senior show &lt;id&gt;','Pełny status seniora'],
      ['adam pipeline test welfare-check-primary','Test call primary pipeline'],
      ['docker compose logs -f ai_engine','Live logs kontenera ai_engine'],
      ['adam scheduler reload','Ponowne załadowanie cron rules'],
    ].map(([cmd,desc]) => `
      <div class="card" style="padding:14px 18px;cursor:pointer">
        <code style="font-family:var(--mono);font-size:11px;color:var(--zloto-700)">${cmd}</code>
        <div style="font-size:12px;color:var(--ink-700);margin-top:6px">${desc}</div>
      </div>
    `).join('')}
  </div>
</div>`;
