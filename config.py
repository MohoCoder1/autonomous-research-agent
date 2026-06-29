import os
# from sys import platform


class Config:
    """
    Centralized Configuration class to hold all the configuration variables
    """

    # default address of the ollama server
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # default model to use from the ollama
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")

    # max search results to fetch from duckduckgo
    MAX_SEARCH_RESULTS = 5

    # timeout for the playwright browser to load the page
    CRAWL_TIMEOUT = 30000


print("Config Loaded Successfully")
