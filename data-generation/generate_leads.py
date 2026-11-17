"""
Generate 50 fictional leads untuk study case "Andi Pratama Coaching".
Output: 2 file CSV
  - 50_leads_sample.csv     (yang diupload ke Sheet tab "leads")
  - 50_leads_answer_key.csv (ground truth untuk evaluasi AI akurasi)
"""
import csv
import os
from datetime import datetime, timedelta
import random

random.seed(42)  # reproducible

# ===== Template pesan per kategori =====

pesan_hot = [
    "Halo, aku punya usaha kuliner frozen food di Bandung, omzet 80jt/bulan. Pengen scale ke 200jt tahun ini. Budget Rp 25jt untuk coaching 3 bulan. Kapan bisa mulai minggu ini?",
    "Owner 3 outlet seblak di Jakarta. Omzet total 450jt/bulan tapi margin tipis. Butuh bantuan struktur biaya + SOP. Budget 30jt, mau mulai ASAP minggu depan.",
    "Punya cloud kitchen 5 menu, omzet 120jt/bulan. Mau bikin franchise butuh sistem operasi rapi. Budget 50jt untuk 6 bulan. Tolong japri jadwal konsultasi.",
    "Aku baru keluar dari korporat, punya modal 500jt mau buka F&B 2 outlet. Butuh mentor dari nol sampe launching. Budget 40jt. Timeline 2 bulan. Urgent.",
    "Pemilik 2 restoran padang. Penjualan turun 30% 3 bulan terakhir. Butuh audit + strategi marketing. Budget 20jt, mau mulai pekan ini.",
    "Catering HQR omzet 60jt/bulan. Mau ekspansi ke B2B korporat. Butuh strategi sales + pricing. Budget 15jt. Bisa diskusi minggu ini?",
    "Pemilik brand snack kemasan, distribusi 50 kota. Mau masuk modern trade butuh strategi. Budget 35jt untuk 4 bulan. Mohon response cepat.",
    "Punya 4 outlet jus buah. Mau standardisasi + bikin SOP franchise. Budget 28jt. Target mulai awal bulan depan. Mohon info jadwal kosong."
]

pesan_warm = [
    "Halo, aku tertarik dengan coaching business. Aku punya usaha kopi kecil omzet 25jt/bulan. Mau tanya programnya seperti apa dan harganya berapa.",
    "Pemilik depot air minum 2 cabang. Pengen develop bisnis tapi belum tahu mulai dari mana. Budget terbatas sekitar 8jt. Ada paket yang cocok?",
    "Punya usaha catering harian rumahan omzet 15jt. Pengen scale up tapi bingung. Mau konsultasi dulu sebelum commit. Kapan available?",
    "Aku baru mulai jualan brownies online 3 bulan, omzet 5jt. Pengen tahu cara scale. Budget belum fix, mau lihat-lihat paket dulu.",
    "Owner warung makan sederhana. Pengen belajar manajemen keuangan. Mungkin butuh coaching bulanan. Budget 5jt untuk 3 bulan. Info dong.",
    "Punya usaha kue kering musiman (Lebaran). Mau bikin konsisten sepanjang tahun. Mau tanya apakah kamu bisa bantu dan berapa investasi.",
    "Aku punya restoran kecil di pinggiran kota. Pengen buka cabang kedua tapi ragu. Butuh second opinion. Boleh konsultasi?",
    "Mau tanya-tanya soal program mentoring UMKM. Aku punya 2 unit usaha kuliner, omzet gabungan 35jt. Pengen sistematisasi operasional.",
    "Halo, aku lihat Instagram kamu tertarik dengan coaching. Punya usaha seblak dengan omzet 12jt. Pengen naik ke 30jt. Bisa bantu?",
    "Aku baru saja resign dari job, mau buka F&B. Butuh mentor tapi budget terbatas. Ada program pemula?",
    "Pemilik bakery kecil. Pengen belajar digital marketing buat naikin penjualan. Mau tanya apakah coaching kamu cover itu.",
    "Punya usaha nasi box kantor. Pengen ekspansi ke kota lain. Butuh strategi. Mau konsultasi dulu sebelum ambil paket.",
    "Aku tertarik dengan program 1 bulan. Usaha aku seblak, omzet 8jt. Pengen coba dulu sebelum commit paket besar. Info harga ya.",
    "Mau tanya program coaching untuk pemula. Aku masih kuliah, jualan makanan frozen omzet 3jt. Mungkin tahun depan baru serius.",
    "Pengen tahu detail program coaching kamu. Aku punya kafe kecil, mau improve. Kirim info lengkap ke email ya.",
    "Halo, aku lihat testimoni klien kamu. Aku punya masalah serupa. Mau diskusi. Kapan jadwal kosong minggu depan?",
    "Punya ide usaha snack tapi belum eksekusi. Butuh motivasi + struktur. Mungkin coaching cocok. Info dong paketnya."
]

pesan_cold = [
    "Halo, ada promo gak?",
    "Lihat Instagram, kapan workshop gratisnya?",
    "Aku mahasiswa, ada kelas online gratis?",
    "Tanya-tanya dulu ya, belum siap bayar.",
    "Boleh minta ebook gratisnya?",
    "Pengen tahu saja, belum ada budget.",
    "Follow dari TikTok, kapan live lagi?",
    "Aku cuma survey-survey dulu.",
    "Ada webinar gratis bulan ini?",
    "Lihat iklan, iseng isi form.",
    "Mau tanya harga termurah paket berapa?",
    "Belum punya bisnis, tapi pengen belajar dulu.",
    "Aku cuma mau tahu, jangan dihubungi dulu ya.",
    "Bisa konsultasi gratis 15 menit aja?",
    "Mau subscribe newsletter aja.",
    "Ada trial class?",
    "Pengen tahu apakah cocok untuk pemula banget.",
    "Boleh minta info brosur digitalnya?",
    "Ada program untuk pelaku pemula banget? Gratis?",
    "Lagi cari mentor gratis, ada saran?"
]

pesan_spam = [
    "MAIN BANDAR JUDI ONLINE MENANG BERAPAPUN DI BAYAR HUBUNGI 0812xxxx",
    "Kunjungi situs kami bit.ly/promo-murah2024 diskon 90%",
    "Butuh pinjaman 500jt tanpa jaminan? WA 0822xxxx",
    "Test",
    "asdfghjkl"
]

# ===== Nama Indonesia =====
nama_depan = ["Andi", "Budi", "Citra", "Dewi", "Eko", "Fitri", "Gilang", "Hana", "Indra", "Jihan",
              "Krisna", "Lina", "Maya", "Nanda", "Oki", "Putri", "Rama", "Sari", "Tono", "Umar",
              "Vina", "Wawan", "Xena", "Yoga", "Zahra", "Bagus", "Cahya", "Dian", "Eka", "Fajar",
              "Galih", "Hesti", "Iqbal", "Joko", "Kiki", "Lia", "Maman", "Nisa", "Oscar", "Prita",
              "Reza", "Sinta", "Tri", "Utami", "Vito", "Wulan", "Yusuf", "Zaki", "Bella", "Candra"]
nama_belakang = ["Pratama", "Santoso", "Wijaya", "Susanti", "Hidayat", "Lestari", "Kurniawan",
                 "Anggraini", "Setiawan", "Maharani", "Permana", "Utami", "Halim", "Puspita",
                 "Nugroho", "Safitri", "Wibowo", "Hardiansyah", "Ramadhan", "Cahyani", "Firmansyah",
                 "Oktaviani", "Saputra", "Maulana", "Yulianti"]

# ===== Distribusi target =====
# 8 hot + 17 warm + 20 cold + 5 spam = 50
all_pesan = (
    [(p, "hot") for p in pesan_hot] +
    [(p, "warm") for p in pesan_warm] +
    [(p, "cold") for p in pesan_cold] +
    [(p, "spam") for p in pesan_spam]
)
random.shuffle(all_pesan)
all_pesan = all_pesan[:50]

budget_for = {
    "hot":  ["> Rp 20 jt", "Rp 5–20 jt"],
    "warm": ["Rp 500rb–5jt", "Rp 5–20 jt", "< Rp 500rb"],
    "cold": ["< Rp 500rb", "Rp 500rb–5jt"],
    "spam": ["< Rp 500rb", "Rp 500rb–5jt"],
}

# ===== Generate leads dengan timestamp 7 hari terakhir =====
now = datetime.now()
leads = []
for i, (pesan, kategori) in enumerate(all_pesan):
    days_ago    = random.randint(0, 6)
    hours_ago   = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

    nama = f"{random.choice(nama_depan)} {random.choice(nama_belakang)}"

    if random.random() < 0.7:
        kontak = f"08{random.randint(1000000000, 9999999999)}"
    else:
        kontak = f"{nama.split()[0].lower()}{random.randint(1, 99)}@gmail.com"

    budget = random.choice(budget_for[kategori])

    leads.append({
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "nama": nama,
        "kontak": kontak,
        "budget": budget,
        "pesan": pesan,
        "expected_kategori": kategori,
    })

# Sort by timestamp desc (terbaru di atas)
leads.sort(key=lambda x: x["timestamp"], reverse=True)

# ===== Save 2 file CSV =====
os.makedirs("/home/z/my-project/download", exist_ok=True)

# File 1: sample (tanpa kolom expected_kategori) — untuk upload ke Sheet
with open("/home/z/my-project/download/50_leads_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "nama", "kontak", "budget", "pesan"])
    writer.writeheader()
    for l in leads:
        row = {k: l[k] for k in ["timestamp", "nama", "kontak", "budget", "pesan"]}
        writer.writerow(row)

# File 2: answer key (untuk evaluasi AI akurasi nanti)
with open("/home/z/my-project/download/50_leads_answer_key.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "nama", "expected_kategori"])
    writer.writeheader()
    for l in leads:
        writer.writerow({
            "timestamp": l["timestamp"],
            "nama": l["nama"],
            "expected_kategori": l["expected_kategori"],
        })

# ===== Statistik =====
from collections import Counter
dist = Counter(l["expected_kategori"] for l in leads)
print(f"✅ Generated {len(leads)} leads")
print(f"Distribusi: hot={dist['hot']}, warm={dist['warm']}, cold={dist['cold']}, spam={dist['spam']}")
print(f"Range timestamp: {leads[-1]['timestamp']} → {leads[0]['timestamp']}")
print()
print("Sample 3 lead pertama (terbaru):")
for l in leads[:3]:
    print(f"  [{l['expected_kategori'].upper():4}] {l['nama']} — budget={l['budget']}")
    print(f"        pesan: {l['pesan'][:80]}...")
    print()
