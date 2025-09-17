import requests
import uvicorn
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/")

async def root(request: Request):
    data = await request.json()  # 获取事件数据
    #time.sleep(1)
    print(data)

    requests.post('http://localhost:3000/send_group_msg', json={
        'group_id': 965244857,
        'message': [{
            'type': 'text',
            'data': {
                'text': '我回来了，孩子们'
            }
        }]
    })

    return {}

if __name__ == "__main__":
    # 启动服务
    uvicorn.run(app, port=8080)