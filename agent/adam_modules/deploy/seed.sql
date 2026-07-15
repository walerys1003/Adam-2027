-- ==================================================================
-- Adam — SEED SQL (WP-5) · dane referencyjne / bez PII
-- ==================================================================
-- UWAGA: dane seniorów (PESEL/telefon) są szyfrowane Fernet + blind index
-- i NIE mogą być wstawiane surowym INSERT-em. Do nich służy skrypt:
--     python -m adam_modules.deploy.seed_staging
--
-- Ten plik zawiera wyłącznie dane referencyjne, które są bezpieczne jako
-- czysty SQL (idempotentnie, ON CONFLICT DO NOTHING). Uruchomienie:
--     psql "$ADAM_DATABASE_URL" -f adam_modules/deploy/seed.sql
-- (SQLite: sqlite3 adam.db < adam_modules/deploy/seed.sql)
-- ==================================================================

-- Marketplace — kategorie usług (spójne z frontendem: ORDER_CATEGORIES).
-- Tabela tworzona defensywnie, gdyby migracje jej nie zakładały pod tą nazwą.
CREATE TABLE IF NOT EXISTS marketplace_categories (
    id        INTEGER PRIMARY KEY,
    slug      VARCHAR(48) NOT NULL UNIQUE,
    label     VARCHAR(80) NOT NULL,
    icon      VARCHAR(48) NOT NULL
);

INSERT INTO marketplace_categories (id, slug, label, icon) VALUES
    (1, 'pharmacy',   'Apteka / leki',        'Pill'),
    (2, 'groceries',  'Zakupy spożywcze',     'ShoppingCart'),
    (3, 'meals',      'Posiłki / catering',   'UtensilsCrossed'),
    (4, 'transport',  'Transport / dojazd',   'Car'),
    (5, 'cleaning',   'Sprzątanie',           'Sparkles'),
    (6, 'repairs',    'Drobne naprawy',       'Wrench'),
    (7, 'care',       'Opieka / pielęgnacja', 'HeartHandshake'),
    (8, 'company',    'Towarzystwo / wizyta', 'Users'),
    (9, 'hairdresser','Fryzjer / kosmetyka',  'Scissors')
ON CONFLICT (id) DO NOTHING;

-- ==================================================================
-- Kolejny krok: dane seniorów demonstracyjnych (z szyfrowaniem PII):
--     python -m adam_modules.deploy.seed_staging
-- ==================================================================
