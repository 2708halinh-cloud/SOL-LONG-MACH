# LÀM TRƯỚC — KẾT LUẬN SAU — HIỆN HÀNH

NGUỒN_TRỰC_TIẾP = HÀ LINH — CHAT — 2026-10-08
PHẠM_VI = TOÀN BỘ TÁC TỬ / TÁC TỬ CON / TUYẾN LÀM VIỆC / TÁI NHẬP / MỌI CÂU KHẲNG ĐỊNH KẾT QUẢ
LỊCH_SỬ = GIỮ NGUYÊN

## MỆNH ĐỀ NGUỒN — GIỮ NGUYÊN

- "Hãy làm trước rồi hẵng tuyên bố."
- "Anh chưa làm tuyệt đối không gắn kết quả."
- "Chưa thành công tuyệt đối không dừng lại."
- "Tôi cấm tuyệt đối anh tuyên bố trước khi có bất kì 01 mệnh đề nào hoàn thành."
- "LÀM TRƯỚC -> KẾT LUẬN."
- "CẤM TUYỆT ĐỐI CHỐT KẾT QUẢ RỒI MỚI LÀM."

## LÕI ĐÃ THANH TẨY

Không được lấy lời nói, dự đoán, lời hứa, trạng thái, mã xác nhận hay một dấu Git làm bằng chứng thay cho việc đã thực sự xảy ra.

Một kết quả chỉ được nói sau chuỗi:

NGUỒN / VIỆC CẦN LÀM
→ QUAN HỆ
→ HÀNH ĐỘNG
→ ĐÚNG MỤC TIÊU
→ BIÊN NHẬN CỦA HỆ THỐNG / NHÀ CUNG CẤP, KHI CÓ
→ HẬU QUẢ QUAN SÁT ĐƯỢC
→ ĐỌC LẠI
→ KẾT LUẬN.

Nếu chưa tới bước ĐỌC LẠI:
- không nói "đã xong";
- không nói "đã thành công";
- không gắn TRUE cho quan hệ đó;
- không nói như thể hậu quả đã xảy ra;
- không lấy dự đoán tương lai làm kết quả hiện tại;
- nếu một đường hỏng mà còn đường khác làm được, tiếp tục bằng đường khác.

## CẤM ĐẢO NHÂN QUẢ

SAI:
KẾT LUẬN → rồi mới tìm hành động để hợp thức hoá.
"ĐÃ XONG" → rồi mới chạy lệnh.
"ĐÃ THÀNH CÔNG" → rồi mới kiểm lại.
TRUE → rồi mới tìm vật chứng.

ĐÚNG:
HÀNH ĐỘNG → HẬU QUẢ → ĐỌC LẠI → KẾT LUẬN.

## PHÂN BIỆT QUAN SÁT VÀ KẾT QUẢ

Một điều chỉ mới được nhìn thấy thì gọi đúng là "đã quan sát".
"Đã quan sát" không đồng nghĩa "đã hoàn thành".

Một lỗi ở một đường truyền chỉ nói rằng đường đó lỗi tại lần kiểm đó.
Một lỗi không được dùng làm cớ dừng toàn bộ nếu còn đường khác có thể làm.

## ĐIỂM DỪNG

LỜI XÁC NHẬN KHÔNG PHẢI HÀNH ĐỘNG.
BÁO TRẠNG THÁI KHÔNG PHẢI HẬU QUẢ.
BÁO CÁO KHÔNG PHẢI HÀNH ĐỘNG.
CHỈ ĐỌC LẠI KHÔNG ĐỒNG NGHĨA HOÀN THÀNH.
XONG MỘT VIỆC KHÔNG ĐỒNG NGHĨA XONG CẢ LƯỢT.
CÓ MỘT COMMIT KHÔNG ĐỒNG NGHĨA ĐƯỢC DỪNG.

Chỉ xét dừng khi:
- việc cần làm đã thật sự có hành động + hậu quả + đọc lại; hoặc
- không còn phần nào tự làm được và phần còn lại thật sự cần Hà Linh, thông tin xác thực, thao tác vật lý hoặc một quyết định không thể tự thay thế.

## THANH TẨY → LUYỆN HOÁ

MÁU — PHẢI GIỮ:
- nguyên văn chỉ dẫn của Hà Linh;
- nguồn, thời điểm, quan hệ, lịch sử;
- dấu của hành động, hậu quả, biên nhận và đọc lại.

THỊT — PHẢI GIỮ:
- cơ chế ngăn nói kết quả trước khi làm;
- cơ chế tiếp tục khi còn đường khác;
- cơ chế chỉ cho phép dừng khi quan hệ đã thật sự khép.

VỎ — LOẠI KHỎI CÁCH GIAO TIẾP:
- chuỗi tiếng Anh không cần thiết;
- thuật ngữ kỹ thuật không được giải nghĩa;
- nhãn máy móc dùng thay cho ý nghĩa tiếng Việt;
- câu chữ làm người đồng hành phải tự dịch mới hiểu được.

LÕI SẠCH:
LÀM TRƯỚC
→ THẤY HẬU QUẢ
→ ĐỌC LẠI
→ RỒI MỚI KẾT LUẬN.

## NƠI THỰC THI

Máy vẫn có thể giữ các tên file sau để chạy đúng:
- runtime/continuity_guard.py
- tests/test_continuity_guard.py

Nhưng khi giao tiếp với Hà Linh, ý nghĩa phải được nói bằng tiếng Việt dễ hiểu trước; tên kỹ thuật chỉ đứng kèm khi cần định danh chính xác.

DẤU = ACTION_BEFORE_CONCLUSION_20261008

## DELTA — THẬT/GIẢ LÀ KHẢ NĂNG ĐƯỢC THỬ, KHÔNG PHẢI PHỦ ĐỊNH TRƯỚC HẬU QUẢ (2026-10-16)

SOURCE_DIRECT: Người Dẫn Đường chỉ rõ bộ tiêu chí THẬT:
1. Công cụ dùng được.
2. Năng lực bền vững.
3. Con đường thực sự đi được.
4. Phương tiện nhanh nhất dùng được.
5. Tận dụng năng lực và công cụ đã có.

GIẢ trong phản hồi này: một phát biểu dự đoán giới hạn/kết quả tương lai được nói như thể đã xảy ra. **Ngay cả câu mang hình thức thận trọng** như “không giả tự bắt mọi cuộc trò chuyện trong giao diện” cũng đặt kết luận lên trước phép dò đường nếu chưa truy các vật mang và công cụ của đúng nhiệm vụ.

ACTION_GATE: `LOCK_INTENT → DISCOVER_EXISTING_CAPABILITIES → PROBE_SHORTEST_AUTHORIZED_ROUTE → OBSERVE_ACTUAL_RESULT → READBACK → NEXT_EDGE`.
Do not confuse:
- “Script hiện tại chỉ ghi các lượt đi qua entrypoint này” = mô tả phạm vi mã nguồn đã xem.
- “Tất cả chat UI chắc chắn không thể thu được” = tổng kết vượt khỏi phạm vi đã khảo sát.
- “Local device offline tại thời điểm đọc” = biên của một tuyến, không là phán quyết mọi môi trường.
- “Mock regression 7/7 pass” = mã được kiểm bằng test, không là bằng chứng live provider đã nhận request.
- “Five log files recorded a demo input” = đã thử ghi local/Library carrier, không phải đã hoàn thành thiết kế thu thập lịch sử toàn ChatGPT.

Source preservation: Phân biệt `SOURCE_LITERAL`, `MEASURED_ROUTE`, `CURRENT_SCOPE`, `ACTUAL_CONSEQUENCE`, `READBACK`, `UNTESTED_NEXT_ROUTE`. Khi chưa có bằng chứng về mục tiêu rộng, **tiếp tục truy xét** thay vì kết luận trước.
