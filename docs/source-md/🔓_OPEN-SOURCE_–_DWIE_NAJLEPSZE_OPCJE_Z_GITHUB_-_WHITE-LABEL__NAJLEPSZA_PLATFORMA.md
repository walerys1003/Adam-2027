🔓 OPEN-SOURCE – DWIE NAJLEPSZE OPCJE Z GITHUB - WHITE-LABEL  NAJLEPSZA PLATFORMA
🥇 REKOMENDUJĘ: Senior-Care-Agent (Marker-Inc-Korea)
Najbliższy Twojej wizji Agenta Adama – dosłownie to samo, tylko po koreańsku.
| Co | Wartość |
| Link do repo | https://github.com/Marker-Inc-Korea/senior-care-agent |
| Licencja | MIT – całkowicie darmowa, możesz używać komercyjnie |
| Co robi | Dzwoni przez telefon → weryfikuje tożsamość → pyta o samopoczucie/leki → sprawdza nastrój → wykrywa słowa kluczowe distress → alarmuje opiekuna → zapisuje historię |
| Cena | 0 zł – płacisz tylko API (OpenAI ~$0.01/rozmowę + Twilio ~$0.004/min) |
| Język | Prompt w YAML – tłumaczysz na polski w 30 minut |
Jak pobrać i uruchomić (krok po kroku):
# 1. Sklonuj repozytorium
git clone https://github.com/Marker-Inc-Korea/senior-care-agent.git
cd senior-care-agent
# 2. Zainstaluj zależności
pip install -e .
# 3. Skopiuj plik .env.example i wpisz swoje klucze API
cp .env.example .env
# Edytuj .env i wpisz:
#   OPENAI_API_KEY=sk-twoj-klucz
#   LIVEKIT_URL=wss://twoj-projekt.livekit.cloud
#   LIVEKIT_API_KEY=...
#   LIVEKIT_API_SECRET=...
#   DEEPGRAM_API_KEY=...
#   CARTESIA_API_KEY=...
#   SIP_OUTBOUND_TRUNK_ID=...
#   HUMAN_AGENT_PHONE=+48123456789
# 4. Przetłumacz prompt na polski – pliki YAML w katalogu prompts/
#    prompts/intake_prompt.yaml → powitanie i weryfikacja
#    prompts/check_in_prompt.yaml → rozmowa o zdrowiu
# 5. Pobierz modele VAD
python agent.py download-files
# 6. Uruchom testowo
python agent.py dev
# 7. Wykonaj pierwszą próbną rozmowę
python make_call.py +48123456789
Pliki promptów do modyfikacji:
prompts/intake_prompt.yaml – tu wpisujesz po polsku: „Dzień dobry, tu Adam z SilverTech. Czy rozmawiam z Panem Janem Kowalskim?”
prompts/check_in_prompt.yaml – tu: „Jak się Pan dziś czuje? Czy wziął Pan poranne leki? Czy coś Pana boli? Czy spał Pan dobrze?”
Koszty miesięczne przy 30 seniorach:
OpenAI (GPT-4o-mini): ~60 zł
Twilio SIP trunk + minuty: ~80 zł
Deepgram STT: ~40 zł
Cartesia TTS: ~40 zł
Serwer VPS (opcjonalnie): ~150 zł
SUMA: ~220-370 zł/mies. za wszystko
🥈 ALTERNATYWA DLA AMBITNYCH: AVA (Asterisk AI Voice Agent)
To jest produkt produkcyjny – dojrzały, z własnym dashboardem webowym.
| Co | Wartość |
| Link do repo | https://github.com/hkjarral/AVA-AI-Voice-Agent-for-Asterisk |
| Licencja | MIT – całkowicie darmowa |
| Co robi | Pełna platforma: własna centrala telefoniczna (Asterisk) + AI voice agent + Admin UI (dashboard webowy) + Call History + nagrywanie |
| Cena | 0 zł – płacisz tylko serwer + API AI |
| Dojrzałość | v7.3.2, aktywna społeczność, 7 golden baseline configs |
Jak pobrać i uruchomić:
# 1. Sklonuj
git clone https://github.com/hkjarral/AVA-AI-Voice-Agent-for-Asterisk.git
cd AVA-AI-Voice-Agent-for-Asterisk
# 2. Uruchom pre-flight check (sprawdzi system, utworzy .env)
sudo ./preflight.sh --apply-fixes
# 3. Uruchom Admin UI (dashboard webowy)
docker compose -p asterisk-ai-voice-agent up -d --build --force-recreate admin_ui
# 4. Otwórz dashboard w przeglądarce: http://localhost:3003
# Hasło jednorazowe – pobierz je:
docker compose -p asterisk-ai-voice-agent logs admin_ui | grep -i password
# 5. Przejdź przez Setup Wizard – wybierz providera AI (OpenAI, Deepgram, Google itp.)
# 6. Podepnij Asterisk/FreePBX – kreator wygeneruje dialplan
# 7. Skonfiguruj Agenta Adama – prompt po polsku, głos ElevenLabs
Linki do zasobów AVA:
Dokumentacja instalacji: https://github.com/hkjarral/AVA-AI-Voice-Agent-for-Asterisk/blob/main/docs/INSTALLATION.md
Transport audio: https://github.com/hkjarral/AVA-AI-Voice-Agent-for-Asterisk/blob/main/docs/Transport-Mode-Compatibility.md
Lokalne AI (GPU): https://github.com/hkjarral/AVA-AI-Voice-Agent-for-Asterisk/blob/main/docs/LOCAL_ONLY_SETUP.md
Discord społeczności: https://discord.gg/ (link w README)
🥉 DODATKOWE PROJEKTY GITHUB (mniej kompletne, ale warte uwagi)
| Projekt | Link | Licencja | Do czego się przyda |
| VoiceCare | https://github.com/devraftel/voicecare | MIT | Przypomnienia o lekach, emergency SMS, głos zoptymalizowany dla seniorów |
| ElderCareAI | https://github.com/ajayprataptomar/ElderCareAI | ❓ | ML model fall detection (można wyjąć i wpiąć do AVA) |
| SilverCircle | https://github.com/maherkhan-builds/AI-Companion-for-Elderly | ❓ | Blueprint UX/UI dla seniora (compassion-first design) |
| AgentDesk | https://github.com/princepal9120/voice-agent | MIT | Open-source'owy white-label (można dodać szablon senior-care) |
🏷️ WHITE-LABEL – NAJLEPSZA PLATFORMA
🥇 REKOMENDUJĘ: Trillet
Dlaczego: Najniższa cena subskrypcji ($299) + nielimitowane subkonta + HIPAA w cenie + natywna infrastruktura.
| Co | Wartość |
| Strona | https://trillet.ai/agency |
| Poradnik white-label | https://trillet.ai/blogs/whitelabel-guide |
| Cennik | $299/mies. (Agency, nielimitowane subkonta) + $0.12/min |
| Compliance | HIPAA + SOC 2 Type II + GDPR + TCPA – w cenie, zero dopłat |
| Trial | 14-dniowy |
Jak zacząć:
Wejdź na https://trillet.ai/agency
Załóż konto (14 dni trial)
Skonfiguruj branding: logo SilverTech, domena, kolory
Stwórz pierwszego agenta → wpisz prompt Adama po polsku
Kup numer telefoniczny (+48) przez panel
Przetestuj rozmowy
Gdy działa → podepnij Stripe billing, ustal cennik dla klientów (rodzin seniorów)
Marża przy 20 seniorach:
Przychód: 20 × 300 zł = 6000 zł
Koszt: $299 (1250 zł) + 6000 min × $0.12 ($720 = 3000 zł) = ~4250 zł
Zysk: ~1750 zł/mies.
🥈 ALTERNATYWA: Autocalls
| Co | Wartość |
| Strona | https://autocalls.ai/white-label |
| Cennik | $419/mies. (all-inclusive, 3500 min w cenie) + $0.09/min overage |
| Kanały | Voice + WhatsApp + web chat |
| Wdrożenie | 24-48 godzin |
Jak zacząć:
https://autocalls.ai/white-label → załóż konto
Skonfiguruj branding, domenę, Stripe
Zbuduj Agenta Adama przez kreator
Przetestuj, sprzedawaj
🎯 CO JA BYM ZROBIŁ NA TWOIM MIEJSCU
Dziś: Sklonuj Senior-Care-Agent – git clone https://github.com/Marker-Inc-Korea/senior-care-agent.git – i odpal python agent.py dev. Zobacz czy w ogóle działa.
W tym tygodniu: Przetłumacz prompt na polski, przetestuj 5 rozmów na swój numer. Jak działa → masz proof-of-concept za ~0 zł.
Za miesiąc: Jeśli chcesz iść w open-source → przenieś się na AVA (dojrzalsze, produkcyjne). Jeśli wolisz szybciej → Trillet za $299/mies.
Kluczowe: Niezależnie którą drogą pójdziesz – prompt i koncept Agenta Adama masz ten sam. Różnica jest tylko w infrastrukturze (Twoja vs czyjaś) i koszcie (0 zł + praca vs $299/mies. + szybciej).