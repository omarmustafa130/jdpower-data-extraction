import os
import subprocess
import sys
import time
import platform

required_libraries = [
    "pandas",
    "openpyxl",
    "playwright",
    "g4f",
    "playwright-stealth",
    "ollama",
    "langchain-core",    # For langchain_core
    "langchain-ollama",  # For langchain_ollama integration
]

def install_libraries():
    print("Installing required libraries...")
    for library in required_libraries:
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

def install_playwright_browsers():
    print("Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])

def setup_ollama():
    print("\nSetting up Ollama...")
    
    # Install Ollama
    try:
        if platform.system() == "Windows":
            ollama_exe = os.path.expanduser("~/Downloads/OllamaSetup.exe")
            subprocess.check_call([
                "powershell",
                f"Invoke-WebRequest -Uri https://ollama.com/download/OllamaSetup.exe -OutFile {ollama_exe}"
            ])
            subprocess.check_call([ollama_exe, "/S"])
        else:
            subprocess.check_call("curl -fsSL https://ollama.ai/install.sh | sh", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Ollama installation failed: {e}")
        sys.exit(1)

    # Start Ollama service
    print("Starting Ollama service...")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            subprocess.Popen(["ollama", "serve"], start_new_session=True)
        time.sleep(10)
    except Exception as e:
        print(f"Failed to start Ollama: {e}")

    # Download DeepSeek model
    print("Pulling DeepSeek-R1:7B model...")
    try:
        subprocess.check_call(["ollama", "pull", "deepseek-r1:7b"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull model: {e}")
        print("Manually run: ollama pull deepseek-r1:7b")

def validate_installation():
    print("\nValidating installations...")
    
    try:
        # Check Python packages
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_ollama.llms import OllamaLLM
        print("LangChain components verified")

        # Test Ollama connection
        llm = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
        test_response = llm.invoke("Say 'hello world'")
        print("Ollama connection test successful:", test_response.strip())

    except ImportError as e:
        print(f"Missing LangChain component: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ollama validation failed: {e}")
        sys.exit(1)

def main():
    install_libraries()
    install_playwright_browsers()
    setup_ollama()
    validate_installation()
    
    print("\nSetup complete! Now you can use:")
    print("""
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

llm = OllamaLLM(model="deepseek-r1:7b", temperature=0.7)
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
chain = prompt | llm

response = chain.invoke({"topic": "quantum physics"})
print(response)
    """)

if __name__ == "__main__":
    if platform.system() == "Windows":
        print("Note: On Windows, run as Administrator if you encounter permission issues")
    main()