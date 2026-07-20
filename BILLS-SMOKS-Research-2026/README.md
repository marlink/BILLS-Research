# BILLS Smoks B2B Research & Audits (2026)

This repository contains market research reports, lead databases, technical domain audits, and interactive dashboards compiled for **BILLS Smoks** (exclusive distributor of Powermatic & Hawk-Matic injector machines).

---

## 📂 Key Files & Directories

### 📊 Lead Databases & Dashboards
*   **[07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv](07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv)**: The master leads database containing 376 verified Polish tobacco, FMCG, and accessories wholesalers/distributors.
*   **[DASH-Katalog-Leadow-B2B-PL.html](DASH-Katalog-Leadow-B2B-PL.html)**: Interactive e-commerce dashboard to search, filter, and prioritize the B2B leads by Voivodeship, priority scale, and type.

### 📄 Executive PDF Reports
*   **[24-Extras-Tobacco-Distributors-PL.pdf](24-Extras-Tobacco-Distributors-PL.pdf)**: **B2B Wholesaler Directory PDF** (15 pages). High-density regional list of partners, with market leaders highlighted in gold with a `★ LIDER ★` tag and their brand portfolios mapped dynamically.
*   **[25-BILLS-SMOKS-Domeny-i-Profile.pdf](25-BILLS-SMOKS-Domeny-i-Profile.pdf)**: **Domain Audit & Shop Benchmarking PDF** (4 pages). Technical audit of 20 domains and functional benchmarking of 8 active shops.
*   **[25-BILLS-SMOKS-Domeny.csv](25-BILLS-SMOKS-Domeny.csv)**: Detailed domain WHOIS and DNS hosting results.

### ⚙️ Automation Scripts
*   **[generate_unified_report.py](generate_unified_report.py)**: Audits the domain registration states, dns resolutions, and HTTP availability live. It updates `25-BILLS-SMOKS-Domeny.csv` and compiles `25-BILLS-SMOKS-Domeny-i-Profile.pdf`.

---

## 🚀 How to Run the Domain Audit

To run a live technical audit on the domains, execute the script using the Python virtual environment:
```bash
/Users/apple/Documents/Docs/Bills/Research/Wholesale/scraper/.venv/bin/python generate_unified_report.py
```
This will query DNS records, check HTTP/SSL certificates, and compile the final reports.
