# Lab 4: Investigate a Simulated Credential Attack

**Day 2: Cyber Threats, Attack Investigation & AI Security** · V8 alignment: **2.3, 2.5, 4.8** · CompTIA **Security+ (SY0-701)** aligned

Students play SOC analysts. They investigate a simulated **password-spraying** attack against the fictional company `corp.local`, first in the **Windows authentication logs** and then in the **network traffic** with Wireshark, and they learn how the two sources of evidence confirm each other.

> ✅ **Classroom-safe:** all data is **synthetic**. No live malware, no real attack, no real users or passwords. No server or VM needed.

| | |
|---|---|
| ⏱ **Duration** | ≈ 75 minutes |
| 👥 **Class size** | Designed for **22 students → 11 pairs** |
| 🎯 **Level** | Beginner / Security+ candidates |
| 📥 **Get the files** | `git clone https://github.com/Tsuyoiman/cybersec-lab4-credential-attack.git` (or **Code → Download ZIP**) |
| 🔎 **Log search page** | **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/** (same data as `data/auth_logs.csv`) |

---

## 📑 Contents

1. [Security+ objectives covered](#1-security-objectives-covered)
2. [Learning outcomes](#2-learning-outcomes)
3. [Tools needed](#3-tools-needed)
4. [Instructor preparation](#4-instructor-preparation)
5. [Lab flow at a glance](#5-lab-flow-at-a-glance)
6. [Cheat sheet: what everything means](#6-cheat-sheet-what-everything-means)
7. [Step-by-step lab flow](#7-step-by-step-lab-flow)
   - [Step 0: Set up](#step-0-set-up-5-min)
   - [Step 1: The scenario](#step-1-the-scenario-5-min)
   - [Step 2: Teach the evidence](#step-2-teach-the-evidence-10-min)
   - [Step 3: Investigate the logs](#step-3-investigate-the-logs-20-min)
   - [Step 4: Confirm in Wireshark](#step-4-confirm-in-wireshark-20-min)
   - [Step 5: Build the timeline together](#step-5-build-the-timeline-together-5-min)
   - [Step 6: Response & prevention discussion](#step-6-response--prevention-discussion-10-min)
8. [Built-in false positives](#8-built-in-false-positives)
9. [Troubleshooting](#9-troubleshooting)
10. [Repository files](#10-repository-files)

---

## 1. Security+ objectives covered

| SY0-701 objective | How this lab covers it |
|---|---|
| **2.4** Analyze indicators of malicious activity | Password spraying vs brute force, account lockout, logins at unusual times, unknown source IP |
| **4.4** Security alerting and monitoring | Reviewing authentication logs, designing a detection rule |
| **4.6** Identity and access management | MFA, password policy, lockout thresholds, privileged accounts |
| **4.8** Incident response process | Detection → analysis → containment → eradication → recovery → lessons learned |
| **4.9** Use data sources to support an investigation | **Log data** (Windows Security events) + **packet captures** (Wireshark), correlated |

**Exam tip:** *"many accounts, one or two passwords each, from one source"* = **password spraying**. *"One account, many passwords"* = **brute force**.

---

## 2. Learning outcomes

By the end of the lab, students can:

1. Explain the difference between **brute force** and **password spraying**
2. Read Windows Security events **4624, 4625, 4740**, plus logon types and failure codes
3. Filter and count log data to find an **abnormal authentication pattern**
4. Use **Wireshark filters** to find the same attack in network traffic
5. Explain why **two evidence sources** (logs + network) are stronger than one
6. Build an **attack timeline**
7. Tell real attacks apart from **false positives**
8. Recommend **containment** and **prevention** measures

---

## 3. Tools needed

| Tool | Needed? | Notes |
|---|---|---|
| Web browser | ✅ Yes | Runs the log search page |
| **Wireshark** | ✅ Yes | Free: [wireshark.org/download](https://www.wireshark.org/download.html) |
| Git | ❌ Optional | To `git clone`. Without it, use **Code → Download ZIP** |
| Excel / Sheets / LibreOffice | ❌ Optional | Can open `auth_logs.csv`. **Excel is NOT required** |
| Internet | ❌ Optional | After cloning or downloading, everything works offline (`docs/index.html`) |

---

## 4. Instructor preparation

- [ ] **Install Wireshark** on every lab PC. This is the only install
- [ ] **Test the log search page:** open https://tsuyoiman.github.io/cybersec-lab4-credential-attack/ and check it shows **"326 of 326 events"**
- [ ] **Test Wireshark:** open `data/network_capture.pcap`, type `ntlmssp.auth.username` in the filter bar, press Enter, and check that 96 packets appear
- [ ] **No internet in the lab?** Copy the cloned folder to each PC or a USB drive. Students double-click `docs/index.html`
- [ ] Put students into **11 pairs**
- [ ] Have a whiteboard ready for the **timeline** (Step 5)

---

## 5. Lab flow at a glance

| Step | Activity | Time |
|---|---|---|
| 0 | Set up: clone the repo, open the log search page, open Wireshark | 5 min |
| 1 | The scenario | 5 min |
| 2 | Teach the evidence (attack types, Event IDs, codes) | 10 min |
| 3 | **Investigate the logs** in the log search page | 20 min |
| 4 | **Confirm in Wireshark** | 20 min |
| 5 | Build the timeline together | 5 min |
| 6 | Response & prevention discussion | 10 min |
| | **Total** | **≈ 75 min** |

---

## 6. Cheat sheet: what everything means

### 6.1 Brute force vs password spraying

| | Brute force | Password spraying |
|---|---|---|
| **Targets** | **One** account | **Many** accounts |
| **Passwords tried** | **Many** per account | **One or two** common ones (e.g. `Winter2026!`) |
| **Triggers lockout?** | Yes, quickly | Usually **no**, because each account gets only 1–2 tries and stays under the lockout limit |
| **What it looks like in logs** | Lots of failures for **one user** | Failures across **many users** from **one source IP**, close together |
| **Why attackers use it** | Simple | Quiet: avoids lockouts, and someone always uses a weak `Season+Year!` password |

### 6.2 Windows Security Event IDs

| Event ID | Name | Meaning |
|---|---|---|
| **4624** | Logon success | Someone **logged in successfully** |
| **4625** | Logon failure | A login **failed** (wrong password or unknown user) |
| **4740** | Account locked out | Too many failures, so the account was **locked** |

### 6.3 Logon types (the `LogonType` column)

| Type | Name | Meaning |
|---|---|---|
| **2** | Interactive | Typed at the **keyboard** of the PC |
| **3** | Network | Logged in **over the network** (file share / SMB) |
| **5** | Service | A Windows **service** started (e.g. backup) |
| **7** | Unlock | **Unlocked** a locked screen |
| **10** | RemoteInteractive | **Remote Desktop (RDP)**: full control of the computer from elsewhere |

### 6.4 Failure codes (the `SubStatus` column on 4625)

| Code | Meaning | What it tells the analyst |
|---|---|---|
| **0xC000006A** | Wrong password | The username **exists**, so the attacker had a list of real users |
| **0xC0000064** | User name does not exist | The attacker is **guessing** usernames (admin, test, guest…) |
| **0xC000006D** | Logon failure (in the `Status` column) | Appears on **every** failed logon |

### 6.5 Log search page: what each control does

| Control | What it does |
|---|---|
| **Event ID** dropdown | Show only successes (4624), failures (4625) or lockouts (4740) |
| **Source IP** box | Show only events from one IP address |
| **User** box | Show only events for one username |
| **Logon type** dropdown | Show only keyboard / network / RDP logons, etc. |
| **From / To** | Show only a time window |
| **Search anything** | Free-text search across all columns (e.g. a code like `0xC0000064`) |
| **Reset** | Clear all filters |
| **Download filtered CSV** | Save what's on screen as a CSV file |
| **Column headers** | Click to sort (▲ ascending / ▼ descending) |
| Underlined **IP or username** in the table | Click it to filter by it |
| **Count by Source IP** panel (right) | How many events each IP has **using the current filters**. The heading shows how many different IPs there are. Click a row to filter by it |
| **Count by User** panel (right) | How many events each user has using the current filters. The heading shows how many **different** users there are |
| Row colours | 🟢 green = 4624 success · 🔴 red = 4625 failure · 🟠 orange = 4740 lockout |

### 6.6 Wireshark screen: the three panes

| Pane | Where | What it shows |
|---|---|---|
| **Packet list** | Top | One row per packet: `No.`, `Time`, `Source`, `Destination`, `Protocol`, `Length`, `Info` |
| **Packet details** | Middle | The selected packet opened up as a tree. Click **`>`** to expand |
| **Packet bytes** | Bottom | Raw bytes (hex). Not needed for this lab |
| **Filter bar** | Above the packet list (green when valid, red when wrong) | Type a filter, then press **Enter** |

### 6.7 Wireshark filters used in this lab

| Filter | Meaning | What you'll see |
|---|---|---|
| `ntlmssp.auth.username` | Every packet that carries a **login username** | 96 login attempts |
| `smb2.nt_status == 0xc000006d` | Server replies saying **"logon failure"** | 95 failures |
| `smb2.cmd == 1 && smb2.nt_status == 0 && smb2.flags.response == 1` | Server replies to a login (`cmd == 1` = Session Setup) that **succeeded** (`nt_status == 0`) | 1 success |
| `ntlmssp.auth.username == "j.tan"` | Login attempts for one specific user | 2 attempts |
| `ip.addr == 203.0.113.77` | All traffic to or from one IP | Everything the attacker did |
| `tcp.port == 3389` | Traffic on port **3389 = Remote Desktop (RDP)** | The RDP session |
| `rdp` | Only RDP connection setup packets | Shows `mstshash=` (the username used for RDP) |
| `dns` | Name lookups | The attacker looking up `dc01.corp.local` |

### 6.8 Network terms

| Term | Meaning |
|---|---|
| **SMB / port 445** | Windows file sharing. Logins over the network use it |
| **NTLM / NTLMSSP** | The Windows login protocol inside SMB. It carries the **username** (not the password) |
| **RDP / port 3389** | Remote Desktop, for controlling a computer remotely |
| **PCAP** | A file containing **recorded** network traffic, replayed in Wireshark |
| **DC01 / 10.10.1.10** | The **domain controller**: the server that checks every login |

### 6.9 Optional: PowerShell instead of the log search page

```powershell
cd data
$log = Import-Csv .\auth_logs.csv
# Failed logons per source IP
$log | Where-Object EventID -eq 4625 | Group-Object SourceIP | Sort-Object Count -Descending | Select-Object Count, Name
# Everything one IP did, in time order
$log | Where-Object SourceIP -eq '203.0.113.77' | Format-Table TimeCreated, EventID, TargetUserName, LogonType, SubStatus
```

---

## 7. Step-by-step lab flow

> 🧑‍🏫 = instructor  👩‍💻 = students  ✅ = what they should see  💬 = teaching point to say out loud

### Step 0: Set up (5 min)

👩‍💻 **0.1 Get the files.** Open **PowerShell** or **Git Bash** and run:

```bash
git clone https://github.com/Tsuyoiman/cybersec-lab4-credential-attack.git
cd cybersec-lab4-credential-attack
```

No Git? On this GitHub page click the green **`<> Code`** button → **Download ZIP**, then right-click the ZIP → **Extract All**.

The folder contains:

| File | What it is | Open with |
|---|---|---|
| `data/auth_logs.csv` | DC01's Windows Security log (326 events) | Log search page (or Sheets / PowerShell) |
| `data/network_capture.pcap` | Recorded network traffic from the same night | **Wireshark** |
| `docs/index.html` | Log search page (offline copy) | Any browser, double-click |

👩‍💻 **0.2 Open the log search page:** https://tsuyoiman.github.io/cybersec-lab4-credential-attack/ (or double-click `docs/index.html`).

✅ The page title is **DC01 Security Log Viewer**, with **"326 of 326 events"** at the top right.

💬 *"This page is the same data as `auth_logs.csv`, just searchable, like the SIEM a real SOC uses."*

👩‍💻 **0.3 Open Wireshark** from the Start menu to check it works.

---

### Step 1: The scenario (5 min)

🧑‍🏫 **Read aloud:**

> "On the morning of **12 November 2026**, IT staff at Corp couldn't log in because their accounts were **locked out**. One user, **j.tan**, says she was asleep at 3 a.m., but her account shows activity at that time.
> You are the **SOC analyst on duty**. You have the security log from the domain controller **DC01** and a network recording from the same night. **Find out what happened.**"

👩‍💻 Pairs discuss for one minute: *"What kind of attack causes lockouts and a strange 3 a.m. login?"* Take two or three guesses from the class and keep them on the board.

---

### Step 2: Teach the evidence (10 min)

🧑‍🏫 **Ask:** *"What's the difference between trying 1,000 passwords on **one** account and trying **one** password on 1,000 accounts?"*

Teach from the cheat sheet:
1. [6.1 Brute force vs password spraying](#61-brute-force-vs-password-spraying)
2. [6.2 Event IDs](#62-windows-security-event-ids), [6.3 Logon types](#63-logon-types-the-logontype-column) and [6.4 Failure codes](#64-failure-codes-the-substatus-column-on-4625)

🧑‍🏫 **Demo the log search page (3 min)** using [6.5](#65-log-search-page-what-each-control-does):
1. Set **Event ID → 4624**. ✅ Only green rows.
2. Set **Event ID → 4625**. ✅ Only red rows.
3. Point to **Count by Source IP** on the right. 💬 *"This counts events per IP for whatever filter you set."*
4. **Stop here.** Don't click anything else. Let students find the attacker themselves.
5. Click **Reset**.

---

### Step 3: Investigate the logs (20 min)

👩‍💻 Pairs work in the **log search page**. 🧑‍🏫 Walk around, and after each sub-step ask one pair to share what they found.

#### 3.1 How big is the problem?
- **Clicks:** click **Reset**, then read the counter. Then set **Event ID → 4625 – Logon failed**.
- ✅ **326** events in total and **104** failed logons.

#### 3.2 Who is attacking?
- **Clicks:** keep **Event ID = 4625**. Look at the **Count by Source IP** panel on the right.
- ✅ **203.0.113.77** has **95** failures. The next IP has only **3**.
- 💬 *"One IP is responsible for almost every failure. It's also not an internal `10.10.x.x` address."*

#### 3.3 How many accounts did it try?
- **Clicks:** click **203.0.113.77** in the right panel (it fills the **Source IP** box). Look at the **Count by User** heading and list.
- ✅ The heading shows **(42 users)**. Most have only **2** failures each. Four accounts (the admins) have **5**, and j.tan has **1**. Hold on to those two oddities, because they come back in 3.6 and 3.7.
- 💬 *"Many accounts, few tries each: that's the pattern of **password spraying**."*

#### 3.4 What did the attacker know?
- **Clicks:** keep the IP filter. Type `0xC0000064` in **Search anything**.
- ✅ 16 rows for names like **admin, test, guest, user1, john.smith, backup, scanner, training**. These users **don't exist**.
- **Clicks:** clear the search box and type `0xC000006A` instead.
- ✅ Real employee names. The attacker had a list of **real usernames** and also guessed some common ones.
- Clear the search box.

#### 3.5 When did it happen?
- **Clicks:** click the **TimeCreated** column header (▲ oldest first). Scroll through.
- ✅ The attack runs in **three rounds**:

| Round | Time | What |
|---|---|---|
| 1 | **02:47:12 – 02:48:25** | Password #1 against all 42 names |
| 2 | **03:02:07 – 03:03:19** | Password #2 against all names |
| 3 | **03:15:04 – 03:15:38** | 3 more guesses each against 4 **admin** accounts |

- 💬 *"Attempts are 1–3 seconds apart, faster than any human types. This is a **script**."*

#### 3.6 Did the attacker get in?
- **Clicks:** keep **Source IP = 203.0.113.77**. Set **Event ID → 4624 – Logon success**.
- ✅ Two rows, both for **j.tan**:
  - **03:02:57**, logon type **3** (network). The round 2 password **worked**.
  - **03:21:37**, logon type **10** (**Remote Desktop**). The attacker then took control remotely.
- 💬 *"This explains j.tan's 3 a.m. activity. Her password was guessed, and the attacker used it to RDP in."*

#### 3.7 Why were IT staff locked out?
- **Clicks:** click **Reset**. Set **Event ID → 4740 – Account locked**.
- ✅ **administrator, it.admin, svc_backup, helpdesk** were locked at **03:15:30 – 03:15:39**.
- 💬 *"In round 3 the attacker focused on **privileged** accounts. Normal users got only 2 tries, under the limit of 5. The admin accounts got 5, so they locked."*

#### 3.8 False positive check: s.lim
- **Clicks:** **Reset**. Type `s.lim` in **User**.
- ✅ 3 failures at **09:05** from **10.10.20.39** (her own PC, `WS-119`), logon type **2** (at the keyboard), then **success at 09:06:03**.
- 💬 *"Not an attack: her own desk, during work hours, one account, and she got in a minute later. That's a typo. Analysts must not raise an alarm for normal behaviour."*

✅ **Checkpoint:** before moving on, every pair should be able to say *"203.0.113.77 password-sprayed 42 accounts between 02:47 and 03:15, got into j.tan, used RDP, and locked out 4 admin accounts."*

---

### Step 4: Confirm in Wireshark (20 min)

💬 *"Logs can be wrong, incomplete or deleted by an attacker. A good analyst confirms the story from a **second source**: the network. The log is the security guard's notebook, and Wireshark is the CCTV recording."*

#### 4.1 Open the recording
1. Open **Wireshark**.
2. Click **File → Open**.
3. Go to the lab folder → `data` → select **`network_capture.pcap`** → **Open**.
4. Click **View → Time Display Format → Date and Time of Day**.

✅ About **1,237 packets**, with dates on **2026-11-12**.

> ⚠️ Wireshark shows times in **your PC's time zone**, and the logs are **UTC+8 (Singapore)**. If the PC is in another zone the **hours** will differ, but the **minutes:seconds** still match.

#### 4.2 Find the login attempts
1. Click the **filter bar** (above the packet list, *"Apply a display filter…"*).
2. Type `ntlmssp.auth.username`
3. Press **Enter**.

✅ **96 packets**. Look at the columns:
- **Source:** always **203.0.113.77** (the attacker)
- **Destination:** **10.10.1.10** (DC01)
- **Protocol:** **SMB2**
- **Info:** `Session Setup Request, NTLMSSP_AUTH, User: CORP\user1`, then `CORP\s.lim`, `CORP\bb.kumar`…

💬 *"The **Info** column already shows the username. It's the same IP and the same names we found in the logs."*

#### 4.3 See the username inside the packet (packet details)
1. With the 4.2 filter still on, **single-click the first packet** in the list.
2. In the **middle pane (packet details)**, click the **`>`** arrows to expand, in this order:
   1. **SMB2 (Server Message Block Protocol version 2)**
   2. **Session Setup Request (0x01)**
   3. **Security Blob**
   4. **GSS-API Generic Security Service Application Program Interface**
   5. **Simple Protected Negotiation**
   6. **negTokenTarg**
   7. **NTLM Secure Service Provider**
3. Near the bottom of that section:
   - **Domain name:** `CORP`
   - **User name:** the account being tried (e.g. `user1`)
   - **Host name:** `DESKTOP-7Q1X9ZA` (the attacker's computer)

💬 *"The login message carries the **username**, not the password. The password is protected inside the NTLM Response. The **Host name** matches the `WorkstationName` in the logs."*

> 💡 Double-clicking a packet opens it in a **separate window** with the same tree. It's easier to single-click and use the middle pane.

#### 4.4 Make the username a column
1. In the packet details, **right-click "User name"**.
2. Click **Apply as Column**.

✅ A new **User name** column appears in the packet list, so every attempt's username is visible at a glance. Scroll down to watch the spray move through the user list.

> To remove it later: right-click the column header → **Remove this Column**.

#### 4.5 See the failures
1. Click the filter bar, delete the old filter, type `smb2.nt_status == 0xc000006d`, then press **Enter**.

✅ **95 packets**, **Source: 10.10.1.10** (the server answering), **Info:** `Session Setup Response, Error: STATUS_LOGON_FAILURE`.

💬 *"95 failures, the same number as the 4625 events from this IP in the logs."*

#### 4.6 Find the one successful login
1. Type `smb2.cmd == 1 && smb2.nt_status == 0 && smb2.flags.response == 1` and press **Enter**.

✅ **1 packet** (No. **875**) at **03:02:57**, **Info:** `Session Setup Response` with **no error**. The server said "OK".

2. To see **who** logged in, type `ntlmssp.auth.username == "j.tan"` and press **Enter**.

✅ **2 packets**: one at **02:47:53** (round 1, failed) and one at **03:02:57** (No. **874**), the request right before the success.

💬 *"Same time as Event 4624 for j.tan in the logs. The network confirms it: **j.tan was compromised at 03:02:57**."*

#### 4.7 See the Remote Desktop session
1. Type `rdp` and press **Enter**.

✅ **2 packets** at **03:21:31**:
- No. 1182 from **203.0.113.77**, **Info:** `Cookie: mstshash=j.tan, Negotiate Request`
- No. 1183 from **10.10.1.10**, **Info:** `Negotiate Response`

2. Type `tcp.port == 3389` and press **Enter**.

✅ **55 packets**. After the handshake the traffic shows as **TLSv1.2 Application Data** because RDP is encrypted.

💬 *"`mstshash` is the username the RDP client sends. The attacker used **j.tan's stolen password** to open Remote Desktop. We can't see what they did inside because it's encrypted, but the **log** (4624 type 10 at 03:21:37) confirms the session logged on."*

#### 4.8 The big picture (statistics)
1. Clear the filter (click the **X** in the filter bar).
2. Click **Statistics → Conversations**, then the **IPv4** tab.

✅ **203.0.113.77 ↔ 10.10.1.10** has about **1,209 packets**. Every other conversation has fewer than 10.

💬 *"Even without filters, Statistics shows one IP dominating the traffic to the server, another quick way to spot an attacker."*

3. Optional: type `dns` and press **Enter**. ✅ At **02:46:58** the attacker looked up `dc01.corp.local`, **14 seconds before** the attack started. That's reconnaissance.

✅ **Checkpoint:** every finding from the logs (IP, usernames, failures, j.tan success, RDP) is **confirmed** on the network.

---

### Step 5: Build the timeline together (5 min)

🧑‍🏫 Build this on the whiteboard, asking pairs to call out each line:

| Time (UTC+8) | What happened | Log evidence | Network evidence |
|---|---|---|---|
| 02:46:58 | Attacker looks up the domain controller | — | DNS query for `dc01.corp.local` |
| 02:47:12 – 02:48:25 | **Round 1:** password #1 against 42 names | 42 × **4625** | 42 × `STATUS_LOGON_FAILURE` |
| 03:02:07 – 03:03:19 | **Round 2:** password #2 against all names | 41 × **4625** | 41 × `STATUS_LOGON_FAILURE` |
| **03:02:57** | **j.tan compromised** | **4624** type 3 | Session Setup Response, success |
| 03:15:04 – 03:15:38 | **Round 3:** 3 more guesses × 4 admin accounts | 12 × **4625** | 12 × `STATUS_LOGON_FAILURE` |
| 03:15:30 – 03:15:39 | 4 admin accounts **locked out** | 4 × **4740** | *(not visible: happens inside the server)* |
| **03:21:31 – 03:21:37** | Attacker **RDPs in as j.tan** | **4624** type 10 | RDP `mstshash=j.tan`, port 3389 |

💬 *"Some evidence exists **only in logs** (the lockouts) and some shows best on the **network** (the RDP connection details). That's why analysts need both."*

---

### Step 6: Response & prevention discussion (10 min)

🧑‍🏫 Ask the class, and write the answers in two columns on the board:

**"What do we do right now?" (containment & recovery)**
- Disable **j.tan** and reset her password, and end her sessions
- **Block 203.0.113.77** at the firewall
- Check what j.tan's account did after 03:21 (files, new accounts, scheduled tasks)
- Unlock the 4 admin accounts **after** confirming they weren't compromised, and reset their passwords

**"How do we stop this happening again?" (prevention)**
- **MFA** on all accounts, especially remote access and admins
- **Don't expose RDP/SMB to the internet.** Require a VPN
- **Banned-password list** to block `Season+Year!` style passwords
- **Detection rule:** alert when one IP fails against **10+ different accounts** in 30 minutes, or when a **4624 follows many 4625s** from the same IP
- Separate admin accounts, and don't let service accounts log in interactively

🧑‍🏫 **Final discussion questions:**
1. *"Why were admins locked out but normal users weren't?"* Normal users got 2 tries, under the threshold of 5. The admins got 5.
2. *"If the attacker waited one hour between tries, how would we still catch them?"* Count **distinct usernames per IP over 24 hours**, and alert on logins from **new IPs or at unusual hours**.
3. *"Were our guesses from Step 1 right?"*

💬 **Security+ wrap-up:** map the lab to the incident response process: **Detection** (lockouts reported) → **Analysis** (logs + PCAP) → **Containment** (block IP, disable j.tan) → **Eradication / Recovery** (reset passwords, unlock accounts) → **Lessons learned** (MFA, detection rule).

---

## 8. Built-in false positives

The data includes normal activity that *looks* suspicious, so students practise judgement:

| Event | Looks like | Actually |
|---|---|---|
| `s.lim`: 3 × 4625 at 09:05 | Brute force | Typo at her own desk (type 2, her own PC), then success |
| `svc_backup` logons at 01:00 and 23:00 | Night-time activity | Scheduled backup service (type 5, no source IP) |
| `it.admin` RDP at 21:14 | Remote login at night | IT admin over the internal VPN range `10.10.99.x` from a known IT laptop |
| Single 4625s during the day | Attacks | Ordinary typos, each followed by a success seconds later |

---

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `git` is not recognized | Git isn't installed. Use **Code → Download ZIP** |
| Log search page won't load | Double-click `docs/index.html` in the lab folder |
| Log search shows 0 events | Click **Reset** |
| Wireshark: "file not found" | **Extract** the ZIP first, don't just open it |
| Filter bar turns **red** | Typo in the filter. Copy it exactly from [6.7](#67-wireshark-filters-used-in-this-lab) |
| Filter is green but no packets | Press **Enter** after typing |
| Times don't match the logs | **View → Time Display Format → Date and Time of Day**. Hours may differ by time zone, so compare minutes:seconds |
| Can't find "User name" | Apply `ntlmssp.auth.username` first, single-click a packet, then expand the tree in the order in [4.3](#43-see-the-username-inside-the-packet-packet-details) |
| Too many columns after "Apply as Column" | Right-click the column header → **Remove this Column** |

---

## 10. Repository files

```
├── README.md                  ← this guide: flow, cheat sheet, exact steps
├── data/
│   ├── auth_logs.csv          ← DC01 Windows Security log (326 events, 12 Nov 2026, UTC+8)
│   └── network_capture.pcap   ← recorded network traffic from the same night (Wireshark)
├── docs/
│   └── index.html             ← log search page (same data as auth_logs.csv; works offline)
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
