# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Đào Thị Huyền  
> **Mã Sinh Viên / Mã Học viên:** 2A202602670  
> **Chủ đề Lựa chọn:** Trợ lý Dịch vụ Khách hàng VinBus — Tra cứu lộ trình tuyến xe bus điện và đăng ký vé tháng (Gợi ý 4.2, docs/DANH_SACH_DE_TAI.md)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Các yêu cầu tra cứu, đăng ký và đặc biệt TC04 cần phân tích ý định, trích xuất tham số và thực hiện theo thứ tự. Phiên bản hiện tại mới thể hiện đầy đủ một bước tool trong TC04. |
| **2. Tool Interaction** | 5 / 5 | Agent sử dụng MCP Server để gọi `route_query` và `register_monthly_ticket`, nhận observation có cấu trúc từ lớp dữ liệu backend. |
| **3. Dynamic Decision** | 4 / 5 | Agent quyết định trả lời trực tiếp với TC01, gọi tool với các tuyến hợp lệ và xử lý `NOT_FOUND` với VB99. TC04 chưa tiếp tục gọi tool đăng ký sau khi tra cứu. |
| **4. Long Horizon Goal** | 3 / 5 | Luồng đăng ký có nhiều thông tin cần giữ xuyên suốt, nhưng implementation hiện tại kết thúc sau observation đầu tiên thay vì duy trì mục tiêu qua nhiều lượt tool. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Tổng điểm > 12/20: Bài toán phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dưới đây là đoạn trích thực tế từ file `docs/trace_waterfall.json` sau khi chạy `python src/app.py --all` với `GeminiProvider`:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu thông tin lộ trình tuyến xe bus điện VB01.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "route_query",
    "arguments": {"route_id": "VB01"},
    "observation": {
      "status": "SUCCESS",
      "route_id": "VB01",
      "data": {
        "route_name": "Vinhomes Ocean Park - Long Biên",
        "price_monthly": 200000
      }
    },
    "latency_ms": 1623.81
  },
  {
    "step": 2,
    "query": "Hãy tra cứu thông tin lộ trình tuyến xe bus điện VB01.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Thông tin lộ trình tuyến VB01 (Vinhomes Ocean Park - Long Biên): Từ Vinhomes Ocean Park đến Bến xe Long Biên, Giờ hoạt động: 05:30 - 22:00, Giá vé tháng: 200000 VNĐ.",
    "latency_ms": 10.0
  }
]
```

Tổng trace có 9 sự kiện: 5 `FINAL_ANSWER` và 4 `TOOL_EXECUTION`. TC05 trả về `NOT_FOUND` đúng quy định, không bịa dữ liệu. TC04 đã tra cứu thành công VB02 nhưng chưa phát sinh bước đăng ký vé tháng tiếp theo.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã cấu hình Gemini và chạy test suite với `GeminiProvider`.
- **Tổng số Test Cases đã chạy:** **5 / 5 test cases** (TC04 còn thiếu bước đăng ký theo kỳ vọng).
- **Số lượt gọi Tool qua MCP Server:** **4 lượt** (`route_query` 3 lượt, `register_monthly_ticket` 1 lượt).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
