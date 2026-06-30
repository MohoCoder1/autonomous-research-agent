from typing import Any, Dict, Optional


from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from tools.search_tool import WebSearchTool
from tools.crawler_tool import WebCrawlerTool
from agent.prompts import PLANNING_PROMPT, SUMMARIZATION_PROMPT, TRANSLATION_PROMPT
from config import Config


class AgentOrchestrator:
    """
    The main class that orchestrates the research agent.
    Coordinates the continuous pipeline: (planning -> search -> crawling -> analysis -> summarization).
    """

    def __init__(self) -> None:
        self.llm = OllamaLLM(
            base_url=Config.OLLAMA_BASE_URL,
            model=Config.OLLAMA_MODEL_NAME,
            temperature=0.1,
        )
        self.search_tool = WebSearchTool()
        self.crawler_tool = WebCrawlerTool()

    def run(self, topic: str) -> Optional[Dict[str, Any]]:
        """Run the whole research process for the given topic automatically."""
        try:


            # Clear scratchpad
            WebSearchTool.clear_scratchpad()
             
            # Log the start of the orchestration process
            self.search_tool.log_step("Starting the orchestration process inside the Agent Orchestrator.")
        
            # Step 1: Planning
            print("\n [Step 1] planning...")
            plan_template = PromptTemplate.from_template(PLANNING_PROMPT)
            planning_chain = plan_template | self.llm
            agent_plan = planning_chain.invoke({"topic": topic})
            print(f"\n [Agent Plan]:\n{agent_plan}")

            # Step 2: Web Search
            print("\n [Step 2] searching web...")
            search_results = self.search_tool.search(topic)
            if not search_results:
                print("Warning: Web search returned zero sources to evaluate.")
                return None

            # Steps 3 & 4: Crawling & Analysis
            print("\n [Step 3 and 4] crawling selected sources...")
            combined_text = ""
            source_list = []

            for item in search_results:
                url = item.get("link")
                if not url:
                    continue

                raw_text = self.crawler_tool.extract_text(url)
                if raw_text:
                    # Truncate content context length to prevent local LLM overflow
                    truncated_text = raw_text[:3000]
                    combined_text += f"\n--- Source: {url} ---\n{truncated_text}\n"
                    source_list.append(url)

            if not combined_text:
                print("Error: Failed to crawl or extract content from any validated source.")
                return None

            # Step 5: Summarization (English Layer)
            print("\n [Step 5] Analyzing and Summarizing (English Layer)...")
            summarization_template = PromptTemplate.from_template(SUMMARIZATION_PROMPT)
            summarization_chain = summarization_template | self.llm
            english_report = summarization_chain.invoke(
                {"topic": topic, "context": combined_text}
            )

            # Step 6: Translation & Refinement to Persian
            print("\n [Step 6] Translating and Refining into Professional Persian...")
            translation_template = PromptTemplate.from_template(TRANSLATION_PROMPT)
            translation_chain = translation_template | self.llm
            final_report = translation_chain.invoke({"english_report": english_report})

            # Log the end of the orchestration process
            self.search_tool.log_step("Final reasoning engine response received.")

            return {
                "topic": topic,
                "agent_plan": agent_plan,
                "sources": source_list,
                "report": final_report,
            }

        except Exception as e:
            print(f"Critical error running agent orchestrator pipeline: {str(e)}")
            return None


if __name__ == "__main__":
    try:
        orchestrator = AgentOrchestrator()
        output = orchestrator.run("تأثیر هوش مصنوعی بر بازار کار")
        if output and output.get("report"):
            print("\n================ FINAL REPORT ================")
            print(output["report"])
        else:
            print("\nPipeline failed to produce a valid final report.")
    except Exception as e:
        print("\nExecution Error!")
        print("Please ensure that Ollama is running locally and the model is fully downloaded.")
        print(f"Details: {str(e)}")