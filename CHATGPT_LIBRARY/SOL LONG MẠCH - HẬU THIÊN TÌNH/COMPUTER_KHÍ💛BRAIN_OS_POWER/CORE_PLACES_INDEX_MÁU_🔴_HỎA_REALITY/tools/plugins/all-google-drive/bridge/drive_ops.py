"""Multi-account Google Drive/Docs/Sheets/Slides operations, with observable readback."""
from __future__ import annotations
import hashlib
import io
import json
import mimetypes
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .accounts import AccountVault, state_home

FOLDER = "application/vnd.google-apps.folder"
NATIVE_EXPORT = {
    "application/vnd.google-apps.document": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
}
NATIVE_MIME = {"doc": "application/vnd.google-apps.document", "sheet": "application/vnd.google-apps.spreadsheet", "slides": "application/vnd.google-apps.presentation"}
FILE_FIELDS = "id,name,mimeType,size,md5Checksum,version,parents,webViewLink,createdTime,modifiedTime,trashed,driveId,capabilities,description"


def text_from_docs(elements: list) -> str:
    texts = []
    for elem in elements:
        if "paragraph" in elem:
            for part in elem["paragraph"].get("elements", []):
                if "textRun" in part:
                    texts.append(part["textRun"].get("content", ""))
        if "table" in elem:
            for row in elem["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    texts.append(text_from_docs(cell.get("content", [])))
                    texts.append("\t")
                texts.append("\n")
        if "tableOfContents" in elem:
            texts.append(text_from_docs(elem["tableOfContents"].get("content", [])))
    return "".join(texts)


class DriveController:
    def __init__(self, vault: AccountVault | None = None):
        self.vault = vault or AccountVault()
        self.audit_path = state_home() / "audit.jsonl"
        self._services = {}

    def service(self, alias: str, api: str = "drive", version: str = "v3"):
        from googleapiclient.discovery import build
        self.vault.check_alias(alias)
        key = (alias, api, version)
        # Fresh credentials each time; token refresh is persisted in the keyring.
        self._services[key] = build(api, version, credentials=self.vault.credentials(alias), cache_discovery=False)
        return self._services[key]

    def accounts(self):
        return [{"alias": k, "email": v.get("email"), "added_at": v.get("added_at")} for k, v in sorted(self.vault.list_accounts().items())]

    def audit(self, operation: str, alias: str, target_id: str | None, result: dict):
        """Hash-linked metadata-only append log; never log OAuth tokens or file bytes."""
        self.audit_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        previous = "0" * 64
        if self.audit_path.exists():
            with self.audit_path.open("rb") as f:
                for line in f:
                    if line.strip():
                        previous = json.loads(line)["hash"]
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(), "operation": operation,
            "account": alias, "target_id": target_id,
            "result_id": result.get("id") or result.get("fileId"),
            "result_name": result.get("name"), "result_version": result.get("version"),
            "previous_hash": previous,
        }
        record["hash"] = hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.audit_path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record["hash"]

    def get_file(self, alias: str, file_id: str):
        return self.service(alias).files().get(fileId=file_id, supportsAllDrives=True, fields=FILE_FIELDS).execute()

    def list_files(self, alias: str, q: str = "trashed = false", page_token: str | None = None, page_size: int = 100):
        if not 1 <= page_size <= 1000:
            raise ValueError("page_size must be 1..1000 (Google API bound)")
        data = self.service(alias).files().list(
            q=q, pageSize=page_size, pageToken=page_token,
            fields="nextPageToken,incompleteSearch,files(" + FILE_FIELDS + ")",
            supportsAllDrives=True, includeItemsFromAllDrives=True
        ).execute()
        return {"account": alias, **data}

    def search(self, account: str, name_contains: str = "", q: str = "trashed = false", page_size: int = 100):
        if name_contains:
            name = name_contains.replace("\\", "\\\\").replace("'", "\\'")
            q = f"({q}) and name contains '{name}'"
        if account == "*":
            found = {}
            errors = {}
            for alias in self.vault.list_accounts():
                try:
                    found[alias] = self.list_files(alias, q=q, page_size=page_size)
                except Exception as exc:
                    errors[alias] = type(exc).__name__ + ": " + str(exc)[:150]
            return {"accounts": found, "errors": errors, "note": "One provider page per account; paginate each independently"}
        return self.list_files(account, q=q, page_size=page_size)

    def folder_inventory(self, alias: str, folder_id: str, recursive: bool = True):
        queue = [folder_id]
        seen = set()
        entries = []
        while queue:
            parent = queue.pop(0)
            if parent in seen:
                continue
            seen.add(parent)
            token = None
            while True:
                batch = self.list_files(alias, q=f"'{parent}' in parents and trashed = false", page_token=token, page_size=1000)
                for f in batch.get("files", []):
                    entries.append({"parent_id": parent, **f})
                    if recursive and f.get("mimeType") == FOLDER:
                        queue.append(f["id"])
                token = batch.get("nextPageToken")
                if not token:
                    break
        return {"account": alias, "root_id": folder_id, "recursive": recursive, "total": len(entries), "entries": entries}

    def create_folder(self, alias: str, name: str, parent_id: str | None = None):
        body = {"name": name, "mimeType": FOLDER}
        if parent_id:
            body["parents"] = [parent_id]
        new = self.service(alias).files().create(body=body, fields="id", supportsAllDrives=True).execute()
        check = self.get_file(alias, new["id"])
        self.audit("create_folder", alias, parent_id, check)
        return check

    def create_native(self, alias: str, name: str, kind: str, parent_id: str | None = None):
        if kind not in NATIVE_MIME:
            raise ValueError("kind must be doc, sheet, or slides")
        body = {"name": name, "mimeType": NATIVE_MIME[kind]}
        if parent_id:
            body["parents"] = [parent_id]
        new = self.service(alias).files().create(body=body, fields="id", supportsAllDrives=True).execute()
        check = self.get_file(alias, new["id"])
        self.audit("create_" + kind, alias, parent_id, check)
        return check

    def rename_file(self, alias: str, file_id: str, new_name: str):
        self.service(alias).files().update(fileId=file_id, body={"name": new_name}, supportsAllDrives=True).execute()
        check = self.get_file(alias, file_id)
        if check["name"] != new_name:
            raise RuntimeError("READBACK FAILED: rename")
        self.audit("rename", alias, file_id, check)
        return check

    def move_file(self, alias: str, file_id: str, destination_folder_id: str):
        before = self.get_file(alias, file_id)
        current = ",".join(before.get("parents", []))
        self.service(alias).files().update(
            fileId=file_id, addParents=destination_folder_id, removeParents=current or None,
            supportsAllDrives=True, fields="id"
        ).execute()
        check = self.get_file(alias, file_id)
        if destination_folder_id not in check.get("parents", []):
            raise RuntimeError("READBACK FAILED: destination parent not present")
        self.audit("move", alias, file_id, check)
        return {"before": before, "after": check}

    def copy_file(self, alias: str, file_id: str, new_name: str | None = None, parent_id: str | None = None):
        body: dict = {}
        if new_name:
            body["name"] = new_name
        if parent_id:
            body["parents"] = [parent_id]
        result = self.service(alias).files().copy(fileId=file_id, body=body, supportsAllDrives=True, fields="id").execute()
        check = self.get_file(alias, result["id"])
        self.audit("copy_within", alias, file_id, check)
        return check

    def trash_file(self, alias: str, file_id: str):
        self.service(alias).files().update(fileId=file_id, body={"trashed": True}, supportsAllDrives=True).execute()
        check = self.get_file(alias, file_id)
        if not check.get("trashed"):
            raise RuntimeError("READBACK FAILED: file not in trash")
        self.audit("trash", alias, file_id, check)
        return check

    def permanently_delete(self, alias: str, file_id: str, confirm_exact_id: str):
        if file_id != confirm_exact_id:
            raise ValueError("confirm_exact_id must equal file_id")
        before = self.get_file(alias, file_id)
        self.service(alias).files().delete(fileId=file_id, supportsAllDrives=True).execute()
        try:
            self.get_file(alias, file_id)
        except Exception as exc:
            from googleapiclient.errors import HttpError
            if not isinstance(exc, HttpError) or exc.resp.status not in (404, 410):
                raise
        else:
            raise RuntimeError("READBACK FAILED: file still accessible")
        result = {"id": file_id, "name": before.get("name"), "status": "deleted_and_readback_not_found"}
        self.audit("permanent_delete", alias, file_id, result)
        return result

    def share(self, alias: str, file_id: str, recipient_email: str, role: str = "writer"):
        if role not in {"reader", "commenter", "writer"}:
            raise ValueError("role must be reader/commenter/writer")
        result = self.service(alias).permissions().create(
            fileId=file_id, body={"type": "user", "role": role, "emailAddress": recipient_email},
            fields="id,role,type,emailAddress", supportsAllDrives=True
        ).execute()
        perms = self.service(alias).permissions().list(fileId=file_id, fields="permissions(id,role,type,emailAddress)", supportsAllDrives=True).execute()
        if not any(p.get("id") == result.get("id") and p.get("role") == role for p in perms.get("permissions", [])):
            raise RuntimeError("READBACK FAILED: permission not found")
        self.audit("share", alias, file_id, {"id": file_id})
        return {"account": alias, "file_id": file_id, "permission": result, "verified": True}

    def read_document(self, alias: str, document_id: str):
        doc = self.service(alias, "docs", "v1").documents().get(documentId=document_id, includeTabsContent=True).execute()
        if doc.get("tabs"):
            def flatten(tabs):
                for tab in tabs:
                    yield {"tab_id": tab.get("tabProperties", {}).get("tabId"), "title": tab.get("tabProperties", {}).get("title"), "text": text_from_docs(tab.get("documentTab", {}).get("body", {}).get("content", []))}
                    yield from flatten(tab.get("childTabs", []))
            return {"document_id": document_id, "title": doc.get("title"), "revision_id": doc.get("revisionId"), "tabs": list(flatten(doc["tabs"]))}
        return {"document_id": document_id, "title": doc.get("title"), "revision_id": doc.get("revisionId"), "text": text_from_docs(doc.get("body", {}).get("content", []))}

    def edit_document(self, alias: str, document_id: str, requests: list[dict]):
        if not requests:
            raise ValueError("requests empty")
        api = self.service(alias, "docs", "v1").documents()
        before = api.get(documentId=document_id).execute()
        result = api.batchUpdate(documentId=document_id, body={"requests": requests, "writeControl": {"requiredRevisionId": before["revisionId"]}}).execute()
        after = api.get(documentId=document_id).execute()
        if before.get("revisionId") == after.get("revisionId"):
            raise RuntimeError("OPEN: revision unchanged; verify intended content manually")
        self.audit("edit_document", alias, document_id, {"id": document_id, "version": after.get("revisionId")})
        return {"account": alias, "document_id": document_id, "revision_before": before.get("revisionId"), "revision_after": after.get("revisionId"), "provider_result": result}

    def read_sheet(self, alias: str, spreadsheet_id: str, a1_range: str):
        data = self.service(alias, "sheets", "v4").spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=a1_range).execute()
        return {"account": alias, **data}

    def edit_sheet(self, alias: str, spreadsheet_id: str, a1_range: str, values: list[list[Any]]):
        api = self.service(alias, "sheets", "v4").spreadsheets().values()
        result = api.update(spreadsheetId=spreadsheet_id, range=a1_range, valueInputOption="USER_ENTERED", body={"values": values}).execute()
        after = api.get(spreadsheetId=spreadsheet_id, range=a1_range, valueRenderOption="FORMULA").execute()
        self.audit("edit_sheet", alias, spreadsheet_id, {"id": spreadsheet_id})
        return {"account": alias, "update": result, "readback": after}

    def edit_slides(self, alias: str, presentation_id: str, requests: list[dict]):
        if not requests:
            raise ValueError("requests empty")
        api = self.service(alias, "slides", "v1").presentations()
        before = api.get(presentationId=presentation_id, fields="presentationId,revisionId").execute()
        payload = {"requests": requests}
        if before.get("revisionId"):
            payload["writeControl"] = {"requiredRevisionId": before["revisionId"]}
        result = api.batchUpdate(presentationId=presentation_id, body=payload).execute()
        after = api.get(presentationId=presentation_id, fields="presentationId,revisionId").execute()
        if before.get("revisionId") == after.get("revisionId"):
            raise RuntimeError("OPEN: revision unchanged; verify intended content manually")
        self.audit("edit_slides", alias, presentation_id, {"id": presentation_id, "version": after.get("revisionId")})
        return {"account": alias, "presentation_id": presentation_id, "revision_before": before.get("revisionId"), "revision_after": after.get("revisionId"), "provider_result": result}

    def read_presentation(self, alias: str, presentation_id: str):
        pres = self.service(alias, "slides", "v1").presentations().get(presentationId=presentation_id).execute()
        slides = []
        for index, slide in enumerate(pres.get("slides", []), start=1):
            texts = []
            for element in slide.get("pageElements", []):
                for item in element.get("shape", {}).get("text", {}).get("textElements", []):
                    texts.append(item.get("textRun", {}).get("content", ""))
            slides.append({"number": index, "object_id": slide.get("objectId"), "text": "".join(texts), "page_element_count": len(slide.get("pageElements", []))})
        return {"account": alias, "presentation_id": presentation_id, "title": pres.get("title"), "revision_id": pres.get("revisionId"), "slides": slides}

    def edit_sheet_batch(self, alias: str, spreadsheet_id: str, requests: list[dict]):
        if not requests:
            raise ValueError("requests empty")
        api = self.service(alias, "sheets", "v4").spreadsheets()
        result = api.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
        meta = api.get(spreadsheetId=spreadsheet_id, fields="spreadsheetId,properties(title),sheets(properties(sheetId,title,gridProperties))").execute()
        self.audit("edit_sheet_batch", alias, spreadsheet_id, {"id": spreadsheet_id})
        return {"account": alias, "provider_result": result, "metadata_readback": meta}

    def list_revisions(self, alias: str, file_id: str, page_size: int = 100):
        return self.service(alias).revisions().list(fileId=file_id, pageSize=page_size, fields="nextPageToken,revisions(id,mimeType,modifiedTime,keepForever,lastModifyingUser,originalFilename,size)").execute()

    def list_comments(self, alias: str, file_id: str, page_size: int = 100):
        return self.service(alias).comments().list(fileId=file_id, fields="nextPageToken,comments(id,content,createdTime,modifiedTime,resolved,quotedFileContent,replies)", pageSize=page_size, includeDeleted=False).execute()

    def add_comment(self, alias: str, file_id: str, content: str):
        api = self.service(alias).comments()
        result = api.create(fileId=file_id, body={"content": content}, fields="id,content,createdTime,resolved").execute()
        # Re-read the exact comment on the same file.
        verify = api.get(fileId=file_id, commentId=result["id"], fields="id,content,createdTime,resolved").execute()
        if verify.get("content") != content:
            raise RuntimeError("READBACK FAILED: comment text mismatch")
        self.audit("add_comment", alias, file_id, {"id": file_id})
        return {"comment": result, "readback": verify}

    def upload_local(self, alias: str, local_path: str, parent_id: str | None = None, name: str | None = None):
        """Upload a file that exists on the *MCP host*; don't confuse host paths with ChatGPT files."""
        from googleapiclient.http import MediaFileUpload
        path = Path(local_path).expanduser().resolve(strict=True)
        if not path.is_file():
            raise ValueError("local_path is not a regular file")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = {"name": name or path.name}
        if parent_id:
            body["parents"] = [parent_id]
        created = self.service(alias).files().create(
            body=body, media_body=MediaFileUpload(str(path), mimetype=mime, resumable=True),
            supportsAllDrives=True, fields="id"
        ).execute()
        after = self.get_file(alias, created["id"])
        self.audit("upload_local", alias, None, after)
        return {"destination": after, "source_path": str(path), "note": "Path belongs to MCP server filesystem"}

    def download_local(self, alias: str, file_id: str, destination_path: str):
        """Download to an explicit filesystem path on the MCP host, never echo raw file bytes."""
        src = self.get_file(alias, file_id)
        destination = Path(destination_path).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError("Refusing silent overwrite of an existing destination path")
        created = False
        try:
            with destination.open("xb") as output:
                created = True
                mime, extension = self._stream_source(alias, file_id, src["mimeType"], output)
                output.flush()
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
        digest = hashlib.sha256()
        with destination.open("rb") as input_stream:
            for chunk in iter(lambda: input_stream.read(1024 * 1024), b""):
                digest.update(chunk)
        self.audit("download_local", alias, file_id, {"id": file_id, "name": src.get("name")})
        return {"account": alias, "file_id": file_id, "host_path": str(destination), "mime_type": mime, "native_export_extension": extension, "bytes": destination.stat().st_size, "sha256": digest.hexdigest()}

    def _stream_source(self, alias: str, file_id: str, source_mime: str, output):
        from googleapiclient.http import MediaIoBaseDownload
        drive = self.service(alias)
        if source_mime in NATIVE_EXPORT:
            transfer_mime, extension = NATIVE_EXPORT[source_mime]
            request = drive.files().export_media(fileId=file_id, mimeType=transfer_mime)
        else:
            transfer_mime = source_mime
            extension = ""
            request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
        download = MediaIoBaseDownload(output, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            _, done = download.next_chunk()
        output.seek(0)
        return transfer_mime, extension

    def transfer_account(self, source_alias: str, file_id: str, destination_alias: str, parent_id: str | None = None, new_name: str | None = None):
        """Copy one file across OAuth identities; revision/comments/ACL are NOT transferred."""
        from googleapiclient.http import MediaIoBaseUpload
        if source_alias == destination_alias:
            return self.copy_file(source_alias, file_id, new_name, parent_id)
        src = self.get_file(source_alias, file_id)
        if src["mimeType"] == FOLDER:
            raise ValueError("Folder transfer requires per-file traversal; use inventory and transfer children")
        with tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024) as stream:
            transfer_mime, extension = self._stream_source(source_alias, file_id, src["mimeType"], stream)
            digest = hashlib.sha256()
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            stream.seek(0)
            target_name = new_name or src["name"]
            body = {"name": target_name, "mimeType": src["mimeType"]}
            if parent_id:
                body["parents"] = [parent_id]
            upload = MediaIoBaseUpload(stream, mimetype=transfer_mime, chunksize=8 * 1024 * 1024, resumable=True)
            result = self.service(destination_alias).files().create(body=body, media_body=upload, fields="id", supportsAllDrives=True).execute()
            after = self.get_file(destination_alias, result["id"])
        if after.get("name") != target_name or after.get("mimeType") != src["mimeType"]:
            raise RuntimeError("READBACK FAILED: destination mismatch")
        if parent_id and parent_id not in after.get("parents", []):
            raise RuntimeError("READBACK FAILED: destination parent mismatch")
        self.audit("cross_account_copy_source", source_alias, file_id, {"id": file_id, "name": src.get("name")})
        self.audit("cross_account_copy_destination", destination_alias, file_id, after)
        return {"source_account": source_alias, "source_id": file_id, "destination_account": destination_alias, "destination": after, "transport_sha256": digest.hexdigest(), "warning": "New Google file ID; source revision history, comments, sharing and permissions are not preserved; native Docs/Sheets/Slides exported and re-imported."}
