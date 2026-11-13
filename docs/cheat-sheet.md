# Lab 4 Cheat Sheet: Evidence You Are Looking For

## 1. Brute force vs password spraying

| | Brute force | Password spraying |
|---|---|---|
| Targets | **One** account | **Many** accounts |
| Passwords tried | **Many** per account | **One or two** common ones (e.g. `Winter2026!`) |
| Triggers lockout? | Yes, quickly | Usually **no**, because each account only gets a few tries |
| What you see in logs | Lots of failures for one user | Failures spread across many users **from one source**, in a short time |

## 2. Windows Security Event IDs

| Event ID | Meaning |
|---|---|
| **4624** | An account successfully logged on |
| **4625** | An account **failed** to log on |
| **4740** | A user account was **locked out** |
| 4771 | Kerberos pre-authentication failed (not in this dataset) |

## 3. Logon types

| Type | Meaning |
|---|---|
| 2 | Interactive: sitting at the keyboard |
| 3 | Network: file share, SMB, etc. |
| 5 | Service: a Windows service starting |
| 7 | Unlock: unlocking a locked screen |
| 10 | **RemoteInteractive: Remote Desktop (RDP)** |

## 4. Failure codes (SubStatus on 4625)

| Code | Meaning | Why it matters |
|---|---|---|
| `0xC000006A` | Wrong password, but **the user exists** | The attacker guessed a real username |
| `0xC0000064` | **User name does not exist** | The attacker is guessing usernames too |
| `0xC000006D` | General "logon failure" (Status field) | Appears on every failed logon |

## 5. Tools: how to filter

### Log search page (`docs/index.html`, same data as auth_logs.csv)
- Choose **Event ID → 4625** to see only failures.
- Look at **Count by Source IP** on the right. Click an IP to filter by it.
- Click a column header to sort.
- Use **From / To** to zoom in on a time window.

### Google Sheets / Excel / LibreOffice Calc
1. Open `auth_logs.csv`.
2. Select row 1, then **Data → Filter** (Sheets: *Create a filter*).
3. Filter `EventID` = `4625`.
4. To count per IP: **Insert → Pivot table**. Rows = `SourceIP`, Values = COUNTA of `EventID`.

### PowerShell (built into Windows)
Open PowerShell in the `data` folder, then:

```powershell
# Load the log
$log = Import-Csv .\auth_logs.csv

# Failed logons per source IP (most first)
$log | Where-Object EventID -eq 4625 | Group-Object SourceIP | Sort-Object Count -Descending | Select-Object Count, Name

# How many DIFFERENT users did one IP try?   (replace the IP)
($log | Where-Object { $_.EventID -eq 4625 -and $_.SourceIP -eq 'x.x.x.x' } | Select-Object -Unique TargetUserName).Count

# Everything that IP did, in time order
$log | Where-Object SourceIP -eq 'x.x.x.x' | Format-Table TimeCreated, EventID, TargetUserName, LogonType, SubStatus

# Lockouts
$log | Where-Object EventID -eq 4740 | Format-Table TimeCreated, TargetUserName, WorkstationName
```

### Wireshark (`network_capture.pcap`)
Useful display filters (type in the green filter bar, then press Enter):

| Filter | Shows |
|---|---|
| `ntlmssp.auth.username` | Every login attempt, with the username being tried |
| `smb2.nt_status == 0xc000006d` | Server replies: **logon failure** |
| `smb2.cmd == 1 && smb2.nt_status == 0 && smb2.flags.response == 1` | Server replies: **logon success** |
| `ip.addr == x.x.x.x` | All traffic to/from one IP |
| `tcp.port == 3389` | Remote Desktop (RDP) traffic |
| `rdp` | RDP connection requests (look for `mstshash=` = username) |

Tips:
- **View → Time Display Format → Date and Time of Day** shows real clock times you can match to the log.
  Wireshark shows times in **your PC's time zone**. The log is in **UTC+8 (Singapore)**. If your PC uses another time zone, the hours will be shifted.
- Right-click a field (e.g. *User name*) in the packet details, then **Apply as Column**.
- **Statistics → Conversations → IPv4** shows which IPs talked the most.
