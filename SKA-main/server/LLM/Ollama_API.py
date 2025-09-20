import requests
import aiohttp

class OllamaAPI():
    '''
    负责与Ollama API通讯，只负责通讯
    '''
    def __init__(self) -> None:
        self.http_api = "http://192.168.30.13:11434/api"
        self.model = "qwen3:30b-a3b-instruct-2507-q4_K_M"
        pass

    async def ollama_chat(self, msg):
        '''
        实现聊天功能的接口
        
        args: 
            msg:    json格式的请求文：如下
            
                {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user", //或system/assistant
                            "content": "<text>"
                            //可以多轮
                        }
                    ],
                    "stream": False
                    "options": <>
                }

        return:
            resurt: json格式的响应报文
        '''
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.http_api}/chat",
                    json = msg
                ) as response:
                    result = await response.json()
                    return result
                
        except aiohttp.ClientError as e:
            print(f"Ollama_API: 网络请求错误: {e}")
            return None
        except Exception as e:
            if str(e) != '':
                print(f"Ollama_API: 未知错误: {e}")
                return None    
            
    async def ollama_generate(self, text):
        '''
        注意：仅用于测试
        '''
    # 生成文本
        response = requests.post(
            "http://192.168.30.13:11434/api/generate",
            json={
                "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
                "prompt": f"{text}",
                "stream": False
            }
        )
        reslut = response.json()
        print(reslut)
        return reslut
    
