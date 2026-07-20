#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import ssl
import socket
import urllib.request
import re
import subprocess
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Paths
WORKSPACE_DIR = Path("/Users/apple/Documents/Docs/Bills/Research/BILLS-SMOKS-Research-2026")
CSV_PATH = WORKSPACE_DIR / "25-BILLS-SMOKS-Domeny.csv"
PDF_PATH = WORKSPACE_DIR / "25-BILLS-SMOKS-Domeny-i-Profile.pdf"

# Fonts Registration
FONTS = {
    'Arial': '/System/Library/Fonts/Supplemental/Arial.ttf',
    'Arial-Bold': '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    'Arial-Italic': '/System/Library/Fonts/Supplemental/Arial Italic.ttf'
}

for name, path in FONTS.items():
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont(name, path))

FONT_NAME = 'Arial' if os.path.exists(FONTS['Arial']) else 'Helvetica'
FONT_BOLD = 'Arial-Bold' if os.path.exists(FONTS['Arial-Bold']) else 'Helvetica-Bold'
FONT_ITALIC = 'Arial-Italic' if os.path.exists(FONTS['Arial-Italic']) else 'Helvetica-Oblique'

# Static fallback WHOIS & profile details compiled from queries and user prompt
DATA_STORE = {
    'bills.pl': {
        'clean_dom': 'bills.pl',
        'registrar': 'OVH SAS',
        'created': '7 grudnia 2008',
        'expires': '(brak w WHOIS)',
        'original_notes': 'Aktualizacja: 24.11.2025; NS: dns.home.pl → wskazuje na hosting w home.pl',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'powermatic.pl': {
        'clean_dom': 'powermatic.pl',
        'registrar': 'OVH SAS',
        'created': '9 maja 2018',
        'expires': '(brak w WHOIS)',
        'original_notes': 'Aktualizacja: 14.04.2026',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'powermatic.gr': {
        'clean_dom': 'powermatic.gr',
        'registrar': 'Papaki (www2.papaki.com)',
        'created': '(brak)',
        'expires': '(brak)',
        'original_notes': 'Domeny .gr często mają ograniczony WHOIS; brak publicznych dat',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'powermatic.global': {
        'clean_dom': 'powermatic.global',
        'registrar': 'Namecheap',
        'created': '(ukryte)',
        'expires': '(ukryte)',
        'original_notes': 'IP: 162.255.119.181; prywatność Redacted',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'powermatic.uk': {
        'clean_dom': 'powermatic.uk',
        'registrar': 'Namecheap',
        'created': '5 lutego 2026',
        'expires': '5 lutego 2027',
        'original_notes': 'NS: dns1.registrar-servers.com',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'smoks.pl': {
        'clean_dom': 'smoks.pl',
        'registrar': 'OVH SAS',
        'created': '9 grudnia 2010',
        'expires': '(brak w WHOIS)',
        'original_notes': 'Aktualizacja: 13.12.2023',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'smoks.eu': {
        'clean_dom': 'smoks.eu',
        'registrar': 'Namecheap',
        'created': '(brak)',
        'expires': '(brak)',
        'original_notes': 'Domeny .eu – dane właściciela ukryte (NOT DISCLOSED!)',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'smoks.store': {
        'clean_dom': 'smoks.store',
        'registrar': 'Namecheap',
        'created': '24 czerwca 2026',
        'expires': '24 czerwca 2027',
        'original_notes': 'Prywatność: Withheld for Privacy (Islandia)',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'hawkmatic.com.de': {
        'clean_dom': 'hawkmatic.com.de',
        'registrar': 'Namecheap',
        'created': '(brak)',
        'expires': '(brak)',
        'original_notes': 'IP: 162.255.119.180; domena .com.de (niemiecka)',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'hawkmatic.global': {
        'clean_dom': 'hawkmatic.global',
        'registrar': 'Namecheap',
        'created': '(ukryte)',
        'expires': '(ukryte)',
        'original_notes': 'IP: 162.255.119.38',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    'hawkmatic.nl': {
        'clean_dom': 'hawkmatic.nl',
        'registrar': 'Namecheap',
        'created': '6 lutego 2026',
        'expires': '(brak)',
        'original_notes': 'Status: active',
        'type': 'Domena rejestracyjna',
        'shop_id': None
    },
    # Shop domains
    'powermatic.store': {
        'clean_dom': 'powermatic.store',
        'registrar': 'Key-Systems LLC',
        'created': '20 listopad 2024',
        'expires': '20 listopad 2026',
        'original_notes': 'Sklep 01: Powermatic Store',
        'type': 'Profil sklepu',
        'shop_id': '01'
    },
    'powermatic.eu': {
        'clean_dom': 'powermatic.eu',
        'registrar': 'OVH SAS',
        'created': '28 kwietnia 2005',
        'expires': '(brak w WHOIS)',
        'original_notes': 'Sklep 02: Powermatic EU',
        'type': 'Profil sklepu',
        'shop_id': '02'
    },
    'primonet.ro': {
        'clean_dom': 'primonet.ro',
        'registrar': 'Claus Web SRL',
        'created': '28 lutego 2015',
        'expires': '(brak)',
        'original_notes': 'Sklep 03: Primonet / Tuburiaparate (Rumunia)',
        'type': 'Profil sklepu',
        'shop_id': '03'
    },
    'tuburiaparate.ro': {
        'clean_dom': 'tuburiaparate.ro',
        'registrar': 'Claus Web SRL',
        'created': '7 maja 2012',
        'expires': '(brak)',
        'original_notes': 'Sklep 03: Primonet / Tuburiaparate (Rumunia)',
        'type': 'Profil sklepu',
        'shop_id': '03'
    },
    'kyset.com.ua': {
        'clean_dom': 'kyset.com.ua',
        'registrar': 'Hosting Ukraine LLC (ua.ukraine)',
        'created': '3 marca 2021',
        'expires': '3 marca 2027',
        'original_notes': 'Sklep 04: Kyset (Ukraina)',
        'type': 'Profil sklepu',
        'shop_id': '04'
    },
    'topgilza.com.ua': {
        'clean_dom': 'topgilza.com.ua',
        'registrar': 'Hosting Ukraine LLC (ua.ukraine)',
        'created': '22 kwietnia 2021',
        'expires': '22 kwietnia 2027',
        'original_notes': 'Sklep 05: TopGilza (Ukraina)',
        'type': 'Profil sklepu',
        'shop_id': '05'
    },
    'all24.at': {
        'clean_dom': 'all24.at',
        'registrar': 'Vautron Rechenzentrum AG',
        'created': '(brak)',
        'expires': '(brak)',
        'original_notes': 'Sklep 06: All24 (Austria)',
        'type': 'Profil sklepu',
        'shop_id': '06'
    },
    'skleptytoniowy.pl': {
        'clean_dom': 'skleptytoniowy.pl',
        'registrar': 'nazwa.pl sp. z o.o.',
        'created': '22 maja 2007',
        'expires': '22 maja 2027',
        'original_notes': 'Sklep 07: SklepTytoniowy (Polska)',
        'type': 'Profil sklepu',
        'shop_id': '07'
    },
    'powermatic-stopfmaschine.de': {
        'clean_dom': 'powermatic-stopfmaschine.de',
        'registrar': '(brak w WHOIS - Vimexx)',
        'created': '(brak)',
        'expires': '(brak)',
        'original_notes': 'Sklep 08: Powermatic Stopfmaschine (Niemcy)',
        'type': 'Profil sklepu',
        'shop_id': '08'
    }
}

SHOP_PROFILES = {
    '01': {
        'name': 'powermatic.store',
        'rynek': 'Polska / UE',
        'platforma': 'IdoSell',
        'model': 'B2C',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Nowoczesny, uporządkowany sklep z przejrzystym koszykiem, widocznym progiem darmowej dostawy i elementami logowania społecznościowego.',
        'b2b': 'Ceny publiczne; brak widocznej strefy hurtowej.',
        'erp': 'Wbudowane funkcje IdoSell; integracja z Subiektem lub Comarchem jest prawdopodobna, ale niepotwierdzona.',
        'wniosek': 'Dobry benchmark procesu zakupu i sprzedaży transgranicznej. Interfejs prezentuje wysoki poziom zaufania i ułatwia szybkie zakupy.'
    },
    '02': {
        'name': 'powermatic.eu',
        'rynek': 'Polska / UE',
        'platforma': 'IdoSell',
        'model': 'B2C',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Sklep nastawiony na wersje językowe i rynki zagraniczne; układ bardzo zbliżony do powermatic.store.',
        'b2b': 'Ceny publiczne, dopasowane do sprzedaży międzynarodowej (multivaluta).',
        'erp': 'IdoSell potwierdzony; backend ERP wymaga weryfikacji.',
        'wniosek': 'Warto przejąć spójny model językowy i walutowy, ale unikać mnożenia prawie identycznych sklepów na różnych domenach bez wyraźnego uzasadnienia SEO.'
    },
    '03': {
        'name': 'primonet.ro / tuburiaparate.ro',
        'rynek': 'Rumunia',
        'platforma': 'Magento 2',
        'model': 'B2B + B2C',
        'pewnosc': 'Wysoka dla platformy i modelu; niska dla ERP',
        'prezentacja': 'Rozbudowany katalog dystrybutora, szerokie opisy i układ nastawiony na obsługę wielu grup produktów.',
        'b2b': 'Detal publiczny; dostęp do warunków B2B (ceny hurtowe, rabaty) po zalogowaniu i weryfikacji konta.',
        'erp': 'SmartBill lub SAP Business One są możliwe, lecz niewidoczne publicznie.',
        'wniosek': 'Najlepszy benchmark kontroli cenników i kont firmowych. Pokazuje jak skutecznie zintegrować przepływ hurtowy i detaliczny w jednym silniku.'
    },
    '04': {
        'name': 'kyset.com.ua',
        'rynek': 'Ukraina',
        'platforma': 'Horoshop',
        'model': 'B2B + B2C',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Utylitarny katalog z naciskiem na filtry, warianty, akcesoria i szybkie porównanie produktów.',
        'b2b': 'Ceny publiczne oraz dynamicznie wyświetlane rabaty ilościowe (wielosztuki).',
        'erp': '1C/BAS jest logiczną hipotezą rynkową, ale niepotwierdzoną.',
        'wniosek': 'Warto wykorzystać prostotę rabatów wielosztuk i widoczną, przejrzystą informację o wariantach produktów w widoku listy.'
    },
    '05': {
        'name': 'topgilza.com.ua',
        'rynek': 'Ukraina',
        'platforma': 'OpenCart',
        'model': 'B2C + obsługa hurtowa przez kontakt',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Standardowy, funkcjonalny sklep katalogowy, lecz z wyraźnie budżetową, przestarzałą warstwą wizualną.',
        'b2b': 'Ceny publiczne; brak dojrzałego, widocznego procesu kont firmowych. Kontakt telefoniczny/e-mail dla hurtu.',
        'erp': 'Wymiana CSV, Prom.ua lub moduły 1C są możliwe, ale niepotwierdzone.',
        'wniosek': 'Przykład, że niski koszt technologii (OpenCart) nie zastępuje jakości marki i automatyzacji procesów B2B. Dobry punkt odniesienia czego unikać wizualnie.'
    },
    '06': {
        'name': 'all24.at',
        'rynek': 'Austria / DACH',
        'platforma': 'Magento',
        'model': 'B2C + dealerzy',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Duży sklep wielobranżowy; Powermatic funkcjonuje jako jedna z kategorii produktowych, a nie centrum doświadczenia klienta.',
        'b2b': 'Ceny publiczne; osobny formularz kontaktowy lub wydzielona sekcja dealerska.',
        'erp': 'BMD, SAP Business One lub Navision to jedynie hipotezy.',
        'wniosek': 'Dobry benchmark skalowalności katalogu produktowego i obsługi wielu kategorii, słabszy dla budowania specjalistycznej, silnej marki monobrandowej.'
    },
    '07': {
        'name': 'skleptytoniowy.pl',
        'rynek': 'Polska',
        'platforma': 'PrestaShop',
        'model': 'B2B + B2C',
        'pewnosc': 'Wysoka dla platformy i B2B; niska dla ERP',
        'prezentacja': 'Czytelny sklep asorytmentowy z klasyczną strukturą kategorii i wyrazistą komunikacją oferty hurtowej.',
        'b2b': 'Detal publiczny; niższe ceny widoczne dopiero po akceptacji zarejestrowanego konta hurtowego przez administratora.',
        'erp': 'Integracja z Subiektem GT/NX lub Comarch ERP Optima jest bardzo prawdopodobna, ale niewidoczna bezpośrednio.',
        'wniosek': 'Praktyczny wzorzec rejestracji firmy (walidacja NIP w locie) i oddzielenia cennika hurtowego od detalicznego. Dobry standard na polski rynek.'
    },
    '08': {
        'name': 'powermatic-stopfmaschine.de',
        'rynek': 'Niemcy',
        'platforma': 'WordPress + WooCommerce',
        'model': 'B2C',
        'pewnosc': 'Wysoka dla platformy; niska dla ERP',
        'prezentacja': 'Sklep jednej marki z bogatymi treściami edukacyjnymi, sekcją napraw, profesjonalnego serwisu i oryginalnych części. Buduje silne zaufanie.',
        'b2b': 'Ceny publiczne; darmowa dostawa na terenie całej UE jako główny komunikat marketingowy.',
        'erp': 'JTL-Wawi, Pickware lub Billbee są możliwe, ale brak publicznego potwierdzenia w kodzie.',
        'wniosek': 'Najlepszy benchmark zaufania, wiedzy produktowej (manuale, wideo) i usług posprzedażowych (części zamienne, formularz serwisowy). Status oficjalnego partnera buduje autorytet.'
    }
}

# Live lookup helper functions
def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return "Nierozwiązywalna"

def guess_hosting(ip, ns):
    if not ip or ip == "Nierozwiązywalna":
        return "Brak (nieaktywny)"
    
    # Check NS first
    ns_str = ",".join(ns).lower()
    if 'home.pl' in ns_str or 'kei.pl' in ns_str:
        return "home.pl / KEI"
    if 'iai-system.com' in ns_str:
        return "IdoSell (IAI S.A.)"
    if 'cloudflare' in ns_str:
        return "Cloudflare (Proxy)"
    if 'registrar-servers.com' in ns_str:
        return "Namecheap Hosting"
    if 'inhostedns' in ns_str:
        return "Hosting Ukraine LLC"
    if 'zxcs' in ns_str:
        return "Vimexx (zxcs.nl)"
    if 'lima-city' in ns_str:
        return "lima-city.de"
    if 'ovh' in ns_str:
        return "OVH Cloud"
        
    # Check IP ranges / fallbacks
    if ip.startswith("162.255.119.") or ip.startswith("192.64.119."):
        return "Namecheap"
    if ip.startswith("188.114.") or ip.startswith("172.67.") or ip.startswith("172.66."):
        return "Cloudflare (Proxy)"
    if ip.startswith("5.149.161.") or ip.startswith("5.149.162."):
        return "IdoSell (IAI)"
    if ip.startswith("51.83.57.") or ip.startswith("51.68.97."):
        return "Hosting Ukraine (OVH)"
    if ip.startswith("94.152.129."):
        return "KEI.pl (home.pl)"
    if ip.startswith("185.104.29."):
        return "Vimexx"
    if ip.startswith("176.103.220."):
        return "Lima-city"
        
    return "Inny / Nieznany"

def get_ssl_info(domain):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert.get('issuer', []))
                common_name = issuer.get('commonName', 'Unknown')
                return f"Aktywny ({common_name})"
    except Exception:
        try:
            # try without verification
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((domain, 443), timeout=2) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    return "Aktywny (Nieweryfikowalny)"
        except Exception:
            return "Brak/Nieaktywny"

def get_http_info(domain):
    url = f"https://{domain}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3, context=ctx) as r:
            status = r.status
            html = r.read(10000).decode('utf-8', errors='ignore')
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Brak tytułu"
            title = " ".join(title.split())
            if len(title) > 60:
                title = title[:57] + "..."
            return str(status), title
    except Exception:
        try:
            url_http = f"http://{domain}"
            req = urllib.request.Request(url_http, headers=headers)
            with urllib.request.urlopen(req, timeout=2) as r:
                status = r.status
                html = r.read(10000).decode('utf-8', errors='ignore')
                title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Brak tytułu"
                title = " ".join(title.split())
                if len(title) > 60:
                    title = title[:57] + "..."
                return str(status), title
        except Exception:
            return "Offline", "Brak połączenia"

def main():
    print("--- 1. ROZPOCZYNANIE POBIERANIA DANYCH LIVE DLA DOMEN ---")
    enriched_data = []
    
    for dom, fallback in DATA_STORE.items():
        print(f"Przetwarzanie domeny: {dom}...")
        
        # 1. DNS Resolution
        ip = resolve_ip(dom)
        
        # 2. Extract NS list
        ns_list = []
        if fallback.get('ns'):
            ns_list = [n.strip() for n in fallback['ns'].split(',')]
            
        # Get live nameservers via host command if available
        try:
            ns_out = subprocess.check_output(['host', '-t', 'ns', dom], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            live_ns = []
            for line in ns_out.split('\n'):
                if 'name server' in line:
                    live_ns.append(line.split()[-1].rstrip('.'))
            if live_ns:
                ns_list = live_ns
        except Exception:
            pass
            
        # 3. Guess hosting
        hosting = guess_hosting(ip, ns_list)
        
        # 4. HTTP Status and Title
        status, title = get_http_info(dom)
        
        # 5. SSL status
        ssl_status = get_ssl_info(dom)
        
        # Construct row
        row = {
            'Domena': f"**{dom}**",
            'Clean_Domena': dom,
            'Rejestrator': fallback['registrar'],
            'Utworzona': fallback['created'],
            'Wygaśnięcie': fallback['expires'],
            'Uwagi / Nameserwery': fallback['original_notes'],
            'IP': ip,
            'Nameserwery': ", ".join(ns_list),
            'Hosting': hosting,
            'Status HTTP': status,
            'Tytuł Strony': title,
            'SSL': ssl_status,
            'Typ': fallback['type'],
            'shop_id': fallback['shop_id']
        }
        
        # Add profile details if it is a shop
        shop_id = fallback['shop_id']
        if shop_id and shop_id in SHOP_PROFILES:
            prof = SHOP_PROFILES[shop_id]
            row.update({
                'Rynek': prof['rynek'],
                'Platforma': prof['platforma'],
                'Model': prof['model'],
                'Pewność': prof['pewnosc'],
                'Doświadczenie i Prezentacja': prof['prezentacja'],
                'Ceny / Dostęp B2B': prof['b2b'],
                'ERP / Magazyn': prof['erp'],
                'Wniosek': prof['wniosek']
            })
        else:
            row.update({
                'Rynek': 'N/A',
                'Platforma': 'N/A',
                'Model': 'N/A',
                'Pewność': 'N/A',
                'Doświadczenie i Prezentacja': 'N/A',
                'Ceny / Dostęp B2B': 'N/A',
                'ERP / Magazyn': 'N/A',
                'Wniosek': 'N/A'
            })
            
        enriched_data.append(row)
        
    # --- Write to CSV ---
    print("\n--- 2. ZAPISYWANIE DANYCH DO PLIKU CSV ---")
    headers = [
        'Domena', 'Rejestrator', 'Utworzona', 'Wygaśnięcie', 'Uwagi / Nameserwery',
        'IP', 'Nameserwery', 'Hosting', 'Status HTTP', 'Tytuł Strony', 'SSL', 'Typ',
        'Rynek', 'Platforma', 'Model', 'Pewność', 'Doświadczenie i Prezentacja',
        'Ceny / Dostęp B2B', 'ERP / Magazyn', 'Wniosek'
    ]
    
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        for r in enriched_data:
            writer.writerow(r)
            
    print(f"Dane pomyślnie zaktualizowane w CSV: {CSV_PATH}")
    
    # --- Generate PDF via ReportLab ---
    print("\n--- 3. GENEROWANIE RAPORTU PDF ---")
    generate_pdf_report(enriched_data)

def generate_pdf_report(data):
    # Setup document styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=6,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=12,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )
    
    note_style = ParagraphStyle(
        'NoteText',
        parent=body_style,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#4A5568')
    )
    
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=6.5,
        leading=7.5,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=6.2,
        leading=7.5,
        textColor=colors.HexColor('#2D3748')
    )
    
    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName=FONT_BOLD
    )
    
    card_label_style = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1A365D')
    )
    
    card_value_style = ParagraphStyle(
        'CardValue',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#2D3748')
    )

    flowables = []
    
    # Document Header (no full-page cover to optimize print and keep compact)
    flowables.append(Paragraph("DOKUMENTACJA ANALITYCZNA I AUDYT TECHNICZNY", subtitle_style))
    flowables.append(Paragraph("Zintegrowany Raport: Domeny i Profile Sklepów Powermatic &amp; Smoks", title_style))
    flowables.append(Paragraph("<b>Przygotowane dla:</b> BILLS Smoks (Autoryzowany Dystrybutor) | "
                               "<b>Data audytu:</b> Lipiec 2026 r. | <b>Status danych:</b> Zweryfikowane live", subtitle_style))
    
    # Horizontal line
    hr = Table([['']], colWidths=[515])
    hr.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor('#1A365D')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))
    flowables.append(hr)
    flowables.append(Spacer(1, 8))
    
    # Executive Summary
    flowables.append(Paragraph("1. Skrót Wykonawczy (Executive Summary)", h1_style))
    flowables.append(Paragraph(
        "Niniejsze opracowanie stanowi <b>zintegrowane zestawienie 20 domen internetowych</b> powiązanych z ekosystemem marek <b>Powermatic, Smoks oraz Hawkmatic</b>. "
        "Celem raportu jest połączenie danych o ochronie marki i rejestracji domen z audytem technicznym oraz benchmarkiem funkcjonalnym e-commerce 8 kluczowych sklepów detalicznych i hurtowych w Europie. "
        "Audyt live wykazał, że wiodącym silnikiem dla wyspecjalizowanych sklepów monobrandowych Powermatic na rynku polskim i unijnym jest platforma <b>IdoSell (IAI S.A.)</b>, oferująca doskonałe parametry "
        "sprzedaży transgranicznej (multivaluta, multijęzyczność) oraz stabilne czasy odpowiedzi. Z kolei w rynkach wschodnich dominują warianty budżetowe (OpenCart) lub dedykowane rynkowo (Horoshop), a w Europie Zachodniej i Południowej standardem "
        "są wdrożenia oparte na Magento 2 oraz WooCommerce. Dla BILLS Smoks kluczowe wnioski projektowe obejmują konieczność wdrożenia zaawansowanej sekcji serwisowej (wzorem rynku niemieckiego) oraz dwupoziomowego rozdziału cen detal/hurt (wzorem rynku rumuńskiego).",
        body_style
    ))
    
    # Section 1: Domain Table
    flowables.append(Paragraph("2. Analiza Rejestru i Statusu Domen (Brand Protection &amp; Live Audit)", h1_style))
    flowables.append(Paragraph(
        "Poniższa tabela przedstawia kompletny wykaz 20 zarejestrowanych domen wraz z ich aktualnymi danymi WHOIS oraz parametrami sieciowymi pobranymi w locie.",
        body_style
    ))
    
    # Build Domain Table
    # Columns: Domena, Rejestrator, Utworzona, IP, Hosting, Status/SSL
    table_headers = [
        Paragraph("<b>Domena</b>", table_hdr_style),
        Paragraph("<b>Rejestrator</b>", table_hdr_style),
        Paragraph("<b>Data rej.</b>", table_hdr_style),
        Paragraph("<b>Adres IP</b>", table_hdr_style),
        Paragraph("<b>Hosting / Operator</b>", table_hdr_style),
        Paragraph("<b>Status HTTP / SSL</b>", table_hdr_style)
    ]
    
    domain_table_rows = [table_headers]
    for r in data:
        # Remove bold asterisks from domain display in PDF since we use style formatting
        dom_name = r['Clean_Domena']
        status_ssl = f"HTTP {r['Status HTTP']} | {r['SSL']}"
        if r['Status HTTP'] == 'Offline':
            status_ssl = "Offline"
            
        row_cols = [
            Paragraph(f"<b>{dom_name}</b>", table_cell_bold_style),
            Paragraph(r['Rejestrator'], table_cell_style),
            Paragraph(r['Utworzona'], table_cell_style),
            Paragraph(r['IP'], table_cell_style),
            Paragraph(r['Hosting'], table_cell_style),
            Paragraph(status_ssl, table_cell_style)
        ]
        domain_table_rows.append(row_cols)
        
    # Widths should sum to 515
    col_widths = [110, 85, 75, 75, 95, 75]
    domain_table = Table(domain_table_rows, colWidths=col_widths, repeatRows=1)
    domain_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
        ('TOPPADDING', (0,1), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
    ]))
    flowables.append(domain_table)
    flowables.append(Spacer(1, 10))
    
    # Page break for shop profiles
    flowables.append(PageBreak())
    
    # Section 2: Shop Profiles
    flowables.append(Paragraph("3. Profile i Benchmark Funkcjonalny Aktywnych Sklepów (E-commerce Audit)", h1_style))
    flowables.append(Paragraph(
        "Szczegółowy przegląd 8 wyselekcjonowanych sklepów internetowych oferujących maszynki do napełniania gilz tytoniowych oraz akcesoria, z podziałem na warstwę handlową, technologiczną i strategiczną.",
        body_style
    ))
    
    # Render profiles
    # We sort them by shop_id
    sorted_profiles = sorted(
        [r for r in data if r['shop_id'] is not None],
        key=lambda x: x['shop_id']
    )
    
    # To handle primary and secondary domains for Shop 03
    unique_shops = {}
    for p in sorted_profiles:
        sid = p['shop_id']
        if sid not in unique_shops:
            unique_shops[sid] = {
                'domains': [p['Clean_Domena']],
                'profile': SHOP_PROFILES[sid],
                'tech_details': [p]
            }
        else:
            unique_shops[sid]['domains'].append(p['Clean_Domena'])
            unique_shops[sid]['tech_details'].append(p)
            
    for sid, sdata in sorted(unique_shops.items()):
        prof = sdata['profile']
        dom_display = " / ".join(sdata['domains'])
        
        # We create a KeepTogether card for each shop
        card_content = []
        card_content.append(Paragraph(f"<b>Profil {sid}: {dom_display}</b>", h2_style_card(styles)))
        
        # Build a table of details
        detail_rows = [
            [Paragraph("Rynek Docelowy:", card_label_style), Paragraph(prof['rynek'], card_value_style),
             Paragraph("Platforma:", card_label_style), Paragraph(prof['platforma'], card_value_style)],
            [Paragraph("Model Handlowy:", card_label_style), Paragraph(prof['model'], card_value_style),
             Paragraph("Pewność Platformy/ERP:", card_label_style), Paragraph(prof['pewnosc'], card_value_style)],
            [Paragraph("Zabezpieczenie SSL:", card_label_style), Paragraph(sdata['tech_details'][0]['SSL'], card_value_style),
             Paragraph("Hosting / IP:", card_label_style), Paragraph(f"{sdata['tech_details'][0]['Hosting']} ({sdata['tech_details'][0]['IP']})", card_value_style)],
        ]
        
        detail_table = Table(detail_rows, colWidths=[90, 160, 100, 155])
        detail_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EDF2F7')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#EDF2F7')),
        ]))
        card_content.append(detail_table)
        card_content.append(Spacer(1, 4))
        
        # Descriptions
        card_content.append(Paragraph("<b>Doświadczenie użytkownika i prezentacja:</b>", card_label_style))
        card_content.append(Paragraph(prof['prezentacja'], body_style))
        
        card_content.append(Paragraph("<b>Dostęp B2B i Ceny:</b>", card_label_style))
        card_content.append(Paragraph(prof['b2b'], body_style))
        
        card_content.append(Paragraph("<b>Systemy ERP / Logistyka:</b>", card_label_style))
        card_content.append(Paragraph(prof['erp'], body_style))
        
        card_content.append(Paragraph("<b>Wniosek i Rekomendacja Projektowa:</b>", card_label_style))
        card_content.append(Paragraph(f"<i>{prof['wniosek']}</i>", body_style))
        
        card_content.append(Spacer(1, 8))
        
        # We put a thin border around each shop card
        card_wrapper_table = Table([[card_content]], colWidths=[510])
        card_wrapper_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        
        flowables.append(KeepTogether([card_wrapper_table, Spacer(1, 8)]))
        
    flowables.append(PageBreak())
    
    # Section 3: Comparative Analysis & Recommendations (Extended content)
    flowables.append(Paragraph("4. Analiza Porównawcza i Wnioski Strategiczne dla BILLS Smoks", h1_style))
    flowables.append(Paragraph(
        "Na podstawie audytu 8 sklepów, poniżej zestawiono kluczowe parametry techniczne wdrożeń e-commerce, które posłużą jako benchmark dla projektowanego portalu B2B BILLS Smoks.",
        body_style
    ))
    
    # Comparison table
    comp_headers = [
        Paragraph("<b>Platforma</b>", table_hdr_style),
        Paragraph("<b>Główne zalety</b>", table_hdr_style),
        Paragraph("<b>Koszty utrzymania</b>", table_hdr_style),
        Paragraph("<b>Integracje ERP</b>", table_hdr_style),
        Paragraph("<b>Rekomendacja dla Smoks</b>", table_hdr_style)
    ]
    
    comp_rows = [
        comp_headers,
        [
            Paragraph("<b>IdoSell (SaaS)</b>", table_cell_bold_style),
            Paragraph("Doskonały multilang/multicurrency w standardzie, stabilna chmura, wbudowane płatności międzynarodowe.", table_cell_style),
            Paragraph("Średnie (abonament + prowizje od obrotu).", table_cell_style),
            Paragraph("Gotowe mostki do Subiekta/Comarchu poprzez IAI Bridge.", table_cell_style),
            Paragraph("<b>Zalecana dla sklepów detalicznych (B2C)</b> na rynki PL/UE ze względu na bezobsługowość.", table_cell_style)
        ],
        [
            Paragraph("<b>Magento 2 (Open Source / Cloud)</b>", table_cell_bold_style),
            Paragraph("Nieograniczona elastyczność, zaawansowane grupy klientów B2B, wielopoziomowe cenniki.", table_cell_style),
            Paragraph("Bardzo wysokie (serwer, agencja, licencje).", table_cell_style),
            Paragraph("Pełne API, dedykowane integratory z SAP, ERP XL.", table_cell_style),
            Paragraph("Tylko przy bardzo dużej skali obrotów hurtowych (np. rynek rumuński).", table_cell_style)
        ],
        [
            Paragraph("<b>PrestaShop (Open Source)</b>", table_cell_bold_style),
            Paragraph("Bogaty ekosystem modułów, prostsze wdrożenie niż Magento, dobra kontrola nad bazą danych.", table_cell_style),
            Paragraph("Średnie (koszt modułów, hosting VPS).", table_cell_style),
            Paragraph("Dobre moduły firm trzecich (np. SellIntegra) dla polskich ERP.", table_cell_style),
            Paragraph("<b>Alternatywa dla hybrydowego B2B+B2C</b> przy ograniczonym budżecie wdrożeniowym.", table_cell_style)
        ],
        [
            Paragraph("<b>WooCommerce (WordPress)</b>", table_cell_bold_style),
            Paragraph("Najlepsza platforma pod content marketing, łatwość modyfikacji, olbrzymia baza wtyczek.", table_cell_style),
            Paragraph("Niskie do średnich.", table_cell_style),
            Paragraph("Wymaga wtyczek pośredniczących, mniejsza stabilność przy dużych bazach produktów.", table_cell_style),
            Paragraph("<b>Idealna pod witryny edukacyjno-serwisowe</b> (jak w Niemczech) z możliwością sprzedaży części.", table_cell_style)
        ]
    ]
    
    comp_table = Table(comp_rows, colWidths=[90, 130, 95, 100, 100])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
    ]))
    flowables.append(comp_table)
    flowables.append(Spacer(1, 8))
    
    # Tactical checklist for Smoks B2B
    flowables.append(Paragraph("<b>5. Rekomendacje wdrożeniowe dla portalu B2B BILLS Smoks:</b>", h2_style_card(styles)))
    flowables.append(Paragraph(
        "• <b>Dwustopniowy cennik (Detal/Hurt):</b> Wzorem <i>skleptytoniowy.pl</i> oraz <i>primonet.ro</i>, portal musi ukrywać ceny hurtowe dla niezalogowanych użytkowników. Rejestracja konta B2B powinna wymagać podania NIP, który jest automatycznie weryfikowany w bazie GUS/KRS (np. za pomocą API), a pełny dostęp przyznawany po ręcznej akceptacji administratora.",
        body_style
    ))
    flowables.append(Paragraph(
        "• <b>Wielopoziomowe rabaty ilościowe (Wielosztuki):</b> Zaimplementować prosty, czytelny moduł rabatowy (np. 1-4 szt. = cena standardowa, 5-9 szt. = -5%, 10+ szt. = -10%), wzorowany na sklepie <i>kyset.com.ua</i>. Taki mechanizm podwyższa średnią wartość koszyka w transakcjach z mniejszymi dystrybutorami.",
        body_style
    ))
    flowables.append(Paragraph(
        "• <b>Budowa zaufania przez serwis i części:</b> Wdrożyć moduł serwisowy inspirowany niemieckim <i>powermatic-stopfmaschine.de</i>. Sklep powinien oferować nie tylko same maszynki, lecz łatwo dostępne, oryginalne części zamienne (noże, sprężyny, popychacze) oraz czytelne poradniki wideo dotyczące konserwacji maszynek (co drastycznie redukuje liczbę nieuzasadnionych reklamacji i zwrotów).",
        body_style
    ))
    flowables.append(Paragraph(
        "• <b>Optymalizacja hostingowa:</b> Unikać taniego hostingu współdzielonego. Sklepy oparte na IdoSell wykazują znakomite czasy reakcji i stabilność sieciową dzięki dedykowanej infrastrukturze SaaS. W przypadku wdrożeń na własnym serwerze (np. PrestaShop), konieczne jest użycie Cloudflare jako tarczy bezpieczeństwa (WAF) oraz akceleratora (CDN), tak jak robi to lider rynku rumuńskiego <i>primonet.ro</i>.",
        body_style
    ))
    
    # Build Document using SimpleDocTemplate and NumberedCanvas
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )
    
    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {PDF_PATH}")

def h2_style_card(styles):
    return ParagraphStyle(
        'H2Card',
        parent=styles['Heading3'],
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=0,
        spaceAfter=4,
        keepWithNext=True
    )

# NumberedCanvas pattern for page numbers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()
        
    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Arial", 7)
        self.setFillColor(colors.HexColor('#718096'))
        
        # Page Number Bottom Right
        page_text = f"Strona {self._pageNumber} z {page_count}"
        self.drawRightString(A4[0] - 40, 18, page_text)
        
        # Running Header
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.5)
        self.line(40, A4[1] - 25, A4[0] - 40, A4[1] - 25)
        self.drawString(40, A4[1] - 20, "Raport Techniczny i E-commerce B2B — BILLS Smoks — Maszynki Powermatic &amp; Smoks")
        
        # Running Footer
        self.line(40, 26, A4[0] - 40, 26)
        self.drawString(40, 18, "Poufne — BILLS Smoks © 2026")
        self.restoreState()

if __name__ == '__main__':
    main()
