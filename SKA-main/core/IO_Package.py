import time
import json
import os
import ast


class IOPack():
    '''
    与SKA交互的标准数据包的基类
    '''
    def __init__(self, pack, type) -> None:
        self.time = time.time()
        self.pack = pack
        self.type = type
        self.user = ''
        self.content = ''
        self.normalize()

    def __del__(self):
        print("Class instance destroyed：", self.__class__.__name__)

    def normalize(self):
        '''
        解析数据包并标准化数据结构
        '''
        # 解析数据包类型(json或文本)
        return self


class CoreInput(IOPack):
    '''
    作为SKA的输入数据包
    
    数据可以来自: QQ消息, 心跳唤醒, 服务事件等
    根据promote.json中定义的input格式处理不同类型的数据包
    '''

    def __init__(self, pack, type) -> None:
        # 初始化所有属性
        self.source = ''
        self.pack_type = 'unknown'
        self.pack_source = 'unknown'
        self.is_valid = False
        self.card = ''  # 用户昵称
        self.response = ''  # LLM响应内容
        self.event = ''  # 系统事件
        
        super().__init__(pack, type)
        
        self.detect_pack_info(pack)
        self.normalize()

    def detect_pack_info(self, pack):
        '''
        检测输入数据包的结构和来源
        
        Args:
            pack: 输入的数据包，可能是字符串或字典
        '''
        # 如果pack是字符串，先尝试解析
        if isinstance(pack, str):
            try:
                # 处理非标准JSON（如单引号）
                data = self._parse_string_to_dict(pack)
                self.is_valid = True
                self.pack_type = 'json'
                
                # 根据JSON字段判断来源
                if isinstance(data, dict):
                    # 判断是否来自QQ消息
                    if 'message_type' in data and 'raw_message' in data:
                        self.pack_source = 'qq_message'
                        self.pack_type = 'qq_json'
                    # 判断是否来自LLM响应(self_response)
                    elif 'response' in data:
                        self.pack_source = 'self_response'
                        self.pack_type = 'llm_json'
                    # 判断是否来自系统事件
                    elif 'event' in data and 'type' in data:
                        self.pack_source = 'system_event'
                        self.pack_type = 'event_json'
                    else:
                        self.pack_source = 'unknown_json'
                        
            except (json.JSONDecodeError, ValueError, SyntaxError):
                # 不是有效的JSON格式，判断为纯文本
                self.pack_type = 'text'
                self.pack_source = 'text_input'
                self.is_valid = True
        elif isinstance(pack, dict):
            self.is_valid = True
            self.pack_type = 'dict'
            
            # 根据字典中的字段判断来源
            if 'message_type' in pack and 'raw_message' in pack:
                self.pack_source = 'qq_message'
            elif 'response' in pack:
                self.pack_source = 'self_response'
            elif 'event' in pack and 'type' in pack:
                self.pack_source = 'system_event'
            else:
                self.pack_source = 'unknown_dict'
        else:
            self.pack_type = 'unknown'
            self.pack_source = 'unknown'
            self.is_valid = False

    def _parse_string_to_dict(self, str_data):
        '''
        将字符串解析为字典，支持标准JSON和Python字典格式
        '''
        str_data = str_data.strip()
        
        # 如果是标准JSON格式
        if str_data.startswith('{') and str_data.endswith('}'):
            try:
                # 先尝试标准JSON解析
                return json.loads(str_data)
            except json.JSONDecodeError:
                # 如果失败，尝试使用ast.literal_eval解析Python字典格式
                try:
                    return ast.literal_eval(str_data)
                except (ValueError, SyntaxError):
                    # 如果还失败，抛出异常
                    raise ValueError("无法解析字符串为字典格式")
        else:
            raise ValueError("输入不是字典格式的字符串")

    def normalize(self):
        '''
        解析数据包并标准化Input类结构
        根据promote.json中定义的input格式处理
        '''
        if isinstance(self.pack, dict):
            # 处理QQ消息
            if self.pack_source == 'qq_message':
                self.time = self.pack.get('time', time.time())
                self.type = self.pack.get('message_type', 'unknown')
                self.user = self.pack.get('user_id', '')
                self.content = self.pack.get('raw_message', '')
                self.source = self.pack.get('message_type', '')
                # 从sender对象中获取card/nickname
                sender = self.pack.get('sender', {})
                self.card = sender.get('card', sender.get('card', ''))
            
            # 处理LLM响应(self_response)
            elif self.pack_source == 'self_response':
                self.time = self.pack.get('created_at', time.time())
                self.type = 'self_response'
                self.content = self.pack.get('response', '')
                self.response = self.pack.get('response', '')
            
            # 处理系统事件
            elif self.pack_source == 'system_event':
                self.time = time.time()
                self.type = 'system_event'
                self.event = self.pack.get('event', '')
                self.content = self.pack.get('task', '')
            
            # 处理其他字典格式
            else:
                self.time = self.pack.get('time', time.time())
                self.type = self.pack.get('type', 'unknown')
                self.user = self.pack.get('user_id', '')
                self.content = self.pack.get('content', '')
                self.source = self.pack.get('source', '')

        elif isinstance(self.pack, str):
            # 如果是字符串，尝试解析为JSON
            try:
                data = self._parse_string_to_dict(self.pack)
                if isinstance(data, dict):
                    # 处理QQ消息
                    if self.pack_source == 'qq_message':
                        self.time = data.get('time', time.time())
                        self.type = 'qq_' + data.get('message_type', 'unknown')
                        self.user = data.get('user_id', '')
                        self.content = data.get('raw_message', '')
                        self.source = data.get('message_type', '')
                        # 从sender对象中获取card/nickname
                        sender = data.get('sender', {})
                        self.card = sender.get('card', sender.get('card', ''))
                    
                    # 处理LLM响应(self_response)
                    elif self.pack_source == 'self_response':
                        self.time = data.get('created_at', time.time())
                        self.type = 'self_response'
                        self.content = data.get('response', '')
                        self.response = data.get('response', '')
                    
                    # 处理系统事件
                    elif self.pack_source == 'system_event':
                        self.time = time.time()
                        self.type = 'system_event'
                        self.event = data.get('event', '')
                        self.content = data.get('task', '')
                    
                    # 处理其他字典格式
                    else:
                        self.time = data.get('time', time.time())
                        self.type = data.get('type', 'unknown')
                        self.user = data.get('user_id', '')
                        self.content = data.get('content', '')
                        self.source = data.get('source', '')
                else:
                    # 纯文本内容
                    self.content = self.pack
                    self.type = 'text'
            except (ValueError, SyntaxError):
                # 无法解析为JSON的纯文本
                self.content = self.pack
                self.type = 'text'
        return self


class CoreOutput(IOPack):
    '''
    基本的输出数据包，根据promote.json中定义的output格式生成
    支持group_msg, private_msg, self_msg三种类型
    '''
    def __init__(self, pack, type) -> None:
        self.target = ''
        self.card = ''  # 用户昵称
        super().__init__(pack, type)

    def normalize(self):
        '''
        解析数据包并标准化Output类结构
        根据promote.json中定义的output格式处理
        '''
        if isinstance(self.pack, dict):
            # 处理group_msg类型
            if self.pack.get('target') == 'group_msg':
                self.target = self.pack.get('target', '')
                self.type = self.pack.get('type', 'text')
                self.content = self.pack.get('content', '')
            
            # 处理private_msg类型
            elif self.pack.get('target') == 'private_msg':
                self.target = self.pack.get('target', '')
                self.type = self.pack.get('type', 'text')
                self.content = self.pack.get('content', '')
                self.card = self.pack.get('card', '')
            
            # 处理self_msg类型
            elif self.pack.get('target') == 'self':
                self.target = self.pack.get('target', '')
                self.type = self.pack.get('type', 'text')
                self.content = self.pack.get('content', '')
                self.card = self.pack.get('card', '')
            
            # 处理其他字典格式
            else:
                self.time = self.pack.get('time', time.time())
                self.type = self.pack.get('type', 'output')
                self.user = self.pack.get('user', '')
                self.content = self.pack.get('content', '')
                self.target = self.pack.get('target', '')
        
        elif isinstance(self.pack, str):
            # 处理纯文本格式
            self.content = self.pack
            self.type = 'text'
            self.target = 'group_msg'  # 默认发送到群聊
            
        return self


class ExpandOutput(CoreOutput):
    '''
    扩增的输出操作,在需要调用工具等时使用
    '''


def test():
    '''
    测试CoreInput和CoreOutput类的功能
    '''
    # 确保在正确的目录下
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    misc_dir = os.path.join(project_root, 'misc')
    qq_msg_path = os.path.join(misc_dir, 'QQmsg_example.ini')
    LLM_msg_path = os.path.join(misc_dir, 'LLM_outputs_example.ini')
    
    # 读取QQ消息示例
    with open(qq_msg_path, 'r', encoding='utf-8') as f:
        qq_msg_str = f.read()
    
    # 读取LLM消息示例
    with open(LLM_msg_path, 'r', encoding='utf-8') as f:
        LLM_msg_str = f.read()    

    # 测试CoreInput类输入 QQ_msg
    print("=== 测试CoreInput类 QQ_msg===")
    input_QQ_obj = CoreInput(qq_msg_str, "qq_json")
    
    print(f"原始数据包: {input_QQ_obj.pack}")
    print(f"数据包类型: {input_QQ_obj.pack_type}")
    print(f"数据包来源: {input_QQ_obj.pack_source}")
    print(f"是否有效: {input_QQ_obj.is_valid}")
    print(f"时间: {input_QQ_obj.time}")
    print(f"类型: {input_QQ_obj.type}")
    print(f"用户: {input_QQ_obj.user}")
    print(f"内容: {input_QQ_obj.content}")
    print(f"来源: {input_QQ_obj.source}")
    print(f"昵称: {input_QQ_obj.card}")
    
    # 测试CoreInput类 LLM_msg
    print("\n=== 测试CoreInput类 LLM_msg===")
    input_LLM_obj = CoreInput(LLM_msg_str, "llm_json")
    
    print(f"原始数据包: {input_LLM_obj.pack}")
    print(f"数据包类型: {input_LLM_obj.pack_type}")
    print(f"数据包来源: {input_LLM_obj.pack_source}")
    print(f"是否有效: {input_LLM_obj.is_valid}")
    print(f"时间: {input_LLM_obj.time}")
    print(f"类型: {input_LLM_obj.type}")
    print(f"用户: {input_LLM_obj.user}")
    print(f"内容: {input_LLM_obj.content}")
    print(f"响应: {input_LLM_obj.response}")
    
    # 测试系统事件
    print("\n=== 测试系统事件 ===")
    system_event = {
        "type": "system",
        "event": "heartbeat",
        "task": "证明你还活着的心跳信号"
    }
    input_system_obj = CoreInput(system_event, "system_event")
    print(f"数据包来源: {input_system_obj.pack_source}")
    print(f"类型: {input_system_obj.type}")
    print(f"事件: {input_system_obj.event}")
    print(f"内容: {input_system_obj.content}")

    # 测试CoreOutput类 - group_msg
    print("\n=== 测试CoreOutput类 group_msg ===")
    output_group_data = {
        "target": "group_msg",
        "type": "text",
        "content": "欢迎欢迎!"
    }
    output_group_obj = CoreOutput(output_group_data, "group_msg")
    
    print(f"原始数据包: {output_group_obj.pack}")
    print(f"时间: {output_group_obj.time}")
    print(f"类型: {output_group_obj.type}")
    print(f"内容: {output_group_obj.content}")
    print(f"目标: {output_group_obj.target}")
    
    # 测试CoreOutput类 - private_msg
    print("\n=== 测试CoreOutput类 private_msg ===")
    output_private_data = {
        "target": "private_msg",
        "type": "text",
        "card": "LUKAS",
        "content": "这是私聊内容"
    }
    output_private_obj = CoreOutput(output_private_data, "private_msg")
    
    print(f"原始数据包: {output_private_obj.pack}")
    print(f"时间: {output_private_obj.time}")
    print(f"类型: {output_private_obj.type}")
    print(f"内容: {output_private_obj.content}")
    print(f"目标: {output_private_obj.target}")
    print(f"昵称: {output_private_obj.card}")
    
    # 测试文本输出
    print("\n=== 测试文本输出 ===")
    text_output = CoreOutput("纯文本回复", "text")
    print(f"类型: {text_output.type}")
    print(f"内容: {text_output.content}")
    print(f"目标: {text_output.target}")

if __name__ == "__main__":
    test()