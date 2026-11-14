# QUY ƯỚC — SUB-GHZ SUPPORTED PROTOCOLS / UNLEASHED FIRMWARE

**Ngày ghi nhận:** 2026-10-14  
**Nguồn trực tiếp:** Văn bản “Sub-GHz Supported Protocols” do người dùng cung cấp trong cuộc trò chuyện.  
**Phạm vi:** Ứng dụng **SubGHz mặc định** của Unleashed Firmware. Ứng dụng riêng như **Weather Station** có danh mục giao thức riêng; không được gộp nhầm.

## 1. Nguyên tắc nhận định

- Danh sách gồm giao thức **được liệt kê là hỗ trợ**, cả **đã thử nghiệm và chưa thử nghiệm**. Không có chứng cứ thử nghiệm trên từng mục thì trạng thái = `TEST_STATUS_UNKNOWN`.
- Phân biệt `LISTED_SUPPORTED` (có tên trong tài liệu), `IMPLEMENTED_IN_CURRENT_BUILD` (chỉ khi xác minh build/version), `DECODE_VERIFIED`, `EMULATION_VERIFIED`, `HARDWARE_VERIFIED`. Không tự động nâng cấp trạng thái từ cấp thấp lên cấp cao.
- Giữ phân nhóm gốc: `STATIC_DYNAMIC` gồm `GARAGE_GATE`, `SENSORS_SMART_HOME`, `ALARMS`, `GENERIC_REMOTES`; `KEELOQ_MANUFACTURER` gồm `GARAGE_GATE` và `ALARMS_UNKNOWN_ORIGIN`.
- Mọi dữ liệu cần provenance: `source=user_supplied_2026-10-14`, văn bản gốc/đường dẫn repository nếu được xác minh, firmware revision, thời gian ghi nhận, tình trạng chưa xác minh. Không khẳng định tương ứng bản firmware mới nhất.

## 2. Tần số, điều chế và bit

- Đơn vị là **MHz**. Trong phần chú giải nguồn, “433 MHz thường nghĩa là 433.92 MHz”, “868 MHz = 868.35 MHz” là **quy ước gần đúng của tài liệu**, không phải phép thay thế vô điều kiện. Các trị số **433.42, 434.42, 430.5, 868.80, 310, 315, 390, 300, 303, 318...** phải được giữ nguyên khi ghi cụ thể.
- Nếu dòng giao thức **không ghi tần số**, đặt `frequencies_mhz: null`, `frequency_status: UNKNOWN`; tuyệt đối không điền theo nhóm hoặc “thường dùng”.
- Giữ **nguyên nhãn điều chế được ghi trong nguồn** (`AM650`, `FM`, `FSK476`, `FSK12K`, ...); các nhãn mô tả **cấu hình nhận/đọc remote**, không tự xác nhận cấu hình phát.
- Theo nguồn: `FM` có nghĩa thử các điều chế FM sẵn có; `FSK???` ứng với tùy chọn `FM???` tại `SubGHz → Read → Config`. Đó là mô tả giao diện của tài liệu, không phải khẳng định đồng nhất mọi loại FSK/FM.
- `bits` phải là độ dài khung nguồn ghi. Nếu nguồn không nêu thì để `null`, không suy từ thương hiệu hoặc kỹ thuật mã hóa. Nếu nguồn có nhiều dạng khung (vd. `12, 24 bits`), lưu **mảng** `[12,24]`.

## 3. Phân biệt loại mã và khả năng

- `Static`: mã/khung truyền cố định theo mô tả nguồn.
- `Dynamic` / `Rolling Code`: bộ đếm hoặc trạng thái thay đổi; **không** coi capture cũ là mã có thể dùng lặp lại.
- `Pseudo-Dynamic` và `Simple Dynamic`: giữ nguyên nhãn; không đổi thành `Static` hoặc `Dynamic` chung khi mất thông tin.
- `KeeLoq`: một họ mã nhảy, có nhiều kiểu learning, seed, phần serial trong Hop và khóa nhà sản xuất. Các khác biệt này phải giữ **theo từng dòng**, không suy ra cùng một chìa khóa hay cách học giữa các hãng.
- `Decode only`: chỉ giải mã; không tuyên bố phát/giả lập (vd. iDO).
- `Static mode only`: chế độ mã động **không được hỗ trợ** (vd. Nero Radio).
- Một tên giống nhau không đồng nghĩa cùng thuật toán hoặc key: `Genius` và `FAAC SLH` có thể dùng khung giống nhau nhưng **manufacture key khác nhau** theo nguồn.
- Ghi chú như `unverified`, `custom button map unverified`, `receiver checks ... (unverified)` phải được bảo toàn như `UNVERIFIED_NOTE`, không nâng thành sự thật đã thử nghiệm.
- Tên hiển thị trong **Add Manually** là một trường riêng `add_manually_label`, không tự động gán bằng tên protocol, tần số đo được hoặc chức năng phát.

## 4. Quy ước KeeLoq

- Câu “mặc định `simple` và `10bits` cho phần serial trong Hop” là **chú giải mặc định của danh mục KeeLoq được cung cấp**, không phải thuộc tính bắt buộc của mọi hãng.
- `normal`, `simple`, `special`, `table driven`, `magic XOR` và các mô tả `no serial part`, `8/10/12-bit`, `ByteReversed` phải được giữ riêng nếu dòng có nêu.
- Tần số của một mục KeeLoq chỉ được điền khi **dòng mục đó** thực sự cung cấp; ghi chú “most KeeLoq manufacturers operate in 433/868 MHz” không đủ để gán tần số cho từng hãng.
- Ghi chú về seed, serial, key và chức năng học chỉ có giá trị mô tả tài liệu; không coi đây là quyền thao tác với hệ thống kiểm soát ra vào.

## 5. Schema giao thức tối thiểu

```json
{
  "name": "Giao thức / hãng như được ghi trong nguồn",
  "source_section": "STATIC_DYNAMIC | KEELOQ_MANUFACTURER",
  "category": "GARAGE_GATE | SENSORS_SMART_HOME | ALARMS | GENERIC_REMOTES | ALARMS_UNKNOWN_ORIGIN",
  "frequencies_mhz": null,
  "source_frequency_text": null,
  "read_modulation": null,
  "frame_bits": null,
  "code_type": "STATIC | DYNAMIC | PSEUDO_DYNAMIC | SIMPLE_DYNAMIC | KEELOQ | UNKNOWN",
  "support_scope": "LISTED_SUPPORTED",
  "capability_limitations": [],
  "add_manually_label": null,
  "learning_or_seed_note": null,
  "unverified_notes": [],
  "test_status": "TEST_STATUS_UNKNOWN",
  "firmware_version": null,
  "source": "USER_SUPPLIED_2026-10-14"
}
```

Số liệu chưa biết phải là `null`, không gán `0`, không lấy trị mặc định đoán mò. Chỉ điền trường nào có chứng cứ từ đúng một dòng gốc và giữ ghi chú nguyên văn.

## 6. Các ngoại lệ tiêu biểu không được làm mất khi phân tích

- **iDO**: `433MHz`, `AM650`, 48 bits, `Dynamic`, **Decode only**.
- **Nero Radio**: `434.42MHz`, `AM650`, 56 bits, **Static mode only**, Dynamic **unsupported**.
- **Cardin S449**: `433.92MHz`, `FSK12K`, KeeLoq 64 bits; receiver checks 10 bits được nguồn đánh dấu **unverified**.
- **Sommer**: `434.42MHz, 868.80MHz`, `FSK12K (or FSK476)`; không đổi 868.80 thành 868.35.
- **Somfy Telis**: `433.42MHz`, `AM650`, 56 bits Dynamic; Add Manually hiển thị `433MHz` nhưng tạo **433.42MHz**.
- **Security+2.0 Keypad**: 86 bits Dynamic; khác khung Security+2.0 thường 62 bits Dynamic.
- **Prastel**: mục 25-bit Static khác mục 42-bit Dynamic; mapping 4 nút của dòng Dynamic **unverified**.
- **Nice O-Code**: mô tả FloR-S keyed bởi 16-bit installer code phải được giữ như ghi chú nguồn; không mặc nhiên suy ra khả năng giả lập hay dùng lại bản ghi.
- **Genius**: khung liên quan FAAC SLH nhưng manufacture key riêng; giữ `Manufacture: Genius` như ghi chú định danh nguồn.
- **Erreka**: có mô tả seed/learning và nhãn Add Manually khác nhau theo 433/868; không xem trạng thái đó là kiểm chứng giải mã/phát.

## 7. Giới hạn thao tác, bằng chứng và readback

Đây là **quy ước phân loại/tra cứu**, không phải giao thức kết nối phần cứng, không phải trình mô phỏng, không phải tài liệu xác thực quyền truy cập. Hoạt động ghi/phát RF, pairing, kiểm tra bộ thu phải diễn ra trên thiết bị **có quyền sở hữu hoặc ủy quyền rõ ràng** và tuân thủ băng tần, công suất, quy định khu vực. Không hướng dẫn mở cổng/khóa trái phép hoặc vượt qua rolling code.

Một xác nhận vận hành phải có đủ: `device`, `firmware_revision`, `transceiver`, `frequency`, `modulation`, `sample/source`, `actual_operation`, `result`, `timestamp`, `readback`. Không ghi `WORKING` khi mới chỉ tạo file.

**T007:** `SOURCE_DIRECT → PARSE/CLASSIFY → UNKNOWN_PRESERVED → VALIDATE → READBACK → [optional HARDWARE TEST]`. Chưa có kiểm chứng firmware và thiết bị thật trong phiên này, nên trạng thái vận hành `OPEN`.

**Nguồn trích dẫn:** tài liệu do người dùng dán, phần mở đầu “Sub-GHz Supported Protocols”, mục “Static & Dynamic protocols list”, “KeeLoq Rolling Code Supported Manufacturers list” và “Protocol Type Reference”. Tài liệu yêu cầu **mention source when copying**: tên nguồn `Unleashed Firmware`, không được thay bằng tuyên bố của người biên soạn.
