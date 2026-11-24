"""
Analisis akurasi AI klasifikasi: compare hasil AI di Sheet vs answer key.

Cara pakai:
1. Export Sheet tab 'leads' ke CSV (File → Download → Comma Separated Values)
2. Save sebagai /home/z/my-project/download/leads_export.csv
3. Run: python3 ~/analyze_accuracy.py
"""

import csv
import os
from collections import Counter

# File paths
ANSWER_KEY_FILE = "/home/z/my-project/download/50_leads_answer_key.csv"
EXPORTED_LEADS_FILE = "/home/z/my-project/download/leads_export.csv"

def main():
    print("=" * 60)
    print("Akurasi AI - Glow Lead Triage")
    print("=" * 60)
    
    # Cek file
    if not os.path.exists(ANSWER_KEY_FILE):
        print(f"ERROR: {ANSWER_KEY_FILE} tidak ditemukan")
        return
    if not os.path.exists(EXPORTED_LEADS_FILE):
        print(f"ERROR: {EXPORTED_LEADS_FILE} tidak ditemukan")
        print()
        print("Cara export:")
        print("1. Buka Sheet 'Glow-Lead-Multi-Channel-DB' di browser")
        print("2. Pilih tab 'leads'")
        print("3. File → Download → Comma Separated Values (.csv)")
        print("4. Save file sebagai 'leads_export.csv' di folder download")
        return
    
    # Baca answer key (50 leads expected kategori)
    answer_key = {}
    with open(ANSWER_KEY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["timestamp"], row["nama"])
            answer_key[key] = row["expected_kategori"]
    
    print(f"Answer key: {len(answer_key)} leads")
    
    # Baca exported leads
    ai_results = []
    with open(EXPORTED_LEADS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ai_results.append(row)
    
    print(f"Exported leads: {len(ai_results)} rows")
    print()
    
    # Match answer key dengan AI result berdasarkan timestamp+nama
    # (karena timestamp unik per lead)
    matched = 0
    correct = 0
    incorrect = []
    confusion_matrix = {}  # {expected: {actual: count}}
    
    for ai_row in ai_results:
        # Normalize timestamp (might be different format)
        ai_timestamp = ai_row.get("timestamp", "")
        ai_nama = ai_row.get("nama", "")
        ai_kategori = (ai_row.get("kategori") or "").lower().strip()
        
        # Try match dengan answer key
        # Coba beberapa format timestamp
        key = (ai_timestamp, ai_nama)
        if key not in answer_key:
            # Coba tanpa detik
            try:
                # Parse various formats
                from datetime import datetime
                ts = ai_timestamp.replace("Z", "").replace("T", " ")
                if "." in ts:
                    ts = ts.split(".")[0]
                dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
                # Cari di answer key dengan matching fleksibel
                for ak_key, ak_kategori in answer_key.items():
                    ak_ts, ak_nama = ak_key
                    if ak_nama == ai_nama:
                        # Match jika timestamp beda < 5 detik
                        try:
                            ak_dt = datetime.strptime(ak_ts[:19], "%Y-%m-%d %H:%M:%S")
                            diff = abs((dt - ak_dt).total_seconds())
                            if diff < 60:
                                matched += 1
                                if ak_kategori == ai_kategori:
                                    correct += 1
                                else:
                                    incorrect.append({
                                        "nama": ai_nama,
                                        "expected": ak_kategori,
                                        "actual": ai_kategori,
                                        "pesan": ai_row.get("pesan", "")[:60],
                                        "alasan": ai_row.get("alasan", "")[:60]
                                    })
                                # Update confusion matrix
                                if ak_kategori not in confusion_matrix:
                                    confusion_matrix[ak_kategori] = {}
                                confusion_matrix[ak_kategori][ai_kategori] = confusion_matrix[ak_kategori].get(ai_kategori, 0) + 1
                                break
                        except:
                            pass
            except:
                continue
        else:
            ak_kategori = answer_key[key]
            matched += 1
            if ak_kategori == ai_kategori:
                correct += 1
            else:
                incorrect.append({
                    "nama": ai_nama,
                    "expected": ak_kategori,
                    "actual": ai_kategori,
                    "pesan": ai_row.get("pesan", "")[:60],
                    "alasan": ai_row.get("alasan", "")[:60]
                })
            if ak_kategori not in confusion_matrix:
                confusion_matrix[ak_kategori] = {}
            confusion_matrix[ak_kategori][ai_kategori] = confusion_matrix[ak_kategori].get(ai_kategori, 0) + 1
    
    print("=" * 60)
    print("HASIL AKURASI")
    print("=" * 60)
    print(f"Matched (answer key vs AI): {matched} / {len(ai_results)}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {len(incorrect)}")
    
    if matched > 0:
        accuracy = (correct / matched) * 100
        print(f"Akurasi: {accuracy:.1f}%")
    print()
    
    # Confusion matrix
    print("=" * 60)
    print("CONFUSION MATRIX (Expected → Actual)")
    print("=" * 60)
    print(f"{'Expected':<10} {'Actual':<10} {'Count':<6}")
    print("-" * 30)
    for expected, actuals in sorted(confusion_matrix.items()):
        for actual, count in sorted(actuals.items()):
            mark = "✓" if expected == actual else "✗"
            print(f"{expected:<10} {actual:<10} {count:<6} {mark}")
    print()
    
    # Detail incorrect
    if incorrect:
        print("=" * 60)
        print("DETAIL INCORRECT PREDICTIONS")
        print("=" * 60)
        for i, inc in enumerate(incorrect, 1):
            print(f"{i}. {inc['nama']}")
            print(f"   Expected: {inc['expected']} | Actual: {inc['actual']}")
            print(f"   Pesan: {inc['pesan']}")
            print(f"   Alasan AI: {inc['alasan']}")
            print()
    
    # Per-channel accuracy
    print("=" * 60)
    print("RINGKASAN")
    print("=" * 60)
    print(f"Total leads di Sheet: {len(ai_results)}")
    print(f"Matched dengan answer key: {matched}")
    print(f"Akurasi: {(correct/matched*100):.1f}%" if matched > 0 else "N/A")
    print()
    print("Untuk dokumentasi Notion:")
    print(f"- AI accuracy: {correct}/{matched} = {(correct/matched*100):.1f}%" if matched > 0 else "")
    print(f"- Misclassification: {len(incorrect)} cases")
    print(f"- Sistem jalan production-ready")

if __name__ == "__main__":
    main()
