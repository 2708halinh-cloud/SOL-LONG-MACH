#!/usr/bin/env python3
"""SOL video adapter: text->video and image->video via a user-run ComfyUI endpoint.

Stdlib only; does NOT install models or start GPU services. An API-format
ComfyUI video workflow (with model files installed) is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import uuid

VIDEO_EXTS = {".mp4", ".webm", ".mov", ".mkv", ".gif"}


def mutate_workflow(workflow: dict, prompt: str, prompt_node: str, image_node: str | None = None, image_name: str | None = None) -> dict:
    """Return a deep copy; never mutate a source workflow."""
    result = json.loads(json.dumps(workflow))
    if not isinstance(result, dict) or not result:
        raise ValueError("Workflow API must be a nonempty node-id to node dictionary")
    try:
        prompt_inputs = result[str(prompt_node)]["inputs"]
    except (KeyError, TypeError):
        raise ValueError(f"Prompt node {prompt_node} not found") from None
    for field in ("text", "prompt"):
        if field in prompt_inputs:
            prompt_inputs[field] = prompt
            break
    else:
        raise ValueError(f"Node {prompt_node} has no text/prompt input")
    if image_node is not None:
        if not image_name:
            raise ValueError("image_name is required for image-to-video")
        try:
            image_inputs = result[str(image_node)]["inputs"]
        except (KeyError, TypeError):
            raise ValueError(f"Image node {image_node} not found") from None
        if "image" not in image_inputs:
            raise ValueError(f"Node {image_node} has no image input")
        image_inputs["image"] = image_name
    return result


def find_video_outputs(history_record: dict) -> list[dict]:
    found = []
    for node_id, output in history_record.get("outputs", {}).items():
        if not isinstance(output, dict):
            continue
        for key in ("videos", "gifs", "images", "files"):
            for item in output.get(key, []):
                if not isinstance(item, dict):
                    continue
                name = item.get("filename", "")
                if Path(name).suffix.lower() in VIDEO_EXTS:
                    found.append({"node_id": str(node_id), "filename": name, "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")})
    return found


class ComfyClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: int = 30):
        p = urlparse(base_url)
        if p.scheme not in {"http", "https"} or not p.hostname:
            raise ValueError("ComfyUI URL must be http(s) with a host")
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, route: str, *, data: bytes | None = None, content_type: str | None = None) -> bytes:
        headers = {"Accept": "application/json"}
        if content_type:
            headers["Content-Type"] = content_type
        req = Request(self.base + route, data=data, headers=headers, method="POST" if data is not None else "GET")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except HTTPError as e:
            raise RuntimeError(f"ComfyUI HTTP {e.code}: {e.read(400).decode('utf-8', 'replace')}") from e
        except URLError as e:
            raise RuntimeError(f"ComfyUI unavailable: {e.reason}") from e

    def upload_image(self, path: Path) -> str:
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError("Existing PNG/JPEG/WebP input required")
        boundary = "sol_" + uuid.uuid4().hex
        b = boundary.encode("ascii")
        safe_name = path.name.replace('"', "_").replace("\r", "_").replace("\n", "_")
        mime = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        body = (b"--" + b + b"\r\n" + f'Content-Disposition: form-data; name="image"; filename="{safe_name}"\r\n'.encode()
                + f"Content-Type: {mime}\r\n\r\n".encode() + path.read_bytes() + b"\r\n" + b"--" + b + b"\r\n"
                + b'Content-Disposition: form-data; name="overwrite"\r\n\r\nfalse\r\n' + b"--" + b + b"--\r\n")
        out = json.loads(self.request("/upload/image", data=body, content_type=f"multipart/form-data; boundary={boundary}"))
        return out["name"]

    def queue(self, workflow: dict) -> str:
        body = json.dumps({"prompt": workflow, "client_id": uuid.uuid4().hex}, ensure_ascii=False).encode("utf-8")
        data = json.loads(self.request("/prompt", data=body, content_type="application/json"))
        if "prompt_id" not in data:
            raise RuntimeError(f"ComfyUI declined workflow: {data.get('error', data)}")
        return data["prompt_id"]

    def await_result(self, prompt_id: str, timeout_seconds: int = 900, poll_seconds: float = 2.0) -> dict:
        end = time.monotonic() + timeout_seconds
        while time.monotonic() < end:
            batch = json.loads(self.request("/history/" + prompt_id))
            if prompt_id in batch:
                record = batch[prompt_id]
                status = record.get("status", {})
                if status.get("status_str") == "error" or status.get("completed") is False:
                    raise RuntimeError("ComfyUI execution reported error/incomplete: " + json.dumps(status, ensure_ascii=False)[:600])
                return record
            time.sleep(poll_seconds)
        raise TimeoutError("Video is not complete; queue continues on ComfyUI. Prompt ID: " + prompt_id)

    def download_video(self, item: dict, dest: Path) -> dict:
        query = urlencode({"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")})
        data = self.request("/view?" + query)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise FileExistsError(f"Refusing to overwrite {dest}")
        dest.write_bytes(data)
        return {"path": str(dest), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SOL local video generation via existing ComfyUI workflows")
    ap.add_argument("mode", choices=["text-to-video", "image-to-video"])
    ap.add_argument("--workflow", required=True, type=Path, help="ComfyUI API-format video workflow JSON")
    ap.add_argument("--prompt", required=True, help="Vietnamese or other natural-language video prompt")
    ap.add_argument("--prompt-node", required=True, help="ComfyUI positive-prompt node ID")
    ap.add_argument("--image", type=Path, help="Source image for image-to-video")
    ap.add_argument("--image-node", help="ComfyUI LoadImage node ID")
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--output-dir", default="video_outputs", type=Path)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true", help="Validate and show workflow preview, without network or rendering")
    args = ap.parse_args(argv)
    if args.mode == "image-to-video" and (not args.image or not args.image_node):
        ap.error("image-to-video requires --image and --image-node")
    if args.mode == "text-to-video" and (args.image or args.image_node):
        ap.error("text-to-video does not use --image or --image-node")
    workflow = json.loads(args.workflow.read_text(encoding="utf-8"))
    client = None if args.dry_run else ComfyClient(args.server)
    image_name = None
    if args.mode == "image-to-video":
        if not args.image.is_file():
            ap.error("Image file does not exist")
        image_name = ("DRY_RUN_" + args.image.name) if args.dry_run else client.upload_image(args.image)
    prepared = mutate_workflow(workflow, args.prompt, args.prompt_node, args.image_node, image_name)
    if args.dry_run:
        print(json.dumps({"mode": args.mode, "prepared": True, "nodes": len(prepared), "will_render": False}, ensure_ascii=False))
        return 0
    prompt_id = client.queue(prepared)
    print(json.dumps({"prompt_id": prompt_id, "state": "queued", "mode": args.mode}, ensure_ascii=False), flush=True)
    record = client.await_result(prompt_id, args.timeout)
    items = find_video_outputs(record)
    if not items:
        raise RuntimeError(f"ComfyUI run {prompt_id} finished but no video output in history")
    results = []
    for i, item in enumerate(items):
        ext = Path(item["filename"]).suffix.lower()
        dest = args.output_dir / (prompt_id + ("_" + str(i) if i else "") + ext)
        results.append(client.download_video(item, dest))
    receipt = {"schema": "SOL_VIDEO_RECEIPT/1.0", "mode": args.mode, "prompt_id": prompt_id,
               "workflow_sha256": hashlib.sha256(args.workflow.read_bytes()).hexdigest(), "videos": results}
    receipt_path = args.output_dir / (prompt_id + ".receipt.json")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, TimeoutError, FileExistsError) as error:
        raise SystemExit("ERROR: " + str(error))
