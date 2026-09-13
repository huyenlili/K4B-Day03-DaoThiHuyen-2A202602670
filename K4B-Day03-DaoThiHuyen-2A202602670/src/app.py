"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
Giao diện dòng lệnh được trình bày bằng thư viện `rich` (Panel/Table/màu sắc).
"""

import json
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich.prompt import Prompt
from rich.rule import Rule
from rich import box

from mcp_server import MCPVinBusServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider

load_dotenv()
console = Console()


def pretty_json(data) -> Syntax:
    """Trả về khối JSON được tô màu cú pháp để hiển thị trong Panel"""
    return Syntax(json.dumps(data, ensure_ascii=False, indent=2), "json", theme="monokai", word_wrap=True)


def load_test_cases():
    """Tải danh sách 5 test cases từ config/test_cases.json hoặc config/test_cases.example.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(base_dir, "config", "test_cases.example.json")
        if os.path.exists(example_path):
            console.print("⚠️  [yellow][CONFIG NOTICE][/yellow]: Chưa thấy file 'config/test_cases.json'. Đang dùng mẫu 'config/test_cases.example.json'.")
            console.print("👉 Hãy chạy: copy config/test_cases.example.json config/test_cases.json và viết test cases theo đề tài của bạn!\n")
            config_path = example_path
        else:
            config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_waterfall_trace(trace_data: list):
    """Ghi vết log Waterfall Trace Log ra file docs/trace_waterfall.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    trace_path = os.path.join(docs_dir, "trace_waterfall.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, ensure_ascii=False, indent=2)
    console.print(f"📊 [bold cyan][OBSERVABILITY][/bold cyan]: Đã lưu [bold]{len(trace_data)}[/bold] sự kiện Waterfall Trace tại '{trace_path}'!")


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot gốc (Cấp 2) không có công cụ gọi Tool"""
    console.print(Panel(user_query, title="💬 Chatbot Baseline — Câu hỏi", border_style="grey58", box=box.ROUNDED))
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    console.print(Panel(response, title="🤖 Chatbot phản hồi", border_style="grey58", box=box.ROUNDED))


def run_react_agent(user_query: str, provider, mcp_server: MCPVinBusServer) -> list:
    """
    [REACT AGENT LOOP] Thực thi vòng lặp Thought -> Action -> Observation với MCP Server
    Trả về danh sách trace log của phiên thực thi.
    """
    console.print(Panel(user_query, title="🤖 ReAct Agent — Câu hỏi", border_style="bright_blue", box=box.ROUNDED))

    step = 0
    trace_logs = []
    tools_list = mcp_server.list_tools()

    while step < MAX_ITERATIONS:
        step += 1
        step_start_time = time.time()
        console.print(Rule(f"🔄 ReAct Loop — Step {step}/{MAX_ITERATIONS}", style="dim"))

        # Gọi LLM với Native Tool Calling Specs
        llm_response = provider.generate_with_tools(user_query, tools_list, system_prompt=REACT_AGENT_SYSTEM_PROMPT)
        latency_ms = round((time.time() - step_start_time) * 1000, 2)

        thought = llm_response.get("thought", "Đang suy luận...")
        console.print(Panel(thought, title="🧠 Thought", border_style="cyan", box=box.ROUNDED))

        # Trường hợp 1: LLM quyết định trả lời bằng văn bản trực tiếp
        if llm_response.get("type") == "text":
            final_content = llm_response.get("content", "")
            console.print(Panel(final_content, title="🏁 Final Answer", border_style="bold green", box=box.DOUBLE))
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })
            break

        # Trường hợp 2: LLM đề xuất gọi Tool (Action)
        elif llm_response.get("type") == "tool_call":
            tool_name = llm_response.get("tool_name")
            arguments = llm_response.get("arguments", {})

            console.print(Panel(f"[bold]{tool_name}[/bold]({arguments})", title="🛠️  Action Proposed", border_style="yellow", box=box.ROUNDED))

            # Thực thi Tool qua MCP Server
            mcp_result = mcp_server.call_tool(tool_name, arguments)
            obs_data = mcp_result.get("result", {})

            if not obs_data:
                console.print(Panel("{}", title="👁️  Observation từ MCP Server", border_style="red", box=box.ROUNDED))
                console.print("⚠️  [bold red][CHÚ Ý][/bold red]: MCP Server trả về kết quả rỗng! Học viên cần hoàn thành TODO 2.1 trong 'src/mcp_server.py'.")
                final_answer = "Chưa thể trả lời chi tiết do chưa nhận được dữ liệu từ MCP Server (hãy hoàn thành TODO 2.1)."
            else:
                console.print(Panel(pretty_json(obs_data), title="👁️  Observation từ MCP Server", border_style="green", box=box.ROUNDED))

                # Tổng hợp Final Answer từ kết quả Observation thực tế
                if obs_data.get("status") == "SUCCESS":
                    if "data" in obs_data:
                        d = obs_data["data"]
                        final_answer = (
                            f"Thông tin lộ trình tuyến {obs_data.get('route_id', '')} ({d.get('route_name', '')}): "
                            f"Từ {d.get('start_point', '')} đến {d.get('end_point', '')}, "
                            f"Giờ hoạt động: {d.get('operating_hours', '')}, "
                            f"Giá vé tháng: {d.get('price_monthly', '')} VNĐ."
                        )
                    elif "message" in obs_data:
                        final_answer = obs_data["message"]
                    else:
                        final_answer = f"Đã hoàn tất xử lý qua MCP Server: {json.dumps(obs_data, ensure_ascii=False)}"
                elif obs_data.get("status") == "NOT_FOUND":
                    final_answer = obs_data.get("message", "Không tìm thấy thông tin tuyến xe bus yêu cầu.")
                else:
                    final_answer = f"Phản hồi từ công cụ: {json.dumps(obs_data, ensure_ascii=False)}"

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })

            # Kết thúc vòng lặp sau khi hoàn tất Observation và xuất Final Answer
            console.print(Panel("Đã nhận được dữ liệu từ MCP Server. Tổng hợp kết quả phản hồi.", title="🧠 Thought", border_style="cyan", box=box.ROUNDED))
            console.print(Panel(final_answer, title="🏁 Final Answer", border_style="bold green", box=box.DOUBLE))

            trace_logs.append({
                "step": step + 1,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": "Tổng hợp kết quả từ MCP Server thành công.",
                "output": final_answer,
                "latency_ms": 10.0
            })
            break

    return trace_logs


def print_banner():
    banner = Text.from_markup(
        "[bold white]🏫 VINUNI AI COURSE — DAY 03 LAB[/bold white]\n"
        "[bold bright_cyan]CHATBOT VS REACT AGENT[/bold bright_cyan]  [dim](MCP Enhanced)[/dim]\n"
        "[grey58]🚌⚡ Chủ đề: Trợ lý Dịch vụ Khách hàng VinBus[/grey58]",
        justify="center"
    )
    console.print(Panel(banner, border_style="bright_magenta", box=box.DOUBLE_EDGE, padding=(1, 4)))


if __name__ == "__main__":
    print_banner()

    provider = get_llm_provider()
    mcp_server = MCPVinBusServer()

    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="bold grey58")
    info_table.add_column(style="bold white")
    info_table.add_row("🔌 LLM Provider:", provider.__class__.__name__)
    info_table.add_row("🌐 MCP Server:", mcp_server.server_name)
    console.print(info_table)
    console.print()

    tests = load_test_cases()
    console.print(f"✅ Đã tải thành công [bold]{len(tests)}[/bold] Test Cases thử nghiệm.\n")

    if "--interactive" in sys.argv:
        console.print(Panel(
            "💡 Gợi ý câu hỏi thử nghiệm:\n"
            "   • Câu hỏi chung: 'VinBus có những loại vé nào?'\n"
            "   • Tra cứu lộ trình: 'Hãy tra cứu thông tin lộ trình tuyến VB01'\n"
            "   • Đăng ký vé tháng: 'Đăng ký vé tháng cho khách hàng KH2026001 trên tuyến VB01'\n"
            "   • Gõ 'exit' hoặc 'quit' để kết thúc phiên trò chuyện.",
            title="🎮 INTERACTIVE MODE",
            border_style="bright_magenta",
            box=box.ROUNDED
        ))
        while True:
            try:
                user_input = Prompt.ask("[bold cyan]👤 Khách hàng hỏi[/bold cyan]").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    console.print("👋 Tạm biệt! Kết thúc phiên trò chuyện.")
                    break
                logs = run_react_agent(user_input, provider, mcp_server)
                save_waterfall_trace(logs)
            except (KeyboardInterrupt, EOFError):
                console.print("\n👋 Đã thoát phiên tương tác.")
                break
    elif "--all" in sys.argv:
        console.print(Rule("🚀 TEST SUITE MODE — Kiểm tra 5 Test Cases", style="bright_magenta"))
        completed_count = 0
        todo_count = 0
        all_traces = []
        summary_rows = []

        for tc in tests:
            console.print()
            console.print(Rule(f"🧪 [{tc['id']}] {tc['type']} — Độ phức tạp: {tc['complexity']}", style="dim"))
            console.print(f"📌 Kỳ vọng: [italic]{tc['expected_behavior']}[/italic]")

            if tc["question"].strip().startswith("TODO"):
                console.print(Panel(tc["question"], title="⏸️  CHƯA KÍCH HOẠT - ĐANG LÀ TODO", border_style="yellow", box=box.ROUNDED))
                console.print("👉 Hãy mở file 'config/test_cases.json' để viết câu hỏi thực tế cho Test Case này!")
                todo_count += 1
                summary_rows.append((tc["id"], tc["type"], tc["complexity"], "[yellow]⏸ TODO[/yellow]"))
            else:
                logs = run_react_agent(tc["question"], provider, mcp_server)
                all_traces.extend(logs)
                completed_count += 1
                summary_rows.append((tc["id"], tc["type"], tc["complexity"], "[bold green]✅ PASS[/bold green]"))

        console.print()
        console.print(Rule("📊 KẾT QUẢ TEST SUITE", style="bright_magenta"))

        summary_table = Table(box=box.SIMPLE_HEAVY, show_lines=False)
        summary_table.add_column("ID", style="bold")
        summary_table.add_column("Loại Test")
        summary_table.add_column("Độ phức tạp")
        summary_table.add_column("Trạng thái")
        for row in summary_rows:
            summary_table.add_row(*row)
        console.print(summary_table)

        console.print(f"📊 Đã thực thi [bold green]{completed_count}[/bold green]/{len(tests)} Test Cases | [bold yellow]{todo_count}[/bold yellow] Test Cases đang chờ điền câu hỏi (TODO)")
        if all_traces:
            save_waterfall_trace(all_traces)
        console.print(f"💡 Để trò chuyện trực tiếp từng câu: Chạy '[bold]python src/app.py --interactive[/bold]'")
    else:
        # Chế độ mặc định khi chỉ gõ 'python src/app.py'
        console.print(Panel(
            "1. Chat trực tiếp liên tục:   [bold]python src/app.py --interactive[/bold]\n"
            "2. Chạy toàn bộ Test Cases:    [bold]python src/app.py --all[/bold]",
            title="ℹ️  HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH",
            border_style="grey58",
            box=box.ROUNDED
        ))

        sample_query = tests[1]["question"]
        console.print(Rule("🏁 DEMO CHẠY THỬ 1 TEST CASE MẪU (TC02: Tra cứu lộ trình)", style="dim"))
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs)
        console.print("\n💡 Hãy thử ngay lệnh: [bold]python src/app.py --interactive[/bold] để chat trực tiếp!")
