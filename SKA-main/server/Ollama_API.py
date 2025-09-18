import requests

class OllamaAPI():
    def __init__(self) -> None:
        self.http_api = "http://192.168.30.13:11434/api"
        pass
    
    async def ollama_one_shot(self, text):
    # 生成文本
        response = requests.post(
            "http://192.168.30.13:11434/api/generate",
            json={
                "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
                "prompt": f"{text}",
                "stream": False
            }
        )
        return response.json()
