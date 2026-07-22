#!/usr/bin/env python3
"""
Background File Watcher for Real-Time B2B Dashboard Synchronization
-------------------------------------------------------------------
Monitors 07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv for any edits/saves
and automatically updates DASH-Katalog-Leadow-B2B-PL.html in real time.
"""

import sys
import os
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYNC_SCRIPT = os.path.join(SCRIPT_DIR, "sync_b2b_leads.py")
CSV_PATH = "/Users/apple/Documents/Docs/Bills/Research/BILLS-SMOKS-Research-2026/07-MASTER-Katalog-Wszystkich-Leadow-B2B-PL.csv"

def get_mtime():
    if os.path.exists(CSV_PATH):
        return os.path.getmtime(CSV_PATH)
    return 0

def run_sync():
    print(f"[{time.strftime('%H:%M:%S')}] ⚡ Change detected in Master CSV! Triggering Dashboard Sync...")
    try:
        res = subprocess.run([sys.executable, SYNC_SCRIPT, "--sync-only"], capture_output=True, text=True)
        print(res.stdout.strip())
        if res.stderr:
            print("Stderr:", res.stderr.strip())
    except Exception as e:
        print(f"Error executing sync: {e}")

def main():
    print("==========================================================")
    print(" 🔄 BILLS B2B Master CSV -> HTML Dashboard Auto-Sync Watcher")
    print("==========================================================")
    print(f" Monitoring: {CSV_PATH}")
    print(" Edit and save the CSV file at any time to auto-update HTML.")
    print(" Press Ctrl+C to stop watching.\n")

    last_mtime = get_mtime()
    
    while True:
        try:
            time.sleep(1.0)
            current_mtime = get_mtime()
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                run_sync()
        except KeyboardInterrupt:
            print("\nStopped watcher process.")
            sys.exit(0)

if __name__ == "__main__":
    main()
