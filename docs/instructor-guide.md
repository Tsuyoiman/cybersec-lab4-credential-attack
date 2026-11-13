# Lab 4 Instructor Guide: Investigate a Simulated Credential Attack

**Class size:** designed for 22 students → **11 pairs** (or 6–7 groups of 3–4)
**Duration:** ≈ 75 minutes · **V8 alignment:** 2.3, 2.5, 4.8

---

## Before class (checklist)

- [ ] Every PC has a **web browser** (for `docs/index.html`). That's enough for Part A
- [ ] **Wireshark** installed on every PC (free, wireshark.org). This is the only install needed
- [ ] Repo downloaded (Code → Download ZIP) and copied to each PC, a shared folder or a USB drive, **or** students use the GitHub Pages link
- [ ] Open `network_capture.pcap` once on a lab PC to confirm Wireshark works
- [ ] Worksheet shared (print, or share `docs/student-worksheet.md`)
- [ ] **Answer key** kept on your machine only. It is not in this repo

> **No Excel?** No problem. Students can use the browser viewer (`docs/index.html`), Google Sheets, LibreOffice Calc, or PowerShell. All are covered in the cheat sheet.

---

## Lesson flow

### 1. Hook (10 min)
Read the scenario aloud (from the README). Then ask:

> "What's the difference between trying 1,000 passwords on **one** account and trying **one** password on 1,000 accounts?"

Draw both on the board. Key points to land:
- **Brute force:** many passwords against one account. Lockout stops it fast.
- **Password spraying:** a few common passwords against many accounts. Each account sees only 1–2 failures, **under the lockout threshold**, so the attack stays quiet.
- Attackers spray because some users always pick `Season+Year!` style passwords.

### 2. Evidence cheat sheet (10 min)
Walk through `docs/cheat-sheet.md`: Event IDs 4624 / 4625 / 4740, logon types 2 / 3 / 10, SubStatus `0xC000006A` vs `0xC0000064`.

**Live demo (3 min):** open the browser viewer, set *Event ID = 4625*, and point at the **Count by Source IP** panel. Stop there and **don't** click the top IP. Let students discover it.

### 3. Part A: The logs (20 min)
Pairs answer A1–A10 on the worksheet. Walk around and use these prompts:
- Stuck at A2 → "Filter to failures first, then look at the counts on the right."
- Stuck at A6 → "Count how many *different users* that one IP tried."
- Stuck at A7 → "Filter by the attacker IP only, and remove the Event ID filter."

### 4. Part B: Wireshark (15 min)
Pairs answer B1–B5. Common issues:
- **Times don't match the log.** Set *View → Time Display Format → Date and Time of Day*. Wireshark uses the PC's time zone and the log is UTC+8.
- **"I don't see usernames."** Use the filter `ntlmssp.auth.username`, expand *SMB2 → Session Setup → Security Blob → NTLMSSP*, then right-click *User name → Apply as Column*.

### 5. Report (15 min)
Each pair completes `docs/report-template.md` (or Parts C–D of the worksheet). They take screenshots as evidence.

### 6. Debrief (5 min)
Ask 2–3 pairs to present their timeline. Then discuss:
1. "Why didn't regular users get locked out, but the admin accounts did?"
2. "s.lim had 3 failures. Why isn't she part of the attack?"
3. "If the attacker waited one hour between tries, how would you still catch it?"
   (Answer: count **distinct usernames per source IP over a longer window**, alert on any 4624 that follows many 4625s from the same IP, and alert on logins from unusual IPs or times.)

---

## What students learn

| Skill | Where in the lab |
|---|---|
| Brute force vs password spraying | Hook, A6 |
| Reading Windows auth events (4624/4625/4740, logon types, status codes) | Cheat sheet, A1–A9 |
| Filtering / counting log data to find anomalies | A2–A5 |
| Separating false positives from real attacks | A10 |
| Using Wireshark to confirm findings (correlation) | B1–B5 |
| Building an attack timeline | Part C |
| Recommending account protections | Part D, report |

---

## Built-in "traps" (false positives)

The dataset includes a few normal events that look suspicious, so students practise judgement:

| Event | Looks like | Actually |
|---|---|---|
| `s.lim`, 3 × 4625 at 09:05 | Brute force | She mistyped her own password at her own desk (type 2, her own PC), then succeeded |
| `svc_backup` logons at 01:00 and 23:00 | Night-time activity | Scheduled backup service (type 5, no source IP) |
| `it.admin` RDP at 21:14 | Remote login at night | IT admin over the internal VPN range `10.10.99.x` from a known IT laptop |
| A few single 4625s during the day | Attacks | Ordinary typos, each followed by a success seconds later |

---

## Grading suggestion (20 points)

| Area | Points |
|---|---|
| Correct attacker IP, attack type, and time window | 4 |
| Compromised account identified with evidence | 4 |
| Lockouts explained (which accounts, why) | 2 |
| Wireshark confirmation (B1–B4) | 4 |
| False positive (s.lim) correctly dismissed with reasoning | 2 |
| Recommendations: realistic, both immediate and long-term | 4 |

Grade **reasoning**, not just labels. "It's spraying **because** one IP tried 42 different users with only 2–3 attempts each" scores higher than "spraying".
