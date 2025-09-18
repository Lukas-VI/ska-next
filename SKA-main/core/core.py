import time
import asyncio

from server.Ollama_API import OllamaAPI
from server.L2Bot_server import QQHttpServer
from server.MCP.MCP import MCP

from .IO_Package import CoreInput, CoreOutput

class Core():
    '''
    机器人的核心服务
    '''
    def __init__(self) -> None:
        
        self.beat_count = 0 #存活心跳记录
        self.bpm = 1
        self.even_flag = 0

        self.Input = ''
        self.Outpit = ''
        
        #实例化sub服务
        self.Agent_API = OllamaAPI()
        self.QQServer = QQHttpServer()
        self.MCPServer = MCP()


    async def services_epoch(self):
        '''
        定义本交互(思考)轮次内进行的操作

        如: 收到心跳消息包 -> LLM推理 -> 选择操作: 回复/记忆/等待/执行
        
        '''
        #基础功能收发
        await self.basic_toolchain()

    async def basic_toolchain(self):
        '''
        最基础的消息收发逻辑
        '''
        input = CoreInput(self.QQServer.recive_data)
        output = CoreOutput(await self.Agent_API.ollama_one_shot(input.content))
        await self.QQServer.send_text(output.content)        

    async def heart_beat(self):
        '''
        服务主循环

        static beat:    固定时间 / 时间触发 
        
        trigger beat:   监听处理事件触发    

        实际上就是使用两个频率不同的嵌套无限循环,实现对所有事件的监听
        '''
        while True:
            
            while self.msg_triger():
                await asyncio.sleep(10)

            time.sleep(60 / self.bpm)
            await Core.services_epoch(self)
            

    def msg_triger(self):
        '''
        聊天信号触发
        '''
        if self.even_flag:
            self.even_flag = 0
            return 1
        
        elif self.scheduler():
            return 1
        
        else:
            return 0

    def chain_router(self):
        '''
        全局服务路由

        用于选择合适的toolchain
        '''

    def manage(self):
        '''
        资源与API查询/管理/调度
        '''

    def scheduler(self):
        '''
        日程调度

        应该写成一个新的事件类
        '''

        return 0


if __name__ == "__main__":
    SKACore = Core()    