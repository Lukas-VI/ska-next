import httpx
import asyncio
import requests
import json

class QQHttpServer():
    def __init__(self) -> None:
        self.l2Bot_api = 'http://localhost:3000/'
        self.recive_data = dict
        self.msg = ''
        self.target_id = {'msg_type':'group', 'id':965244857}
        self.send_mode = 'send_group_msg'
        #self.json : dict
        self.buffer = []
        asyncio.run(self.get_data())

    async def get_data(self):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream('GET', self.l2Bot_api+'_events') as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        #self.recive_data = line.split("data:", 1)[1]

                        self.format_message_str(line.split("data:", 1)[1])
                        

    async def send_text(self, text):
        requests.post(self.l2Bot_api+self.send_mode, json={
        'group_id': self.target_id['id'],
        'message': [{
            'type': 'text',
            'data': {
                'text': f'{text}'
            }
        }]
    })

    def format_message_str(self, input_str):
        """
        格式化给定的 JSON 字符串，使其更易读。
        
        args:
            input_str (str): 原始的 JSON 字符串
        
        """

        # 解析原始字符串为字典
        self.recive_data = json.loads(input_str)
        
        # 使用 json.dumps 美化输出，按键排序，缩进为 4 空格
        formatted = json.dumps(input_str, ensure_ascii=False, indent=4, sort_keys=True)
        print(formatted)
    
    def detact_new_msg(self):
        if not self.buffer:
            self.buffer[0] = self.recive_data
            self.buffer[1] = self.recive_data
        else:
            self.buffer[1] = self.buffer[0]
            self.buffer[0] = self.recive_data
        if self.buffer[0] != self.buffer[1]:
            return True
        else:
            return False


if __name__ == "__main__":
    QQServer = QQHttpServer()
    print("L2Bot langched")
