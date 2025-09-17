import requests
import time

from server.Ollama_API import OllamaAPI
from server.L2Bot_server import QQHttpServer
from server.MCP.MCP import MCP

class Core():
    def __init__(self) -> None:
        
        self.beat_count = 0 #存活心跳记录
        self.bpm = 
        
        self.Input = ''
        self.Outpit = ''
        
        #实例化sub服务
        Agent_API = OllamaAPI()
        QQServer = QQHttpServer()
        MCPServer = MCP()


    async def services_epoch(self, pack):
        '''
        定义本交互(思考)轮次内进行的操作

        如: 收到心跳消息包 -> LLM推理 -> 选择操作: 回复/记忆/等待/执行
        
        '''


    async def heart_beat(self):
        '''
        心跳, 一个心跳执行一轮,解决触发问题

        static beat: 
        trigger beat: 处理事件 
        '''
        while True:
            await Core.services_epoch(self, pack)
            

    def slot_triger(self):
        '''
        全局信号触发
        '''

    def chain_router(self):
        '''
        全局服务路由
        '''

    def manage(self):
        '''
        资源与API管理调度
        '''

    def scheduler(self):
        '''
        日程调度
        '''

