import sys
import asyncio
import signal

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
        
        self.task = None
        self.event = asyncio.Event()  # 异步事件对象
        self.should_exit = False  # 退出标志

        #实例化sub服务
        self.Agent_API = OllamaAPI()
        self.QQServer = QQHttpServer()
        self.MCPServer = MCP()

        #实例化事件监听
        self.qq_event = QQnewMsg(self.QQServer, self.event)
        self.scheduler_event = Scheduler()
        
        # 注册信号处理器
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """设置信号处理器以优雅地处理退出信号"""
        def signal_handler(signum, frame):
            print(f"\n[{signum}]，正在准备退出...")
            self.should_exit = True
            # 触发事件以确保任何等待的协程能够继续执行并检测到退出
            self.event.set()
            
        # 注册SIGINT (Ctrl+C) 和 SIGTERM信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """
        启动所有异步(网络)服务
        """
        # 启动QQ服务器
        await self.QQServer.start()
        # 事件监听任务已在QQnewMsg初始化时自动启动
        print("所有服务已启动")

    async def services_epoch(self):
        '''
        定义本交互(思考)轮次内进行的操作,业务流程

        如: 收到心跳消息包 -> Agent推理 -> 选择操作: 回复/记忆/等待/执行
        
        '''
        #基础功能收发
        print("start_services")
        await self.basic_toolchain()

    async def basic_toolchain(self):
        '''
        最基础的消息收发逻辑

        未来将集成到工具类进行解耦
        '''
        # 获取当前函数名作为task值
        self.task = sys._getframe().f_code.co_name
        print(f"task: [{self.task}]")
        input = CoreInput(self.QQServer.recive_data, "qq_json")
        output = CoreOutput(await self.Agent_API.ollama_one_shot(input.content), "ollama_json")
        await self.QQServer.send_text(output.content)
        self.task = None

    async def heart_beat(self):
        '''
        重构服务主循环 - 采用事件驱动架构
        优势：
        1. 使用原生asyncio.Event实现高效事件通知（避免轮询）
        2. 心跳与事件监听完全解耦
        3. 支持真正的并行处理
        4. 代码逻辑更清晰简洁
        '''
        print("Core Start")
        while not self.should_exit:
            # 并发等待：事件触发 或 心跳周期完成
            try:
                # 等待事件触发（带心跳超时）
                await asyncio.wait_for(
                    self.event.wait(), 
                    timeout=60 / self.bpm
                )
                print('事件触发')                
                # 重置事件
                self.event.clear()
                
                # 检查是否需要退出
                if self.should_exit:
                    break
                    
                await self.services_epoch()
                
                
            except asyncio.TimeoutError:
                # 心跳周期完成
                self.beat_count += 1
                print(f'[{self.beat_count}] 心跳触发')
                # 此处可添加机器人主动行为逻辑
                # 例如：await self.autonomous_action()
        
        print("核心服务已停止")
    
    async def autonomous_action(self):
        """机器人主动行为示例"""
        # 实现自主活动逻辑，如：
        # - 定时发送提醒
        # - 主动查询信息
        # - 与其他服务交互
        pass

    def event_lisener(self):
        '''
        事件监听
        '''
        # 直接返回事件标志
        return int(self.qq_event)
        
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