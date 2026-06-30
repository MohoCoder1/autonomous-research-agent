from datetime import datetime
from config import Config
from ddgs import DDGS


class WebSearchTool:
    """
    This class is used to search the web for the given query, rank them by quality, 
    and log internal transitions in a short-term scratchpad memory.
    """

    # short-term memory to save steps taken by the tool
    scratchpad = []

    @classmethod
    def clear_scratchpad(cls):
        """Clear the scratchpad for a new topic."""
        cls.scratchpad.clear()

    def __init__(self):
        # getting the max search results from the config file
        self.max_results = Config.MAX_SEARCH_RESULTS
        
        # trusted domains for ranking the quality of resources
        self.trusted_domains = ["medium.com", "github.com", "arxiv.org", "techcrunch.com", "wikipedia.org", "reuters.com"]

    def log_step(self, message: str):
        """log steps taken by the tool"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        WebSearchTool.scratchpad.append(f"[{timestamp}] {message}")

    def evaluate_and_rank_sources(self, raw_results: list) -> list:
        """rank sources by the quality of resources"""
        if not raw_results:
            return []

        self.log_step("starting the ranking process for the quality of resources")
        ranked_results = []
        
        for item in raw_results:
            score = 50  # basic score
            url = item.get("link", "").lower()
            snippet = item.get("snippet", "").lower()
            
            # 1. domain credibility evaluation
            if any(domain in url for domain in self.trusted_domains):
                score += 20
                self.log_step(f"Positive score for valid domain: {url[:30]}...")
                
            # 2. content freshness evaluation (special for content of the current year 2026 and 2025)
            if "2026" in snippet or "2026" in url:
                score += 25
            elif "2025" in snippet or "2025" in url:
                score += 15
                
            # 3. content depth evaluation (length of the snippet)
            if snippet and len(snippet) > 250:
                score += 15
                
            item["quality_score"] = score
            ranked_results.append(item)
            
        # sorting the results from the highest score to the lowest quality score
        ranked_results.sort(key=lambda x: x.get("quality_score", 50), reverse=True)
        self.log_step(f"ranking process completed. The best source with the score {ranked_results[0]['quality_score']} was confirmed.")
        return ranked_results

    def search(self, query: str) -> list:
        """search a query and return the title, link and snippet of top results"""
        print(f"Searching the web for: {query}")
        self.log_step(f"Received search query: '{query}'")
        results_list = []

        try:
            # use DuckDuckGo safely and clean with ddgs
            with DDGS() as ddgs:
                # search (text) in web
                ddgs_gen = ddgs.text(query, max_results=self.max_results)
                for r in ddgs_gen:
                    results_list.append(
                        {
                            "title": r.get("title"),
                            "link": r.get("href"), # create URL address
                            "snippet": r.get("body"), # summary of the page which shows by google
                        }
                    )
            
            # ranking and quality filtering of resources
            final_ranked_results = self.evaluate_and_rank_sources(results_list)
            return final_ranked_results
            
        except Exception as e:
            error_msg = f"Error during search {query}: {str(e)}"
            print(error_msg)
            self.log_step(f"Error during search: {str(e)}")
            return []


if __name__ == "__main__":
    search_tool = WebSearchTool()
    # testing the web search tool with a sample query
    results = search_tool.search("What is LangChain?")
    print("\n=====Search Results Found (Ranked By Quality)=====")
    for index, item in enumerate(results, 1):
        print(f"{index}. {item['title']} [Score: {item.get('quality_score', 'N/A')}]\n")
        print(f"   Link: {item['link']}\n")
        
    print("=====Scratchpad Memory Logs=====")
    print("\n".join(search_tool.scratchpad))
