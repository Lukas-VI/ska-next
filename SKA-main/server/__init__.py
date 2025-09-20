from .L2Bot_server import QQHttpServer
from .LLM.Ollama_API import OllamaAPI

if __name__ =="__main__":
    Agent_API = OllamaAPI()
    QQServer = QQHttpServer()