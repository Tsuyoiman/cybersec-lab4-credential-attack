# Lab 4 Step-by-Step Guide

**Investigate a Simulated Credential Attack** · ≈ 75 minutes · work in **pairs**

Follow the steps in order. Each step tells you **what to do**, **where to click**, and **what to write down**.
Keep the [Cheat Sheet](cheat-sheet.md) open in another tab and write your answers in the [Student Worksheet](student-worksheet.md).

```
 STEP 0   Get set up                         (5 min)
 STEP 1   Read the scenario                  (5 min)
 STEP 2   Learn the evidence                 (10 min)
 STEP 3   Part A: investigate the logs       (20 min)
 STEP 4   Part B: confirm in Wireshark       (15 min)
 STEP 5   Build the timeline                 (5 min)
 STEP 6   Write the incident report          (10 min)
 STEP 7   Present & debrief                  (5 min)
```

---

## STEP 0: Get set up (5 min)

**0.1 Open the online log viewer** (you'll use this for Part A):
👉 **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/**

You should see a dark page titled **DC01 Security Log Viewer** with a table of events and **"326 of 326 events"** at the top right.

**0.2 Download the lab files** (you'll need the network capture for Part B):
1. Go to the repository: https://github.com/Tsuyoiman/cybersec-lab4-credential-attack
2. Click the green **`<> Code`** button, then **Download ZIP**.
3. Unzip the file (right-click → **Extract All**).
4. Inside you'll find the `data` folder with `auth_logs.csv` and `network_capture.pcap`.

**0.3 Check Wireshark is installed.** Open it from the Start menu. If it's missing, tell your instructor.

> **No internet?** Open `docs/index.html` from the unzipped folder by double-clicking it. It's the same viewer and works offline.

✅ **Checkpoint:** viewer open, ZIP extracted, Wireshark opens.

---

## STEP 1: Read the scenario (5 min)

> On the morning of **12 November 2026**, IT staff at Corp could not log in because their accounts were **locked out**. User `j.tan` says she was asleep at 3 a.m., but her account shows activity at that time.
>
> You are the **SOC analyst on duty**. You have:
> - the security log from the domain controller **DC01** (`auth_logs.csv`)
> - a network capture from the same night (`network_capture.pcap`)
>
> **Your job: find out what happened, prove it, and recommend what to do.**

Discuss with your partner for one minute: *What kind of attack might cause many lockouts and a strange 3 a.m. login?* Write your guess at the top of your worksheet. You'll check it at the end.

---

## STEP 2: Learn the evidence (10 min)

Open the **[Cheat Sheet](cheat-sheet.md)** and make sure you understand:

| You need to know | Key items |
|---|---|
| The attack types | **Brute force** = many passwords against one account. **Password spraying** = one password against many accounts |
| Event IDs | **4624** success · **4625** failure · **4740** locked out |
| Logon types | **2** at keyboard · **3** network · **10** Remote Desktop (RDP) |
| Failure codes | **0xC000006A** wrong password (user exists) · **0xC0000064** user doesn't exist |

**Practice in the viewer (2 min):**
1. Set **Event ID** to **4624 – Logon success** and look at the colours (green = success).
2. Set it to **4625 – Logon failed** (red = failure).
3. Click **Reset**.

✅ **Checkpoint:** you can explain to your partner what 4625 with logon type 3 means.

---

## STEP 3: Part A, investigate the logs (20 min)

Use the **online log viewer**. Answer **A1–A10** on the worksheet as you go.

### 3.1 Count the events → *A1*
- With no filters, read the counter at the top right: **"___ of 326 events"**.
- Set **Event ID → 4625**. Write down the new count.

### 3.2 Find the noisiest source → *A2*
- Keep **Event ID = 4625**.
- Look at the **Count by Source IP** panel on the right. It's sorted from most to least.
- Write down the **top IP** and its count. Compare it with the second one: is it normal?

### 3.3 How many accounts did it try? → *A3*
- Click that IP in the right panel. The **Source IP** filter fills in automatically.
- Now look at **Count by User** on the right. Count how many different usernames appear (scroll the panel), or click the **TargetUserName** column header to sort and count.

### 3.4 What did the attacker know? → *A4*
- Still filtered to that IP, look at the **SubStatus** column.
- Type `0xC0000064` into **Search anything**. Which usernames are these? Are they real staff?
- Clear the search box.

### 3.5 When did it happen? → *A5*
- Click the **TimeCreated** header to sort oldest-first (▲).
- Write down the **first** time. Click again (▼) and write down the **last** time.

### 3.6 Spraying or brute force? → *A6*
- Use what you found in 3.2–3.5. Think about:
  - one source vs many accounts?
  - how many tries per account?
  - how many seconds between attempts?
- Write the type **and two pieces of evidence**.

### 3.7 Did the attacker get in? → *A7*
- Keep the **Source IP** filter. Change **Event ID → 4624 – Logon success**.
- Write down the **account, time, and logon type** of every row you see.

### 3.8 Who got locked out? → *A8*
- Click **Reset**. Set **Event ID → 4740 – Account locked**.
- Write down the accounts and times. *What do these accounts have in common?*

### 3.9 What happened after the break-in? → *A9*
- **Reset**. Type the attacker IP in **Source IP**, and leave **Event ID = All**.
- Sort by **TimeCreated ▲** and scroll to the end. What is the **last** thing this IP did? Check the **LogonType** and look it up in the cheat sheet.

### 3.10 False positive check → *A10*
- **Reset**. Type `s.lim` in **User**.
- She has failed logons too. Compare her events with the attacker's:
  - **Time** of day?
  - **Source IP**: is it her own PC (same IP as her normal logons)?
  - **Logon type**: keyboard or network?
  - What happened **right after** the failures?
- Decide: **attack or normal?** Explain why.

> 💡 **Using a spreadsheet or PowerShell instead?** The same steps work in Google Sheets / LibreOffice (Data → Filter, Insert → Pivot table) or with the PowerShell commands in the cheat sheet.

✅ **Checkpoint:** you know the attacker IP, the attack type, the compromised account and the time window.

---

## STEP 4: Part B, confirm in Wireshark (15 min)

Now prove the same story from **network traffic**. Answer **B1–B5** on the worksheet.

### 4.1 Open the capture
1. Open **Wireshark** → **File → Open** → choose `data/network_capture.pcap` from the unzipped folder.
2. Go to **View → Time Display Format → Date and Time of Day** so the times match the log.

> ⚠️ Wireshark shows times in **your PC's time zone**. The log is in **UTC+8 (Singapore)**. If your PC uses another zone, the hours will be shifted, but the minutes and seconds still match.

### 4.2 See the login attempts → *B1*
- In the green **filter bar** type: `ntlmssp.auth.username` and press **Enter**.
- Look at the **Source** column. Which IP sends all of these? Does it match Part A?

### 4.3 Show the usernames → *B2*
1. Click any packet in the list.
2. In the middle pane, expand: **SMB2 → Session Setup Request → Security Blob → … → NTLMSSP**.
3. Find **User name**, right-click it, then **Apply as Column**.
4. Now every row shows the username tried. Write down three that also appear in the log.

### 4.4 Find the successful login → *B3*
- Use this filter:
  `smb2.cmd == 1 && smb2.nt_status == 0 && smb2.flags.response == 1`
- One reply means "success". Write down its **time**.
- Optional: filter `smb2.nt_status == 0xc000006d` to see all the failures ("logon failure").

### 4.5 What came next? → *B4*
- Filter: `tcp.port == 3389`
- Find the packet with **Cookie: mstshash=** in the Info column. Which username is in it?
- Port 3389 = **Remote Desktop (RDP)**. What does that prove?

### 4.6 Why two sources? → *B5*
- Discuss with your partner, then write: why is it stronger evidence when the **logs** and the **network capture** tell the same story?

📸 **Take screenshots** of 4.2, 4.4 and 4.5 for your report.

✅ **Checkpoint:** the attacker IP, the successful login and the RDP session all match Part A.

---

## STEP 5: Build the timeline (5 min)

Fill in **Part C** of the worksheet. Put the events in **time order**:

| Time | What happened | Evidence |
|---|---|---|
| *first attacker activity* | | |
| *spray round(s)* | | |
| *successful login* | | |
| *lockouts* | | |
| *remote desktop session* | | |

**Tip:** in the viewer, filter by the attacker IP and sort by **TimeCreated ▲**. Look for **gaps** in time, because they separate the attack "rounds".

---

## STEP 6: Write the incident report (10 min)

Copy the **[Report Template](report-template.md)** into a Word/Google doc and fill it in:

1. **Summary**: 2–3 sentences a manager can understand.
2. **Attack details**: the table (IP, type, time window, accounts, compromised account).
3. **Timeline**: from Step 5.
4. **Evidence**: paste your screenshots.
5. **False positives reviewed**: s.lim and anything else that looked odd but wasn't.
6. **Recommendations**: at least **2 immediate** (today) and **3 long-term** (prevention).
   *Think about: passwords, MFA, remote access, blocking, detection rules, admin accounts.*
7. **Lessons learned**: what would have caught this sooner?

Submit it the way your instructor tells you (LMS, email, or print).

---

## STEP 7: Present & debrief (5 min)

Some pairs will present their timeline. Be ready to answer:

1. Why were the **admin accounts** locked out but normal users weren't?
2. Why is **s.lim** not part of the attack?
3. If the attacker waited **one hour** between tries, how would you still detect them?

Finally, look back at the guess you wrote in **Step 1**. Were you right?

---

## ✅ Final checklist before you submit

- [ ] Worksheet A1–A10 answered
- [ ] Worksheet B1–B5 answered
- [ ] Timeline completed (Part C)
- [ ] At least 4 recommendations (Part D)
- [ ] Incident report with screenshots
- [ ] Both partners' names on the report

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| Viewer page won't load | Open `docs/index.html` from the ZIP instead (double-click) |
| Viewer shows 0 events | Click **Reset** |
| Wireshark: "file not found" | Make sure you **extracted** the ZIP first, not just opened it |
| Wireshark: no packets after filter | Check spelling, e.g. `ntlmssp.auth.username` (all lowercase), then press Enter |
| Wireshark times don't match log | Set **View → Time Display Format → Date and Time of Day**. Hours may differ by time zone, so compare minutes:seconds |
| Can't find "User name" in packet details | Use the filter from 4.2 first, then select a packet and expand **SMB2 → Security Blob → NTLMSSP** |
| No Excel | You don't need it. Use the online viewer |
