# Lab 4: Investigate a Simulated Credential Attack

**Day 2: Cyber Threats, Attack Investigation & AI Security** · V8 alignment: **2.3, 2.5, 4.8** · CompTIA **Security+ (SY0-701)** aligned

Students play SOC analysts. They investigate a simulated **password-spraying** attack against the fictional company `corp.local`: they find the attacker in Windows authentication logs, confirm it in network traffic with Wireshark, build a timeline and write an incident report with recommendations.

> ✅ **Classroom-safe:** all data is **synthetic**. No live malware, no real attack, no real users or passwords. No server or VM needed.

| | |
|---|---|
| ⏱ **Duration** | ≈ 75 minutes |
| 👥 **Class size** | Designed for **22 students → 11 pairs** (or 6–7 groups of 3–4) |
| 🎯 **Level** | Beginner / Security+ candidates |
| 📥 **Get the files** | `git clone https://github.com/Tsuyoiman/cybersec-lab4-credential-attack.git` (or **Code → Download ZIP**) |
| 🔎 **Log search page** | **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/** (same data as `data/auth_logs.csv`) |
| ✍️ **Fillable worksheet** | **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/worksheet.html** |

---

## 📑 Contents

1. [Security+ objectives covered](#1-security-objectives-covered)
2. [Learning outcomes](#2-learning-outcomes)
3. [Tools needed](#3-tools-needed)
4. [Instructor preparation (before class)](#4-instructor-preparation-before-class)
5. [Lesson flow at a glance](#5-lesson-flow-at-a-glance)
6. [Step-by-step: teaching the lab](#6-step-by-step-teaching-the-lab)
   - [Step 0: Set up](#step-0-set-up-5-min)
   - [Step 1: Scenario](#step-1-scenario-5-min)
   - [Step 2: Teach the evidence](#step-2-teach-the-evidence-10-min)
   - [Step 3: Part A, investigate the logs](#step-3-part-a-investigate-the-logs-20-min)
   - [Step 4: Part B, confirm in Wireshark](#step-4-part-b-confirm-in-wireshark-15-min)
   - [Step 5: Build the timeline](#step-5-build-the-timeline-5-min)
   - [Step 6: Incident report](#step-6-incident-report-10-min)
   - [Step 7: Debrief](#step-7-debrief-5-min)
7. [Built-in false positives](#7-built-in-false-positives)
8. [Grading rubric](#8-grading-rubric-20-points)
9. [Troubleshooting](#9-troubleshooting)
10. [Repository files](#10-repository-files)

---

## 1. Security+ objectives covered

| SY0-701 objective | How this lab covers it |
|---|---|
| **2.4** Analyze indicators of malicious activity | Password spraying vs brute force, account lockout, logins at unusual times, unknown source IP |
| **4.4** Security alerting and monitoring | Reviewing authentication logs, writing a detection idea for spraying |
| **4.6** Identity and access management | MFA, password policy, lockout thresholds, privileged accounts |
| **4.8** Incident response process | Detection → analysis → containment → eradication → recovery → lessons learned |
| **4.9** Use data sources to support an investigation | **Log data** (Windows Security events) + **packet captures** (Wireshark), correlated |

**Exam tip to tell students:** on Security+, *"many accounts, one or two passwords each, from one source"* = **password spraying**. *"One account, many passwords"* = **brute force**. *"Account lockouts across many users"* is a classic **indicator** of either.

---

## 2. Learning outcomes

By the end of the lab, students can:

1. Explain the difference between **brute force** and **password spraying**
2. Read Windows Security events **4624, 4625, 4740**, plus logon types and failure codes
3. Filter and count log data to find an **abnormal authentication pattern**
4. Use **Wireshark** to confirm log findings in network traffic (**correlation**)
5. Build an **attack timeline**
6. Tell real attack activity apart from **false positives**
7. Write an **incident report** with realistic account-protection recommendations

---

## 3. Tools needed

| Tool | Needed? | Notes |
|---|---|---|
| Web browser | ✅ Yes | Runs the log search page and worksheet. Enough for all of Part A |
| Git | ❌ Optional | To `git clone` the repo. Without it, use **Download ZIP** |
| **Wireshark** | ✅ Yes | Free: [wireshark.org/download](https://www.wireshark.org/download.html). Needed for Part B |
| Excel / Google Sheets / LibreOffice | ❌ Optional | Can open the CSV instead of the log search page. **Excel is NOT required** |
| PowerShell | ❌ Optional | Built into Windows. Commands in the [cheat sheet](docs/cheat-sheet.md) |
| Internet | ❌ Optional | Once the ZIP is downloaded, everything works offline (`docs/index.html`) |

---

## 4. Instructor preparation (before class)

- [ ] **Install Wireshark** on every lab PC. This is the only install
- [ ] **Test the log search page:** open https://tsuyoiman.github.io/cybersec-lab4-credential-attack/ and check it shows **"326 of 326 events"**
- [ ] **Test Wireshark:** download the ZIP, open `data/network_capture.pcap`, type `ntlmssp.auth.username` in the filter bar and check that packets appear
- [ ] **No internet in the lab?** Copy the folder to each PC or a USB drive. Students double-click `docs/index.html` (log search) and `docs/worksheet.html` (worksheet)
- [ ] **Worksheet:** students fill in the online worksheet (link above) and submit the downloaded file. A printable copy is in [`docs/student-worksheet.md`](docs/student-worksheet.md)
- [ ] **Git (optional):** if lab PCs have Git, students clone the repo. Otherwise they use Download ZIP
- [ ] **Answer key:** `ANSWER-KEY.md` is kept **outside this public repo** so students can't see it. Get it from the lab owner
- [ ] Put students into **11 pairs**

---

## 5. Lesson flow at a glance

| Step | Activity | Who | Time |
|---|---|---|---|
| 0 | Set up: git clone (or Download ZIP), open log search page + worksheet, open Wireshark | Students | 5 min |
| 1 | Scenario + first guess | Instructor | 5 min |
| 2 | Teach the evidence (attack types, Event IDs, codes) + demo | Instructor | 10 min |
| 3 | **Part A:** investigate the logs (A1–A10) | Pairs | 20 min |
| 4 | **Part B:** confirm in Wireshark (B1–B5) | Pairs | 15 min |
| 5 | Build the timeline | Pairs | 5 min |
| 6 | Write the incident report | Pairs | 10 min |
| 7 | Present + debrief | Whole class | 5 min |
| | **Total** | | **≈ 75 min** |

---

## 6. Step-by-step: teaching the lab

> 🧑‍🏫 = what the instructor does / says  👩‍💻 = what students do  ✍️ = what students write on the worksheet

### Step 0: Set up (5 min)

👩‍💻 **Students:**

**0.1 Get the lab files: clone the repository (preferred)**

Open a terminal (Windows: **PowerShell** or **Git Bash**) and run:

```bash
git clone https://github.com/Tsuyoiman/cybersec-lab4-credential-attack.git
cd cybersec-lab4-credential-attack
```

**No Git installed?** Download manually instead: on this page click the green **`<> Code`** button → **Download ZIP**, then right-click the ZIP → **Extract All**.

Either way, you now have a folder with:

| File | What it is | Open with |
|---|---|---|
| `data/auth_logs.csv` | DC01 Windows Security log (326 events) | Log search page, Google Sheets, LibreOffice, Excel or PowerShell |
| `data/network_capture.pcap` | Network traffic from the same night | **Wireshark** |
| `docs/index.html` | **Log search page** (offline copy) | Any browser, double-click |
| `docs/worksheet.html` | **Fillable worksheet** (offline copy) | Any browser, double-click |

**0.2 Open the log search page**

- Online: **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/**
- Offline: double-click `docs/index.html` in the folder you just cloned or extracted

> ℹ️ **The log search page shows exactly the same 326 events as `data/auth_logs.csv`.** It's the CSV loaded into a searchable page, like a SIEM, so students can filter, sort and count without Excel. Using the page or the CSV gives the same answers.

You should see **"326 of 326 events"** at the top right.

**0.3 Open the worksheet**

- Online: **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/worksheet.html**
- Offline: double-click `docs/worksheet.html`

Answers save automatically in the browser. At the end, click **Download my answers** (or **Print / Save as PDF**) and submit the file.

**0.4 Check Wireshark** opens from the Start menu.

🧑‍🏫 **Instructor:** walk around and check every pair has the repo cloned (or the ZIP **extracted**, not just opened), the log search page showing 326 events, and the worksheet open.

---

### Step 1: Scenario (5 min)

🧑‍🏫 **Read aloud:**

> "On the morning of **12 November 2026**, IT staff at Corp couldn't log in because their accounts were **locked out**. One user, **j.tan**, says she was asleep at 3 a.m., but her account shows activity at that time.
> You are the **SOC analyst on duty**. You have the security log from the domain controller **DC01** and a network capture from the same night. **Find out what happened, prove it, and recommend what to do.**"

👩‍💻 **Students:** discuss with their partner for one minute: *"What kind of attack causes many lockouts and a strange 3 a.m. login?"*

✍️ Write the guess at the top of the worksheet. They'll check it in Step 7.

---

### Step 2: Teach the evidence (10 min)

🧑‍🏫 **Ask the class:**
> "What's the difference between trying **1,000 passwords on one account** and trying **one password on 1,000 accounts**?"

Draw both on the board:

| | Brute force | Password spraying |
|---|---|---|
| Targets | **One** account | **Many** accounts |
| Passwords | **Many** per account | **One or two** common ones (`Winter2026!`) |
| Lockout? | Yes, quickly | Usually **no**, because each account stays under the threshold |
| In the logs | Lots of failures for one user | Failures across many users **from one source**, close together |

**Key point:** attackers spray because every company has someone using `Season+Year!`, and spraying avoids lockouts.

🧑‍🏫 **Teach the evidence table** (put it on a slide or the board):

| Item | Meaning |
|---|---|
| **Event 4624** | Successful logon |
| **Event 4625** | **Failed** logon |
| **Event 4740** | Account **locked out** |
| **Logon type 2** | At the keyboard (interactive) |
| **Logon type 3** | Over the network (file share / SMB) |
| **Logon type 10** | **Remote Desktop (RDP)** |
| **0xC000006A** | Wrong password, but **the user exists** |
| **0xC0000064** | **User name doesn't exist** (the attacker is guessing names) |

🧑‍🏫 **3-minute demo** in the log search page:
1. Set **Event ID → 4624**: green rows = success.
2. Set **Event ID → 4625**: red rows = failure.
3. Point to the **Count by Source IP** panel on the right: *"This counts events per IP using whatever filter you set."*
4. **Stop here.** Don't click the top IP. Let students discover it.
5. Click **Reset**.

---

### Step 3: Part A, investigate the logs (20 min)

👩‍💻 Pairs use the **log search page** and answer **A1–A10** in the [online worksheet](https://tsuyoiman.github.io/cybersec-lab4-credential-attack/worksheet.html).

| # | Student does this in the log search page | ✍️ Writes down |
|---|---|---|
| **3.1** | No filters, read the counter. Then set **Event ID → 4625** | **A1:** total events, number of failures |
| **3.2** | Keep 4625. Look at **Count by Source IP** (sorted highest first) | **A2:** top IP and its count. Is it normal compared with #2? |
| **3.3** | Click that IP in the right panel (it fills the **Source IP** filter). Look at **Count by User** | **A3:** how many *different* usernames it tried |
| **3.4** | Type `0xC0000064` in **Search anything**. Look at the usernames. Then clear the box | **A4:** what `0xC000006A` vs `0xC0000064` tells you about the attacker |
| **3.5** | Click the **TimeCreated** header (▲ oldest first, ▼ newest first) | **A5:** first and last failure time |
| **3.6** | Think about: one source vs many accounts, tries per account, seconds between tries | **A6:** brute force or spraying, with **2 pieces of evidence** |
| **3.7** | Keep the attacker IP filter. Set **Event ID → 4624** | **A7:** account, time, logon type of any success |
| **3.8** | **Reset**. Set **Event ID → 4740** | **A8:** which accounts were locked out and what they have in common |
| **3.9** | **Reset**. Filter **Source IP** = attacker IP, Event ID = All, sort ▲, scroll to the end | **A9:** what the attacker did *after* getting in (check the logon type) |
| **3.10** | **Reset**. Type `s.lim` in **User**. Compare time, source IP, logon type and what happened next | **A10:** is s.lim part of the attack? Why or why not? |

🧑‍🏫 **Hints if a pair is stuck:**
- Stuck at A2 → *"Filter to failures first, then look at the counts on the right."*
- Stuck at A6 → *"Count how many **different** users that one IP tried, and how many times each."*
- Stuck at A7 → *"Filter by the attacker IP only, then switch to successes."*
- Stuck at A10 → *"Is she logging in from her **own** PC? At her keyboard or over the network? Did she succeed after?"*

> 💡 Pairs that prefer spreadsheets can open `data/auth_logs.csv` in Google Sheets / LibreOffice (**Data → Filter**, **Insert → Pivot table**) or use the PowerShell commands in the [cheat sheet](docs/cheat-sheet.md).

✅ **Checkpoint:** every pair knows the **attacker IP**, the **attack type**, the **compromised account** and the **time window** before moving on.

---

### Step 4: Part B, confirm in Wireshark (15 min)

🧑‍🏫 **Say:** *"Logs can be wrong or deleted. A good analyst confirms the story from a second source: the network."*

👩‍💻 **Students:**

**4.1 Open the capture**
1. Wireshark → **File → Open** → `data/network_capture.pcap` (in the cloned or extracted folder).
2. **View → Time Display Format → Date and Time of Day** so times match the log.

**4.2 See the login attempts** → ✍️ **B1**
- In the green filter bar type `ntlmssp.auth.username`, then press **Enter**.
- Look at the **Source** column. Which IP sends all the attempts? Does it match Part A?

**4.3 Show the usernames** → ✍️ **B2**
1. Click any packet.
2. In the middle pane expand **SMB2 → Session Setup Request → Security Blob → … → NTLM Secure Service Provider**.
3. Right-click **User name** → **Apply as Column**.
4. Write down 3 usernames that also appear in the log.

**4.4 Find the one successful login** → ✍️ **B3**
- Filter: `smb2.cmd == 1 && smb2.nt_status == 0 && smb2.flags.response == 1`
- One reply = success. Write down its time. Does it match A7?
- Optional: `smb2.nt_status == 0xc000006d` shows all the failures ("logon failure").

**4.5 What happened next** → ✍️ **B4**
- Filter: `tcp.port == 3389`
- Find **Cookie: mstshash=** in the Info column. Which username is it?
- Port 3389 = **Remote Desktop**. What does that confirm?

**4.6 Why two sources?** → ✍️ **B5**
- Discuss and write: why is evidence stronger when **logs + network** agree?

📸 Students take screenshots of 4.2, 4.4 and 4.5 for the report.

🧑‍🏫 **Common issues:**
- *"Times don't match."* → Wireshark uses the PC's time zone and the log is UTC+8 (Singapore). Compare **minutes:seconds**.
- *"No packets after filtering."* → Check spelling (all lowercase), then press Enter.

✅ **Checkpoint:** the IP, the successful login and the RDP session all match Part A.

---

### Step 5: Build the timeline (5 min)

👩‍💻 Pairs fill in **Part C** of the worksheet, in time order:

| Time | What happened | Evidence |
|---|---|---|
| *first attacker activity* | | |
| *spray round(s)* | | |
| *successful login* | | |
| *lockouts* | | |
| *remote desktop session* | | |

🧑‍🏫 **Hint:** *"Filter by the attacker IP, sort by time, and look for **gaps**. Gaps separate the attack rounds."*

---

### Step 6: Incident report (10 min)

👩‍💻 Pairs copy the [report template](docs/report-template.md) into a Word / Google doc and complete it. Attach the worksheet file they downloaded (**Download my answers**):

1. **Summary**: 2–3 sentences a manager understands
2. **Attack details**: IP, type, time window, accounts targeted, compromised account
3. **Timeline**: from Step 5
4. **Evidence**: screenshots
5. **False positives reviewed**: e.g. s.lim
6. **Recommendations**: at least **2 immediate** + **3 long-term**
7. **Lessons learned**: what would have caught this sooner?

🧑‍🏫 **Prompt for recommendations:** *"Think about passwords, MFA, remote access, blocking, detection rules and admin accounts."* This links to Security+ **4.6** (IAM) and **4.8** (incident response: containment → eradication → recovery).

---

### Step 7: Debrief (5 min)

🧑‍🏫 Ask 2–3 pairs to present their timeline, then discuss:

1. **"Why were the admin accounts locked out but normal users weren't?"**
   *Normal accounts only got 2 guesses, under the lockout threshold. The attacker focused extra guesses on the admin accounts, which pushed them over it.*
2. **"s.lim had 3 failures. Why isn't she part of the attack?"**
   *Her own PC, at the keyboard (type 2), during work hours, only her account, and she succeeded a minute later. That's a normal typo.*
3. **"If the attacker waited one hour between tries, how would you catch it?"**
   *Count **distinct usernames per source IP over 24 h**, alert on a **4624 after many 4625s from the same IP**, and alert on logins from **new IPs or at unusual hours**.*

👩‍💻 Students check the guess they wrote in Step 1.

**Security+ wrap-up:** map the lab to the incident response phases: **Detection** (lockouts reported) → **Analysis** (logs + PCAP) → **Containment** (block the IP, disable j.tan) → **Eradication / Recovery** (reset passwords, unlock accounts) → **Lessons learned** (MFA, detection rule).

---

## 7. Built-in false positives

The dataset includes normal activity that *looks* suspicious, so students practise judgement:

| Event | Looks like | Actually |
|---|---|---|
| `s.lim`: 3 × 4625 at 09:05 | Brute force | She mistyped her password at her own desk (type 2, own PC), then succeeded |
| `svc_backup` logons at 01:00 and 23:00 | Night-time activity | Scheduled backup service (type 5, no source IP) |
| `it.admin` RDP at 21:14 | Remote login at night | IT admin over the internal VPN range `10.10.99.x` from a known IT laptop |
| Single 4625s during the day | Attacks | Ordinary typos, each followed by a success seconds later |

---

## 8. Grading rubric (20 points)

| Area | Points |
|---|---|
| Correct attacker IP, attack type and time window | 4 |
| Compromised account identified with evidence | 4 |
| Lockouts explained (which accounts, why) | 2 |
| Wireshark confirmation (B1–B4) | 4 |
| False positive (s.lim) correctly dismissed with reasoning | 2 |
| Recommendations: realistic, both immediate and long-term | 4 |

Grade **reasoning**, not just labels. *"Spraying **because** one IP tried 42 different users with only 2–3 attempts each"* scores higher than *"spraying"*.

---

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| Log search page won't load | Open `docs/index.html` from the cloned or extracted folder (double-click) |
| `git` is not recognized | Git isn't installed. Use **Code → Download ZIP** instead |
| Worksheet answers disappeared | They save per browser. Use the same browser, and always click **Download my answers** before leaving |
| Log search shows 0 events | Click **Reset** |
| Wireshark: "file not found" | **Extract** the ZIP first, don't just open it |
| Wireshark: no packets after filter | Check spelling, e.g. `ntlmssp.auth.username` (all lowercase), then press Enter |
| Wireshark times don't match log | **View → Time Display Format → Date and Time of Day**. Hours may differ by time zone, so compare minutes:seconds |
| Can't find "User name" in packet details | Apply the 4.2 filter first, select a packet, expand **SMB2 → Security Blob → NTLMSSP** |
| No Excel | Not needed. Use the log search page |

---

## 10. Repository files

```
├── README.md                  ← this guide (instructor + student steps)
├── data/
│   ├── auth_logs.csv          ← DC01 security log export (326 events, 12 Nov 2026, UTC+8)
│   └── network_capture.pcap   ← matching network traffic (open in Wireshark)
├── docs/
│   ├── index.html             ← log search page (same data as auth_logs.csv; works offline)
│   ├── worksheet.html         ← fillable worksheet (saves, downloads, prints)
│   ├── STEP-BY-STEP.md        ← points to the steps in this README
│   ├── student-worksheet.md   ← printable copy of the worksheet
│   ├── cheat-sheet.md         ← Event IDs, codes, log search / spreadsheet / PowerShell / Wireshark tips
│   ├── report-template.md     ← incident report template
│   └── instructor-guide.md    ← extra teaching notes
└── tools/
    ├── generate_dataset.py    ← rebuilds the data (Python + scapy)
    ├── build_viewer.py        ← rebuilds docs/index.html from the CSV
    └── viewer_template.html
```

<details>
<summary><b>Rebuilding the data (optional)</b></summary>

```bash
pip install scapy
python3 tools/generate_dataset.py   # writes data/auth_logs.csv and data/network_capture.pcap
python3 tools/build_viewer.py       # embeds the CSV into docs/index.html
```
The generator uses a fixed random seed, so every run produces the same dataset.
</details>
