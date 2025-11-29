import importlib.metadata
packages=["langchain","langchain_core","python-dotenv","streamlit","ipykernel","beautifulsoup4","fastapi","html5lib","jinja2",
          "langchain-astradb","langchain-cohere","langchain-groq","lxml","python-multipart","selenium","undetected-chromedriver",
          "uvicorn","structlog","langgraph","ragas","langchain-mcp-adapters","mcp","ddgs","setuptools"]
for package in packages:
    try:
        version = importlib.metadata.version(package)
        print(f"{package}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{package} is not installed.")