import requests
import aiohttp

class OllamaAPI():
    def __init__(self) -> None:
        self.http_api = "http://192.168.30.13:11434/api"
        self.model = "qwen3:30b-a3b-instruct-2507-q4_K_M"
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
        print(response.json())
        return response.json()
    
    async def ollama_chat(self, msg):
        # 实现聊天功能
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.http_api}/chat",
                    json={
                        "model": self.model,
                        "messages": msg,
                        "stream": False
                    }
                ) as response:
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            print(f"网络请求错误: {e}")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None