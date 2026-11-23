# JINEY OPENAI EXPORT — GMAIL SOURCE READBACK — 2026-11-24

## Direct provider evidence
- Provider: Gmail connector.
- Account selected: JINEY, `jakammmm87@gmail.com`.
- Export-start email:
  - Message/thread ID: `19fe074be3970502`
  - Sender: `noreply@tm.openai.com`
  - Recipient: `jakammmm87@gmail.com`
  - Date: `2026-08-08T08:19:34Z`
  - Subject: `ChatGPT - Quá trình xuất dữ liệu của bạn đã bắt đầu`
  - Body states that the requested ChatGPT data export preparation had started.
- Export-ready email:
  - Message/thread ID: `19fe59b190d16d12`
  - Sender: `noreply@tm.openai.com`
  - Recipient: `jakammmm87@gmail.com`
  - Date: `2026-08-09T08:19:34Z`
  - Subject: `ChatGPT - Quá trình xuất dữ liệu của bạn đã sẵn sàng`
  - Body states that the requested export was ready for download.
  - Embedded export object identifier: `f867081742ccbcd6cee4c69501e916e60505f1409b487b0c2b9e5a14a8ba743c-2026-08-08-09-15-35-e946847b03e64ec2a213b07896d0b984.zip`

## What this establishes
- An OpenAI export-ready notification was delivered to the JINEY Gmail account.
- The email identifies a concrete export object identifier and timestamped ZIP name.
- This is stronger than the prior derived source-graph pointer that only recorded an export-ready notice.

## What remains unverified
- The ZIP bytes have not been retrieved in this turn.
- The email's historical signed download URL is not copied into this repository; it contains a signature and is treated as a bearer download credential.
- No checksum, archive central directory, `user.json`, or conversation payload has been read from that ZIP.
- Therefore the email establishes the export notification and its recipient, but not the archive's present availability or the account identity encoded inside the archive.
- The prior derived Markdown packages (636 + 160 conversations) are not substituted for this raw ZIP.

## Next retrieval edge
Search the exact export object identifier / ZIP basename across accessible Dropbox and other authorized carriers; if the original export is absent or the signed URL has expired, preserve that result and locate a still-retained copy. Do not replace the source with another account's export.

## Preservation
- Read-only Gmail retrieval; no message sent, changed, or deleted.
- GitHub record is a source-derived checkpoint, not the ZIP itself and not a local SQLite runtime journal.
- Status remains OPEN.
