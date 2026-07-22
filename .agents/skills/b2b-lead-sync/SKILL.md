---
name: b2b-lead-sync
description: |-
  Automatically ingest, normalize, and add/update B2B company leads into the master catalog (07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv) and dynamically synchronize the interactive e-commerce dashboard (DASH-Katalog-Leadow-B2B-PL.html). Includes real-time CSV file watching.
  Use this skill whenever:
  1. The user asks to add, update, or import new company leads or wholesale partners into the BILLS B2B database.
  2. Research findings or scraped company records (NIP, KRS, CEIDG, website, products, score) need to be stored in the master CSV.
  3. The interactive dashboard DASH-Katalog-Leadow-B2B-PL.html needs to be updated with new or modified lead records.
license: Apache-2.0
metadata:
  version: v1
  publisher: bills
---

# B2B Lead Ingestion & Real-Time Dashboard Synchronization Skill

This skill provides an automated workflow to safely append or update Polish B2B leads, wholesalers, and importers in the master repository:
- **Master CSV**: `BILLS-SMOKS-Research-2026/07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv`
- **Interactive Dashboard**: `BILLS-SMOKS-Research-2026/DASH-Katalog-Leadow-B2B-PL.html`

---

## ⚡ Real-Time Auto-Sync Trigger Options

### Option A: Background File Watcher (Automatic Trigger on CSV Edit)
To automatically update `DASH-Katalog-Leadow-B2B-PL.html` **every time you edit and save** `07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv` (e.g. in Excel, VS Code, or Numbers), launch the background watcher:

```bash
python3 .agents/skills/b2b-lead-sync/scripts/watch_and_sync.py
```
*The watcher monitors the file timestamp and instantly regenerates the HTML dashboard the moment any change is saved.*

---

### Option B: Programmatic & Agent Sync Script (`sync_b2b_leads.py`)

1. **Add/Update a Single Lead via JSON String**:
   ```bash
   python3 .agents/skills/b2b-lead-sync/scripts/sync_b2b_leads.py --add-json '{
     "Firma": "Nazwa Firmy Sp. z o.o.",
     "NIP": "5270000000",
     "Score": 92,
     "Priorytet": "A1 — kontakt natychmiast",
     "Województwo": "Mazowieckie",
     "Miasto": "Warszawa",
     "Email": "kontakt@firma.pl",
     "Telefon": "+48 22 123 45 67",
     "Segment": "S1 — RYO/MYO, gilzy i nabijarki",
     "Relacja": "Potencjalny reseller / odbiorca hurtowy",
     "Kanał": "Hurt B2B regionalny",
     "Skala": "Duży",
     "WWW": "https://firma.pl",
     "Adres": "ul. Przykładowa 1, 00-001 Warszawa",
     "Produkty/marki": "Nabijarki | Gilzy | Tytoń",
     "Status": "Nowy",
     "Następny krok": "Oferta hurtowa Powermatic V+",
     "Uzasadnienie potencjału": "Duży dystrybutor regionalny."
   }'
   ```

2. **Add/Update Multiple Leads from a JSON File**:
   ```bash
   python3 .agents/skills/b2b-lead-sync/scripts/sync_b2b_leads.py --add-file path/to/leads.json
   ```

3. **Instant Manual Re-Sync**:
   ```bash
   python3 .agents/skills/b2b-lead-sync/scripts/sync_b2b_leads.py --sync-only
   ```
