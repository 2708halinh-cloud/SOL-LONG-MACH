# SOURCE_DIRECT_USER — Kỹ năng có tên / resolver / tham chiếu (17/10/2026)

**Nguồn:** Tin nhắn người dùng trong phiên ngày 17/10/2026. Đây là bản lưu lời nguồn; không tự gán ID message hoặc timestamp chi tiết chưa truy được.

> Nếu người dùng đặt tên cho một kỹ năng (bằng $SkillName hoặc văn bản thuần túy), hãy thêm việc sử dụng kỹ năng đó vào kế hoạch làm việc hiện tại của bạn. Nếu tệp bị thiếu, hãy tìm kiếm kỹ năng đó ở nơi khác trong trường hợp đường dẫn đã lỗi thời. Nếu không tìm thấy kỹ năng và kỹ năng đó cần thiết để người dùng hoàn thành nhiệm vụ, hãy dừng lượt chơi và giải thích lý do cho người dùng.
>
> Nếu công việc hiện tại của bạn có thể được hưởng lợi từ một kỹ năng nào đó, nhưng người dùng không yêu cầu kỹ năng đó một cách rõ ràng, hãy sử dụng khả năng phán đoán hợp lý để áp dụng các hướng dẫn, công cụ hoặc quy trình làm việc liên quan đến kỹ năng đó nhằm cải thiện kết quả. Không nên sử dụng một kỹ năng chỉ dựa trên từ khóa, sự liên quan hời hợt hoặc sự sẵn có của một kỹ năng có thể áp dụng được.
>
> Cách sử dụng kỹ năng
> Mở và đọc kỹ năng theo vị trí của nó: các kỹ năng hệ thống tệp nên được đọc từ hệ thống tệp, các kỹ năng thuộc sở hữu của môi trường nên được truy cập thông qua môi trường tương ứng, và các kỹ năng điều phối nên được tìm thấy bằng cách gọi skills.listvới {"authority":{"kind":"orchestrator"}}, chọn gói phù hợp và truyền của nó main_resourcecho skills.read. Tránh đọc lại các kỹ năng khi có thể.
> Khi một SKILL.mdtệp tham chiếu đến một tệp hoặc tài nguyên khác, hãy sử dụng cùng cơ chế truy cập như kỹ năng. Giải quyết các đường dẫn tương đối so với thư mục chứa tệp được hỗ trợ bởi hệ thống tệp SKILL.md. Đối với các kỹ năng điều phối, hãy chuyển mã định danh tài nguyên được tham chiếu chính xác với cùng quyền hạn và gói cho skills.read; không coi skill://mã định danh là đường dẫn hệ thống tệp.

**Vật mang:** Tin nhắn trong hội thoại, không phải tệp provider. Trạng thái trích dẫn nguyên văn: SOURCE_DIRECT_USER.
