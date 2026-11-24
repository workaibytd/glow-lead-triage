"""
Replay 50 leads ke n8n webhook untuk evaluasi akurasi AI klasifikasi.

Cara pakai:
1. Pastikan workflow Glow Lead Triage (1) Published + n8n jalan
2. Run script ini di Terminal: python3 ~/replay_50_leads.py
3. Tunggu 50 leads terkirim (~3 menit dengan delay 3.5s)
4. Buka Sheet tab 'leads' → cek 50 row baru
5. Run script analyze_accuracy.py untuk bandingkan dengan answer key
"""

import urllib.request
import urllib.error
import json
import csv
import time
import os
from datetime import datetime

# Konfigurasi
WEBHOOK_URL = "http://localhost:5678/webhook/glow-wa-input"  # production URL
LEADS_FILE = "/home/z/my-project/download/50_leads_sample.csv"
DELAY_BETWEEN_LEADS = 3.5  # FIX: 3.5 detik supaya gak kena Groq rate limit (TPM 8000)

def send_lead(lead):
    """Kirim 1 lead ke n8n webhook. Return success/error."""
    # Format payload sesuai schema yang diharapkan Apps Script / direct webhook
    # Karena kita kirim ke webhook WA (channel=wa), kita kirim langsung field-nya
    payload = {
        "channel": lead["channel"],  # wa/ig/leadads
        "nama": lead["nama"],
        "kontak": lead["kontak"],
        "budget": lead["budget"],
        "pesan": lead["pesan"],
        "timestamp": lead["timestamp"]
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode("utf-8")
    except Exception as e:
        return False, 0, str(e)

def main():
    print(f"=" * 60)
    print(f"Replay 50 Leads - Glow Lead Triage")
    print(f"=" * 60)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Leads file: {LEADS_FILE}")
    print(f"Delay between leads: {DELAY_BETWEEN_LEADS}s")
    print()
    
    # Cek file leads ada
    if not os.path.exists(LEADS_FILE):
        print(f"ERROR: File {LEADS_FILE} tidak ditemukan")
        return
    
    # Baca CSV leads
    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"Total leads to send: {len(leads)}")
    print()
    
    # Send tiap lead
    success = 0
    failed = 0
    failed_leads = []
    
    for i, lead in enumerate(leads, 1):
        print(f"[{i:2}/50] Sending: {lead['nama'][:20]} | {lead['channel']:8} | {lead['pesan'][:50]}...")
        
        ok, status, response = send_lead(lead)
        
        if ok:
            print(f"        ✅ HTTP {status}")
            success += 1
        else:
            print(f"        ❌ HTTP {status}: {response[:100]}")
            failed += 1
            failed_leads.append({
                "index": i,
                "nama": lead["nama"],
                "error": response[:200]
            })
        
        # Delay supaya gak kena rate limit Groq (TPM 8000)
        if i < len(leads):
            time.sleep(DELAY_BETWEEN_LEADS)
    
    print()
    print(f"=" * 60)
    print(f"RESULT")
    print(f"=" * 60)
    print(f"Total sent: {len(leads)}")
    print(f"Success:    {success}")
    print(f"Failed:     {failed}")
    print()
    
    if failed_leads:
        print("Failed leads:")
        for fl in failed_leads:
            print(f"  #{fl['index']} {fl['nama']}: {fl['error'][:100]}")
    
    print()
    print("NEXT STEPS:")
    print("1. Tunggu 1-2 menit supaya semua lead selesai di-process n8n")
    print("2. Buka Sheet 'Glow-Lead-Multi-Channel-DB' → tab 'leads'")
    print("3. Cek 50 row baru muncul dengan kolom kategori/alasan/score terisi")
    print("4. Run script analyze_accuracy.py untuk evaluasi akurasi")

if __name__ == "__main__":
    main()
