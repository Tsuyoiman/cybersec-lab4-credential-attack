# Lab 4: Investigate a Simulated Credential Attack

**Day 2: Cyber Threats, Attack Investigation & AI Security** · V8 alignment: **2.3, 2.5, 4.8**

Students act as SOC analysts. They investigate a simulated **password-spraying** incident against the fictional company `corp.local`. They find the attacker in Windows authentication logs, confirm it in network traffic with Wireshark, and write a short incident report with recommendations.

> All data in this repository is **synthetic**. No live malware, no real attack, no real users or passwords. It is safe to run in any classroom.

---

## 👉 Start here: [Step-by-Step Lab Guide](docs/STEP-BY-STEP.md)

Follow the guide from Step 0 to Step 7. It tells you exactly what to click and what to write down.

## Quick start (for students)

| What | Where |
|---|---|
| 🔎 **Browser log viewer** (no install, works on any device) | **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/** (or open `docs/index.html` offline) |
| 📄 Log file (CSV) | [`data/auth_logs.csv`](data/auth_logs.csv) |
| 🌐 Network capture | [`data/network_capture.pcap`](data/network_capture.pcap) (open in Wireshark) |
| 🪜 **Step-by-step guide** | [`docs/STEP-BY-STEP.md`](docs/STEP-BY-STEP.md) |
| 📝 Worksheet | [`docs/student-worksheet.md`](docs/student-worksheet.md) |
| 📚 Cheat sheet | [`docs/cheat-sheet.md`](docs/cheat-sheet.md) |
| 🧾 Report template | [`docs/report-template.md`](docs/report-template.md) |

**Download everything:** green **Code** button → **Download ZIP**.

## The scenario

> On the morning of **12 November 2026**, the helpdesk at Corp received calls from IT staff who could not log in because their accounts were **locked out**. One user, `j.tan`, says she was asleep at 3 a.m. but her account shows activity at that time.
>
> You are the SOC analyst on duty. You have been given the security log from the domain controller **DC01** and a network capture from the same night. **Find out what happened.**

## Tools needed

| Tool | Needed? | Notes |
|---|---|---|
| Web browser | ✅ Yes | For the log viewer. This alone is enough for the log part |
| Wireshark | ✅ Yes | Free from [wireshark.org](https://www.wireshark.org/download.html), for Part B |
| Excel / Google Sheets / LibreOffice Calc | Optional | Any of them can open the CSV instead of the browser viewer |
| PowerShell | Optional | Built into Windows. Commands are in the cheat sheet |

No server, VM, or internet connection is required once the files are downloaded.

## Lab flow (≈ 75 min)

| # | Part | Time |
|---|---|---|
| 1 | Hook: brute force vs password spraying | 10 min |
| 2 | Evidence cheat sheet (Event IDs, logon types, status codes) | 10 min |
| 3 | **Part A:** investigate the logs | 20 min |
| 4 | **Part B:** confirm in Wireshark | 15 min |
| 5 | Write incident report + recommendations | 15 min |
| 6 | Debrief | 5 min |

Student walkthrough: [`docs/STEP-BY-STEP.md`](docs/STEP-BY-STEP.md) · Teaching notes: [`docs/instructor-guide.md`](docs/instructor-guide.md)

## Learning outcomes

By the end of the lab, students can:

1. Explain the difference between **brute force** and **password spraying**
2. Read Windows Security events **4624, 4625, 4740**, logon types and failure codes
3. Filter and count log data to find an **abnormal authentication pattern**
4. Use **Wireshark** to confirm log findings in network traffic (**correlation**)
5. Build a simple **attack timeline**
6. Separate real attack activity from **false positives**
7. Write an **incident report** with practical account-protection recommendations

## Repository structure

```
├── README.md                  ← you are here
├── data/
│   ├── auth_logs.csv          ← DC01 security log export (326 events)
│   └── network_capture.pcap   ← matching network traffic
├── docs/
│   ├── index.html             ← browser log viewer (works offline too)
│   ├── STEP-BY-STEP.md        ← student walkthrough, Step 0 → Step 7
│   ├── instructor-guide.md
│   ├── student-worksheet.md
│   ├── cheat-sheet.md
│   └── report-template.md
└── tools/
    ├── generate_dataset.py    ← rebuilds the data (needs Python + scapy)
    ├── build_viewer.py        ← rebuilds docs/index.html from the CSV
    └── viewer_template.html
```

**Answer key:** kept out of this public repo on purpose so students can't see it. The instructor holds it separately.

## Rebuilding the data (optional, instructors)

```bash
pip install scapy
python3 tools/generate_dataset.py   # writes data/auth_logs.csv and data/network_capture.pcap
python3 tools/build_viewer.py       # embeds the CSV into docs/index.html
```

The generator uses a fixed random seed, so every run produces the same dataset.
