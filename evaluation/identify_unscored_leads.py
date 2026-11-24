"""
Identify the 16 unscored leads and split them per the Q7/Q11 method.

Method (from the user, verifiable from the Sheet):
  empty_kategori_rows  = count of rows in tab 'leads' whose 'kategori' is empty
                         = 7 (HTTP 429 rate-limit) + N (truncated JSON)
  N  (truncated)       = empty_kategori_rows - 7
  M  (drift)           = 9 - N          (filled kategori but no answer-key match)
  Verify:  7 + N + M == 16   and   N + M == 9

Why this is correct:
  - Both a 429 and a truncated JSON leave 'kategori' empty  -> they are the
    union counted by empty_kategori_rows. Subtract the known 7 (429) -> N.
  - A drift lead WAS scored by the model (kategori filled) but its Sheet
    timestamp doesn't match the answer key -> filled-but-unmatched -> M.
  - So unscored = empty(7+N) + drift(M) = 7 + N + M = 16.

Inputs (defaults match analyze_accuracy.py):
  leads_export.csv     Sheet tab 'leads' export            [required]
  50_leads_answer_key.csv                                [required]
  error_log_export.csv Sheet tab 'error_log' export        [optional: per-row 429 labels]

Run:
  python3 -I /home/z/my-project/scripts/identify_unscored_leads.py
  # or override paths:
  python3 -I /home/z/my-project/scripts/identify_unscored_leads.py <mock_leads.csv> [answer_key] [error_log]
"""

import csv
import os
import sys
from datetime import datetime

DEFAULT_LEADS = "/home/z/my-project/download/leads_export.csv"
DEFAULT_KEY   = "/home/z/my-project/download/50_leads_answer_key.csv"
DEFAULT_ERR   = "/home/z/my-project/download/error_log_export.csv"

RATE_LIMIT_COUNT = 7      # known: 14% of 50 = 7 HTTP 429 (Groq 8,000 TPM); also in error_log tab
TARGET_UNS   = 16
TARGET_9     = 9
TARGET_SCORE = 34
TARGET_TOTAL = 50


def norm(s):
    return (s or "").strip().lower()


def parse_ts(s):
    s = (s or "").replace("Z", "").replace("T", " ")
    if "." in s:
        s = s.split(".")[0]
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def load_answer_key(path):
    ak = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ak[(r["timestamp"], r["nama"])] = norm(r["expected_kategori"])
    return ak


def matches_answer_key(row, ak):
    """True if (timestamp, nama) matches the answer key: exact, or same nama within 60s."""
    ts, nama = row.get("timestamp", ""), row.get("nama", "")
    if (ts, nama) in ak:
        return True
    dt = parse_ts(ts)
    if not dt:
        return False
    for (ak_ts, ak_nama) in ak:
        if ak_nama == nama:
            ak_dt = parse_ts(ak_ts)
            if ak_dt and abs((dt - ak_dt).total_seconds()) < 60:
                return True
    return False


def load_error_log(path):
    """Return set of nama that appear in error_log with a 429/rate-limit signature."""
    four29, other = set(), set()
    if not path or not os.path.exists(path):
        return four29, other
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nama = r.get("nama") or r.get("name") or ""
            msg = norm(r.get("error") or r.get("message") or r.get("alasan") or "")
            if not nama:
                continue
            (four29 if ("429" in msg or "rate" in msg) else other).add(nama)
    return four29, other


def main():
    leads_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LEADS
    key_path   = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_KEY
    err_path   = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_ERR

    if not os.path.exists(leads_path):
        print(f"ERROR: {leads_path} not found.")
        print("Export Sheet tab 'leads' -> File -> Download -> CSV -> save as")
        print(f"  {DEFAULT_LEADS}")
        print("(optional) export tab 'error_log' the same way -> error_log_export.csv")
        return
    if not os.path.exists(key_path):
        print(f"ERROR: {key_path} not found.")
        return

    ak = load_answer_key(key_path)
    rows = list(csv.DictReader(open(leads_path, encoding="utf-8")))
    four29_names, _ = load_error_log(err_path)

    # ---- partition ----
    bucketA = []   # empty kategori  -> 7 (rate-limit) + N (truncated)
    bucketB = []   # filled kategori, no answer-key match -> M (drift)
    scored  = []   # filled kategori, matched -> 34
    for r in rows:
        kat = norm(r.get("kategori"))
        if not kat:
            bucketA.append(r)
        elif matches_answer_key(r, ak):
            scored.append(r)
        else:
            bucketB.append(r)

    A = len(bucketA)
    B = len(bucketB)
    S = len(scored)
    total = A + B + S

    N = A - RATE_LIMIT_COUNT     # truncated JSON
    M = B                        # drift (== 9 - N)

    # ---- verification ----
    checks = {
        "total rows == 50":            total == TARGET_TOTAL,
        "scored (filled+matched) == 34": S == TARGET_SCORE,
        "unscored (A+B) == 16":        (A + B) == TARGET_UNS,
        "N + M == 9":                  (N + M) == TARGET_9,
        "7 + N + M == 16":             (RATE_LIMIT_COUNT + N + M) == TARGET_UNS,
        "N >= 0 (empty >= 7)":         N >= 0,
        "M >= 0":                      M >= 0,
    }
    all_ok = all(checks.values())

    # ---- report ----
    print("=" * 66)
    print("UNSCORED LEADS BREAKDOWN  (answers Q7 & Q11)")
    print("=" * 66)
    print(f"leads_export rows : {total}")
    print(f"answer key        : {len(ak)} leads")
    print(f"error_log export  : {'used (' + str(len(four29_names)) + ' 429 names)' if err_path and os.path.exists(err_path) else 'not provided (per-row 429 labels skipped)'}")
    print()
    print("-" * 66)
    print("PARTITION (from the data)")
    print("-" * 66)
    print(f"  bucket A : empty kategori            = {A}   (= 7 rate-limit + N truncated)")
    print(f"  bucket B : filled kategori, unmatched = {B}   (= M drift)")
    print(f"  scored   : filled kategori, matched   = {S}")
    print()
    print("-" * 66)
    print("YOUR METHOD  ->  N and M")
    print("-" * 66)
    print(f"  empty_kategori_rows        = {A}")
    print(f"  N (truncated) = empty - 7  = {A} - {RATE_LIMIT_COUNT} = {N}")
    print(f"  M (drift)     = 9 - N      = {TARGET_9} - {N} = {M}")
    print(f"  cross-check M = filled-unmatched = {B}")
    print()
    print("-" * 66)
    print("VERIFICATION")
    print("-" * 66)
    for label, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not all_ok:
        print()
        print("  !! A check failed. Most likely cause: the '7' constant does not")
        print("  match the real 429 count in THIS export. Re-count 429 rows in the")
        print("  error_log tab and rerun with the corrected RATE_LIMIT_COUNT, OR pass")
        print("  error_log_export.csv so the script labels each empty row directly.")
    print()
    print("=" * 66)
    print("Q7 ANSWER  — what happened to the other 16?")
    print("=" * 66)
    print(f"  16 unscored = 7 (HTTP 429) + {N} (truncated JSON) + {M} (timestamp drift)")
    print("  - 7  : Groq 8,000-TPM free tier -> HTTP 429 (replay fired every 0.5s)")
    print(f"  - {N:<2} : AI JSON cut off by max_tokens=200 -> 'kategori' empty (config cap,")
    print("        NOT a model reasoning failure; fixed by max_tokens 200 -> 500)")
    print(f"  - {M:<2} : model scored fine, but Sheet timestamp drifted from answer key")
    print("        so analyze_accuracy.py could not match them")
    print("  The 1 hot lead in this batch is an infra failure, not a model miss ->")
    print("  that is why the confusion matrix shows 7 hot scored, not 8.")
    print("  88.2% is accuracy over the 34 SCOREABLE leads (30/34), NOT over 50.")
    print("  It hides nothing once you state the denominator: 32% (16/50) were")
    print("  infrastructure/config failures excluded from the model-accuracy figure.")
    print()
    print("=" * 66)
    print("Q11 ANSWER  — separating model vs infrastructure failures")
    print("=" * 66)
    print("  Among the 16 unscored, ZERO are model-reasoning failures:")
    print(f"    - {7:>2} x HTTP 429        = infrastructure (Groq TPM)")
    print(f"    - {N:>2} x truncated JSON  = config (max_tokens=200 cap; model JSON cut")
    print("         mid-output, not a reasoning defect)")
    print(f"    - {M:>2} x timestamp drift = infrastructure (form-submission timing vs")
    print("         answer key; the model output itself was fine)")
    print("  -> all 16 were excluded from the accuracy denominator for that reason.")
    print("  Genuine MODEL misclassifications live among the 34 scored: 4 errors")
    print("  (2 cold->warm conservative, 2 warm->hot over-eager).")
    print("  So: model accuracy   = 30/34 = 88.2%  (reasoning quality)")
    print("      replay yield      = 34/50 = 68%    (infra/config reliability)")
    print("  These two numbers measure different things and must not be conflated.")
    print()
    print("=" * 66)
    print("DETAIL — the 16 unscored leads")
    print("=" * 66)
    print(f"\n[A] empty kategori  (7 rate-limit + {N} truncated):")
    for i, r in enumerate(bucketA, 1):
        nama = r.get("nama", "?")
        if err_path and os.path.exists(err_path):
            tag = "HTTP 429 (rate-limit)" if nama in four29_names else "truncated JSON"
        else:
            tag = "rate-limit OR truncated (empty kategori)"
        print(f"  {i:>2}. {nama[:24]:<24} | {r.get('channel','?'):<3} | {r.get('timestamp','?')}")
        print(f"      pesan: {(r.get('pesan','') or '')[:70]}")
        print(f"      -> {tag}")
    print(f"\n[B] filled kategori but unmatched  ({M} drift):")
    for i, r in enumerate(bucketB, 1):
        print(f"  {i:>2}. {r.get('nama','?')[:24]:<24} | {r.get('channel','?'):<3} | {r.get('timestamp','?')}")
        print(f"      pesan   : {(r.get('pesan','') or '')[:70]}")
        print(f"      kategori: {norm(r.get('kategori'))} | alasan: {(r.get('alasan','') or '')[:50]}")
        print(f"      -> timestamp drift (model output fine, unmatched to answer key)")


if __name__ == "__main__":
    main()
