"""
Generate 50 fictional leads untuk study case "Glow Aesthetic Clinic" - V2 Multi-channel.
3 channel input: WhatsApp (manual by admin), Instagram DM (ManyChat), Meta Lead Ads (form).

Output:
  - 50_leads_sample.csv     (50 leads multi-channel, untuk import ke Sheet)
  - 50_leads_answer_key.csv (ground truth untuk evaluasi AI)
"""
import csv
import os
import json
import random
from datetime import datetime, timedelta
from collections import Counter

random.seed(20261106)  # reproducible

# ===== Template pesan per kategori per channel =====

# WhatsApp: singkat, casual, typo, singkatan
wa_hot = [
    "dok brp hrga botox dahi? minat booking jumat ini, budget 15jt",
    "halo dok, aku mau filler hidung. budget 20jt. bisa konsul weekend?",
    "dok aku pernah laser ditempat lain hasinya kurang. concern bekas jerawat. budget 8jt 3x sesi. kapan available?",
    "hai dok, mau PRP hair treatment. rambut rontok parah pp melahirkan. budget 12jt 6x sesi. booking dok anita ya",
    "dok aku mau laser dioda kaki full leg. budget 10jt. mau mulai asap sebelum wedding desember",
    "dok aku 35thn mau anti aging botox + threadlift. budget 25jt. booking jumat sore bisa?",
    "dok mau chemical peel TCA buat melasma. aku pasien lama kartu 0829. budget 5jt 4x. booking dok anita",
    "dok pengen filler tear trough mata. budget 10jt. udh lihat testimoni ig. balas wa aja jgn telp",
]

wa_warm = [
    "dok mau tanya treatment bekas jerawat. yg cocok apa? blm pernah treatment. mau konsul dulu",
    "tertarik facial hydrating. hrga brp? ada paket bulanan gak? blm tentu bisa langsung mau liat2 dulu",
    "dok pipi aku mulai kendur. opsi treatment budget 5jt apa ya. bisa konsul weekend?",
    "pernah denger glow bagus, aku mau coba facial basic dulu. kirim pricelist wa ya",
    "hi aku 28thn mulai fine line. anti aging untuk pemula apa. budget fleksibel mau konsul dulu",
    "dok laser underarm brp per sesi? pernah pakai krim gak mempan. butuh 3-4x sesi ya?",
    "dok aku jerawat hormonal. udah ke dokter kulit umum gak mempan. treatment glow yg bisa bantu. budget 4jt",
    "tertarik PRP wajah tp blm paham side effect. bisa konsul 30menit dulu? mau akhir bulan",
    "halo follow ig glow dari lama. aku mau coba chemical peel. yg pemula apa? aku sensitive skin",
    "tanya botox brp range harganya. cuma mau tau dulu blm commit. mungkin thn depan baru eksekusi",
    "dok kulitku kering+kusam. pengen facial. takut treatment berat. rekomendasi yg ringan? budget 1-2jt",
    "tanya program 3 bulan acne prone. aku working mom 32thn. hasil kelihatan tp gak banyak downtime",
    "halo pernah botox ditempat lain 2thn lalu. mau repeat di glow. bisa konsul dulu sebelum treatment?",
    "tanya laser bopeng jerawat. total 3x sesi brp? aku 26thn budget 6jt. tapi mau pikirin dulu",
    "dok baru pindah jakarta. cari klinik langganan. mau coba basic dulu. info pricelist ya",
    "treatment dark circle mata selain filler ada alternatif? takut jarum. budget 3jt/bln",
    "tertarik program 6 bulan pencerah wajah. share paketnya. blm tahu mau mulai kapan mau compare dulu",
    "dok aku pengen treatment tapi bingung mulai dari mana. blm pernah ke klinik kecantikan. bisa konsultasi?",
    "hai dok, mau tanya harga facial basic + chemical peel pemula. kirim detailnya ya",
    "aku 30thn baru pernah facial di salon. mau naik ke treatment klinik. rekomendasi awal apa?",
]

wa_cold = [
    "ada promo gak bulan ini?",
    "kapan free konsultasi dok",
    "ada trial treatment gratis?",
    "aku mahasiswa ada diskon gak",
    "boleh minta brosur digitalnya",
    "tanya2 dulu ya blm siap",
    "mau subscribe info promo aja",
    "ada kelas edukasi skincare gratis?",
    "kapan live ig lagi dok",
    "brp termurah facial",
    "survey2 dulu",
    "blm ada masalah kulit iseng isi form",
    "glow open franchise gak",
    "boleh minta testimoni klien lama",
    "cari info buat teman bukan untuk aku",
    "ada event open house bln ini",
    "lagi hemat thn depan baru treatment",
    "subscribe newsletter glow aja",
    "brp range harga treatment umum",
    "lokasi klinik & jam buka",
]

wa_spam = [
    "BANDAR JUDI ONLINE TERPERCAYA 24JAM MIN DEPO 10RIBU HUB 0812xxxx",
    "butuh pinjaman cepat 500jt tanpa BI checking? WA 0822xxxx",
    "promo jasa follower IG 10rb untuk 10k follower WA 0813xxxx",
    "MAIN BANDAR JUDI ONLINE MENANG BERAPAPUN DI BAYAR HUBUNGI 0812xxxx",
    "test123",
]

# Instagram DM: singkat, banyak emoji, very casual
ig_hot = [
    "halo dok 💕 aku mau filler hidung, budget 15jt, available weekend? 🙏",
    "hi dok ✨ mau booking botox dahi, budget 10jt, jumat depan bisa? 💗",
    "dok aku mau PRP rambut 💆‍♀️ rambut rontok parah pp melahirkan, budget 12jt 6x sesi, booking dok anita ya 💕",
    "halo dok 💖 laser dioda full leg budget 10jt, mau mulai before wedding Des 🎀 available slot?",
    "hi dok 🌸 mau filler tear trough, budget 10jt, udah lihat testimoni keren 🥰 balas dm ya",
]

ig_warm = [
    "halo dok 💕 mau tanya treatment bekas jerawat, blm pernah treatment, rekomendasi? 🙏",
    "hi ✨ tertarik facial hydrating, ada paket bulanan? mau liat2 dulu 💗",
    "dok pipi mulai kendur 😔 treatment budget 5jt apa ya, bisa konsul weekend? 💕",
    "follow dari lama 🌸 mau coba facial basic dulu, kirim pricelist dm ya 🙏",
    "aku 28thn mulai fine lines 🥲 anti aging pemula rekomendasi? mau konsul 💕",
    "halo 💖 pernah botox 2thn lalu di klinik lain, mau repeat di glow, bisa konsul? 🌸",
    "tertarik PRP wajah tp blm paham side effect 😅 bisa konsul 30menit dulu? 🙏",
    "halo dok 💕 chemical peel untuk pemula apa? aku sensitive skin 💗",
    "treatment dark circle selain filler ada alternatif? 😣 takut jarum, budget 3jt/bln",
    "tertarik program 6 bulan pencerah 💫 share paketnya, mau compare dulu 🌸",
]

ig_cold = [
    "ada promo bulan ini dok? 💕",
    "kapan free konsultasi ✨",
    "trial treatment gratis ada gak 💗",
    "subscribe info promo aja 🌸",
    "kapan live ig lagi dok 💕",
    "survey2 dulu ya 🙏",
    "mau brosur digitalnya 💕",
    "cari info buat teman 🌸",
    "open franchise gak dok ✨",
    "lokasi klinik & jam buka 💗",
    "subscribe newsletter aja 💕",
    "lagi hemat thn depan baru treatment 🥲",
]

ig_spam = [
    "PROMO JASA FOLLOWER IG 10RB UNTUK 10K FOLLOWER DM UNTUK INFO 🚀",
]

# Meta Lead Ads: structured, narrative di-render dari fields
# Format: "Treatment interest: X | Budget: Y | Preferred date: Z | Notes: W"
leadads_hot = [
    "Treatment interest: Botox | Budget: Rp 5–20 jt | Preferred date: This week | Notes: First time, ready to book",
    "Treatment interest: Filler | Budget: > Rp 20 jt | Preferred date: Next weekend | Notes: Already researched, ready to commit",
]

leadads_warm = [
    "Treatment interest: Laser | Budget: Rp 5–20 jt | Preferred date: Within 2 weeks | Notes: Consultation first",
    "Treatment interest: Chemical Peel | Budget: Rp 500rb–5jt | Preferred date: Flexible | Notes: Beginner, sensitive skin",
    "Treatment interest: PRP | Budget: Rp 5–20 jt | Preferred date: End of month | Notes: Want to discuss side effects first",
]

leadads_cold = [
    "Treatment interest: Facial | Budget: < Rp 500rb | Preferred date: Flexible | Notes: Just looking around",
    "Treatment interest: Consultation | Budget: < Rp 500rb | Preferred date: Flexible | Notes: Not ready yet, just want info",
]

leadads_spam = [
    "Treatment interest: Other | Budget: < Rp 500rb | Preferred date: Flexible | Notes: PROMO JASA FOLLOWER IG DM UNTUK INFO",
]

# ===== Nama Indonesia =====
nama_depan_p = ["Anita", "Bella", "Citra", "Dewi", "Elsa", "Fitri", "Gita", "Hana", "Indah",
                "Jihan", "Kartika", "Lina", "Maya", "Nadia", "Olivia", "Putri", "Rani",
                "Sari", "Tari", "Uli", "Vera", "Wati", "Yuni", "Zahra", "Bunga", "Cindy",
                "Dinda", "Erika", "Fiona", "Gisela"]
nama_depan_l = ["Andi", "Bayu", "Dimas", "Eko", "Fajar", "Gilang", "Hendra", "Iqbal",
                "Joko", "Krisna", "Lukman", "Maman", "Nanda", "Oka", "Rama", "Surya",
                "Tono", "Utama", "Wawan", "Yoga", "Zaki", "Bagus", "Cahya", "Reza"]
nama_belakang = ["Pratama", "Santoso", "Wijaya", "Susanti", "Hidayat", "Lestari", "Kurniawan",
                 "Anggraini", "Setiawan", "Maharani", "Permana", "Utami", "Halim", "Puspita",
                 "Nugroho", "Safitri", "Wibowo", "Hardiansyah", "Ramadhan", "Cahyani",
                 "Firmansyah", "Oktaviani", "Saputra", "Maulana", "Yulianti", "Gunawan",
                 "Hartono", "Iskandar", "Januar", "Kusuma", "Marpaung", "Nababan", "Putra"]

budget_for = {
    "hot":  ["> Rp 20 jt", "Rp 5–20 jt"],
    "warm": ["Rp 500rb–5jt", "Rp 5–20 jt", "< Rp 500rb"],
    "cold": ["< Rp 500rb", "Rp 500rb–5jt"],
    "spam": ["< Rp 500rb", "Rp 500rb–5jt"],
}

# ===== Distribusi target (50 leads, 3 channel) =====
# WA: 30 leads (60%) - 4 hot + 10 warm + 13 cold + 3 spam
# IG: 12 leads (24%) - 2 hot + 5 warm + 4 cold + 1 spam
# Lead Ads: 8 leads (16%) - 2 hot + 3 warm + 2 cold + 1 spam
# Total: 8 hot + 18 warm + 19 cold + 5 spam = 50 (close enough to original target)

wa_pool = (
    [(p, "hot") for p in wa_hot[:4]] +
    [(p, "warm") for p in wa_warm[:10]] +
    [(p, "cold") for p in wa_cold[:13]] +
    [(p, "spam") for p in wa_spam[:3]]
)
ig_pool = (
    [(p, "hot") for p in ig_hot[:2]] +
    [(p, "warm") for p in ig_warm[:5]] +
    [(p, "cold") for p in ig_cold[:4]] +
    [(p, "spam") for p in ig_spam[:1]]
)
leadads_pool = (
    [(p, "hot") for p in leadads_hot[:2]] +
    [(p, "warm") for p in leadads_warm[:3]] +
    [(p, "cold") for p in leadads_cold[:2]] +
    [(p, "spam") for p in leadads_spam[:1]]
)

random.shuffle(wa_pool)
random.shuffle(ig_pool)
random.shuffle(leadads_pool)

# ===== Generate leads =====
now = datetime.now()
leads = []

def make_lead(pesan, kategori, channel):
    days_ago    = random.randint(0, 6)
    hours_ago   = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

    # 80% perempuan (demografik klinik kecantikan)
    if random.random() < 0.8:
        nama = f"{random.choice(nama_depan_p)} {random.choice(nama_belakang)}"
    else:
        nama = f"{random.choice(nama_depan_l)} {random.choice(nama_belakang)}"

    # WA & IG: 80% WA number, 20% email
    # Lead Ads: 50% WA, 50% email (lead ads collect both)
    wa_prob = 0.8 if channel in ("wa", "ig") else 0.5
    if random.random() < wa_prob:
        kontak = f"08{random.randint(1000000000, 9999999999)}"
    else:
        kontak = f"{nama.split()[0].lower()}{random.randint(1, 99)}@gmail.com"

    budget = random.choice(budget_for[kategori])

    return {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "channel": channel,
        "nama": nama,
        "kontak": kontak,
        "budget": budget,
        "pesan": pesan,
        "expected_kategori": kategori,
    }

for pesan, kat in wa_pool:
    leads.append(make_lead(pesan, kat, "wa"))
for pesan, kat in ig_pool:
    leads.append(make_lead(pesan, kat, "ig"))
for pesan, kat in leadads_pool:
    leads.append(make_lead(pesan, kat, "leadads"))

# Sort by timestamp desc
leads.sort(key=lambda x: x["timestamp"], reverse=True)

# ===== Save 2 CSV =====
os.makedirs("/home/z/my-project/download", exist_ok=True)

with open("/home/z/my-project/download/50_leads_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "channel", "nama", "kontak", "budget", "pesan"])
    writer.writeheader()
    for l in leads:
        row = {k: l[k] for k in ["timestamp", "channel", "nama", "kontak", "budget", "pesan"]}
        writer.writerow(row)

with open("/home/z/my-project/download/50_leads_answer_key.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "channel", "nama", "expected_kategori"])
    writer.writeheader()
    for l in leads:
        writer.writerow({
            "timestamp": l["timestamp"],
            "channel": l["channel"],
            "nama": l["nama"],
            "expected_kategori": l["expected_kategori"],
        })

# ===== Statistik =====
dist_kat = Counter(l["expected_kategori"] for l in leads)
dist_ch = Counter(l["channel"] for l in leads)
print(f"✅ Generated {len(leads)} leads (multi-channel: Glow Aesthetic Clinic V2)")
print(f"Distribusi kategori: hot={dist_kat['hot']}, warm={dist_kat['warm']}, cold={dist_kat['cold']}, spam={dist_kat['spam']}")
print(f"Distribusi channel: wa={dist_ch['wa']}, ig={dist_ch['ig']}, leadads={dist_ch['leadads']}")
print(f"Range timestamp: {leads[-1]['timestamp']} → {leads[0]['timestamp']}")
print()
print("Sample 6 lead terbaru (multi-channel):")
for l in leads[:6]:
    print(f"  [{l['expected_kategori'].upper():4}] [{l['channel']:8}] {l['nama']} | budget={l['budget']}")
    print(f"        {l['pesan'][:90]}{'...' if len(l['pesan']) > 90 else ''}")
    print()
