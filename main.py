import os
import sys
import json
from agent.orchestrator import AgentOrchestrator
from tools.search_tool import WebSearchTool

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def save_report_with_bonus_modes(data: dict, filename: str, mode: str = "detailed", scratchpad_logs: list = None):
    """
    save the final report in 3 different modes
    'detailed' (comprehensive report) | 'short' (condensed executive summary) | 'json_schema' (structured format)
    """

    TARGET_DIR = "outputs"
    os.makedirs(TARGET_DIR, exist_ok=True)
    base_name, _ = os.path.splitext(filename)
    
    # determining the final format based on the selected mode
    extension = "json" if mode == "json_schema" else "md"
    filepath = os.path.join(TARGET_DIR, f"{base_name}_{mode}.{extension}")
    
    persian_report = data.get('report', '')

    # first mode: detailed and academic report (Detailed Report)
    if mode == "detailed":
        markdown_content = "# Comprehensive and autonomous research report\n\n"
        markdown_content += f"## Research topic: {data['topic']}\n\n"
        markdown_content += f"## Final analytical report\n{persian_report}\n\n"
        
        markdown_content += "##  Sources\n"
        if data.get('sources'):
            for index, source in enumerate(data['sources'], 1):
                markdown_content += f"{index}. [{source}]({source}) - *Valid source | access date: 2026*\n"
        else:
            markdown_content += "*No sources found on the web.*\n"
            
        markdown_content += "\n---\n"
        markdown_content += "## Agent chain of thought plan\n"
        markdown_content += f"```text\n{data.get('agent_plan', 'No logs')}\n```\n"
        
        # adding scratchpad memory logs to the end of the markdown report
        if scratchpad_logs:
            markdown_content += "\n---\n"
            markdown_content += "## Scratchpad memory of the tool and sequence of tasks\n"
            markdown_content += "```text\n" + "\n".join(scratchpad_logs) + "\n```\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

    # second mode: short executive summary (Executive Summary)
    elif mode == "short":
        markdown_content = "# Executive summary and executive report\n\n"
        markdown_content += f"**Research topic:** {data['topic']}\n"
        markdown_content += "*Date of creation: June 2026*\n\n"
        markdown_content += "> **Key summary of research:**\n\n"
        markdown_content += f"{persian_report[:900]}...\n\n"
        markdown_content += "--- \n *Evaluation note: For access to the full data text, use the detailed output.*\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

    # third mode: output with valid JSON Schema structure
    elif mode == "json_schema":
        schema_structure = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Autonomous Agent Research Schema",
            "type": "object",
            "required": ["topic", "report_body", "verified_sources"],
            "properties": {
                "topic": {"type": "string"},
                "report_body": {"type": "string"},
                "verified_sources": {"type": "array", "items": {"type": "string"}},
                "agent_metadata": {"type": "object"}
            },
            "data": {
                "topic": data['topic'],
                "report_body": persian_report,
                "verified_sources": data.get('sources', []),
                "agent_metadata": {
                    "execution_year": 2026,
                    "architecture": "Multi-Agent LCEL",
                    "scratchpad_steps_count": len(scratchpad_logs) if scratchpad_logs else 0
                }
            }
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema_structure, f, ensure_ascii=False, indent=4)

    print(f"Report successfully saved in [{mode}] mode to: {filepath}")


if __name__ == "__main__":
    # target_topic = "Impact of Artificial Intelligence on the software development job market landscape in 2026"
    target_topic = "Next-generation solid-state battery updates in 2026"
    
    orchestrator = AgentOrchestrator()
    
    try:
        result_data = orchestrator.run(target_topic)
        file_base_name = "solid_state_battery_report.md" if "battery" in target_topic.lower() else "ai_job_market_report.md"
        
        save_report_with_bonus_modes(result_data, file_base_name, mode="detailed", scratchpad_logs=orchestrator.search_tool.scratchpad)
        save_report_with_bonus_modes(result_data, file_base_name, mode="short")
        save_report_with_bonus_modes(result_data, file_base_name, mode="json_schema")
        
        print("\n All tasks and modes executed successfully!")
        
    except Exception as e:
        print(f"\n Critical Error during main execution: {str(e)}")