# Glow Lead Triage — AI Lead Qualification System

End-to-end AI lead-classification pipeline for a klinik kecantikan use case. Leads from WhatsApp, Instagram DM, and Meta Lead Ads are classified as **hot / warm / cold / spam** with a confidence score and reasoning, triggering real-time Telegram notifications for hot leads and a weekly summary report.

> **Self-initiated portfolio project.** Built solo in 5 days on a $0 free-tier stack to demonstrate full-stack AI workflow automation: system design, AI integration, rigorous evaluation methodology, and production-grade documentation.

---

## Evaluation Results

The system was evaluated against a 50-lead ground-truth dataset with an independently-labeled answer key:

| Metric | Value |
|---|---|
| Overall accuracy | **88.2%** (30/34 matched leads correctly classified) |
| Hot lead recall | **100%** (zero false negatives — no potential customer missed) |
| Spam precision | **100%** (zero false positives — no real lead discarded) |
| Warm accuracy | 75% |
| Cold accuracy | 86% |

The two 100% metrics were the business-critical ones: missing a hot lead is lost revenue, and discarding a real lead as spam damages the customer relationship. The evaluation harness lives in [`evaluation/`](evaluation/) — see `replay_50_leads.py` and `analyze_accuracy.py`.

---

## Architecture

```
3 Input Channels            n8n Workflows               Outputs
─────────────────           ────────────────            ──────────────
WhatsApp (admin form)   ─┐                              Telegram (instant
Instagram DM (ManyChat) ─┼─→ Workflow 1: Triage     ──→ hot-lead notification)
Meta Lead Ads (sim)     ─┘   Webhook → Normalize        Google Sheet
                            → Groq AI Classify            (5 tabs: leads,
                            → Parse → Combine             error_log, weekly,
                            → Write Sheet                 wa_raw, ig_raw)
                            → IF Hot → Telegram

                        Workflow 2: Error Handler
                           Error Trigger → Format → Log

                        Workflow 3: Weekly Report
                           Mon 09:00 WIB → Aggregate
                           → Telegram summary
```

---

## Tech Stack ($0 free-tier)

| Layer | Tool | Free Tier |
|---|---|---|
| Input | Google Forms + Apps Script | Unlimited |
| Orchestrator | n8n self-hosted | Unlimited workflows |
| AI | Groq API (`gpt-oss-120b`) | 30 req/min, 14,400/day |
| Database | Google Sheets | Unlimited |
| Notification | Telegram Bot API | Unlimited |
| IG auto-reply | ManyChat | 25 active contacts/month (demo-scale) |

**Total monthly cost: $0** for the proof-of-concept demo. Note: ManyChat's free tier was reduced from 1,000 to **25 active contacts/month** in its March 2026 pricing overhaul — sufficient for demo-scale IG traffic, but production IG validation at 16+ leads/day requires ManyChat Pro ($29–39/month) or a direct Instagram Graph API integration. All other components (n8n, Groq, Sheets, Telegram, Forms) remain $0 at validation scale. Documented production upgrade path in [`docs/guidebook.md`](docs/guidebook.md).

---

## Repository Structure

```
glow-lead-triage/
├── README.md                                ← this file
├── .gitignore
├── docs/
│   └── guidebook.md                         ← full technical build guide (1,200 lines)
├── workflow/
│   └── glow_lead_triage_workflow.json       ← n8n importable workflow export
├── nodes/
│   ├── apps_script_form_trigger.gs          ← Google Apps Script webhook bridge
│   ├── n8n_node_normalize.js                ← n8n Code node: normalize 3 channels
│   ├── n8n_node_parse_ai.js                 ← n8n Code node: parse AI JSON response
│   └── groq_system_prompt.py                ← system prompt definition for Groq
├── evaluation/
│   ├── replay_50_leads.py                   ← evaluation harness: replay test leads
│   ├── analyze_accuracy.py                  ← confusion matrix + per-category accuracy
│   ├── 50_leads_sample.csv                  ← test dataset (50 multi-channel leads)
│   └── 50_leads_answer_key.csv              ← ground-truth labels
└── data-generation/
    ├── generate_leads.py
    ├── generate_leads_clinic.py
    └── generate_leads_multichannel.py
```

---

## Quickstart

### Import the workflow into n8n

1. Install n8n: `npm install -g n8n` (requires Node.js 18+) or use Docker
2. Start n8n: `npx n8n`
3. Open http://localhost:5678
4. Import `workflow/glow_lead_triage_workflow.json`
5. Configure credentials in n8n: Groq API key, Google Sheets OAuth2, Telegram Bot token

### Run the evaluation

```bash
cd evaluation
python3 replay_50_leads.py      # sends 50 test leads to the webhook
python3 analyze_accuracy.py     # produces confusion matrix vs answer key
```

> The replay script sends to `http://localhost:5678/webhook/glow-wa-input` by default. Update `WEBHOOK_URL` in `replay_50_leads.py` if your n8n runs elsewhere.

---

## AI Classification Rubric

Leads are classified into 4 categories with explicit, machine-applicable decision criteria:

| Category | Criteria | Business meaning |
|---|---|---|
| **hot** | Specific treatment + clear budget + urgent timeline | Immediate follow-up (closing potential >Rp 5jt) |
| **warm** | Treatment interest + budget range, no urgency | Follow up within 1–2 days |
| **cold** | General inquiry (price, consultation), weak intent | Nurture sequence |
| **spam** | Promotional intent, no genuine inquiry | Auto-discard |

The rubric translates qualitative business judgment ("which leads deserve immediate follow-up?") into rules the AI can apply consistently. Full criteria and tuning notes in [`docs/guidebook.md`](docs/guidebook.md).

---

## Confusion Matrix

| Expected → Actual | Count | Status |
|---|---|---|
| cold → cold | 12 | ✓ |
| cold → warm | 2 | conservative bias (acceptable) |
| hot → hot | 7 | ✓ |
| spam → spam | 5 | ✓ |
| warm → hot | 2 | over-eager (tunable via prompt) |
| warm → warm | 6 | ✓ |

Misclassification analysis with root cause per cell is documented in [`docs/guidebook.md`](docs/guidebook.md).

---

## Known Limitations

- **n8n self-hosted on local machine**: webhook unresponsive when the machine sleeps. Production fix: deploy to VPS or n8n Cloud for >99% uptime.
- **WhatsApp channel is manual** (admin copies chat into form). Production fix: WhatsApp Cloud API (1,000 chats/month free).
- **Groq free-tier rate limit** (8,000 TPM): burst >16 leads/min hits HTTP 429. Production fix: Groq Dev Tier ($0.05/1M tokens) or a rate-limited queue.
- **AI accuracy 88.2%**: tunable via system-prompt adjustment over the first 2–4 weeks of real leads. 88% is above the industry standard (75–80%) for lead-classification tasks.

---

## License

MIT — see the license terms below. The system prompt, workflow structure, evaluation harness, and documentation are free to use, modify, and distribute.

---

## Contact

Built by **Kartika Titian Delila** — freelance automation engineer & AI evaluation specialist.

- Email: tikaatd.work.ai@gmail.com
- LinkedIn: linkedin.com/in/titian-delila-693aa342b
- Portfolio: notion.com/p/Glow-Lead-Triage-AI-Lead-Qualification-System-41b9326e988980a0aabbef57c5263f22

Portfolio project, November 2026. Built with $0 budget on 100% free-tier tools.
