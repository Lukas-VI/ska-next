import time
import asyncio

from server.Ollama_API import OllamaAPI
from server.L2Bot_server import QQHttpServer
from server.MCP.MCP import MCP

from .IO_Package import CoreInput, CoreOutput

from events.e_QQnewMsg import QQnewMsg
from events.e_Scheduler import Scheduler

class Core():
    '''
    机器人的核心服务
    '''
    def __init__(self) -> None:
        
        self.beat_count = 0 #存活心跳记录
        self.bpm = 1

        self.Input = ''
        self.Outpit = ''
        
        #实例化sub服务
        self.Agent_API = OllamaAPI()
        self.QQServer = QQHttpServer()
        self.MCPServer = MCP()

        #实例化事件监听
        self.qq_event = QQnewMsg(self.QQServer)
        self.scheduler_event = Scheduler()
    async def start(self):
        """
        启动所有异步(网络)服务
        """
        # 启动QQ服务器
        await self.QQServer.start()
        print("所有服务已启动")

    async def services_epoch(self):
        '''
        定义本交互(思考)轮次内进行的操作,业务流程

        如: 收到心跳消息包 -> Agent推理 -> 选择操作: 回复/记忆/等待/执行
        
        '''
        #基础功能收发
        await self.basic_toolchain()

    async def basic_toolchain(self):
        '''
        最基础的消息收发逻辑

        未来将集成到工具类进行解耦
        '''
        input = CoreInput(self.QQServer.recive_data)
        output = CoreOutput(await self.Agent_API.ollama_one_shot(input.content))
        await self.QQServer.send_text(output.content)

    async def heart_beat(self):
        '''
        服务主循环

        static beat:    周期触发 
        
        trigger beat:   监听处理事件触发    

        实际上就是使用两个频率不同的嵌套无限循环,实现对所有事件的监听
        '''
        print("Core Start")
        while True:
            while True:
                print("lisenering")
                await asyncio.sleep(1)
                if self.event_lisener() == 1:
                    print('事件触发')
                    break

            await Core.services_epoch(self)
            print("start_services")

            time.sleep(60 / self.bpm)
            self.beat_count += 1
            print(f'[{self.beat_count}]')

    def event_lisener(self):
        '''
        事件监听
        '''

        print("Event Code: ", self.qq_event.flag)
        if self.qq_event.flag == 1:
            return 1
        else:
            return 0


    async def msg_trigger(self):
        '''
        聊天信号触发
        '''
        if self.even_flag:
            self.even_flag = 0
            return 1
        else:
            return 0

    def chain_router(self):
        '''
        全局服务路由

        用于选择合适的toolchain

        计划使用Qwen Agent
        '''

    def manage(self):
        '''
        资源与API查询/管理/调度

        将转入工具
        '''


if __name__ == "__main__":
    SKACore = Core()    