/* ============================================
   MARKETPLACE + WEARABLES FLEET SCREENS
   Panel Admina · nowe funkcje z briefu Marketplace/Wearables
   ============================================ */

/* ============================================
   MARKETPLACE (Panel Admina · Overview)
   4 taby: Zamówienia · Katalog · Partnerzy · Service Gaps
   ============================================ */

const MARKETPLACE_CATEGORIES = [
  {id:'meds-delivery', ic:'💊', name:'Dostawa leków', risk:'niskie', flow:'auto', partners:8, orders24:34, avgPrice:'~15 zł'},
  {id:'groceries', ic:'🛒', name:'Zakupy spożywcze', risk:'niskie', flow:'auto', partners:6, orders24:47, avgPrice:'80–150 zł'},
  {id:'taxi-med', ic:'🚕', name:'Taxi / transport medyczny', risk:'niskie', flow:'auto', partners:12, orders24:23, avgPrice:'25–60 zł'},
  {id:'doctor-home', ic:'👨‍⚕️', name:'Wizyta lekarza domowa', risk:'wysokie', flow:'manual', partners:14, orders24:6, avgPrice:'250–400 zł'},
  {id:'nurse', ic:'🧑‍⚕️', name:'Pielęgniarka domowa', risk:'wysokie', flow:'manual', partners:9, orders24:11, avgPrice:'80–180 zł'},
  {id:'cleaning', ic:'🧹', name:'Sprzątanie mieszkania', risk:'średnie', flow:'hybrid', partners:16, orders24:18, avgPrice:'100–200 zł'},
  {id:'physio', ic:'💪', name:'Rehabilitant / fizjoterapeuta', risk:'wysokie', flow:'manual', partners:7, orders24:4, avgPrice:'120–200 zł'},
  {id:'repairs', ic:'🔧', name:'Drobne naprawy domowe', risk:'wysokie', flow:'manual', partners:5, orders24:2, avgPrice:'150–500 zł'},
  {id:'appointment', ic:'🗓️', name:'Umówienie u specjalisty', risk:'niskie', flow:'manual', partners:'—', orders24:8, avgPrice:'0 zł'},
  {id:'psychology', ic:'💬', name:'Wsparcie psychologiczne', risk:'wysokie', flow:'manual', partners:3, orders24:2, avgPrice:'150–250 zł'},
];

const ORDERS_DATA = [
  {id:'O-8472',cat:'meds-delivery',senior:'HW',seniorName:'Halina Wójcik',partner:'DOZ Wilda · Apteka św. Marcin',price:'34 zł',eta:'45 min',status:'waiting_manual',channel:'adam-call',ts:'3 min temu',cancelWindow:27,riskLevel:'niskie',flowType:'auto',requestSummary:'"Adam, kończy mi się metformina, poproszę zamówić"'},
  {id:'O-8471',cat:'doctor-home',senior:'JK',seniorName:'Janusz Kowalski',partner:'Dr Katarzyna Chmielewska (POZ)',price:'320 zł',eta:'Jutro 14:00',status:'waiting_manual',channel:'adam-call',ts:'12 min temu',cancelWindow:18,riskLevel:'wysokie',flowType:'manual',requestSummary:'"Boli mnie od 3 dni, chciałbym żeby lekarz przyszedł"'},
  {id:'O-8470',cat:'nurse',senior:'RT',seniorName:'Ryszard Tomczak',partner:'Pielęgniarka Marta L. (SilverTech verified)',price:'120 zł',eta:'Czw. 09:00',status:'waiting_manual',channel:'opiekun-panel',ts:'32 min temu',cancelWindow:'—',riskLevel:'wysokie',flowType:'manual',requestSummary:'Zamówione przez opiekuna: "Piotr K. - iniekcja insuliny"'},
  {id:'O-8469',cat:'cleaning',senior:'EM',seniorName:'Ewa Michalska',partner:'CleanPoznań (nowy partner!)',price:'150 zł',eta:'Pt. 10:00',status:'waiting_manual',channel:'adam-call',ts:'44 min temu',cancelWindow:'—',riskLevel:'średnie',flowType:'hybrid',requestSummary:'"Adam, potrzebuję sprzątania w piątek rano"'},
  {id:'O-8468',cat:'taxi-med',senior:'WS',seniorName:'Wanda Sikora',partner:'MPT Poznań',price:'42 zł',eta:'Za 20 min',status:'auto_confirmed',channel:'adam-call',ts:'8 min temu',cancelWindow:'—',riskLevel:'niskie',flowType:'auto',requestSummary:'"Muszę pojechać na wizytę o 15:00"'},
  {id:'O-8467',cat:'groceries',senior:'KB',seniorName:'Krystyna Baran',partner:'Frisco.pl',price:'127 zł',eta:'Dziś 18–20',status:'auto_confirmed',channel:'opiekun-panel',ts:'1h temu',cancelWindow:'—',riskLevel:'niskie',flowType:'auto',requestSummary:'Zamówione przez opiekuna z listą 14 pozycji'},
  {id:'O-8466',cat:'meds-delivery',senior:'AS',seniorName:'Andrzej Szymański',partner:'DOZ Grunwald',price:'22 zł',eta:'2h',status:'auto_confirmed',channel:'adam-call',ts:'1h temu',cancelWindow:'—',riskLevel:'niskie',flowType:'auto'},
  {id:'O-8465',cat:'physio',senior:'ZK',seniorName:'Zbigniew Krawczyk',partner:'FizjoDom Poznań',price:'150 zł',eta:'Śr. 11:00',status:'confirmed',channel:'adam-call',ts:'2h temu',cancelWindow:'—',riskLevel:'wysokie',flowType:'manual'},
  {id:'O-8464',cat:'taxi-med',senior:'HW',seniorName:'Halina Wójcik',partner:'MPT Poznań',price:'38 zł',eta:'W realizacji',status:'in_progress',channel:'adam-call',ts:'2h temu',cancelWindow:'—',riskLevel:'niskie',flowType:'auto'},
  {id:'O-8463',cat:'cleaning',senior:'KB',seniorName:'Krystyna Baran',partner:'CleanPoznań',price:'150 zł',eta:'Zrealizowano',status:'completed',channel:'opiekun-panel',ts:'6h temu',cancelWindow:'—',riskLevel:'średnie',flowType:'hybrid',rating:5},
];

const PARTNERS_DATA = [
  {name:'DOZ · Apteka św. Marcin',cat:['meds-delivery'],nip:'7831234567',oc:true,verified:true,district:['Stare Miasto','Wilda'],rating:4.8,reactionMin:12,orders30:487,complaints30:0,localPriority:true},
  {name:'DOZ Grunwald',cat:['meds-delivery'],nip:'7831234567',oc:true,verified:true,district:['Grunwald'],rating:4.9,reactionMin:8,orders30:342,complaints30:0,localPriority:true},
  {name:'MPT Poznań (Miejskie Przedsiębiorstwo Taksówkowe)',cat:['taxi-med'],nip:'7830001122',oc:true,verified:true,district:['Wszystkie'],rating:4.7,reactionMin:14,orders30:687,complaints30:2,localPriority:true},
  {name:'Frisco.pl',cat:['groceries'],nip:'5252334455',oc:true,verified:true,district:['Wszystkie'],rating:4.6,reactionMin:120,orders30:412,complaints30:8,localPriority:false},
  {name:'Dr Katarzyna Chmielewska (POZ · Wilda)',cat:['doctor-home','appointment'],nip:'7770998877',oc:true,verified:true,district:['Wilda','Jeżyce'],rating:5.0,reactionMin:45,orders30:34,complaints30:0,localPriority:true},
  {name:'Pielęgniarka Marta L. (indywidualna)',cat:['nurse'],nip:'7770887766',oc:true,verified:true,district:['Grunwald','Winogrady'],rating:4.9,reactionMin:60,orders30:87,complaints30:0,localPriority:true},
  {name:'CleanPoznań',cat:['cleaning'],nip:'7830667788',oc:true,verified:true,district:['Wszystkie'],rating:4.5,reactionMin:180,orders30:124,complaints30:3,localPriority:true,newPartner:true},
  {name:'FizjoDom Poznań',cat:['physio'],nip:'7830998812',oc:true,verified:true,district:['Wilda','Grunwald','Stare Miasto'],rating:4.8,reactionMin:240,orders30:56,complaints30:1,localPriority:true},
  {name:'Elektryk Marek W.',cat:['repairs'],nip:'7770112233',oc:true,verified:true,district:['Jeżyce','Wilda'],rating:4.9,reactionMin:120,orders30:18,complaints30:0,localPriority:true},
  {name:'Psycholog Maria N.',cat:['psychology'],nip:'7770556677',oc:true,verified:true,district:['Wszystkie · zdalne+dojazd'],rating:5.0,reactionMin:480,orders30:12,complaints30:0,localPriority:true},
];

SCREEN_RENDERERS.marketplace = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Marketplace · <em>Concierge SilverTech</em></h1>
      <div class="sub">
        <span class="live">Live</span>
        <span class="sep">·</span><span>7 zamówień do potwierdzenia · 3 auto-confirmed dzisiaj</span>
        <span class="sep">·</span><span>10 kategorii MVP · 80 zweryfikowanych partnerów</span>
        <span class="sep">·</span><span>Service gaps: 4 dzielnice bez pokrycia</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Eksport CSV</button>
      <button class="btn btn-ghost">📞 Kontakt partnera</button>
      <button class="btn btn-accent">+ Ręczne zamówienie</button>
    </div>
  </div>

  <!-- KPI marketplace -->
  <div class="kpi-strip">
    <div class="kpi"><div class="lbl">Zamówienia 24h</div><div class="val">83</div><div class="foot pos">↗ +12 vs śr. 7d</div></div>
    <div class="kpi"><div class="lbl">Do potwierdzenia</div><div class="val" style="color:var(--sem-yellow)">7</div><div class="foot">avg wait: 8 min</div></div>
    <div class="kpi"><div class="lbl">Auto-confirmed 24h</div><div class="val">46</div><div class="foot pos">55% wszystkich</div></div>
    <div class="kpi"><div class="lbl">GMV 24h</div><div class="val">4,247<sub>zł</sub></div><div class="foot pos">↗ +18%</div></div>
    <div class="kpi"><div class="lbl">Śr. rating partnerów</div><div class="val">4.7<sub>★</sub></div><div class="foot">12 skarg / 30d</div></div>
    <div class="kpi"><div class="lbl">Service gaps</div><div class="val" style="color:var(--sem-yellow)">4</div><div class="foot">niepokryte dzielnice</div></div>
  </div>

  <!-- Tabs -->
  <div class="subtabs">
    <div class="subtab active" data-tab="orders">Zamówienia <span class="count">10</span></div>
    <div class="subtab" data-tab="catalog">Katalog usług <span class="count">10</span></div>
    <div class="subtab" data-tab="partners">Partnerzy <span class="count">80</span></div>
    <div class="subtab" data-tab="gaps">Service Gaps <span class="count">4</span></div>
  </div>

  <!-- ============ ORDERS TAB ============ -->
  <div class="subtab-panel active" id="tp-orders">
    <!-- Split: Manual (akcyjne) + Auto (informacyjne) -->
    <div class="split-2-1">
      <!-- LEFT — Manual confirmation queue -->
      <div>
        <div class="card">
          <div class="card-head" style="background:var(--sem-yellow-bg);border-bottom-color:var(--sem-yellow)">
            <div>
              <div class="t" style="color:var(--sem-yellow)">🔔 Wymaga potwierdzenia koordynatora · <em>4 pilne</em></div>
              <div class="h-sub" style="color:var(--sem-yellow)">Wysokie ryzyko · zadzwoń do partnera i klienta · potwierdź w UI</div>
            </div>
            <div class="r"><span style="font-family:var(--mono);font-size:11px;color:var(--sem-yellow);letter-spacing:0.08em">AVG WAIT: 8 min</span></div>
          </div>
          <div class="table-wrap"><table class="data compact">
            <thead><tr><th></th><th>Order</th><th>Senior</th><th>Usługa · Partner</th><th>Kanał</th><th>Cena</th><th>ETA</th><th>Akcje</th></tr></thead>
            <tbody>
              ${ORDERS_DATA.filter(o => o.status === 'waiting_manual').map(o => {
                const cat = MARKETPLACE_CATEGORIES.find(c => c.id === o.cat);
                return `
                <tr>
                  <td style="width:36px"><span style="font-size:22px">${cat.ic}</span></td>
                  <td><div class="num-mono" style="color:var(--zloto-700)">${o.id}</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.06em;margin-top:2px">${o.ts}</div></td>
                  <td><div class="a-pill"><div class="a-av">${o.senior}</div><span class="a-name">${o.seniorName}</span></div></td>
                  <td>
                    <div style="font-family:var(--sans);font-size:13px;color:var(--granat-900);font-weight:500">${cat.name}</div>
                    <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px">${o.partner}${o.partner.includes('nowy')?' <span class="b yellow" style="font-size:9px;padding:1px 5px">1. zamówienie</span>':''}</div>
                    <div style="font-family:var(--serif);font-style:italic;font-size:11.5px;color:var(--ink-700);margin-top:5px;line-height:1.4;font-weight:300">${o.requestSummary}</div>
                  </td>
                  <td>
                    <span class="b ${o.channel==='adam-call'?'gold':'info'}" style="font-size:10px">${o.channel==='adam-call'?'📞 Adam-call':'💻 Opiekun'}</span>
                  </td>
                  <td class="num-serif">${o.price}</td>
                  <td class="num-mono">${o.eta}</td>
                  <td style="min-width:180px">
                    <div style="display:flex;gap:4px;flex-wrap:wrap">
                      <button class="btn btn-primary btn-xs" style="background:var(--sem-green)">✓ Potwierdź</button>
                      <button class="btn btn-ghost btn-xs">📞 Partner</button>
                      <button class="btn btn-ghost btn-xs" style="color:var(--sem-red)">✕ Odrzuć</button>
                    </div>
                  </td>
                </tr>
              `;}).join('')}
            </tbody>
          </table></div>
        </div>

        <!-- Auto-confirmed section -->
        <div class="card" style="margin-top:16px">
          <div class="card-head">
            <div>
              <div class="t">Auto-confirmed · <em>przegląd audytorski</em></div>
              <div class="h-sub">Adam potwierdził bezpośrednio z partnerem · zerowe ryzyko · tylko monitoring</div>
            </div>
            <div class="r"><span class="pip green"><span class="dot"></span>Wszystkie OK</span></div>
          </div>
          <div class="table-wrap"><table class="data compact">
            <thead><tr><th></th><th>Order</th><th>Senior</th><th>Usługa · Partner</th><th>Cena</th><th>ETA</th><th>Status</th></tr></thead>
            <tbody>
              ${ORDERS_DATA.filter(o => ['auto_confirmed','confirmed','in_progress','completed'].includes(o.status)).map(o => {
                const cat = MARKETPLACE_CATEGORIES.find(c => c.id === o.cat);
                const statusMap = {auto_confirmed:{c:'green',l:'Auto-confirmed'},confirmed:{c:'green',l:'Confirmed'},in_progress:{c:'info',l:'W realizacji'},completed:{c:'green',l:'Zrealizowano'}};
                const s = statusMap[o.status];
                return `
                <tr>
                  <td style="width:36px"><span style="font-size:18px">${cat.ic}</span></td>
                  <td class="num-mono" style="color:var(--zloto-700)">${o.id}</td>
                  <td><div class="a-pill"><div class="a-av">${o.senior}</div><span class="a-name">${o.seniorName}</span></div></td>
                  <td>
                    <div style="font-family:var(--sans);font-size:12.5px;color:var(--granat-900);font-weight:500">${cat.name}</div>
                    <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:2px">${o.partner}</div>
                  </td>
                  <td class="num-serif">${o.price}</td>
                  <td class="num-mono">${o.eta}</td>
                  <td><span class="pip ${s.c}"><span class="dot"></span>${s.l}</span>${o.rating?` <span style="color:var(--zloto-500);font-size:12px;margin-left:6px">${'★'.repeat(o.rating)}</span>`:''}</td>
                </tr>
              `;}).join('')}
            </tbody>
          </table></div>
        </div>
      </div>

      <!-- RIGHT: Context sidebar -->
      <div>
        <!-- Selected order context -->
        <div class="card">
          <div class="card-head"><div><div class="t">Wybrane zamówienie</div><div class="h-sub">O-8472 · Halina Wójcik · Leki</div></div></div>
          <div style="padding:20px 24px">
            <!-- Senior context -->
            <div style="padding:14px;background:var(--paper-2);border-radius:10px;border-left:3px solid var(--sem-green);margin-bottom:16px">
              <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px">Kontekst seniora</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px">
                <div><span style="color:var(--ink-500)">Semafor:</span> <span class="pip green" style="margin-left:4px"><span class="dot"></span>Green</span></div>
                <div><span style="color:var(--ink-500)">Mood 7d:</span> <span class="num-serif" style="font-size:14px">0.72</span></div>
                <div><span style="color:var(--ink-500)">Adherence:</span> <span class="num-mono">96%</span></div>
                <div><span style="color:var(--ink-500)">Ostatnia rozmowa:</span> <span class="num-mono">08:14</span></div>
              </div>
              <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:11.5px;color:var(--ink-700);line-height:1.5;font-family:var(--serif);font-style:italic;font-weight:300">Metformina kończy się prawdziwie · ostatnia dawka wieczorem 11 lipca · adherence 96% wskazuje że senior naprawdę bierze lek.</div>
            </div>

            <!-- Partner card -->
            <div style="padding:14px;background:white;border:1px solid var(--line);border-radius:10px;margin-bottom:16px">
              <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;margin-bottom:10px">
                <div>
                  <div style="font-family:var(--serif);font-size:15px;color:var(--granat-900);font-weight:500">DOZ · Apteka św. Marcin</div>
                  <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em;margin-top:3px">Wilda, Poznań · <strong style="color:var(--zloto-700)">Local Partner ★</strong></div>
                </div>
                <span class="pip green"><span class="dot"></span>Verified</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;padding-top:10px;border-top:1px solid var(--line)">
                <div><span style="color:var(--ink-500)">NIP:</span> <span class="num-mono">783-123-45-67</span></div>
                <div><span style="color:var(--ink-500)">OC:</span> <span class="pip green" style="font-size:9px"><span class="dot"></span>Ważne</span></div>
                <div><span style="color:var(--ink-500)">Rating:</span> <span class="num-serif" style="font-size:13px">4.8 ★</span></div>
                <div><span style="color:var(--ink-500)">Reakcja:</span> <span class="num-mono">~12 min</span></div>
                <div><span style="color:var(--ink-500)">Zamówień 30d:</span> <span class="num-mono">487</span></div>
                <div><span style="color:var(--ink-500)">Skargi 30d:</span> <span class="num-mono" style="color:var(--sem-green)">0</span></div>
              </div>
            </div>

            <!-- Transcript -->
            <div style="padding:14px;background:var(--granat-900);border-radius:10px;color:white">
              <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-400);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px">Transkrypt fragmentu</div>
              <div style="font-family:var(--serif);font-style:italic;font-size:12.5px;line-height:1.6;color:var(--paper);font-weight:300">
                <div style="margin-bottom:6px"><span style="color:var(--zloto-400);font-style:normal">Adam:</span> „Halino, jak z lekami — starczą jeszcze?"</div>
                <div style="margin-bottom:6px"><span style="color:var(--zloto-400);font-style:normal">HW:</span> „Kończy mi się metformina, poproszę zamówić..."</div>
                <div><span style="color:var(--zloto-400);font-style:normal">Adam:</span> „Zapisałam, koordynatorka potwierdzi w ciągu godziny."</div>
              </div>
              <div style="margin-top:10px;padding-top:8px;border-top:1px solid var(--granat-700);font-family:var(--mono);font-size:10px;color:var(--granat-300);letter-spacing:0.04em">Call C-847288 · 08:14 · 3m 22s · <button class="btn btn-ghost btn-xs" style="background:transparent;color:var(--zloto-400);border-color:var(--granat-700);margin-left:8px">▶ Odsłuchaj</button></div>
            </div>

            <div style="margin-top:16px;display:flex;gap:6px">
              <button class="btn btn-primary" style="flex:1;justify-content:center;background:var(--sem-green)">✓ Potwierdź zamówienie</button>
              <button class="btn btn-ghost">📞</button>
              <button class="btn btn-ghost" style="color:var(--sem-red)">✕</button>
            </div>
          </div>
        </div>

        <!-- Family notification status -->
        <div class="card" style="margin-top:16px">
          <div class="card-head"><div><div class="t">Rodzina · powiadomienia</div><div class="h-sub">30-min okno anulowania</div></div></div>
          <div style="padding:16px 20px">
            <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)">
              <div class="a-av" style="width:28px;height:28px;font-size:11px">AC</div>
              <div style="flex:1"><div style="font-size:12px;color:var(--granat-900);font-weight:500">Anna Chmielewska (córka)</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.02em">Push wysłany · 3 min temu</div></div>
              <span class="pip green"><span class="dot"></span>Seen</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;padding:10px 0">
              <div class="a-av" style="width:28px;height:28px;font-size:11px">PW</div>
              <div style="flex:1"><div style="font-size:12px;color:var(--granat-900);font-weight:500">Piotr Wójcik (syn)</div><div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.02em">SMS wysłany · 3 min temu</div></div>
              <span class="pip yellow"><span class="dot"></span>Not seen</span>
            </div>
            <div style="margin-top:10px;padding:10px;background:var(--sem-green-bg);border-radius:6px;font-size:11px;color:var(--sem-green);text-align:center;font-family:var(--mono);letter-spacing:0.04em">
              🕐 Okno anulowania: <strong>27 minut</strong> pozostało
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ============ CATALOG TAB ============ -->
  <div class="subtab-panel" id="tp-catalog">
    <div class="section-hd"><h2>10 kategorii MVP · <em>pogrupowane wg ryzyka</em></h2><span class="link">Auto-flow (niskie ryzyko) vs Manual (wysokie ryzyko) vs Hybrid</span></div>

    <div class="alert-strip info">
      <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10" cy="10" r="8"/><path d="M10 6v4M10 14v.5"/></svg></div>
      <div class="info-t">
        <div class="title">Świadome wykluczenia z MVP</div>
        <div class="desc"><strong>Opłata rachunków, przelewy finansowe, wnuczek-jak-drugą-osobę</strong> — wektor oszustw. <strong>Fryzjer, catering, stomatolog, optyk, pranie, pedicure, wyjście z psem, kultura</strong> — Faza 2/3 po walidacji MVP.</div>
      </div>
    </div>

    <div class="grid-3">
      ${MARKETPLACE_CATEGORIES.map(c => `
        <div class="card" style="padding:20px 22px;border-left:3px solid var(--sem-${c.risk==='wysokie'?'red':c.risk==='niskie'?'green':'yellow'})">
          <div style="display:flex;align-items:start;justify-content:space-between;gap:8px;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:12px">
              <div style="font-size:28px">${c.ic}</div>
              <div>
                <div style="font-family:var(--serif);font-size:17px;color:var(--granat-900);font-weight:500;letter-spacing:-0.01em">${c.name}</div>
                <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;letter-spacing:0.06em;text-transform:uppercase">${c.partners} partnerów · avg ${c.avgPrice}</div>
              </div>
            </div>
            <span class="b ${c.flow==='auto'?'green':c.flow==='manual'?'red':'yellow'}" style="font-size:10px;flex-shrink:0">${c.flow==='auto'?'AUTO':c.flow==='manual'?'MANUAL':'HYBRID'}</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;padding-top:12px;border-top:1px solid var(--line);font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em">
            <div><strong style="font-family:var(--serif);color:var(--granat-900);font-size:14px;display:block;font-weight:500">${c.orders24}</strong>zamówień 24h</div>
            <div><strong style="font-family:var(--serif);color:var(--granat-900);font-size:14px;display:block;font-weight:500">${c.risk}</strong>poziom ryzyka</div>
          </div>
          <button class="btn btn-ghost btn-sm" style="width:100%;justify-content:center;margin-top:12px">Edytuj kategorię →</button>
        </div>
      `).join('')}
    </div>

    <!-- Guardrails for category detail -->
    <div class="section-hd" style="margin-top:32px"><h2>Guardrails · <em>Wsparcie psychologiczne</em></h2><span class="link">Detail wybranej kategorii wysokiego ryzyka</span></div>
    <div class="grid-2">
      <div class="card">
        <div class="card-head"><div><div class="t">Wzorce rozpoznawania</div><div class="h-sub">Adam prompt patterns</div></div></div>
        <div style="padding:16px 24px">
          <div style="display:grid;gap:8px">
            ${['„chciałbym porozmawiać z kimś"','„czuję się samotny/smutny"','„nie mam z kim pogadać"','„nie widzę już sensu"','„już mi się nie chce"'].map(p => `
              <div style="padding:8px 12px;background:var(--paper-2);border-radius:6px;font-family:var(--serif);font-style:italic;font-size:12.5px;color:var(--ink-700);font-weight:300;line-height:1.4">${p}</div>
            `).join('')}
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><div><div class="t">Wykluczenia / red flags</div><div class="h-sub">Nigdy nie realizuj przez marketplace</div></div></div>
        <div style="padding:16px 24px">
          <div style="display:grid;gap:8px">
            ${[
              {t:'Sygnały suicydalne',d:'→ Semafor Red · triage-crisis agent',red:true},
              {t:'Prośba o receptę na psychotropy',d:'→ „to zawsze lekarz, umówię wizytę"',red:true},
              {t:'Diagnoza depresji',d:'→ „psycholog nie diagnozuje, pomaga"',red:false},
              {t:'Nagłe wsparcie w kryzysie',d:'→ nie czekaj na wizytę, telefon zaufania',red:true},
            ].map(x => `
              <div style="padding:10px 12px;background:${x.red?'var(--sem-red-bg)':'var(--paper-2)'};border-radius:6px;border-left:3px solid var(--sem-${x.red?'red':'yellow'})">
                <div style="font-size:12px;color:var(--granat-900);font-weight:500">${x.t}</div>
                <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;letter-spacing:0.02em">${x.d}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ============ PARTNERS TAB ============ -->
  <div class="subtab-panel" id="tp-partners">
    <div class="filter-bar">
      <div class="field"><label>Kategoria</label>
        <select><option>Wszystkie 10</option>${MARKETPLACE_CATEGORIES.map(c => `<option>${c.ic} ${c.name}</option>`).join('')}</select>
      </div>
      <div class="field"><label>Dzielnica</label>
        <select><option>Poznań · wszystkie</option><option>Wilda</option><option>Jeżyce</option><option>Grunwald</option><option>Stare Miasto</option><option>Winogrady</option><option>Nowe Miasto</option></select>
      </div>
      <div class="field"><label>Status</label>
        <select><option>Wszystkie</option><option>✓ Verified (78)</option><option>Pending (2)</option><option>Suspended (0)</option></select>
      </div>
      <div class="field"><label>Rating min.</label>
        <select><option>Wszystkie</option><option>≥4.5 ★</option><option>≥4.0 ★</option></select>
      </div>
      <div style="flex:1"></div>
      <button class="chip-filter on">Local Poznań <span class="x">×</span></button>
      <button class="chip-filter">Ogólnopolskie</button>
      <button class="chip-filter">Nowi partnerzy (30d)</button>
    </div>

    <div class="grid-2" style="margin-bottom:16px">
      <div class="kpi"><div class="lbl">Zweryfikowanych</div><div class="val">78<sub>/80</sub></div><div class="foot">2 pending weryfikacji</div></div>
      <div class="kpi"><div class="lbl">Local Poznań priority</div><div class="val">64<sub>/80</sub></div><div class="foot pos">80% lokalne</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div><div class="t">Wszyscy partnerzy · <em>80 zweryfikowanych</em></div></div>
        <button class="btn btn-accent btn-sm">+ Dodaj partnera</button>
      </div>
      <div class="table-wrap"><table class="data">
        <thead><tr><th>Partner</th><th>NIP</th><th>OC</th><th>Kategorie</th><th>Dzielnice</th><th>Rating</th><th>Śr. reakcja</th><th>Zamówień 30d</th><th>Skargi</th><th>Status</th></tr></thead>
        <tbody>
          ${PARTNERS_DATA.map(p => `
            <tr>
              <td>
                <div style="font-family:var(--serif);font-size:14px;color:var(--granat-900);font-weight:500">${p.name}${p.localPriority?' <span style="color:var(--zloto-500);font-size:12px;margin-left:4px" title="Local Poznań priority">★</span>':''}${p.newPartner?' <span class="b yellow" style="font-size:9px;padding:1px 5px;margin-left:4px">nowy</span>':''}</div>
              </td>
              <td class="num-mono muted" style="font-size:10px">${p.nip}</td>
              <td>${p.oc?'<span class="pip green"><span class="dot"></span>Ważne</span>':'<span class="pip red"><span class="dot"></span>Brak</span>'}</td>
              <td style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.02em">${p.cat.map(c => MARKETPLACE_CATEGORIES.find(x => x.id===c)?.ic).join(' ')}</td>
              <td style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.02em">${Array.isArray(p.district)?p.district.slice(0,2).join(', '):p.district}${Array.isArray(p.district)&&p.district.length>2?'…':''}</td>
              <td><span class="num-serif">${p.rating.toFixed(1)}</span> <span style="color:var(--zloto-500)">★</span></td>
              <td class="num-mono">${p.reactionMin<60?p.reactionMin+'min':Math.floor(p.reactionMin/60)+'h'}</td>
              <td class="num-mono">${p.orders30}</td>
              <td class="num-mono ${p.complaints30===0?'green':p.complaints30<5?'yellow':'red'}">${p.complaints30}</td>
              <td><span class="pip ${p.verified?'green':'yellow'}"><span class="dot"></span>${p.verified?'Verified':'Pending'}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table></div>
    </div>
  </div>

  <!-- ============ SERVICE GAPS TAB ============ -->
  <div class="subtab-panel" id="tp-gaps">
    <div class="alert-strip info">
      <div class="icon-wrap"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10" cy="10" r="8"/><path d="M10 6v4M10 14v.5"/></svg></div>
      <div class="info-t">
        <div class="title">Service Gaps = plan ekspansji</div>
        <div class="desc">Kiedy Adam nie znajduje partnera w kategorii/dzielnicy, tworzy <code style="font-family:var(--mono);font-size:11px;background:white;padding:1px 6px;border-radius:3px">service_gap</code>. Grupowanie pokazuje, gdzie brakuje pokrycia — priorytetyzacja rekrutacji partnerów.</div>
      </div>
    </div>

    <div class="section-hd"><h2>Prośby bez partnera · <em>ostatnie 30 dni</em></h2><span class="link">Sortowanie: częstotliwość</span></div>

    <div class="grid-2">
      ${[
        {cat:'💪 Rehabilitant',district:'Winogrady',count:52,seniors:34,avgRequestPrice:'~150 zł',recommendation:'Rekrutacja 2 partnerów w Winogradach (obecnie 0)'},
        {cat:'🔧 Elektryk',district:'Stare Miasto',count:23,seniors:19,avgRequestPrice:'~200 zł',recommendation:'1 nowy partner w Starym Mieście'},
        {cat:'💬 Psycholog',district:'Grunwald',count:18,seniors:12,avgRequestPrice:'~200 zł',recommendation:'Psycholog w Grunwaldzie (obecnie zdalne+dojazd z Wildy)'},
        {cat:'👨‍⚕️ Lekarz nocny',district:'Wszystkie',count:14,seniors:14,avgRequestPrice:'~500 zł',recommendation:'Nowa kategoria: dyżury nocne (22:00–06:00)'},
      ].map(g => `
        <div class="card" style="padding:24px;border-left:3px solid var(--sem-yellow)">
          <div style="display:flex;justify-content:space-between;align-items:start;gap:12px;margin-bottom:14px">
            <div>
              <div style="font-family:var(--serif);font-size:22px;color:var(--granat-900);font-weight:500;letter-spacing:-0.015em">${g.cat}</div>
              <div style="font-family:var(--mono);font-size:11px;color:var(--zloto-700);letter-spacing:0.08em;text-transform:uppercase;margin-top:4px">${g.district}</div>
            </div>
            <div style="text-align:right">
              <div style="font-family:var(--serif);font-size:32px;color:var(--sem-yellow);font-weight:500;line-height:1">${g.count}</div>
              <div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;margin-top:2px">próśb 30d</div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px 14px;background:var(--paper-2);border-radius:8px;font-size:12px">
            <div><span style="color:var(--ink-500)">Seniorów:</span> <span class="num-serif" style="font-size:14px">${g.seniors}</span></div>
            <div><span style="color:var(--ink-500)">Avg price:</span> <span class="num-serif" style="font-size:14px">${g.avgRequestPrice}</span></div>
          </div>
          <div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--line)">
            <div style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">Rekomendacja</div>
            <div style="font-family:var(--serif);font-style:italic;font-size:13px;color:var(--granat-900);line-height:1.4;font-weight:400">${g.recommendation}</div>
          </div>
          <div style="display:flex;gap:6px;margin-top:14px">
            <button class="btn btn-ghost btn-sm" style="flex:1;justify-content:center">Znajdź partnera</button>
            <button class="btn btn-ghost btn-sm">Historia próśb</button>
          </div>
        </div>
      `).join('')}
    </div>
  </div>

</div>`;

/* ============================================
   WEARABLES FLEET (Panel Admina · Core Config)
   ============================================ */

const WEARABLE_BRANDS = [
  {id:'xiaomi',name:'Xiaomi Band 8/9',ic:'⌚',api:'Zepp Life API',paired:587,active:583,syncLat:'156ms',errors24:2,priority:1,cost:'99 zł',status:'ok'},
  {id:'apple',name:'Apple Watch',ic:'🍎',api:'HealthKit (iOS bridge)',paired:198,active:194,syncLat:'82ms',errors24:0,priority:2,cost:'—',status:'ok'},
  {id:'garmin',name:'Garmin',ic:'🔵',api:'Garmin Connect Web API',paired:89,active:87,syncLat:'234ms',errors24:1,priority:3,cost:'—',status:'ok'},
  {id:'fitbit',name:'Fitbit',ic:'🟢',api:'Fitbit Web API (Google)',paired:67,active:64,syncLat:'198ms',errors24:3,priority:4,cost:'—',status:'ok'},
];

SCREEN_RENDERERS.wearables = () => `
<div class="content-inner">
  <div class="page-head">
    <div>
      <h1 class="h">Wearables Fleet · <em>4 marki · 941 urządzeń</em></h1>
      <div class="sub">
        <span class="live">Live sync</span>
        <span class="sep">·</span><span>928 aktywnych · 13 offline &gt;24h · 306 seniorów bez opaski</span>
        <span class="sep">·</span><span>Kalibracja: 34 w toku · 907 stabilnych</span>
        <span class="sep">·</span><span>Ręczne nadpisania progów: 47</span>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost">Provider API logs</button>
      <button class="btn btn-ghost">Force sync all</button>
      <button class="btn btn-accent">+ Paruj urządzenie</button>
    </div>
  </div>

  <!-- Provider health cards -->
  <div class="section-hd"><h2>Provider API status</h2><span class="link">Health check co 30s</span></div>
  <div class="grid-4">
    ${WEARABLE_BRANDS.map(b => `
      <div class="card" style="padding:22px 24px;position:relative">
        <div style="position:absolute;top:12px;right:14px;font-family:var(--mono);font-size:9px;color:var(--zloto-700);letter-spacing:0.14em">P${b.priority}</div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
          <div style="font-size:36px">${b.ic}</div>
          <div>
            <div style="font-family:var(--serif);font-size:17px;color:var(--granat-900);font-weight:500;letter-spacing:-0.01em">${b.name}</div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em;margin-top:2px">${b.api}</div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:11px;color:var(--ink-500)">
          <div><strong style="font-family:var(--serif);color:var(--granat-900);font-size:20px;display:block;font-weight:500;letter-spacing:-0.015em">${b.paired}</strong>Sparowanych</div>
          <div><strong style="font-family:var(--serif);color:var(--sem-green);font-size:20px;display:block;font-weight:500">${b.active}</strong>Aktywnych</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding-top:12px;font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.04em">
          <div><strong style="font-family:var(--mono);color:var(--granat-900);display:block;font-size:12px;font-weight:600">${b.syncLat}</strong>Sync latency</div>
          <div><strong style="font-family:var(--mono);color:${b.errors24>0?'var(--sem-yellow)':'var(--sem-green)'};display:block;font-size:12px;font-weight:600">${b.errors24}</strong>Errors 24h</div>
        </div>
        <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center">
          <span class="pip ${b.status==='ok'?'green':'yellow'}"><span class="dot"></span>${b.status==='ok'?'OK':'Degraded'}</span>
          ${b.cost !== '—' ? `<span style="font-family:var(--mono);font-size:10px;color:var(--zloto-700);letter-spacing:0.06em">Koszt urz.: ${b.cost}</span>` : ''}
        </div>
      </div>
    `).join('')}
  </div>

  <!-- Fleet -->
  <div class="section-hd" style="margin-top:32px"><h2>Sparowane urządzenia · <em>941 w flocie</em></h2>
    <div class="n-tabs">
      <button class="on">Wszystkie 941</button>
      <button>Kalibracja 34</button>
      <button>Nadpisania 47</button>
      <button>Offline 13</button>
    </div>
  </div>

  <div class="filter-bar">
    <div class="field"><label>Marka</label>
      <select><option>Wszystkie 4</option><option>⌚ Xiaomi (587)</option><option>🍎 Apple (198)</option><option>🔵 Garmin (89)</option><option>🟢 Fitbit (67)</option></select>
    </div>
    <div class="field"><label>Status</label>
      <select><option>Wszystkie</option><option>Stabilne (907)</option><option>Kalibracja w toku (34)</option><option>Offline &gt;24h (13)</option></select>
    </div>
    <div class="field"><label>Progi</label>
      <select><option>Wszystkie</option><option>Adaptacyjne auto (894)</option><option>Ręcznie nadpisane (47)</option></select>
    </div>
    <div style="flex:1"></div>
    <div style="display:flex;gap:6px;align-items:center;font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.06em">
      <span>LEGENDA:</span>
      <span style="display:inline-flex;align-items:center;gap:4px"><span style="width:8px;height:8px;background:var(--sem-green);border-radius:50%"></span>Stabilne</span>
      <span style="display:inline-flex;align-items:center;gap:4px"><span style="width:8px;height:8px;background:var(--info-blue);border-radius:50%"></span>Kalibracja</span>
      <span style="display:inline-flex;align-items:center;gap:4px"><span style="width:8px;height:8px;background:var(--zloto-500);border-radius:50%"></span>Nadpisane</span>
    </div>
  </div>

  <div class="card">
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Senior</th><th>Marka · Model</th><th>Status sync</th><th>HR / SpO₂</th><th>Progi HR</th><th>Kalibracja</th><th>Ostatnie zdarzenie</th><th></th></tr></thead>
      <tbody>
        ${[
          {senior:'HW',name:'Halina Wójcik',id:'HW-01247',brand:'Xiaomi Band 8',syncStatus:'ok',syncTime:'2 min temu',hr:'72',spo2:'97%',thresholds:{low:50,high:110,mode:'auto'},calibration:{status:'stable',days:'127 dni'},lastEvent:'—'},
          {senior:'SZ',name:'Stanisław Zieliński',id:'SZ-04127',brand:'Apple Watch S9',syncStatus:'ok',syncTime:'LIVE',hr:'158',spo2:'89%',thresholds:{low:55,high:130,mode:'manual',by:'Krzysztof M.',reason:'Rozpoznana arytmia · próg podniesiony 120→130 po konsultacji z lekarzem POZ',date:'12 mar 2026'},calibration:{status:'stable',days:'89 dni'},lastEvent:'AFib · 22:12 dziś'},
          {senior:'MN',name:'Maria Nowak',id:'MN-02341',brand:'Xiaomi Band 8',syncStatus:'ok',syncTime:'5 min temu',hr:'126',spo2:'95%',thresholds:{low:48,high:115,mode:'auto'},calibration:{status:'stable',days:'62 dni'},lastEvent:'Upadek · 14:22 dziś'},
          {senior:'JK',name:'Janusz Kowalski',id:'JK-08823',brand:'Xiaomi Band 8',syncStatus:'ok',syncTime:'8 min temu',hr:'72',spo2:'97%',thresholds:{low:50,high:110,mode:'auto'},calibration:{status:'stable',days:'201 dni'},lastEvent:'—'},
          {senior:'ZK',name:'Zbigniew Krawczyk',id:'ZK-06771',brand:'Garmin Vivosmart 5',syncStatus:'ok',syncTime:'12 min temu',hr:'74',spo2:'97%',thresholds:{low:50,high:120,mode:'manual',by:'Anna W.',reason:'Aktywny senior · pływa 2×/tydz. · próg podniesiony 110→120',date:'02 lip 2026'},calibration:{status:'stable',days:'34 dni'},lastEvent:'—'},
          {senior:'RT',name:'Ryszard Tomczak',id:'RT-05612',brand:'—',syncStatus:'no-device',syncTime:'—',hr:'—',spo2:'—',thresholds:null,calibration:null,lastEvent:'Brak urządzenia'},
          {senior:'KB',name:'Krystyna Baran',id:'KB-03192',brand:'Fitbit Sense 2',syncStatus:'ok',syncTime:'23 min temu',hr:'68',spo2:'98%',thresholds:{low:52,high:105,mode:'auto'},calibration:{status:'calibrating',day:8,total:14},lastEvent:'Kalibracja w toku'},
          {senior:'EM',name:'Ewa Michalska',id:'EM-04938',brand:'Apple Watch SE',syncStatus:'ok',syncTime:'4 min temu',hr:'76',spo2:'96%',thresholds:{low:50,high:110,mode:'auto'},calibration:{status:'stable',days:'156 dni'},lastEvent:'—'},
          {senior:'WS',name:'Wanda Sikora',id:'WS-02114',brand:'Xiaomi Band 8',syncStatus:'offline',syncTime:'2 dni temu',hr:'—',spo2:'—',thresholds:{low:50,high:110,mode:'auto'},calibration:{status:'stable',days:'78 dni'},lastEvent:'Bateria: 3%'},
          {senior:'AS',name:'Andrzej Szymański',id:'AS-07823',brand:'—',syncStatus:'no-device',syncTime:'—',hr:'—',spo2:'—',thresholds:null,calibration:null,lastEvent:'Brak urządzenia'},
        ].map(d => {
          const cal = d.calibration;
          const th = d.thresholds;
          return `
          <tr>
            <td><div class="a-pill"><div class="a-av">${d.senior}</div><span class="a-name">${d.name}</span></div><div class="id" style="font-family:var(--mono);font-size:10px;color:var(--ink-500);margin-top:3px;padding-left:38px">${d.id}</div></td>
            <td>${d.brand === '—' ? '<span class="pip yellow"><span class="dot"></span>Brak</span>' : `<div class="num-mono" style="font-size:12px;color:var(--granat-900)">${d.brand}</div>`}</td>
            <td>${d.syncStatus === 'ok' ? `<span class="pip green"><span class="dot"></span>${d.syncTime}</span>` : d.syncStatus === 'offline' ? `<span class="pip red"><span class="dot"></span>Offline ${d.syncTime}</span>` : `<span class="num-mono muted">—</span>`}</td>
            <td>${d.hr !== '—' ? `<span class="num-mono">${d.hr} bpm</span><br/><span class="num-mono muted" style="font-size:10px">${d.spo2}</span>` : `<span class="num-mono muted">—</span>`}</td>
            <td>
              ${!th ? '<span class="num-mono muted">—</span>' :
                th.mode === 'manual' ?
                  `<div style="border:1.5px solid var(--zloto-500);background:var(--zloto-50);padding:4px 8px;border-radius:6px" title="Ręcznie nadpisane">
                    <div class="num-mono" style="color:var(--zloto-800)">${th.low}–${th.high} bpm</div>
                    <div style="font-family:var(--mono);font-size:9px;color:var(--zloto-700);letter-spacing:0.06em;margin-top:2px">★ ${th.by}</div>
                  </div>` :
                  `<div class="num-mono">${th.low}–${th.high} bpm</div><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);margin-top:2px;letter-spacing:0.04em">auto ±10%</div>`
              }
            </td>
            <td>
              ${!cal ? '<span class="num-mono muted">—</span>' :
                cal.status === 'calibrating' ?
                  `<div style="min-width:100px">
                    <span class="pip info"><span class="dot"></span>Dzień ${cal.day}/${cal.total}</span>
                    <div class="prog" style="color:var(--info-blue);margin-top:4px;height:3px"><div class="fill" style="width:${cal.day/cal.total*100}%"></div></div>
                  </div>` :
                  `<span class="pip green"><span class="dot"></span>Stabilna</span><div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);margin-top:2px;letter-spacing:0.04em">${cal.days}</div>`
              }
            </td>
            <td style="font-family:var(--mono);font-size:11px;color:${d.lastEvent === '—' ? 'var(--ink-500)' : d.lastEvent.includes('Upadek') || d.lastEvent.includes('AFib') ? 'var(--sem-red)' : 'var(--ink-700)'};letter-spacing:0.02em">${d.lastEvent}</td>
            <td><button class="btn btn-ghost btn-sm">Otwórz →</button></td>
          </tr>
        `;}).join('')}
      </tbody>
    </table></div>
  </div>

  <!-- Detail: manual override showcase -->
  <div class="section-hd" style="margin-top:32px"><h2>Szczegóły · <em>Stanisław Zieliński (SZ-04127)</em></h2><span class="link">Widok kalibracji + ręcznie nadpisanego progu</span></div>

  <div class="split-2-1">
    <div class="card">
      <div class="card-head"><div><div class="t">Baseline HR · <em>ostatnie 14 dni</em></div><div class="h-sub">Adaptacyjny baseline · średnia dobowa</div></div><span class="pip green"><span class="dot"></span>Stabilna · 89 dni</span></div>
      <div class="chart-area" style="height:220px;padding:24px">
        <svg class="chart-svg" viewBox="0 0 700 200" preserveAspectRatio="none">
          <!-- Threshold band manual -->
          <rect x="30" y="20" width="670" height="30" fill="var(--sem-red-bg)" opacity="0.4"/>
          <rect x="30" y="145" width="670" height="35" fill="var(--sem-red-bg)" opacity="0.4"/>
          <text x="35" y="35" fill="var(--sem-red)" font-size="10" font-family="var(--mono)" letter-spacing="0.06em">HIGH · 130 bpm ★ MANUAL (Krzysztof M.)</text>
          <text x="35" y="160" fill="var(--sem-red)" font-size="10" font-family="var(--mono)" letter-spacing="0.06em">LOW · 55 bpm ★ MANUAL</text>

          <!-- Normal zone -->
          <line class="grid" x1="30" y1="80" x2="700" y2="80"/>
          <line class="grid" x1="30" y1="110" x2="700" y2="110"/>

          <!-- Baseline avg -->
          <line x1="30" y1="95" x2="700" y2="95" stroke="var(--zloto-500)" stroke-width="1.5" stroke-dasharray="4 4"/>
          <text x="35" y="90" fill="var(--zloto-700)" font-size="10" font-family="var(--mono)" letter-spacing="0.06em">Baseline: 78 bpm (auto)</text>

          <!-- HR line -->
          <path d="M30,95 L80,88 L130,102 L180,92 L230,85 L280,110 L330,115 L380,125 L430,90 L480,88 L530,92 L580,100 L630,155 L680,142 L700,148"
                stroke="var(--granat-700)" stroke-width="2" fill="none"/>
          <circle cx="680" cy="142" r="4" fill="var(--sem-red)" stroke="white" stroke-width="2"/>
          <text x="600" y="130" fill="var(--sem-red)" font-size="11" font-family="var(--serif)" font-weight="500">AFib event · 158 bpm</text>

          <text x="30" y="195">01 lip</text><text x="230" y="195">05 lip</text><text x="430" y="195">08 lip</text><text x="650" y="195">Dziś</text>
        </svg>
      </div>
    </div>

    <div>
      <!-- Manual override highlight -->
      <div class="card" style="border:1.5px solid var(--zloto-500)">
        <div class="card-head" style="background:var(--zloto-50);border-bottom-color:var(--zloto-300)">
          <div>
            <div class="t">★ Ręczne nadpisanie progu</div>
            <div class="h-sub" style="color:var(--zloto-700)">Odpowiedzialność medyczna · audit trail</div>
          </div>
        </div>
        <div style="padding:16px 20px">
          <div style="display:grid;gap:10px;font-size:12.5px;color:var(--ink-700)">
            <div><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;display:block;margin-bottom:2px">Zmodyfikował</span><strong style="color:var(--granat-900);font-family:var(--serif);font-size:14px;font-weight:500">Krzysztof M.</strong> · Koordynator SilverTech</div>
            <div><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;display:block;margin-bottom:2px">Data zmiany</span><span class="num-mono">12 mar 2026 · 14:23</span></div>
            <div><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;display:block;margin-bottom:2px">Zmiana</span><div><span class="num-mono muted">HR high: 120</span> → <strong class="num-mono" style="color:var(--zloto-800)">130 bpm</strong></div></div>
            <div><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;display:block;margin-bottom:2px">Uzasadnienie</span><div style="font-family:var(--serif);font-style:italic;font-size:13px;color:var(--granat-900);line-height:1.5;font-weight:400">„Rozpoznana arytmia · próg podniesiony 120→130 po konsultacji z lekarzem POZ (Dr Chmielewska, potwierdzenie e-mail)"</div></div>
            <div><span style="font-family:var(--mono);font-size:10px;color:var(--ink-500);letter-spacing:0.1em;text-transform:uppercase;display:block;margin-bottom:2px">Podpis</span><span class="num-mono muted" style="font-size:10px">SHA-256 verified · audit_log_87231</span></div>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--line);display:flex;gap:6px">
            <button class="btn btn-ghost btn-sm" style="flex:1;justify-content:center">Edytuj (2FA)</button>
            <button class="btn btn-ghost btn-sm" style="color:var(--sem-red)">Reset auto</button>
          </div>
        </div>
      </div>

      <!-- Opiekun context notes -->
      <div class="card" style="margin-top:16px">
        <div class="card-head"><div><div class="t">Notatki kontekstowe opiekunów</div><div class="h-sub">Soft context · nie edytuje progów</div></div></div>
        <div style="padding:16px 20px">
          <div style="padding:10px 12px;background:var(--paper-2);border-radius:6px;margin-bottom:8px">
            <div style="font-size:12px;color:var(--granat-900);line-height:1.5">„Ojciec chodzi na rehabilitację we wtorki i piątki 10:00–11:30 — HR może wzrastać."</div>
            <div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);margin-top:6px;letter-spacing:0.06em">Anna Chmielewska (córka) · 08 lip · przekazane do Adam context</div>
          </div>
          <div style="padding:10px 12px;background:var(--paper-2);border-radius:6px">
            <div style="font-size:12px;color:var(--granat-900);line-height:1.5">„Pije 2 espresso rano — nie liczyć tego jako tachykardii."</div>
            <div style="font-family:var(--mono);font-size:9px;color:var(--ink-500);margin-top:6px;letter-spacing:0.06em">Piotr Wójcik (syn) · 15 cze · przekazane do Adam context</div>
          </div>
          <button class="btn btn-ghost btn-sm" style="width:100%;justify-content:center;margin-top:12px">+ Dodaj notatkę kontekstową</button>
        </div>
      </div>
    </div>
  </div>
</div>`;
