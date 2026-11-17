/**
 * n8n Code Node 1 — Normalize Data 3 Channel
 * Input: payload webhook dari WA / Lead Ads / IG (schema beda)
 * Output: object unified {channel, nama, kontak, budget, pesan}
 */

// Input dari webhook (n8n inject sebagai $json)
const input = $json;
const channel = input.channel || 'unknown';
const raw = input.raw || {};

let nama, kontak, budget, pesan;

if (channel === 'wa') {
  // Form #1 (WA Admin Input):
  // "Nama admin", "Nama klien (dari chat WA)", "No. WA / kontak klien", "Budget klien", "Copy-paste chat WA asli"
  nama = raw['Nama klien (dari chat WA)'] || '';
  kontak = raw['No. WA / kontak klien'] || '';
  budget = raw['Budget klien'] || '';
  pesan = raw['Copy-paste chat WA asli'] || '';

} else if (channel === 'leadads') {
  // Form #2 (Lead Ads Simulator):
  // "Nama lengkap", "No. WhatsApp", "Email", "Treatment yang diminati", "Budget", "Kapan mau mulai treatment?", "Catatan tambahan"
  nama = raw['Nama lengkap'] || '';
  kontak = raw['No. WhatsApp'] || raw['Email'] || '';
  budget = raw['Budget'] || '';
  const treatment = raw['Treatment yang diminati'] || '';
  const timeline = raw['Kapan mau mulai treatment?'] || '';
  const catatan = raw['Catatan tambahan'] || '';
  // Gabung jadi 1 pesan terstruktur untuk AI
  pesan = `Treatment interest: ${treatment} | Budget: ${budget} | Preferred date: ${timeline} | Notes: ${catatan}`;

} else if (channel === 'ig') {
  // Form #4 (IG DM Simulator):
  // "Nama admin", "IG handle klien (contoh: @jihan.s)", "Kontak WA klien (kalau disebut di DM)", "Budget klien", "Copy-paste DM IG asli"
  nama = raw['IG handle klien (contoh: @jihan.s)'] || '';
  kontak = raw['Kontak WA klien (kalau disebut di DM)'] || '';
  budget = raw['Budget klien'] || '';
  pesan = raw['Copy-paste DM IG asli'] || '';

} else {
  // Fallback: coba field generik
  nama = raw.nama || raw.name || '';
  kontak = raw.kontak || raw.contact || '';
  budget = raw.budget || '';
  pesan = raw.pesan || raw.message || '';
}

// Output object unified
return {
  json: {
    timestamp: input.timestamp || new Date().toISOString(),
    channel: channel,
    nama: nama,
    kontak: kontak,
    budget: budget,
    pesan: pesan
  }
};
