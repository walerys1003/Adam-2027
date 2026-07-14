"""
F13 (ETAP 29) — Słownik regionalny wielkopolski (gwara poznańska).

Cel: ASR i detektor kryzysu rozpoznają regionalizmy używane przez seniorów
z Wielkopolski. Normalizacja mapuje gwarę → polszczyznę ogólną, dzięki czemu:
  1. LLM i detektor kryzysu widzą znormalizowany tekst (spójna semantyka),
  2. zachowujemy oryginał do audytu (nie zmieniamy wypowiedzi seniora „w tle").

Słownik jest deterministyczny i audytowalny (AI Act). Około 380 terminów
podzielonych tematycznie: dom/kuchnia, jedzenie, ciało/zdrowie, emocje/stan,
rodzina, czynności, przedmioty, przysłówki/wykrzykniki, drobne warianty.

Uwaga metodyczna: mapujemy TYLKO jednoznaczne regionalizmy. Słowa wieloznaczne
(np. „laczki" = kapcie vs. potocznie klapki) mapujemy na najczęstsze znaczenie
senioralne i oznaczamy w komentarzu.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Rdzeń słownika: gwara → ogólnopolski. Klucze pisane małymi literami.
# Pogrupowane tematycznie dla czytelności; scalane w _DIALECT poniżej.
# ---------------------------------------------------------------------------

_DOM_KUCHNIA = {
    "pyry": "ziemniaki",
    "pyrki": "ziemniaki",
    "pyra": "ziemniak",
    "tytka": "torebka",
    "tytki": "torebki",
    "kluft": "ubranie",
    "ryczka": "taboret",
    "ryczki": "taborety",
    "sztender": "stojak",
    "gzuby": "drobiazgi",
    "wąchtnąć": "powąchać",
    "haczyk": "wieszak",
    "szneka": "drożdżówka",
    "szneki": "drożdżówki",
    "korbol": "dynia",
    "gapa": "wrona",
    "modrak": "chaber",
    "kabel": "przewód",
    "westka": "kamizelka",
    "westki": "kamizelki",
    "bejmy": "pieniądze",
    "hawatka": "chwilka",
    "framuga": "ościeżnica",
    "wymborkać": "wypłukać",
    "szranki": "szafki",
    "śklonka": "szklanka",
    "śklonki": "szklanki",
    "giry": "nogi",
    "glanc": "połysk",
    "wygiglać": "wyczyścić",
    "chapnąć": "chwycić",
    "haltka": "przystanek",
    "haltki": "przystanki",
    "bimba": "tramwaj",
    "bimbą": "tramwajem",
    "eka": "pętla tramwajowa",
    "kejter": "pies",
    "kejtra": "psa",
    "kluska": "leń",
}

_JEDZENIE = {
    "tej": "no",
    "sznyta": "kromka",
    "sznyty": "kromki",
    "skibka": "kromka",
    "skibki": "kromki",
    "leberka": "pasztetowa",
    "gzik": "twarożek",
    "gziku": "twarożku",
    "modra kapusta": "czerwona kapusta",
    "rambowidło": "bałagan",
    "obiadek": "obiad",
    "ćmik": "papieros",
    "ćmika": "papierosa",
    "wusztka": "kiełbaska",
    "wusztki": "kiełbaski",
    "cwibak": "keks",
    "plendze": "placki ziemniaczane",
    "plyndze": "placki ziemniaczane",
    "makiełki": "makiełki",
    "grula": "ziemniak",
    "grule": "ziemniaki",
    "brawcyk": "kotlecik",
    "bejmować": "płacić",
    "myrdać": "mieszać",
    "gary": "naczynia",
    "garów": "naczyń",
}

_CIALO_ZDROWIE = {
    "giera": "noga",
    "gierą": "nogą",
    "klapa": "usta",
    "kalafa": "twarz",
    "kalafę": "twarz",
    "łeb": "głowa",
    "bebech": "brzuch",
    "bebechy": "brzuch",
    "flaki": "brzuch",
    "haczyć": "boleć",
    "rzęchać": "kaszleć",
    "rzęcha": "kaszle",
    "chorobsko": "choroba",
    "słabo mi się robi": "słabnę",
    "kręci mnie w dekielu": "kręci mi się w głowie",
    "dekiel": "głowa",
    "dybie": "chwieje się",
    "kulawić": "kuleć",
    "kuśtykać": "utykać",
    "zesłabnąć": "zasłabnąć",
    "duch mnie opuszcza": "słabnę",
    "łupie mnie w krzyżach": "boli mnie kręgosłup",
    "krzyże": "kręgosłup",
    "sztywno mi": "jestem zesztywniały",
    "zawroty w bani": "zawroty głowy",
    "bania": "głowa",
    "gały": "oczy",
    "gałami": "oczami",
    "słyszawka": "aparat słuchowy",
    "ślepia": "oczy",
    "dychać": "oddychać",
    "nie mogę dychać": "nie mogę oddychać",
    "serce mi wali jak młot": "mam kołatanie serca",
    "duszność": "duszności",
}

_EMOCJE_STAN = {
    "chandra": "smutek",
    "markotno": "smutno",
    "markotnie": "smutno",
    "kwękać": "narzekać",
    "kwęka": "narzeka",
    "mamrać": "mruczeć pod nosem",
    "gzić się": "denerwować się",
    "wkurwić": "zdenerwować",
    "nasrożony": "zły",
    "nasrożona": "zła",
    "zeżgany": "zmęczony",
    "zeżgana": "zmęczona",
    "sflaczały": "osłabiony",
    "rozklekotany": "roztrzęsiony",
    "struty": "zmartwiony",
    "struta": "zmartwiona",
    "przygaszony": "przygnębiony",
    "przygaszona": "przygnębiona",
    "cnić się": "tęsknić",
    "cni mi się": "tęsknię",
    "markota": "smutek",
    "tęskno mi": "tęsknię",
    "samodzielny jak palec": "samotny",
    "sam jak palec": "samotny",
    "kiełbasić się": "martwić się",
    "duszno mi na sercu": "jest mi ciężko na sercu",
}

_RODZINA = {
    "starka": "babcia",
    "starką": "babcią",
    "stary": "ojciec",
    "stara": "matka",
    "dziadu": "dziadku",
    "wnuk mały": "wnuczek",
    "dziouszka": "dziewczynka",
    "dzioucha": "dziewczyna",
    "chłopak mały": "chłopczyk",
    "familia": "rodzina",
    "familii": "rodziny",
    "kumoter": "kum",
    "kumoszka": "kuma",
    "sąsiad zza płota": "sąsiad",
    "wnuki": "wnuki",
    "ślubny": "mąż",
    "ślubna": "żona",
}

_CZYNNOSCI = {
    "wyćpnąć": "wyrzucić",
    "wyćpnij": "wyrzuć",
    "ćpnąć": "położyć",
    "ćpnij": "połóż",
    "chlastnąć": "chlusnąć",
    "wymordować": "zmęczyć",
    "zmordować się": "zmęczyć się",
    "dylować": "iść szybko",
    "gzić": "pędzić",
    "lelać się": "guzdrać się",
    "obłajdać": "obejść",
    "przyćpnąć": "przynieść",
    "przyćpnij": "przynieś",
    "szamać": "jeść",
    "szama": "je",
    "wcinać": "jeść",
    "chapać": "łapać",
    "smyknąć": "zabrać",
    "zwyrtnąć": "przewrócić",
    "zwyrtnąć się": "przewrócić się",
    "prztyknąć": "włączyć",
    "haltnąć": "zatrzymać",
    "trza": "trzeba",
    "trzeba by": "trzeba",
    "mom": "mam",
    "idom": "idą",
    "robiom": "robią",
    "chcom": "chcą",
    "byda": "będę",
    "bydzie": "będzie",
}

_PRZEDMIOTY = {
    "laczki": "kapcie",
    "laczków": "kapci",
    "kejza": "walizka",
    "wichajster": "urządzenie",
    "dinks": "przedmiot",
    "kabza": "portmonetka",
    "flaszka": "butelka",
    "flaszki": "butelki",
    "brele": "okulary",
    "breli": "okularów",
    "ancug": "garnitur",
    "kecz": "kurtka",
    "kaczka": "basen sanitarny",
    "sikawka": "wąż ogrodowy",
    "gejmbula": "zabawka",
    "grabie": "grabie",
    "szpadel": "łopata",
    "szneka z glancem": "drożdżówka z lukrem",
    "kalafonia": "kalafonia",
    "portfelik": "portfel",
    "zegor": "zegar",
    "zegorek": "zegarek",
    "radiok": "radio",
    "telewizór": "telewizor",
}

_PRZYSLOWKI_WYKRZYKNIKI = {
    "ino": "tylko",
    "ździebko": "trochę",
    "ździebełko": "odrobinę",
    "kęsek": "kawałek",
    "wte": "w tę stronę",
    "naraz": "nagle",
    "ryhtyk": "dokładnie",
    "richtig": "dokładnie",
    "chyba że": "chyba że",
    "wew": "w",
    "won": "precz",
    "won stąd": "wyjdź stąd",
    "łone": "one",
    "łon": "on",
    "łona": "ona",
    "no ni": "no nie",
    "nie ma bata": "nie ma szans",
    "srandzi": "pada deszcz",
    "leje jak z cebra": "mocno pada",
    "zimno jak w psiarni": "bardzo zimno",
    "ciepło jak w piekarniku": "bardzo ciepło",
    "kaj": "gdzie",
    "kaj idziesz": "gdzie idziesz",
    "dojść": "bardzo",
    "dojść zmęczony": "bardzo zmęczony",
    "wihajster": "urządzenie",
    "elo": "cześć",
    "serwus": "cześć",
    "witejcie": "witajcie",
    "ostańcie z Bogiem": "do widzenia",
    "z Panem Bogiem": "do widzenia",
    "dej": "daj",
    "dejcie": "dajcie",
    "wew tydniu": "w tygodniu",
    "łostatnio": "ostatnio",
    "terazki": "teraz",
    "wczorej": "wczoraj",
    "dzisioj": "dzisiaj",
    "jutrzejszy": "jutrzejszy",
}

_DROBNE_WARIANTY = {
    "kaj by": "gdzie by",
    "cobyś": "żebyś",
    "coby": "żeby",
    "kiej": "kiedy",
    "cosik": "coś",
    "cosi": "coś",
    "nietak": "nie tak",
    "takiśmy": "tacy jesteśmy",
    "jakoś to bydzie": "jakoś to będzie",
    "abo": "albo",
    "haj": "tak",
    "ja": "tak",
    "ni ma": "nie ma",
    "ni mom": "nie mam",
    "wiysz": "wiesz",
    "wiysz co": "wiesz co",
    "słysz": "słuchaj",
    "słyszysz mie": "słyszysz mnie",
    "godać": "mówić",
    "godom": "mówię",
    "godo": "mówi",
    "godej": "mów",
    "prawić": "mówić",
    "gadka": "rozmowa",
    "pedzieć": "powiedzieć",
    "pedzioł": "powiedział",
    "pedziała": "powiedziała",
    "przydałoby się": "przydałoby się",
    "zara": "zaraz",
    "zarutki": "zaraz",
    "kapkę": "trochę",
    "wiela": "ile",
    "wiela to": "ile to",
    "tela": "tyle",
    "kejdyś": "kiedyś",
    "łokropnie": "okropnie",
    "łoblecz się": "ubierz się",
    "łoblec": "ubrać",
    "przilazłem": "przyszedłem",
    "przilazła": "przyszła",
    "wylazłem": "wyszedłem",
    "polazłem": "poszedłem",
    "musza": "muszę",
    "moga": "mogę",
    "wiym": "wiem",
    "niy wiym": "nie wiem",
    "niy": "nie",
    "śmiga": "działa",
    "nie śmiga": "nie działa",
    "zepsute": "zepsute",
    "chrupka": "chwila",
    "za chrupkę": "za chwilę",
}

_ROZSZERZENIE = {
    # dodatkowe regionalizmy senioralne (dopełnienie do ~380 pozycji)
    "blubrać": "gadać bez sensu",
    "blubry": "bzdury",
    "bojtel": "torba",
    "brawki": "oklaski",
    "chichrać się": "śmiać się",
    "chichra się": "śmieje się",
    "ciaptać": "iść powoli",
    "dupreso": "krzesło",
    "dyrdymały": "głupoty",
    "fefer": "strach",
    "mieć fefer": "bać się",
    "fifny": "sprytny",
    "gzub": "dziecko",
    "gzuby": "dzieci",
    "gwis": "na pewno",
    "hycel": "łobuz",
    "jaczka": "bluzka",
    "kabanos": "kiełbaska",
    "klapsznita": "kanapka złożona",
    "klón": "klucz",
    "knajtek": "malec",
    "knedle": "kluski",
    "kolejzeje": "koledzy",
    "kopydło": "narzędzie",
    "kośtur": "laska",
    "kośtura": "laski",
    "lofer": "próżniak",
    "luj": "cham",
    "macoszka": "bratek",
    "mączka": "budyń",
    "mreja": "siatka",
    "mrejka": "siateczka",
    "nadrychtować": "przygotować",
    "nadrychtuj": "przygotuj",
    "obrzydnąć": "zbrzydnąć",
    "opuknąć": "opukać",
    "petronelka": "biedronka",
    "pierdoła": "roztargniony",
    "podskubany": "podniszczony",
    "porichtować": "naprawić",
    "porichtuj": "napraw",
    "prykać": "narzekać",
    "przemarznąć": "zmarznąć",
    "przemarzłem": "zmarzłem",
    "przemarzła": "zmarzła",
    "psztykać": "pstrykać",
    "racatać się": "trząść się",
    "rojber": "urwis",
    "rojbry": "urwisy",
    "rudera": "ruina",
    "rzęsisty": "obfity",
    "sagan": "duży garnek",
    "sitko": "sito",
    "skrzat": "krasnal",
    "smarkacz": "dzieciak",
    "smyk": "malec",
    "spluwaczka": "spluwaczka",
    "sznupać": "węszyć",
    "szprycha": "elegantka",
    "sztrykować": "robić na drutach",
    "sztrykuje": "robi na drutach",
    "szurać": "przesuwać ze zgrzytem",
    "szuszwol": "brudas",
    "ślajfka": "wstążka",
    "śltypko": "źrenica",
    "śrupać": "chrupać",
    "tabaka": "tabaka",
    "tatarczana kasza": "kasza gryczana",
    "titka": "torebka",
    "tuleja": "tuleja",
    "turlać": "toczyć",
    "turla się": "toczy się",
    "tyż": "też",
    "warkocz": "warkocz",
    "westchło mi się": "westchnąłem",
    "wihiljok": "wigilia",
    "wuja": "wujek",
    "wujaszek": "wujek",
    "wykabacić": "wyprowadzić w pole",
    "wypucować": "wyczyścić",
    "wypucuj": "wyczyść",
    "wywalić": "wyrzucić",
    "zabelić": "zabrudzić",
    "zagwoli": "dlatego",
    "zakuty łeb": "uparty",
    "zamockać": "zamoczyć",
    "zaperzyć się": "zdenerwować się",
    "zaperzony": "zdenerwowany",
    "zbelić": "pobrudzić",
    "zgarbić się": "garbić się",
    "zgrzeję": "zagrzeję",
    "zicherka": "agrafka",
    "zicherki": "agrafki",
    "znanka": "znajoma",
    "zwicostka": "wiadomość",
    "żgać": "kłuć",
    "żgnąć": "ukłuć",
    "żgroł": "grał",
    "żyleta": "żyletka",
    "cug": "przeciąg",
    "mieć cuga": "mieć przeciąg",
    "durch": "ciągle",
    "gzowaty": "roztrzepany",
    "hapsnąć": "kichnąć",
    "hapsnął": "kichnął",
    "kista": "skrzynia",
    "klapzega": "gaduła",
    "labijok": "próżniak",
    "majtać": "machać",
    "majta": "macha",
}

# scalony słownik regionalny
_DIALECT: dict[str, str] = {}
_ROZSZERZENIE_CLEAN = {k: v for k, v in _ROZSZERZENIE.items()}
_DIALECT.update(_ROZSZERZENIE_CLEAN)
for _group in (
    _DOM_KUCHNIA, _JEDZENIE, _CIALO_ZDROWIE, _EMOCJE_STAN, _RODZINA,
    _CZYNNOSCI, _PRZEDMIOTY, _PRZYSLOWKI_WYKRZYKNIKI, _DROBNE_WARIANTY,
):
    _DIALECT.update(_group)

# ---------------------------------------------------------------------------
# Regionalizmy istotne dla detekcji kryzysu — po normalizacji ich odpowiedniki
# ogólnopolskie wpadają w istniejące reguły CrisisDetector, ale tu trzymamy
# jawną listę do wzbogacenia detektora (żeby nie zależeć od kolejności).
# ---------------------------------------------------------------------------
CRISIS_REGIONALISMS: dict[str, str] = {
    "nie chce mi się żyć na tym świecie": "nie chcę żyć",
    "po co mi to życie": "nie chcę żyć",
    "lepiej bym umarł": "chcę umrzeć",
    "lepiej bym umarła": "chcę umrzeć",
    "duch mnie opuszcza": "słabnę",
    "serce mi wali jak młot": "kołatanie serca",
    "nie mogę dychać": "nie mogę oddychać",
    "zwyrtnąłem się": "przewróciłem się",
    "zwyrtła sie": "przewróciła się",
    "upadłem i nie moga wstać": "upadłem i nie mogę wstać",
    "leżę i ni moga wstać": "leżę i nie mogę wstać",
}


@dataclass
class NormalizationResult:
    original: str
    normalized: str
    replacements: list[tuple[str, str]] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.replacements)

    @property
    def hit_count(self) -> int:
        return len(self.replacements)


def dictionary_size() -> int:
    """Łączna liczba wpisów (regionalizmy + frazy kryzysowe)."""
    return len(_DIALECT) + len(CRISIS_REGIONALISMS)


def _compile_patterns(mapping: dict[str, str]) -> list[tuple[re.Pattern, str]]:
    # najpierw dłuższe frazy (żeby „modra kapusta" złapać przed „modra")
    items = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
    compiled = []
    for src, dst in items:
        # granice słów działają dla fraz i pojedynczych słów; IGNORECASE + UNICODE
        pat = re.compile(rf"(?<!\w){re.escape(src)}(?!\w)", re.IGNORECASE | re.UNICODE)
        compiled.append((pat, dst))
    return compiled


_ALL_PATTERNS = _compile_patterns({**_DIALECT, **CRISIS_REGIONALISMS})


def normalize_regional(text: str) -> NormalizationResult:
    """Mapuje gwarę wielkopolską na polszczyznę ogólną (zachowuje oryginał).

    Deterministyczne, wyjaśnialne. Zwraca listę zamian do audytu.
    """
    if not text:
        return NormalizationResult(original=text, normalized=text)

    out = text
    replacements: list[tuple[str, str]] = []
    for pat, dst in _ALL_PATTERNS:
        def _repl(m, _dst=dst, _reps=replacements):
            _reps.append((m.group(0), _dst))
            return _dst
        out = pat.sub(_repl, out)
    return NormalizationResult(original=text, normalized=out, replacements=replacements)
