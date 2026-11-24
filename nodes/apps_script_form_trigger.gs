/**
 * Google Apps Script — Glow Lead Triage
 * Pasang di tiap Google Form (Form #1, #2, #4) supaya submit Form → trigger webhook ke n8n
 *
 * CARA PASANG:
 * 1. Buka Google Form
 * 2. Klik ⋮ (titik 3 kanan atas) → Script editor
 * 3. Hapus isi Code.gs default, paste seluruh kode ini
 * 4. Klik Save (Cmd+S), kasih nama project "Glow Webhook Trigger"
 * 5. Klik Run → authorize saat diminta (pakai akun Google kamu)
 * 6. Klik Triggers (icon jam di sidebar kiri) → + Add Trigger
 *    - Function to run: onSubmit
 *    - Event type: On form submit
 * 7. Save. Selesai.
 */

function onSubmit(e) {
  if (!e || !e.response) return;

  var form = FormApp.getActiveForm();
  var formTitle = form.getTitle();

  // Tentukan channel + webhook URL berdasarkan title form
  var channel = '';
  var webhookUrl = '';

  if (formTitle.indexOf('Admin WA Input') !== -1) {
    channel = 'wa';
    webhookUrl = 'http://localhost:5678/webhook/glow-wa-input';
  } else if (formTitle.indexOf('Konsultasi Treatment') !== -1) {
    channel = 'leadads';
    webhookUrl = 'http://localhost:5678/webhook/glow-leadads-input';
  } else if (formTitle.indexOf('Admin IG DM') !== -1) {
    channel = 'ig';
    webhookUrl = 'http://localhost:5678/webhook/glow-ig-input';
  }

  if (!webhookUrl) {
    Logger.log('Form tidak dikenali: ' + formTitle);
    return;
  }

  // Ambil semua response dari form submission
  var itemResponses = e.response.getItemResponses();
  var raw = {};
  for (var i = 0; i < itemResponses.length; i++) {
    var item = itemResponses[i];
    raw[item.getItem().getTitle()] = item.getResponse();
  }

  // Payload terstandardisasi untuk n8n
  var payload = {
    timestamp: e.response.getTimestamp().toISOString(),
    channel: channel,
    form_title: formTitle,
    raw: raw
  };

  // Kirim ke n8n webhook
  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(webhookUrl, options);
    Logger.log('Webhook terkirim: ' + response.getResponseCode());
  } catch (err) {
    Logger.log('Error kirim webhook: ' + err.toString());
  }
}
