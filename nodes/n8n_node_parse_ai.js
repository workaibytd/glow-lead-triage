/**
 * n8n Code Node 2 — Parse AI Response
 * Input: response dari Groq API (string JSON atau markdown-wrapped JSON)
 * Output: object {kategori, alasan, score} yang siap ditulis ke Sheet
 */

// Ambil content dari response Groq
const aiContent = $json.choices?.[0]?.message?.content || '';

if (!aiContent) {
  throw new Error('AI response kosong');
}

// Bersihkan: hapus markdown code fence kalau ada
let clean = aiContent.trim();
if (clean.startsWith('```')) {
  // Hapus opening fence (```json atau ```)
  clean = clean.replace(/^```(?:json)?\s*/i, '');
  // Hapus closing fence
  clean = clean.replace(/\s*```\s*$/i, '');
  clean = clean.trim();
}

// Coba parse JSON
let parsed;
try {
  parsed = JSON.parse(clean);
} catch (e) {
  // Fallback: coba ekstrak JSON dari teks (cari { ... })
  const match = clean.match(/\{[\s\S]*\}/);
  if (match) {
    try {
      parsed = JSON.parse(match[0]);
    } catch (e2) {
      throw new Error('AI response bukan JSON valid: ' + clean.substring(0, 100));
    }
  } else {
    throw new Error('AI response tanpa JSON: ' + clean.substring(0, 100));
  }
}

// Validasi field wajib
const kategori = (parsed.kategori || '').toLowerCase();
const alasan = parsed.alasan || '';
const score = parseInt(parsed.score, 10);

if (!['hot', 'warm', 'cold', 'spam'].includes(kategori)) {
  throw new Error('Kategori tidak valid: ' + kategori);
}
if (isNaN(score) || score < 1 || score > 10) {
  throw new Error('Score tidak valid: ' + parsed.score);
}

// Output
return {
  json: {
    kategori: kategori,
    alasan: alasan,
    score: score
  }
};
