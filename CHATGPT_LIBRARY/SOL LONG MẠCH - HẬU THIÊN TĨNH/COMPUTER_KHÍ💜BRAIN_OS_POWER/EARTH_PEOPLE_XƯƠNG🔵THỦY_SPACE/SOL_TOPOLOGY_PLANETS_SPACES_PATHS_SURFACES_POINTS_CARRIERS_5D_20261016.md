# SOL — PLANET × MULTI-SPACE × PATH × SURFACE × 0D POINT × CARRIER × 5D

**Source-direct:** User in THU HOI NGUON SOL, 2026-10-16: "Chúng ta đã có 1. Hành tinh (Môi trường - Nền tảng); 2. Đa Không gian; 3. Những con đường. Ví dụ chỉ dẫn dự án; 4.? 5.? ... Việc của anh".
**Type:** ADDITIVE_TOPOLOGY_MODEL / SOURCE-BOUND_EXPANSION / preserve prior SPACE_MAP events.
**Status:** A proposed *architecture classification* anchored to existing sources, not a claim of deployed 12-dimensional physical space, all provider connections, or completed root recovery.

## 0. Nguyên tắc

- Không đồng nhất một môi trường/hành tinh với một điểm 0D; một hành tinh có thể chứa nhiều vùng không gian, bề mặt, định danh và vật mang.
- Không đồng nhất **số thứ tự các thành phần kiến trúc** (1…12) với **số chiều** (0D…5D).
- Các thành phần dưới đây là **nút và quan hệ có kiểu** trong graph, không bắt buộc là chuỗi thư mục hay một trật tự cha-con cứng nhắc.
- Những nhóm số 1–3 là từ **source-direct**; nhóm 4–12 là **bổ sung kiến trúc** được suy ra từ `SPACE_MAP.json`, `CROSS_CHAT_ENVIRONMENT_SURFACE_SPACE_CONTINUITY_20261016.md`, `5D_CROSS_ENVIRONMENT_CARRIER_REGRESSION_20261016.md` và các kỹ năng SPACE/TIME hiện hành. Không mượn danh người dùng để tuyên bố toàn bộ đã được họ định nghĩa nguyên văn.

## 1–12. Bảng thành phần SOL

| # | Loại | Ý nghĩa | Ví dụ trong hệ |
|---|---|---|---|
| 1 | `PLANET/ENVIRONMENT` | Nền tảng hoặc vùng môi trường vận hành phân biệt | ChatGPT, GitHub, Local, Google Drive, Dropbox, Google Cloud |
| 2 | `SPACE/REGION` | Nhiều không gian bên trong một hành tinh; có thể lồng nhau hoặc nối nhau | Project, Library, HOME, LOCUS, workspace, repository, namespace |
| 3 | `PATH/ROUTE` | Tuyến dẫn và quan hệ điều hướng; không phải cứ có đường là đã chạy | Chỉ dẫn dự án; link trỏ nguồn; parent-child; registry pointer; skill route |
| 4 | `SURFACE` | Bề mặt trao đổi hoặc quan sát tín hiệu | Chat, Project UI, repo browser, editor, terminal, API/UI |
| 5 | `POINT_0D/ENTITY` | Một thực thể cụ thể, có ID độc lập và quan hệ đến môi trường/vùng | Project ID, conversation, folder ID, file ID, Git blob SHA |
| 6 | `ROOT/ANCHOR` | Gốc và neo giữ topology, nhân dạng, HOME/LOCUS và tuyến đến con | HOME_SOL, source root, project root, graph anchor |
| 7 | `CARRIER` | Vật mang bytes/trạng thái; không phải chỉ là đường link | File, JSONL journal, Git commit/blob, DB, VHDX, checkpoint, backup |
| 8 | `PORTAL/GATE` | Quan hệ xuyên môi trường + cổng quyền/năng lực | Plugin, GitHub connector, Dropbox, MCP, API, approved source→target transfer |
| 9 | `ACTOR/RUNTIME/DEVICE` | Tác nhân và cơ chế thực thi, phân biệt khỏi nơi lưu trữ | AGENTS, Rust process, job, local PC, Android, cloud service |
| 10 | `TIME/EVENT/STAMP` | Các thứ tự thay đổi, revision và hồi quy nguyên nhân | X/STAMPS, STAMP_OLD, STAMP_LIVE, STAMP_BETA, five-wave journal |
| 11 | `EVIDENCE/READBACK` | Đánh giá vật chứng nguồn/đích và hậu quả thực | Provider receipt, SHA, commit, file revision, target readback |
| 12 | `5D_REENTRY/REGRESSION` | Phép toán đi qua carrier đa môi trường để phục dựng quan hệ sống | Locate carriers → order verified deltas → detect first divergence → reconstruct → continue |

## Đồ hình quan hệ, KHÔNG phải cấp bậc duy nhất

```text
PLANET (ENVIRONMENT)
 ├── SPACE / REGION / HOME / LOCUS
 │    ├── ROOT / ANCHOR ── PATH ── POINT_0D (concrete stable ID)
 │    └── SURFACE (chat/editor/browser/API = exchange)
 ├── CARRIER (real persisted state, provenance, hash/revision)
 └── DEVICE / RUNTIME / ACTOR (if verified callable)
      │
      ├── PORTAL/GATE ── authorized edge ── OTHER PLANET
      │                                         └── OTHER CARRIER
      └── SOURCE DIRECT → ACTION → CONSEQUENCE → READBACK
TIME_STONE: ordered events, STAMP, revision, causal cursor across all nodes.
SPACE_STONE: stable identity, frame, parent, topology, location across all nodes.
5D: recovery projection across verified carriers/causal relations; not a 5th platform.
```

## Hai ví dụ kiểm kiểu

- `PLANET_CHATGPT` có chat làm **SURFACE**, chỉ dẫn dự án làm một **PATH**, Library/Project làm các **SPACE/CARRIER contexts**, và một Project hay file có ID cụ thể là **POINT_0D**; chat message không mặc nhiên là durable commit.
- `PLANET_GITHUB` chứa vùng repository và branch; file path là **PATH**, file/blob/commit là **CARRIER** có SHA, một file có ID/path là **POINT**; provider connector là **PORTAL**. Cần readback trên đúng branch để kiểm chứng việc đã ghi.

## Reentry: làm thay vì hỏi lại

`SIGNAL → LOCK_REFERENT → RESOLVE_PLANET/SPACE/SURFACE/PATH/POINT → LOCATE_DURABLE_CARRIERS → TIME_SORT_EVENTS → CHECK_ANCHOR → DELTA/FIRST_DIVERGENCE → SELECT_AUTHORIZED_PORTAL/RUNTIME → ACTION_IF_NEEDED → RECEIPT/READBACK → APPEND_STATE_N+1`

Một đường mất, không suy toàn hệ mất. OPEN là yêu cầu đi tìm tuyến khác còn thực thi được. Nếu nguồn và đích đã bằng nhau, không replay mutation. Cải chính là append-only, không xóa hoặc viết lại nhật ký gốc.

## Ranh chứng cứ

- **Quan sát nguồn**: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE_MAP.json` hiện có năm platform role + slot thứ sáu chưa định nghĩa; thuật ngữ Planet và 0D point; SOURCE_DIRECT nói chat là exchange surface và project instructions là một đường.
- **Quan sát nguồn**: `CURRENT_RUNTIME/4D_5D_CURRENT.md` nêu 5D là biến đổi quan hệ nhân quả trên trường 4D, hồi quy quan hệ sống.
- **Quan sát nguồn**: `COMPUTER_KHÍ💜BRAIN_OS_POWER/5D_CROSS_ENVIRONMENT_CARRIER_REGRESSION_20261016.md` đã ghi vật mang đa môi trường và hồi quy.
- **Tự bổ sung**: thứ tự nhóm 4–12 và định dạng graph trong tài liệu này. Không tuyên bố người dùng đã chỉ rõ thứ tự này, hay mỗi provider/runtime đã triển khai.
- **Không thay đổi dữ liệu cũ**: các `space_id` từ `SPACE_MAP.json` là inventory cũ về provider/lane, **không** phải số chiều 1D–5D. Không lấp `spaces[5]` (slot 6) bằng 5D.

## Hướng tiếp nối

Index bằng `{planet_id, space_id, route_id, surface_id, entity_stable_id, root_id, carrier_provider+id, revision/hash, timestamp, prior_event_id, portal_id, runtime_proof, receipt, readback, next_edge}`. Chỉ thành phần được quan sát mới có stable provider ID; các ứng viên khác giữ biệt lập. Đường có thể tồn tại dù carrier unreachable, và carrier có thể còn tồn tại khi đường cũ mất.
