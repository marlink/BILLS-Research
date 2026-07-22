#!/usr/bin/env python3
"""
B2B Lead Synchronization Script for BILLS Smoks Research
--------------------------------------------------------
Appends/updates B2B leads in 07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv
and automatically regenerates inlined leadsData in DASH-Katalog-Leadow-B2B-PL.html.
"""

import sys
import os
import csv
import json
import re
import argparse

CSV_PATH = "/Users/apple/Documents/Docs/Bills/Research/BILLS-SMOKS-Research-2026/07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv"
HTML_PATH = "/Users/apple/Documents/Docs/Bills/Research/BILLS-SMOKS-Research-2026/DASH-Katalog-Leadow-B2B-PL.html"

FIELDNAMES = [
    'Rank', 'Priorytet', 'Score', 'Firma', 'Relacja', 'Segment', 'Kanał',
    'Województwo', 'Miasto', 'Skala', 'Email', 'Telefon', 'Osoba/Dział decyzyjny',
    'Stanowisko', 'WWW', 'Adres', 'NIP', 'KRS', 'Produkty/marki', 'Status',
    'Owner', 'Następny krok', 'Uzasadnienie potencjału', 'Źródła', 'Uwagi'
]

def clean_value(val):
    if val is None:
        return ""
    s = str(val).strip()
    if s.endswith('.0') and s[:-2].isdigit():
        s = s[:-2]
    return s

def normalize_lead(lead_dict):
    normalized = {}
    for fn in FIELDNAMES:
        normalized[fn] = clean_value(lead_dict.get(fn, ""))
    
    # Defaults
    if not normalized['Status']:
        normalized['Status'] = 'Nowy'
    if not normalized['Owner']:
        normalized['Owner'] = 'BILLS — hurt@bills.pl'
    if not normalized['Score']:
        normalized['Score'] = '70'
    
    try:
        normalized['Score'] = int(float(normalized['Score']))
    except ValueError:
        normalized['Score'] = 70
        
    return normalized

def read_master_csv():
    if not os.path.exists(CSV_PATH):
        return []
    
    leads = []
    with open(CSV_PATH, encoding='utf-8-sig', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {}
            for k, v in row.items():
                clean_key = k.replace('\ufeff', '').strip()
                clean_row[clean_key] = clean_value(v)
            leads.append(normalize_lead(clean_row))
    return leads

def write_master_csv(leads):
    # Sort leads by Score descending, then Rank
    leads.sort(key=lambda x: int(x['Score']), reverse=True)
    for idx, l in enumerate(leads, start=1):
        l['Rank'] = idx

    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for l in leads:
            writer.writerow(l)
    print(f"✓ Saved {len(leads)} leads to Master CSV: {CSV_PATH}")
    return leads

def sync_html_dashboard(leads):
    if not os.path.exists(HTML_PATH):
        print(f"✗ HTML Dashboard file not found at: {HTML_PATH}")
        return False
    
    with open(HTML_PATH, encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Re-sort leads by Score descending for JS
    leads_for_json = []
    for l in leads:
        d = dict(l)
        d['Rank'] = int(d['Rank'])
        d['Score'] = int(d['Score'])
        leads_for_json.append(d)

    json_data = json.dumps(leads_for_json, ensure_ascii=False, indent=4)
    new_inlined_js = f"let leadsData = {json_data};"

    # Replace let leadsData = [...]; in HTML
    pattern = r'let\s+leadsData\s*=\s*\[.*?\];'
    if not re.search(pattern, html, re.DOTALL):
        print("✗ Could not locate 'let leadsData = [...];' in HTML dashboard.")
        return False

    updated_html = re.sub(pattern, new_inlined_js, html, flags=re.DOTALL)

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"✓ Synchronized HTML Dashboard with {len(leads_for_json)} records: {HTML_PATH}")
    return True

def add_or_update_lead(new_lead_dict):
    normalized = normalize_lead(new_lead_dict)
    leads = read_master_csv()

    # Check for existing lead by NIP or Firma name
    existing_idx = None
    if normalized['NIP']:
        for idx, l in enumerate(leads):
            if l['NIP'] and l['NIP'] == normalized['NIP']:
                existing_idx = idx
                break
    
    if existing_idx is None and normalized['Firma']:
        for idx, l in enumerate(leads):
            if l['Firma'].lower() == normalized['Firma'].lower():
                existing_idx = idx
                break

    if existing_idx is not None:
        print(f"➜ Updating existing lead: {leads[existing_idx]['Firma']} (NIP: {leads[existing_idx]['NIP']})")
        leads[existing_idx].update(normalized)
    else:
        print(f"➜ Adding new lead: {normalized['Firma']} (Score: {normalized['Score']})")
        leads.append(normalized)

    updated_leads = write_master_csv(leads)
    sync_html_dashboard(updated_leads)

def main():
    parser = argparse.ArgumentParser(description="Sync B2B leads between CSV master and HTML Dashboard")
    parser.add_argument("--sync-only", action="store_true", help="Re-sync CSV master data directly into HTML dashboard")
    parser.add_argument("--add-json", type=str, help="JSON string of the lead to add/update")
    parser.add_argument("--add-file", type=str, help="Path to JSON file containing lead or list of leads")

    args = parser.parse_args()

    if args.sync_only:
        leads = read_master_csv()
        write_master_csv(leads)
        sync_html_dashboard(leads)
    elif args.add_json:
        try:
            data = json.loads(args.add_json)
            if isinstance(data, list):
                for item in data:
                    add_or_update_lead(item)
            else:
                add_or_update_lead(data)
        except Exception as e:
            print(f"✗ Failed to parse JSON argument: {e}")
            sys.exit(1)
    elif args.add_file:
        try:
            with open(args.add_file, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    add_or_update_lead(item)
            else:
                add_or_update_lead(data)
        except Exception as e:
            print(f"✗ Failed to read file {args.add_file}: {e}")
            sys.exit(1)
    else:
        # Default: sync
        leads = read_master_csv()
        write_master_csv(leads)
        sync_html_dashboard(leads)

if __name__ == "__main__":
    main()
