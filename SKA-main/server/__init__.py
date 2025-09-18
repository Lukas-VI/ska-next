from .L2Bot_server import QQHttpServer
from .Ollama_API import OllamaAPI

if __name__ =="__main__":
    Agent_API = OllamaAPI()
    QQServer = QQHttpServer()