from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from config import Config

class WebCrawlerTool:
    
    def __init__(self) -> None:
        # Initialize the timeout for the crawler from the config file
        self.timeout = Config.CRAWL_TIMEOUT

    def extract_text(self, url: str) -> str:
        """Playwright gets a url link, loads it, extracts visible text, and returns it."""
        try:
            with sync_playwright() as p: 
                # Launch chromium in headless mode
                browser = p.chromium.launch(headless=True)
                
                # Dynamic Protection: Ignore HTTPS/SSL errors to prevent unnecessary crash
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()

                print(f"Fetching content from: {url}")
                
                # Go to the url with strict timeout configurations
                page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                
                # Get raw html content
                html_content = page.content()
                browser.close()
                
                return self._clean_html(html_content)

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return ""

    def _clean_html(self, html: str) -> str:
        """Remove scripts, styles, navigation, footer elements, and extra whitespace from html."""
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')

        # Strip unneeded structural/bloat elements to save LLM context window tokens
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.extract()
        
        # Extract plain text content
        text = soup.get_text(separator=" ")
        
        # Clean whitespaces clean and compress empty lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        return clean_text

if __name__ == "__main__":
    crawler = WebCrawlerTool()
    sample_text = crawler.extract_text("https://www.varzesh3.com")
    print("=====Sample Web Page Text====")
    print(f"\n{sample_text[:500]}")           

                
                
      
        

    