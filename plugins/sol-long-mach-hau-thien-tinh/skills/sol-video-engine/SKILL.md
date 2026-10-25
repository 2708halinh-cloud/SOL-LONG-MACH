---
name: sol-video-engine
description: Create videos from text or an uploaded image using a real user-controlled ComfyUI inference engine. Route from SOL/TESSERACT X_0, require local backend, use receipt readback and never confuse an adapter with a rendered video.
---
# SOL VIDEO ENGINE / V0.1

## Entry contract

`X_0_DAO_TAC_NHAN → VIDEO_ROUTER → MODE(text-to-video | image-to-video) → COMFYUI API → VIDEO_OUTPUT → SHA256 READBACK → X_0`.

This is a USER-owned local-first capability plugin. It can be selected in ChatGPT as a reusable skill. **An installed plugin does not mean that ComfyUI, models, the GPU or a long-running service is already active.** No credit-consuming provider is contacted without a real configured connection. Nothing uploads to Drive or an external service by default.

## Capabilities

- **TEXT → VIDEO:** take Vietnamese/English text, select an installed video model workflow, set text/prompt input and queue a ComfyUI render.
- **IMAGE → VIDEO:** take an accessible source image, upload to the user-controlled local ComfyUI endpoint, set the image node and optional motion prompt, then queue a render.
- **READBACK:** download returned MP4/WEBM/MOV/MKV/GIF from the ComfyUI output endpoint, refuse overwrite, preserve SHA-256 and per-render JSON receipt.
- **DRY-RUN:** validate API workflow JSON and node mapping without consuming GPU or starting a render.

## Required target/runtime

1. An authorized local/remote executor able to run Python 3.9+.
2. A live ComfyUI server (default `http://127.0.0.1:8188`).
3. A model installation plus API-format ComfyUI **video** workflow appropriate for the selected mode, e.g. Wan video workflows; actual model weight, GPU memory and license are backend concerns.
4. Exact prompt-node ID; for image-to-video, also exact `LoadImage` node ID and source image path.

Do not fabricate `prompt_id`, `mp4` outputs or assume locally listed folders are running model services. If the host lacks access, preserve the edge and test the next callable executor.

## CLI examples

From `skills/sol-video-engine/scripts/` or with explicit script path:

```bash
python3 sol_video_engine.py text-to-video --workflow path/to/wan_text_api.json --prompt "Một con mèo đi giữa khu rừng phát sáng, máy quay tiến chậm" --prompt-node 6 --output-dir ./out
python3 sol_video_engine.py image-to-video --workflow path/to/wan_image_api.json --image photo.png --image-node 12 --prompt "Nhân vật bước nhẹ, gió thổi tóc, máy quay pan trái" --prompt-node 6 --output-dir ./out
python3 sol_video_engine.py text-to-video --workflow path/to/wan_text_api.json --prompt "Mặt trời mọc" --prompt-node 6 --dry-run
```

IDs **6/12** above are examples, not inferred universal identifiers. Export workflow from ComfyUI in API-format and inspect its actual node IDs. The script does not install models, generate fake video via FFmpeg, or depend on Node.js.

## Source reconciliation

- GitHub source repo: `2708halinh-cloud/x-time-web` (local checkout observed at `C:\Users\halin\x-time-web` on 2026-10-11); the SOL personal-access GitHub REST route is an independent source/provenance capability.
- This plugin's release is a private skill-level adapter, not evidence of any GitHub commit/PR and not a substitute for original repo content.
- Preserve existing X_0 ring stages and original GGDV material. Do not modify disks/VHDX during this capability setup.
- The script uses Python stdlib and only performs network requests to its explicitly supplied ComfyUI server.

## Tests

Run `python3 -m unittest discover -s tests -v` with `PYTHONPATH=scripts` (or run `python3 -m unittest discover -s tests` if installed/import path is configured). Tests cover workflow mutation and output extraction; not GPU rendering.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/sol-video-engine/sol-video-engine/skill.md
skills://plugins/sol-video-engine/sol-video-engine/scripts/sol_video_engine.py
skills://plugins/sol-video-engine/sol-video-engine/tests/test_sol_video_engine.py