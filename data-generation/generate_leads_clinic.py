"""
Generate 50 fictional leads untuk study case "Glow Aesthetic Clinic".
Tema: klinik kecantikan di Jakarta.
4 kategori: hot (siap treatment premium), warm (butuh edukasi), cold (cuma nanya), spam.

Output:
  - 50_leads_sample.csv     (yang diupload ke Sheet tab "leads")
  - 50_leads_answer_key.csv (ground truth untuk evaluasi AI akurasi)
"""
import csv
import os
from datetime import datetime, timedelta
import random
from collections import Counter

random.seed(2026)  # reproducible

# ===== Template pesan per kategori =====

pesan_hot = [
    "Halo dok, aku mau booking botox untuk dahi + crow's feet. Budget 15jt. Bisa jadwalin minggu ini? Aku dari Surabaya, akan ke Jakarta Jumat depan.",
    "Dok, aku tertarik filler hidung + chin. Sudah riset 2 bulan. Budget 20jt. Mau konsultasi weekend ini. Bisa request Dr. Anita langsung?",
    "Pernah treatment laser di klinik lain hasilnya kurang. Pengen coba di Glow. Concern: bekas jerawat + pore besar. Budget 8jt untuk 3x sesi. Kapan available?",
    "Aku mau PRP hair treatment. Rambut rontok parah pasca melahirkan. Budget 12jt untuk paket 6x. Tolong info jadwal kosong dok Anita minggu depan.",
    "Hi dok, aku mau laser dioda untuk kaki (full leg). Budget 10jt. Pernah pakai razor, rambut tumbuh cepat. Mau mulai ASAP sebelum wedding Desember.",
    "Dok, aku 35thn, mau anti-aging treatment kombinasi: botox + threadlift. Budget 25jt. Sudah konsultasi 2 klinik lain, membandingkan. Bisa booking konsultasi Jumat sore?",
    "Mau treatment chemical peel TCA untuk melasma. Aku pasien lama (kartu member 0829). Budget 5jt untuk paket 4x. Booking dok Anita ya.",
    "Aku pengen filler tear trough (mata) karena eye bag kelihatan lelah. Budget 10jt. Sudah lihat testimoni di IG. Tolong balas WA aja, jangan telp."
]

pesan_warm = [
    "Halo dok, aku mau tanya treatment untuk bekas jerawat. Yang cocok apa ya? Belum pernah treatment sebelumnya. Mau konsultasi dulu.",
    "Aku tertarik facial hydrating. Harganya berapa? Ada paket rutin bulanan gak? Belum tentu bisa langsung, mau lihat-lihat dulu.",
    "Dok, area pipi aku mulai kendur. Mau tahu opsi treatment yang sesuai budget 5jt. Boleh konsultasi akhir pekan?",
    "Pernah dengar klinik Glow bagus, aku pengen coba facial basic dulu sebelum naik ke treatment lain. Kirim pricelist ke WA ya.",
    "Hi, aku 28thn, mulai kelihatan fine line. Mau tahu anti-aging treatment yang buat pemula. Budget fleksibel, mau konsultasi dulu.",
    "Mau tanya laser untuk underarm. Berapa per sesi? Aku pernah pakai krim gak mempan. Mungkin butuh 3-4x sesi ya?",
    "Dok, aku punya masalah jerawat hormonal. Sudah ke dokter kulit umum tapi gak mempan. Mau tahu treatment di Glow yang bisa bantu. Budget sekitar 4jt.",
    "Tertarik PRP wajah. Tapi belum paham apa side effect-nya. Bisa konsultasi 30 menit dulu sebelum decide? Mau akhir bulan.",
    "Halo, aku follow IG Glow dari lama. Aku mau coba chemical peel. Yang untuk pemula apa? Aku sensitive skin. Tapi belum siap treatment mahal.",
    "Aku mau tanya botox. Berapa range harganya? Aku cuma mau tau dulu, belum commit. Mungkin tahun depan baru eksekusi.",
    "Dok, kulitku kering + kusam. Pengen coba facial. Tapi aku takut treatment berat. Bisa rekomendasi yang ringan dulu? Budget 1-2jt.",
    "Pengen tahu program perawatan 3 bulan untuk acne prone skin. Aku working mom 32thn. Mau treatment yang hasilnya kelihatan tapi gak banyak downtime.",
    "Halo, aku pernah botox di klinik lain 2 tahun lalu. Sekarang mau repeat. Mau coba Glow. Bisa konsul dulu sebelum treatment?",
    "Aku mau tanya laser untuk bopeng jerawat. Berapa total biaya 3x sesi? Aku 26thn, budget sekitar 6jt. Tapi mau pikirin dulu.",
    "Dok, aku baru pindah ke Jakarta. Cari klinik langganan. Mau coba treatment basic dulu sebelum yang intens. Info pricelist ya.",
    "Mau tanya treatment untuk dark circle mata. Selain filler ada alternatif? Aku takut jarum. Budget sekitar 3jt per bulan.",
    "Aku tertarik program 6 bulan untuk mencerahkan wajah. Bisa di-share paketnya? Belum tahu mau mulai kapan, mau compare dulu."
]

pesan_cold = [
    "Halo, ada promo gak bulan ini?",
    "Lihat IG, kapan free konsultasi ya?",
    "Ada trial treatment gratis?",
    "Aku mahasiswa, ada diskon?",
    "Boleh minta brosur digitalnya?",
    "Tanya-tanya dulu ya, belum siap.",
    "Mau subscribe info promo aja.",
    "Ada kelas edukasi skincare gratis?",
    "Follow dari TikTok. Kapan live lagi?",
    "Cuma mau tahu harga termurah facial.",
    "Aku cuma survey-survey dulu.",
    "Belum ada masalah kulit, iseng isi form.",
    "Pengen tahu apakah Glow open franchise.",
    "Boleh minta testimoni klien lama?",
    "Mau cari info buat teman, bukan untuk aku.",
    "Ada event open house bulan ini?",
    "Lagi hemat, tahun depan baru treatment.",
    "Mau subscribe newsletter Glow aja.",
    "Cuma mau tahu range harga treatment umum.",
    "Pengen tahu lokasi klinik & jam buka."
]

pesan_spam = [
    "MAIN BANDAR JUDI ONLINE TERPERCAYA 24 JAM MIN DEPO 10RIBU HUB 0812xxxx",
    "Butuh pinjaman cepat 500jt tanpa BI checking? WA 0822xxxx",
    "Kunjungi situs diskon obat kuat bit.ly/promo2024 100% asli",
    "Promo jasa follower IG 10rb untuk 10k follower WA 0813xxxx",
    "Test123"
]

# ===== Nama Indonesia (lebih beragam gender) =====
nama_depan_p = ["Anita", "Bella", "Citra", "Dewi", "Elsa", "Fitri", "Gita", "Hana", "Indah",
                "Jihan", "Kartika", "Lina", "Maya", "Nadia", "Olivia", "Putri", "Rani",
                "Sari", "Tari", "Uli", "Vera", "Wati", "Yuni", "Zahra", "Bunga", "Cindy"]
nama_depan_l = ["Andi", "Bayu", "Dimas", "Eko", "Fajar", "Gilang", "Hendra", "Iqbal",
                "Joko", "Krisna", "Lukman", "Maman", "Nanda", "Oka", "Rama", "Surya",
                "Tono", "Utama", "Wawan", "Yoga", "Zaki", "Bagus", "Cahya", "Reza"]
nama_belakang = ["Pratama", "Santoso", "Wijaya", "Susanti", "Hidayat", "Lestari", "Kurniawan",
                 "Anggraini", "Setiawan", "Maharani", "Permana", "Utami", "Halim", "Puspita",
                 "Nugroho", "Safitri", "Wibowo", "Hardiansyah", "Ramadhan", "Cahyani",
                 "Firmansyah", "Oktaviani", "Saputra", "Maulana", "Yulianti", "Gunawan",
                 "Hartono", "Iskandar", "Januar", "Kusuma", "Marpaung"]

# ===== Budget per kategori =====
budget_for = {
    "hot":  ["> Rp 20 jt", "Rp 5–20 jt"],
    "warm": ["Rp 500rb–5jt", "Rp 5–20 jt", "< Rp 500rb"],
    "cold": ["< Rp 500rb", "Rp 500rb–5jt"],
    "spam": ["< Rp 500rb", "Rp 500rb–5jt"],
}

# ===== Distribusi target: 8 hot + 17 warm + 20 cold + 5 spam = 50 =====
all_pesan = (
    [(p, "hot") for p in pesan_hot] +
    [(p, "warm") for p in pesan_warm] +
    [(p, "cold") for p in pesan_cold] +
    [(p, "spam") for p in pesan_spam]
)
random.shuffle(all_pesan)
all_pesan = all_pesan[:50]

# ===== Generate =====
now = datetime.now()
leads = []
for i, (pesan, kategori) in enumerate(all_pesan):
    days_ago    = random.randint(0, 6)
    hours_ago   = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

    # 80% perempuan (sesuai demografik klien klinik kecantikan)
    if random.random() < 0.8:
        nama = f"{random.choice(nama_depan_p)} {random.choice(nama_belakang)}"
    else:
        nama = f"{random.choice(nama_depan_l)} {random.choice(nama_belakang)}"

    if random.random() < 0.75:
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

leads.sort(key=lambda x: x["timestamp"], reverse=True)

# ===== Save 2 CSV =====
os.makedirs("/home/z/my-project/download", exist_ok=True)

with open("/home/z/my-project/download/50_leads_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "nama", "kontak", "budget", "pesan"])
    writer.writeheader()
    for l in leads:
        row = {k: l[k] for k in ["timestamp", "nama", "kontak", "budget", "pesan"]}
        writer.writerow(row)

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
dist = Counter(l["expected_kategori"] for l in leads)
print(f"✅ Generated {len(leads)} leads (tema: Glow Aesthetic Clinic)")
print(f"Distribusi: hot={dist['hot']}, warm={dist['warm']}, cold={dist['cold']}, spam={dist['spam']}")
print(f"Range timestamp: {leads[-1]['timestamp']} → {leads[0]['timestamp']}")
print()
print("Sample 5 lead terbaru:")
for l in leads[:5]:
    print(f"  [{l['expected_kategori'].upper():4}] {l['nama']} | budget={l['budget']}")
    print(f"        {l['pesan'][:100]}{'...' if len(l['pesan']) > 100 else ''}")
    print()
