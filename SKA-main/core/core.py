import sys
import asyncio
import signal
import json  # noqa: F401

from server.LLM.Ollama_API import OllamaAPI
from server.L2Bot_server import QQHttpServer
from server.MCP.MCP import MCP

from .IO_Package import CoreInput, CoreOutput

from events.e_QQnewMsg import QQnewMsg
from events.e_Scheduler import Scheduler

# 导入Qwen Agent相关模块
try:
    from Agent.Kynia_qwen import init_agent_service
    QWEN_AGENT_AVAILABLE = True
except ImportError:
    QWEN_AGENT_AVAILABLE = False
    init_agent_service = None
    print("Warning: Qwen Agent not available, falling back to Ollama API")

class Core():
    '''
    机器人的核心服务
    '''
    def __init__(self) -> None:
        
        self.beat_count = 0 #存活心跳记录
        self.bpm = 1

        self.Input = CoreInput("initial_msg", 'initial_msg')
        self.Output : CoreOutput
        self.messages = []
        
        self.task = None
        self.event = asyncio.Event()  # 异步事件对象
        self.should_exit = False  # 退出标志

        #实例化sub服务
        self.Agent_API = OllamaAPI()
        self.QQServer = QQHttpServer()
        self.MCPServer = MCP()

        # 实例化Qwen Agent（如果可用）
        self.qwen_agent = None
        if QWEN_AGENT_AVAILABLE and init_agent_service:
            try:
                self.qwen_agent = init_agent_service()
                print("Qwen Agent initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Qwen Agent: {e}")
                self.qwen_agent = None

        #实例化事件监听
        self.qq_event = QQnewMsg(self.QQServer, self.event)
        self.scheduler_event = Scheduler()
        
        # 注册信号处理器
        self._setup_signal_handlers()
        
        # 加载提示词模板
        self._load_prompt_template()
    
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
    
    def _load_prompt_template(self):
        """加载提示词模板"""
        try:
            with open('SKA-main/Agent/prompt_template.md', 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
            print("Prompt template loaded successfully")
        except Exception as e:
            print(f"Failed to load prompt template: {e}")
            self.prompt_template = ""
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
                print(self.event, '事件触发')                
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
        if QWEN_AGENT_AVAILABLE:
            await self.qwen_agent_toolchain()
        else:
            await self.basic_toolchain()

    async def basic_toolchain(self):
        '''
        最基础的消息收发逻辑

        未来将集成到工具类进行解耦
        '''
        # 获取当前函数名作为task值
        self.task = sys._getframe().f_code.co_name
        print(f"task: [{self.task}]")
        self.Input = CoreInput(self.QQServer.recive_data, "qq_json")
        self.output = CoreOutput(await self.Agent_API.ollama_chat(self.Input.content), "ollama_json")
        await self.QQServer.send_text(self.output)
        self.task = None

    def msg_construct(self, input: CoreInput):
        """
        添加一条信息来自input
        
        Args:
            input: CoreInput对象，包含输入的消息数据
        """
        # 如果messages为空，添加系统提示
        if not self.messages:
            # 检查是否有加载的提示词模板
            if hasattr(self, 'prompt_template') and self.prompt_template:
                self.messages.append({
                    'role': 'system', 
                    'content': self.prompt_template
                })
        
        # 添加用户消息
        content = None
        if input.source == "qq_message": 
            content = {
                "message_type": input.type,
                "raw_message": input.content,
                "card": input.card,
                "time": input.time
            }
        elif input.source == "self_response":
            content = {
                "response": input.response
            }
        elif input.source == "system": 
            content = {
                "type": "system",
                "event": input.event,
                "task": input.content
            }
        if content is not None:
            self.messages.append({
                'role': 'user',
                'content': content
            })


    async def qwen_agent_toolchain(self):
        '''
        使用Qwen Agent的消息处理逻辑
        '''
        # 获取当前函数名作为task值
        self.task = sys._getframe().f_code.co_name
        print(f"task: [{self.task}]")
        
        try:
            # 使用Qwen Agent处理消息
            if self.qwen_agent is not None:
                # 从QQ服务器获取消息内容
                input_msg = self.Input
                if self.QQServer.recive_data:
                    input_msg = CoreInput(self.QQServer.recive_data, "qq_json")
                # 构造符合Qwen Agent要求的消息格式
                self.msg_construct(input_msg)
                
                # 使用Qwen Agent处理消息
                response_plain_text = ''
                # 转换消息格式以符合Qwen Agent的要求
                for response in self.qwen_agent.run(messages=list(self.messages)):
                    # 获取最后一次响应作为结果
                    response_plain_text = response
                
                # 提取响应内容
                if isinstance(response_plain_text, list) and len(response_plain_text) > 0:
                    result = response_plain_text[-1]  # 获取最后一个响应
                    if isinstance(result, dict) and 'content' in result:
                        result_content = json.load(result['content'])
                    else:
                        result_content = str(result)
                else:
                    result_content = str(response_plain_text)
                
                # 将assistant的回复添加到消息历史中
                if result_content:
                    self.messages.append({
                        'role': 'assistant',
                        'content': result_content
                    })
                self.Output = CoreOutput(result_content, "LLM_response")
                if self.Output.target == "private_msg" or "private_msg":
                    # 如果Agent返回了结果，则发送结果
                    await self.QQServer.send_text(self.Output)
                elif self.Output.target == 'internal':
                    pack = {
                        "response": self.Output.content
                    }
                    self.Input = CoreInput(pack, "LLM_response")
                else:
                    # 如果没有结果，回退到基本工具链
                    await self.basic_toolchain()
            else:
                # 如果没有Qwen Agent，回退到基本工具链
                await self.basic_toolchain()
        except Exception as e:
            print(f"Error in Qwen Agent toolchain: {e}")
            # 出错时回退到基本工具链
            await self.basic_toolchain()
            
        self.task = None

    async def agent_basic_toolchain(self):
        '''
        最基础的消息收发逻辑

        未来将集成到工具类进行解耦
        '''
        
        # 获取当前函数名作为task值
        self.task = sys._getframe().f_code.co_name
        print(f"task: [{self.task}]")
        input = CoreInput(self.QQServer.recive_data, "qq_json")
        output = CoreOutput(await self.Agent_API.ollama_generate(input.content), "ollama_json")
        await self.QQServer.send_text(output)
        self.task = None

    async def autonomous_toolchain(self):
        """机器人主动行为示例"""
        # 实现自主活动逻辑，如：
        # - 定时发送提醒
        # - 主动查询信息
        # - 与其他服务交互
        pass

    async def event_listener(self):
        """
        异步事件监听器
        返回最新的消息事件数据
        """
        while not self.should_exit:
            # 检查QQ事件是否有新消息
            if self.qq_event.flag == 1:
                # 获取消息数据并重置标志
                message_data = self.qq_event.last_data
                self.qq_event.flag = 0  # 重置事件标志
                return message_data
            await asyncio.sleep(0.1)  # 避免忙等待
        return None
        
    async def chain_router(self):
        """
        全局服务路由
        根据输入内容和系统状态选择最合适的处理链
        """
        # 默认路由策略
        if self.qwen_agent and self.prompt_template:
            return self.qwen_agent_toolchain
        else:
            return self.basic_toolchain
            
    async def manage(self):
        """
        资源与API查询/管理/调度
        提供系统状态监控和资源管理功能
        """
        return {
            "status": "running" if not self.should_exit else "stopping",
            "heartbeat_count": self.beat_count,
            "bpm": self.bpm,
            "active_task": self.task,
            "agent_type": "qwen" if self.qwen_agent else "ollama",
            "qq_server_status": "connected" if self.QQServer.is_connected else "disconnected",
        }


if __name__ == "__main__":
    SKACore = Core()