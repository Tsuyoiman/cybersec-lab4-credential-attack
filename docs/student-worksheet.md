# Lab 4 Student Worksheet: Investigate a Simulated Credential Attack

> ✍️ **Fill this in online:** **https://tsuyoiman.github.io/cybersec-lab4-credential-attack/worksheet.html**. It saves as you type, and you can download or print your answers.
> This page is the printable copy of the same questions.

**Names:** .............................. **Group:** .......... **Date:** ............

## Scenario

On the morning of **12 November 2026**, IT staff at Corp could not log in because their accounts were **locked out**. User `j.tan` says she was asleep at 3 a.m., yet her account shows activity at that time.

You are the SOC analyst. Use the domain controller log (`auth_logs.csv`) and the network capture (`network_capture.pcap`) to find out what happened.

Keep the [cheat sheet](cheat-sheet.md) open while you work.

---

## Part A: The logs (20 min)

Use the browser log viewer, a spreadsheet, or PowerShell.

**A1.** How many events are in the log in total? How many are **failed logons (4625)**?

> Total: .......... Failed (4625): ..........

**A2.** Which **Source IP** has the most failed logons? How many?

> IP: .................... Number of failures: ..........

**A3.** How many **different usernames** did that IP try?

> ..........

**A4.** Look at the `SubStatus` codes from that IP. Some are `0xC000006A` and some are `0xC0000064`. What does each one tell you about what the attacker knew?

> ......................................................................

**A5.** What is the **time window** of the attack (first and last failure from that IP)?

> From: ............ To: ............

**A6.** Is this **brute force** or **password spraying**? Give **two** pieces of evidence.

> Type: ....................<br>
> Evidence 1: ..............................................................<br>
> Evidence 2: ..............................................................

**A7.** Did any account **successfully** log on (4624) from the same IP? Which account, at what time, and with which logon type?

> Account: ............ Time: ............ Logon type: .......... (meaning: ............)

**A8.** Were any accounts **locked out (4740)**? Which ones? What do these accounts have in common?

> ......................................................................

**A9.** What did the attacker do **after** getting in? (Look at every event from that IP after the successful logon.)

> ......................................................................

**A10. False positive check.** User `s.lim` has 3 failed logons in a row. Is she part of the attack? Explain using the **time, source IP and logon type**.

> ......................................................................

---

## Part B: Wireshark (15 min)

Open `network_capture.pcap` in Wireshark. Set **View → Time Display Format → Date and Time of Day**.

**B1.** Apply the filter `ntlmssp.auth.username`. Which IP is sending the login attempts? Does it match your answer to A2?

> ......................................................................

**B2.** Add the **User name** as a column (right-click the field, then **Apply as Column**). Name **three** usernames the attacker tried that you also saw in the log.

> ......................................................................

**B3.** Find the **one** login that the server accepted. Use the success filter from the cheat sheet. What time is it? Does it match A7?

> ......................................................................

**B4.** Apply `tcp.port == 3389`. What protocol is this, and which username appears in the `mstshash` cookie? What does this confirm?

> ......................................................................

**B5.** Why is it useful to find the **same evidence in two different sources** (logs + network)?

> ......................................................................

---

## Part C: Timeline (5 min)

Fill in the attack in time order.

| Time | What happened | Evidence (Event ID / packet) |
|---|---|---|
| | | |
| | | |
| | | |
| | | |
| | | |

---

## Part D: Recommendations

List **at least 4** actions. Include at least one **immediate response** and at least one **long-term prevention**.

| # | Action | Immediate or long-term? | Why it helps |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## Challenge (if you finish early)

The attacker sent one attempt every 1–3 seconds. Suppose they waited **one hour** between attempts instead. Would the "count failures per IP" method still catch them? Describe a detection rule that would.

> ......................................................................
