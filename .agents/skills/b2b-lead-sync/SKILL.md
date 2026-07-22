---
name: b2b-lead-sync
description: |-
  Automatically ingest, normalize, and add/update B2B company leads into the master catalog (07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv) and dynamically synchronize the interactive e-commerce dashboard (DASH-Katalog-Leadow-B2B-PL.html).
  Use this skill whenever:
  1. The user asks to add, update, or import new company leads or wholesale partners into the BILLS B2B database.
  2. Research findings or scraped company records (NIP, KRS, CEIDG, website, products, score) need to be stored in the master CSV.
  3. The interactive dashboard DASH-Katalog-Leadow-B2B-PL.html needs to be updated with new or modified lead records.
license: Apache-2.0
metadata:
  version: v1
  publisher: bills
---

# B2B Lead Ingestion & Dashboard Synchronization Skill

This skill provides an automated workflow to safely append or update Polish B2B leads, wholesalers, and importers in the master repository:
- **Master CSV**: `BILLS-SMOKS-Research-2026/07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv`
- **Interactive Dashboard**: `BILLS-SMOKS-Research-2026/DASH-Katalog-Leadow-B2B-PL.html`

---

## 🛠️ Automated Execution Script

The core synchronization script is located at:
```bash
python3 .agents/skills/b2b-lead-sync/scripts/sync_b2b_leads.py
```

### Usage Options:

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

3. **Re-sync CSV Master to Dashboard HTML**:
   ```bash
   python3 .agents/skills/b2b-lead-sync/scripts/sync_b2b_leads.py --sync-only
   ```

---

## 📋 Required Schema Fields

All leads must follow the 25 standard columns:
- `Rank`: Auto-assigned based on `Score` descending order.
- `Priorytet`: Priority tier (`A1 — kontakt natychmiast`, `A2 — kontakt w 7 dni`, `B — kampania regionalna`, `C — weryfikacja i nurturing`, `D — niski priorytet/wykluczyć`).
- `Score`: Numerical rating (1–100).
- `Firma`: Company trade & legal name.
- `Relacja`: Relationship type (`Potencjalny reseller / odbiorca hurtowy`, `Partner dystrybucyjny/importer`, `Możliwy konflikt produktowy`).
- `Segment`: Segment ID (`S1 — RYO/MYO, gilzy i nabijarki`, `S2 — Hurtownie tytoniowe/FMCG`, etc.).
- `Kanał`: Distribution channel (`Hurt B2B regionalny`, `Hurt ogólnopolski`, `Importer/dystrybutor krajowy`).
- `Województwo`: Polish Voivodeship or `Ogólnopolska`.
- `Miasto`: City location.
- `Skala`: Business scale (`Duży`, `Średni`, `Mały`).
- `Email`: Contact email address(es).
- `Telefon`: Contact phone number(s).
- `Osoba/Dział decyzyjny`: Board members or purchasing managers.
- `Stanowisko`: Job position.
- `WWW`: Website URL.
- `Adres`: Registered business address.
- `NIP`: 10-digit Polish Tax ID (cleaned of trailing `.0`).
- `KRS`: National Court Register number.
- `Produkty/marki`: Main brands / products distributed.
- `Status`: Lead status (`Nowy`, `Do weryfikacji`, `Wykluczony`).
- `Owner`: Lead owner (default: `BILLS — hurt@bills.pl`).
- `Następny krok`: Recommended action step.
- `Uzasadnienie potencjału`: Rationale for score & partnership fit.
- `Źródła`: Source URLs / verification links.
- `Uwagi`: Notes, VIES status, or Allegro profile notes.

---

## ⚡ Agent Workflow Summary

Whenever new leads are discovered or edited:
1. Parse company details & NIP/KRS validation.
2. Run `sync_b2b_leads.py` with `--add-json` or `--add-file`.
3. Confirm that both `07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv` and `DASH-Katalog-Leadow-B2B-PL.html` have been updated cleanly.
