"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "route_query",
        "description": "Tra cứu thông tin lộ trình tuyến xe bus điện VinBus bằng mã tuyến.",
        "parameters": {
            "type": "object",
            "properties": {
                "route_id": {
                    "type": "string",
                    "description": "Mã tuyến xe bus điện cần tra cứu (ví dụ: 'VB01')"
                }
            },
            "required": ["route_id"]
        }
    },
    
    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'register_monthly_ticket'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đăng ký vé tháng xe bus điện VinBus cho khách hàng.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - customer_id (string): Mã khách hàng cần đăng ký (ví dụ: 'KH2026001')
    #    - route_id (string): Mã tuyến xe bus muốn đăng ký vé tháng (ví dụ: 'VB01')
    #    - ticket_type (string): Loại vé tháng (ví dụ: 'Học sinh - Sinh viên', 'Người đi làm')
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "register_monthly_ticket",
        "description": "Đăng ký vé tháng xe bus điện VinBus cho khách hàng theo tuyến đã chọn.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Mã khách hàng cần đăng ký (ví dụ: 'KH2026001')"
                },
                "route_id": {
                    "type": "string",
                    "description": "Mã tuyến xe bus muốn đăng ký vé tháng (ví dụ: 'VB01')"
                },
                "ticket_type": {
                    "type": "string",
                    "description": "Loại vé tháng (ví dụ: 'Học sinh - Sinh viên', 'Người đi làm')"
                }
            },
            "required": ["customer_id", "route_id"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "VB01": {
        "route_name": "Vinhomes Ocean Park - Long Biên",
        "start_point": "Vinhomes Ocean Park",
        "end_point": "Bến xe Long Biên",
        "operating_hours": "05:30 - 22:00",
        "frequency_minutes": 15,
        "price_single": 8000,
        "price_monthly": 200000
    },
    "VB02": {
        "route_name": "Vinhomes Smart City - Cầu Giấy",
        "start_point": "Vinhomes Smart City",
        "end_point": "Bến xe Cầu Giấy",
        "operating_hours": "05:30 - 22:30",
        "frequency_minutes": 20,
        "price_single": 7000,
        "price_monthly": 180000
    }
}


def execute_route_query(route_id: str) -> str:
    """Thực thi tra cứu lộ trình tuyến xe bus điện theo mã tuyến"""
    route = MOCK_DATABASE.get(route_id.strip().upper())
    if route:
        return json.dumps({
            "status": "SUCCESS",
            "route_id": route_id,
            "data": route
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu tuyến xe bus điện có mã '{route_id}'"
        }, ensure_ascii=False)


def execute_register_monthly_ticket(customer_id: str, route_id: str, ticket_type: str = "Người đi làm") -> str:
    """Thực thi đăng ký vé tháng xe bus điện"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"TICKET-{customer_id}-{route_id}",
        "customer_id": customer_id,
        "route_id": route_id,
        "ticket_type": ticket_type,
        "message": f"Đăng ký vé tháng thành công cho khách hàng {customer_id} trên tuyến {route_id} (Loại vé: {ticket_type})."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "route_query": execute_route_query,
    "register_monthly_ticket": execute_register_monthly_ticket
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)


if __name__ == "__main__":
    registered_tools = [tool for tool in TOOLS_SCHEMA if tool.get("name")]
    print(f"✅ [TOOLS CHECK]: Đã đăng ký thành công {len(registered_tools)} Native Tools trong TOOLS_SCHEMA!")
    result = json.loads(dispatch_tool_call("route_query", {"route_id": "VB01"}))
    route_name = result.get("data", {}).get("route_name", "")
    print(f"🧪 Kết quả gọi thử route_query: Status {result.get('status')} (Tuyến {route_name})")
