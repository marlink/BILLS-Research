#!/usr/bin/env python3
"""
CEIDG API v3 Batch Lead Enrichment Script
-----------------------------------------
Safely queries Ministerstwo Rozwoju i Technologii CEIDG API v3
with strict rate-limiting (4s delay per request) and batch controls.
Updates 07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv & DASH-Katalog-Leadow-B2B-PL.html.
"""

import sys
import os
import time
import urllib.request
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
from sync_b2b_leads import read_master_csv, write_master_csv, sync_html_dashboard

ENV_PATH = "/Users/apple/Documents/Docs/Bills/Research/BILLS-SMOKS-Research-2026/.env"

def get_ceidg_token():
    if not os.path.exists(ENV_PATH):
        print(f"✗ .env file not found at {ENV_PATH}")
        return None
    with open(ENV_PATH, encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('CEIDG_API_TOKEN='):
                return line.strip().split('=', 1)[1].strip('\"\' ')
    return None

def query_ceidg_api(nip, token):
    url = f"https://dane.biznes.gov.pl/api/ceidg/v3/firmy?nip={nip}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (BILLS B2B Research)')

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                firmy = data.get('firmy', [])
                if firmy:
                    return firmy[0]
            return None
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  ⚠️ Rate limit reached (429)! Cooling down for 60 seconds...")
            time.sleep(60)
        else:
            print(f"  ✗ HTTP Error {e.code} for NIP {nip}: {e.reason}")
        return None
    except Exception as e:
        print(f"  ✗ Network error for NIP {nip}: {e}")
        return None

def run_enrichment(batch_size=3, delay_sec=4.0):
    token = get_ceidg_token()
    if not token:
        print("✗ Cannot proceed without CEIDG_API_TOKEN in .env")
        return

    leads = read_master_csv()
    updated_count = 0
    queried_count = 0

    print("==========================================================")
    print(" 🏛️ CEIDG API v3 Safe Batch Lead Enrichment")
    print("==========================================================")
    print(f" Request Delay: {delay_sec} seconds")
    print(f" Target Batch Size: {batch_size} companies\n")

    for l in leads:
        nip = l.get('NIP', '').strip()
        # Only query valid 10-digit NIPs that haven't been CEIDG-verified yet
        if nip and len(nip) == 10 and nip.isdigit():
            if 'CEIDG status:' in l.get('Uwagi', '') or 'CEIDG:' in l.get('Uwagi', ''):
                continue  # Already verified via CEIDG API

            queried_count += 1
            print(f"[{queried_count}/{batch_size}] Querying CEIDG API for {l['Firma']} (NIP: {nip})...")
            
            res = query_ceidg_api(nip, token)
            if res:
                wlasciciel = res.get('wlasciciel', {})
                imie = wlasciciel.get('imie', '')
                nazwisko = wlasciciel.get('nazwisko', '')
                regon = wlasciciel.get('regon', '')
                status = res.get('status', 'AKTYWNY')
                data_rozp = res.get('dataRozpoczecia', '')

                adres_obj = res.get('adresDzialalnosci', {})
                ulica = adres_obj.get('ulica', '')
                budynek = adres_obj.get('budynek', '')
                miasto = adres_obj.get('miasto', '')
                kod = adres_obj.get('kod', '')
                woj = adres_obj.get('wojewodztwo', '')

                full_addr = f"{ulica} {budynek}, {kod} {miasto}".strip(', ')

                # Update lead fields with verified CEIDG data
                if imie and nazwisko:
                    l['Osoba/Dział decyzyjny'] = f"{imie} {nazwisko} (Właściciel)"
                    l['Stanowisko'] = "Właściciel / Owner"
                if regon and not l['KRS']:
                    l['KRS'] = f"REGON: {regon}"
                if full_addr and not l['Adres']:
                    l['Adres'] = full_addr
                if miasto and not l['Miasto']:
                    l['Miasto'] = miasto
                if woj and not l['Województwo']:
                    l['Województwo'] = woj.capitalize()

                ceidg_note = f"CEIDG status: {status} (od {data_rozp}). REGON: {regon}."
                if ceidg_note not in l['Uwagi']:
                    l['Uwagi'] = (l['Uwagi'] + ' ' + ceidg_note).strip()

                updated_count += 1
                print(f"  ✓ Verified: {res.get('nazwa')} | Owner: {imie} {nazwisko} | Status: {status}")
            else:
                l['Uwagi'] = (l['Uwagi'] + ' CEIDG: Podmiot nieodnaleziony w rejestrze JDG (możliwy Sp. z o.o./KRS).').strip()
                print(f"  ℹ️ Not found in CEIDG (likely Sp. z o.o./KRS entity).")

            # Enforce safe delay between requests
            if queried_count < batch_size:
                print(f"  ⏳ Waiting {delay_sec}s safety throttle...")
                time.sleep(delay_sec)

            if queried_count >= batch_size:
                print(f"\n✋ Batch limit of {batch_size} reached. Stopping current session.")
                break

    if updated_count > 0 or queried_count > 0:
        write_master_csv(leads)
        sync_html_dashboard(leads)
        print(f"\n🎉 Successfully processed {queried_count} companies ({updated_count} enriched via CEIDG API)!")

def main():
    parser = argparse.ArgumentParser(description="CEIDG API Batch Lead Enrichment")
    parser.add_argument("--batch-size", type=int, default=3, help="Number of companies to query in this batch")
    parser.add_argument("--delay", type=float, default=4.0, help="Delay in seconds between API requests")
    args = parser.parse_args()

    run_enrichment(batch_size=args.batch_size, delay_sec=args.delay)

if __name__ == "__main__":
    main()
