import time
import requests

async def test_ollama_api(json):
    time.sleep(0.75)
    text=json["raw_message"]
    LLM_response = await ollama_one_shot(text)
    return LLM_response

async def ollama_one_shot(text):
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
    return response.json()['response']