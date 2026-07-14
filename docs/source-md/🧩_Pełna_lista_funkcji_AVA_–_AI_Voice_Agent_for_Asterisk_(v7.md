🧩 Pełna lista funkcji AVA – AI Voice Agent for Asterisk (v7.3.2)
Na podstawie repozytorium hkjarral/AVA-AI-Voice-Agent-for-Asterisk, oto kompletny, szczegółowy spis wszystkich funkcji:
1. 📞 PODSTAWOWA TELEFONIA (Asterisk-Native)
| Funkcja | Status | Opis |
| Integracja z Asterisk/FreePBX | ✅ | Natywne połączenie przez ARI (Asterisk REST Interface), brak zewnętrznych providerów telefonii |
| Dialplan AI_AGENT | ✅ v7.0.0 | Wybór agenta przez zmienną kanałową: Set(AI_AGENT=sales-agent) |
| Dialplan AI_PROVIDER | ✅ | Per-call override providera: Set(AI_PROVIDER=google_live) |
| Multi-instance providerów | ✅ v6.5.2 | Wiele instancji tego samego typu providera z izolowanymi credentials (np. acme_google_live + globex_google_live) |
| Outbound Calling (Alpha) | ✅ v6.x | Zaplanowane kampanie wychodzące, voicemail drop, bramka zgody (consent gate) |
| DID-based routing | ✅ | Routing po numerze DDI z użyciem Asterisk Gosub |
| AudioSocket | ✅ | Transport audio przez AudioSocket (domyślny) |
| ExternalMedia RTP | ✅ | Transport audio przez ExternalMedia/RTP |
| PCMA/μ-law @ 8 kHz | ✅ | Natywne kodowanie Asterisk |
2. 🤖 SILNIKI AI – 7 ZŁOTYCH BAZOWYCH KONFIGURACJI
| # | Provider | Typ | Latencja | Konfiguracja |
| 1 | OpenAI Realtime (GPT‑4o‑realtime, GPT‑realtime‑1.5, GPT‑realtime‑2, GPT‑realtime‑mini) | full‑agent | <2s | ai-agent.golden-openai.yaml |
| 2 | Deepgram Voice Agent (Flux v2 + nova‑3, Think stage) | full‑agent | <3s | ai-agent.golden-deepgram.yaml |
| 3 | Google Live API (Gemini 2.0 Flash / Gemini 3.1 Flash, Vertex AI) | full‑agent | <2s | ai-agent.golden-google-live.yaml |
| 4 | ElevenLabs Conversational AI (premium voices) | full‑agent | <2s | ai-agent.golden-elevenlabs.yaml |
| 5 | xAI Grok Voice Agent (5 głosów: eve/ara/rex/sal/leo + custom cloned) | full‑agent | realtime | ai-agent.golden-grok.yaml |
| 6 | Local Hybrid (lokalny STT/TTS + chmurowy LLM) | pipeline | zmienna | ai-agent.golden-local-hybrid.yaml |
| 7 | Telnyx AI Inference (53+ modeli: GPT‑4o, Claude, Llama) | pipeline | zmienna | ai-agent.golden-telnyx.yaml |
Dodatkowe LLM:
| Provider | Opis |
| MiniMax LLM (M3, M2.7, M2.7‑highspeed) | OpenAI‑compatible API, tool‑calling, długi kontekst |
| Azure Speech Service (STT + TTS) | REST batch, WebSocket streaming, SSML, SSRF prevention |
| Ollama (self‑hosted LLM) | Llama 3.2, Mistral, Qwen 2.5 – zero API key, 100% on‑premise |
3. 🔧 SYSTEM MODULARNYCH PIPELINE’ÓW
| Element | Opcje |
| STT (Speech‑to‑Text) | Whisper (cloud), Faster‑Whisper (local), Whisper.cpp, Sherpa‑ONNX, Kroko ASR, Vosk, Deepgram STT, Google STT, Azure STT, T‑one STT (rosyjski) |
| LLM (Language Model) | OpenAI, Google Gemini, Deepgram, ElevenLabs, Grok, Telnyx (53+ modeli), MiniMax, Ollama (lokalne: Llama, Mistral, Qwen), llama.cpp |
| TTS (Text‑to‑Speech) | OpenAI TTS, ElevenLabs, Google TTS, Deepgram Aura, Piper (lokalny), Kokoro (lokalny), MeloTTS (lokalny), Silero TTS (lokalny, multi‑język), Azure TTS |
| Miksowanie | Dowolne kombinacje STT + LLM + TTS |
| Streaming LLM→TTS overlap | ✅ v6.4.1 – sentence‑boundary token streaming, <2s perceived latency |
| Pipeline filler audio | ✅ – natychmiastowe “One moment please” |
| Direct PCM→μ‑law | ✅ – 10‑50ms oszczędności na odpowiedź |
4. 🖥️ ADMIN UI (Web Dashboard)
| Funkcja | Opis |
| Setup Wizard | Wizualna konfiguracja providerów krok po kroku |
| Dashboard | Metryki real‑time, status kontenerów, wskaźnik połączenia Asterisk |
| Agents Tab | Tworzenie, edycja, zarządzanie agentami z UI; szablony (receptionist, after‑hours, appointment booker) |
| Multi‑agent dashboard | Live KPI: aktywne agenty, aktywne połączenia, przekierowania, statystyki per‑agent |
| Live‑status Dashboard | SSE push (nie poll) – sub‑sekundowa konwergencja stanu systemu |
| Call History | Pełna historia połączeń, transkrypty, detale, odtwarzanie nagrań |
| Call Recordings Playback | Odtwarzanie .ulaw, .WAV, .gsm bezpośrednio w przeglądarce (transkodowanie server‑side) |
| YAML Editor | Monaco‑based editor z walidacją, kolorowanie nazw tooli wg statusu |
| Live Logs | WebSocket‑based log streaming |
| Asterisk Setup Page | Live ARI status, module checklist, config audit z komendami naprawczymi |
| Provider Forms | Uniform per‑instance credential uploader (paste‑style), ~260 inline tooltipów |
| System Topology | Tri‑state per‑component health, 2‑strike debounce, responsive provider grid |
| EnvPage | Sekcja “Per‑Instance Provider Credentials” – audyt credentiali bez SSH |
| WCAG AA Accessibility | Skip‑to‑content, programmatic labels, focus‑trapping modal, non‑colour status cues |
| One‑time admin password | Generowane przy pierwszym starcie, wymuszona zmiana |
5. 🛠️ AI‑POWERED ACTIONS (Tool Calling)
Telefoniczne:
| Tool | Opis |
| transfer | Transfer na extension, queue, ring group |
| cancel_transfer | Anulowanie transferu w trakcie dzwonienia |
| hangup_call | Zakończenie połączenia z pożegnaniem (transport‑safe) |
| leave_voicemail | Przekierowanie na voicemail |
| Attended Transfer | ✅ v6.4.0 – 3 tryby: basic_tts, ai_briefing, caller_recording |
| Live Agent Transfer | ✅ v6.1.1 – transfer do żywego agenta |
Email:
| Tool | Opis |
| send_email_summary | Automatyczne podsumowanie do admina (disabled by default) |
| request_transcript | Transkrypt na żądanie rozmówcy (disabled by default) |
HTTP Tools (3 fazy):
| Faza | Opis |
| Pre‑call (generic_http_lookup) | HTTP lookup przed połączeniem (np. CRM) |
| In‑call (in_call_http_lookup) | HTTP lookup w trakcie połączenia |
| Post‑call (generic_webhook) | Webhook po zakończeniu połączenia |
Kalendarze:
| Integracja | Opis |
| Google Calendar | Multi‑account, per‑context binding, Domain‑Wide Delegation, free/busy |
| Microsoft Calendar | Outlook/M365 przez device‑code OAuth, Graph free/busy, per‑context binding |
| Reschedule reliability | Server‑side event_id resolution, 400/404 fallback |
Pozostałe:
| Funkcja | Opis |
| MCP Tool Integration | Eksperymentalne narzędzia MCP (Model Context Protocol) |
6. 🩺 CLI TOOLS (Narzędzia linii poleceń)
| Komenda | Opis |
| agent setup | Interaktywny wizard konfiguracji |
| agent setup --list-targets | Lista providerów/pipeline’ów bez zmian |
| agent check | Standardowy raport diagnostyczny |
| agent check --local | Weryfikacja lokalnego AI server (STT, LLM, TTS) |
| agent check --remote <ip> | Weryfikacja zdalnego GPU |
| agent update | Pull + rebuild/restart |
| agent rca --call <id> --no-llm | Deterministyczna post‑call root‑cause analysis |
| agent config validate | Walidacja provider, pipeline, transport, audio |
| agent dialplan --agent <slug> | Generowanie snippetów dialplan |
| agent version | Wersja systemu |
7. 🔒 BEZPIECZEŃSTWO I PRYWATNOŚĆ
| Funkcja | Opis |
| MIT License | Pełna otwartość, bez vendor lock‑in |
| Self‑hosted | 100% kontroli nad danymi, zgodność z RODO/GDPR |
| Local STT/TTS | Audio nigdy nie opuszcza serwera (Local Hybrid) |
| Fully Local | CPU‑only, GPU, split‑server – zero chmurowych API |
| Guardrails (v6.3.1) | Hangup guardrails, tool‑call parsing robustness |
| One‑time admin password | v7.0.0 – koniec z admin/admin |
| Config export bez .env | v7.0.0 – sekrety nie wyciekają |
| Azure SSRF prevention | v6.3.2 |
| PII logging discipline | Ochrona danych wrażliwych w logach |
| JWT_SECRET | Automatycznie generowany przez preflight |
| Opt‑in dialplan redirect | v7.3.2 – bezpieczniejsze recovery providera |
| AES‑256 szyfrowanie (opcjonalne) | Dla danych w spoczynku |
8. 🔊 ZAAWANSOWANE FUNKCJE AUDIO I GŁOSU
| Funkcja | Opis |
| Per‑agent voices (v7.3.0) | Każdy agent ma własny głos – dropdown per provider |
| Voice picker | OpenAI 10 GA voices, Grok 5+sugestie custom, Google Live 30 prebuilt, Deepgram Aura |
| Provider‑level default voice | Fallback gdy agent bez głosu |
| Barge‑in | Przerywanie agenta przez rozmówcę (konfigurowalne) |
| Silence Watchdog (v7.3.1) | 30s ciszy → “Are you still there?” → 15s oczekiwania → końcowe ostrzeżenie → hangup |
| Watchdog per‑agent | Konfiguracja globalna + override per agent |
| Transport‑safe hangup | Opróżnianie buforów AudioSocket/ExternalMedia przed rozłączeniem |
| Call Recordings | Nagrywanie rozmów (.ulaw, .WAV, .gsm), odtwarzanie w UI, transkodowanie server‑side |
| Background Music | v4.4.1 – muzyka ambientowa podczas rozmów |
| Russian Speech (v6.4.0) | Sherpa Offline STT, T‑one STT, Silero TTS |
| Filler Audio | Natychmiastowe “One moment please” przed odpowiedzią |
9. ⚙️ KONFIGURACJA
| Funkcja | Opis |
| Three‑file config | ai-agent.yaml (golden baselines) + ai-agent.local.yaml (overrides) + .env (sekrety) |
| Deep merge | Operator‑override’y łączone z upstream bez konfliktów |
| Agent templates | Receptionist, after‑hours, appointment booker, inne |
| Provider failover | Automatyczne przełączanie |
| Automatic migration (v6→v7) | Istniejące contexty → agents database |
| Prompt placeholders | {today}, {current_date} itp. |
| Configurable tool names | Kolorowanie w prompt editorze wg statusu (enabled/global/not‑enabled) |
| Operator config | Override’y w ai-agent.local.yaml |
| Per‑agent tool_overrides | Działa na OpenAI Realtime / Deepgram / Google Live |
10. 📊 OBSERWOWALNOŚĆ I MONITORING
| Funkcja | Opis |
| Call History | Per‑call debugging, transkrypty, metadane, źródło głosu, typ zakończenia |
| SSE Live‑status | Server‑Sent Events – sub‑sekundowa aktualizacja stanu |
| Prometheus /metrics | Metryki w formacie Prometheus (domyślnie 127.0.0.1:15000) |
| Health endpoint | /health – {"status":"healthy"} / "degraded" |
| 5s TTL‑cached probes | Dashboard bez blokowania event loop |
| Error banner | Failed polls w UI |
| Stale‑while‑revalidate cache | Natychmiastowy dostęp do ~11 stron konfiguracyjnych |
| SessionStore | Scentralizowany, typowany stan połączenia |
11. 🏗️ ARCHITEKTURA I WDROŻENIE
| Funkcja | Opis |
| Docker Compose | Dwa kontenery: ai_engine + admin_ui + opcjonalny local_ai_server |
| docker‑compose.gpu.yml | Overlay GPU dla CUDA (llama.cpp) |
| Split‑server | PBX na VPS + GPU box osobno (1‑3s/turn) |
| CPU‑only | W pełni lokalne na CPU (5‑15s/turn) |
| Preflight script | ./preflight.sh --apply-fixes – tworzy .env, generuje JWT_SECRET, sprawdza RAM/disk/network |
| Buildx detection | v6.4.1 |
| GPU install gating | Instalacja GPU tylko z flagą --apply-fixes |
| Updater hardening | v7.3.2 – safer ownership, rollback/stash, readiness validation |
| PR quality gates | Admin backend/frontend + CLI cross‑compilation przed merge |
| Python 3.11+ | Nowoczesny stack |
| Asterisk 18+ | Wsparcie dla nowszych wersji |
| Systemd / init.d | Integracja z systemowym zarządzaniem usługami |
12. 🌍 LOKALIZACJA I JĘZYKI
| Funkcja | Opis |
| Dowolny język promptów | System prompt w PL, EN, DE, RU… |
| Polski TTS | ElevenLabs (polski), Google TTS (polski), lokalny Piper (polski model) |
| Polski STT | Whisper, Faster‑Whisper (obsługują polski) |
| Rosyjski (v6.4.0) | Sherpa Offline STT, T‑one STT, Silero TTS |
| 30+ języków | Zależnie od providera STT/TTS |
13. 📈 DOJRZAŁOŚĆ PRODUKCYJNA
| Wskaźnik | Wartość |
| Wersja | 7.3.2 (July 2026) |
| Licencja | MIT |
| Wydania | 7 major releases, stabilny od v4.x |
| Aktualizacje | Aktywny development (ostatnia: 2026‑07‑09) |
| Community | Discord, GitHub Issues, PR |
| Dokumentacja | 40+ plików dokumentacji (README, Installation, Provider Guides, Local Setup, Production, Architektura, Contributing) |
| Golden baselines | 7 przetestowanych, produkcyjnych konfiguracji |
| v7.3.2 validation matrix | Audyt AudioSocket, ExternalMedia, updater, failure‑recovery |
| Release checklist | Manual golden‑baseline gate przed każdym wydaniem |
| Product Hunt | Featured |
14. 📋 PODSUMOWANIE – CO AVA JUŻ MA DLA “AGENTA ADAMA”
| Potrzeba Adama | Status w AVA |
| PSTN/SIP calling do seniorów | ✅ Pełne (Asterisk + outbound alpha) |
| Konwersacje AI po polsku | ✅ (prompt PL + polski TTS/STT) |
| Historia rozmów | ✅ Call History z transkryptami |
| Dashboard dla opiekunów | ✅ Admin UI |
| Wykrywanie ciszy | ✅ Silence Watchdog (30s) |
| Call recordings | ✅ Nagrania + odtwarzanie |
| Nagrywanie rozmów | ✅ |
| Eskalacja / alerty | ⚠️ Tool‑calling (email, webhook) – brak gotowej logiki semafora |
| Przypomnienia o lekach | ⚠️ Możliwe przez HTTP tools + prompt – brak dedykowanego trackera |
| Wykrywanie depresji/kryzysu | ❌ Brak – trzeba dobudować Crisis Detection Engine |
| Baza profili seniorów | ❌ Brak – trzeba dobudować Senior Profile DB |
| Scheduler połączeń | ⚠️ Outbound Calling (Alpha) – jest, ale niedojrzałe |
| Pamięć kontekstowa | ❌ Brak – trzeba dobudować Semantic Memory (RAG/Vector) |
| Integracja wearables | ❌ Brak |
| Marketplace usług | ❌ Brak |
| RODO / AI Act | ⚠️ Self‑hosted = podstawa, ale brak gotowych Consent Manager / Right‑to‑Forget |