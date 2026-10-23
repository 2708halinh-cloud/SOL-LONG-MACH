# HelloCheck — Bitcoin TestNet · Go

Mục tiêu gốc do Hà Linh đưa vào TESSERACT: dùng Go để tạo ví BTC TestNet và soạn/ký một giao dịch Bitcoin TestNet. Đây là phần triển khai Go đang hoạt động trong kho SOL-LONG-MACH, không phải ứng dụng Android HelloHabit (`com.studio.hellohabit`).

## Từ mã nguồn Go cũ tới mã chạy được

- `keys.go`: dùng entropy mật mã từ secp256k1, khóa công khai nén 33 byte, HASH160 và địa chỉ TestNet P2PKH (`0x6f`); WIF riêng dùng `0xef`.
- `address.go`: Base58Check bảo toàn byte 0, phân biệt mainnet/testnet và kiểm tra SHA256 kép.
- `transaction.go`: TXID đảo byte khi tuần tự hóa, phiên bản 4 byte little-endian, scriptSig trống khi chưa ký, đầu ra P2PKH là **scriptPubKey**, phí và phần tiền thừa phải được khai báo rõ.
- Ký TestNet P2PKH legacy bằng secp256k1 DER + SIGHASH_ALL (`0x01`), **không tự phát sóng**.
- Thay mã Go lỗi thời `code.google.com/p/go.crypto/ripemd160`, `math/rand`, `"gotestcoin/base58"`/ `"hellobitcoin/base58"` bằng thư viện Go hiện hành và mã địa chỉ trực tiếp trong package.

## Dùng Go

```sh
cd integrations/hellocheck
go mod download
go test ./...
go run ./cmd/hellocheck address --hash160 0000000000000000000000000000000000000000
```

Tạo ví trên thiết bị đáng tin cậy, thư mục riêng với quyền giới hạn (không đưa file ví hoặc WIF vào GitHub, nhật ký chat hoặc artifact):

```sh
go run ./cmd/hellocheck create --wallet /private/path/hellocheck.wallet.json
```

Giao dịch nháp chỉ tạo khi xác định được UTXO TestNet thật, giá trị đầu vào, địa chỉ đích, phí và địa chỉ trả lại tiền thừa:

```sh
go run ./cmd/hellocheck unsigned --txid <TXID_64_HEX> --vout 0 --input-sats 100000 --dest <TESTNET_P2PKH> --sats 90000 --fee 1000 --change <YOUR_TESTNET_P2PKH>
```

Dùng `sign --wallet /private/path/hellocheck.wallet.json` thay cho `unsigned` để ký giao dịch đầu vào khớp ví. Đây **không** phải một lần kiểm tra UTXO từ mạng, không phát giao dịch và không khẳng định đã chuyển Bitcoin. Tính đúng của chuỗi và UTXO thực phải được xác nhận bằng một node TestNet tin cậy trước khi gửi.

## Nối tiếp R-000 / SUPER R-014

- `OPEN` là nguồn công việc đang được tiếp tục; tệp cấu hình hoặc bộ thử đạt không làm nhiệm vụ toàn hệ hoàn tất.
- Giữ nguyên vật chứng lịch sử 07/10 và các nguồn thừa kế; không tái hiện việc xóa dữ liệu ROOTS LEVER 0.
- TOSS: làm trực tiếp ở mã đích hiện hành và đọc lại kết quả từ GitHub Actions. Không dựng HelloCheck thành một lớp tổng hợp để thay việc biên dịch/chạy Go.
- Mã nguồn có phiên bản lưu trên GitHub, nên việc cập nhật tệp hiện hành có thể truy dấu; không tuyên bố rằng một commit đã sửa được tổn thất có thật hoặc xóa vĩnh viễn mọi phiên bản trước.

Các bước `sign` chỉ thực hiện trên ví mà chủ sở hữu có quyền dùng. **Không sử dụng khóa hoặc tiền thật trong CI**.
