import httpx
import asyncio
import json

class QQHttpServer():
    def __init__(self) -> None:
        self.l2Bot_api = 'http://localhost:3000/'
        self.recive_data = dict
        self.status = 0
        self.target_id = {'msg_type':'group', 'id':965244857}
        self.send_mode = 'send_group_msg'
        #self.json : dict
        self.buffer = []
        # asyncio.run(self.get_data())
        self.is_connected = False
        self.data_task = None  # 用于保存数据接收任务的引用

    '''    async def get_data(self):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream('GET', self.l2Bot_api+'_events') as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        #self.recive_data = line.split("data:", 1)[1]

                        self.format_message_str(line.split("data:", 1)[1])
    '''
    async def start(self):
        """
        启动QQ服务器数据接收任务
        这个方法应该在有事件循环的上下文中调用
        """
        if self.data_task is None or self.data_task.done():
            self.data_task = asyncio.create_task(self.get_data())
            print("QQ服务器数据接收任务已启动")
            return self.data_task
        else:
            print("QQ服务器数据接收任务已在运行中")
            return self.data_task
    
    async def get_data(self):
        """
        异步获取数据
        """
        retry_count = 0
        max_retries = 5
        retry_delay = 5  # 重试间隔（秒）
        
        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    async with client.stream('GET', self.l2Bot_api+'_events') as resp:
                        self.is_connected = True
                        retry_count = 0  # 连接成功，重置重试计数
                        async for line in resp.aiter_lines():
                            if line.startswith("data:"):
                                self.format_message_str(line.split("data:", 1)[1])
            except httpx.ConnectError as e:
                self.is_connected = False
                retry_count += 1
                print(f"连接失败 ({retry_count}/{max_retries}): {str(e)}")
                if retry_count < max_retries:
                    for _ in reversed(range(1, retry_delay + 1)):
                        print("\r" + f"将在 {_} 秒后重试...", end='')
                        await asyncio.sleep(1)
                    print("\r" + "connecting...         ")
                else:
                    print("达到最大重试次数，无法连接")
                    self.status = 404
                    break
            except Exception as e:
                self.is_connected = False
                print(f"L2Bot: 发生未预期的错误: {str(e)}")
                if retry_count < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_count += 1
                else:
                    break                    

    async def send_text(self, text):
        try:
            # 使用异步方式发送消息
            async with httpx.AsyncClient() as client:
                await client.post(self.l2Bot_api+self.send_mode, json={
                    'group_id': self.target_id['id'],
                    'message': [{
                                'type': 'text',
                                'data': {
                                'text': f'{text}'
                        }
                    }]
                })
        except Exception as e:
            print(f"发送消息失败: {str(e)}")

    def format_message_str(self, input_str):
        """
        格式化给定的 JSON 字符串，使其更易读。
        
        args:
            input_str (str): 原始的 JSON 字符串
        
        """

        # 解析原始字符串为字典
        self.recive_data = json.loads(input_str)
        
        # 使用 json.dumps 美化输出，按键排序，缩进为 4 空格
        formatted = json.dumps(self.recive_data, ensure_ascii=False, indent=4, sort_keys=True)
        print(formatted)
    
    def detact_new_msg(self):
        try:
            if not self.buffer:
                self.buffer = [self.recive_data, self.recive_data]
            else:
                self.buffer[1] = self.buffer[0]
                self.buffer[0] = self.recive_data
            if self.buffer[0] != self.buffer[1]:
                return True
            else:
                return False
        except Exception as e:
            print(f"检测新消息时出错: {str(e)}")
            return False


if __name__ == "__main__":
    QQServer = QQHttpServer()
