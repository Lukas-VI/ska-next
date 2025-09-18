import time
import json


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
        print("Class instance destroyed")

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
    '''

    def __init__(self, pack) -> None:
        self.source = ''
        self.pack_type = 'unknown'
        self.pack_source = 'unknown'
        self.is_valid = False
        self.detect_pack_info(pack)
        super().__init__(pack, self.pack_type)

    def detect_pack_info(self, pack):
        '''
        检测输入数据包的结构和来源
        
        Args:
            pack: 输入的数据包，可能是字符串或字典
        '''
        # 如果pack是字符串，先尝试解析
        if isinstance(pack, str):
            try:
                data = json.loads(pack)
                self.is_valid = True
                self.pack_type = 'json'
                
                # 根据JSON字段判断来源
                if isinstance(data, dict):
                    # 判断是否来自QQ消息
                    if all(key in data for key in ['post_type', 'message_type', 'raw_message']):
                        self.pack_source = 'qq_message'
                        self.pack_type = 'qq_json'
                    # 判断是否来自Ollama API
                    elif 'response' in data:
                        self.pack_source = 'ollama_response'
                        self.pack_type = 'ollama_json'
                    # 判断是否来自心跳包或其他系统事件
                    elif 'event' in data or 'type' in data:
                        self.pack_source = 'system_event'
                        self.pack_type = 'event_json'
                    else:
                        self.pack_source = 'unknown_json'
                        
            except json.JSONDecodeError:
                # 不是有效的JSON格式，判断为纯文本
                self.pack_type = 'text'
                self.pack_source = 'text_input'
                self.is_valid = True
        elif isinstance(pack, dict):
            self.is_valid = True
            self.pack_type = 'dict'
            
            # 根据字典中的字段判断来源
            if all(key in pack for key in ['post_type', 'message_type', 'raw_message']):
                self.pack_source = 'qq_message'
            elif 'response' in pack:
                self.pack_source = 'ollama_response'
            elif 'event' in pack or 'type' in pack:
                self.pack_source = 'system_event'
            else:
                self.pack_source = 'unknown_dict'
        else:
            self.pack_type = 'unknown'
            self.pack_source = 'unknown'
            self.is_valid = False

    def normalize(self):
        '''
        解析数据包并标准化Input类结构
        '''
        if isinstance(self.pack, dict):
            self.time = self.pack.get('time', '')
            self.type = self.pack.get('message_type', '') + '_' + self.pack.get('post_type', '')
            self.user = self.pack.get('user_id', '')
            self.content = self.pack.get('raw_message', '')
            self.source = self.pack.get('message_type', '')
        elif isinstance(self.pack, str):
            # 如果是字符串，尝试解析为JSON
            try:
                data = json.loads(self.pack)
                if isinstance(data, dict):
                    self.time = data.get('time', '')
                    self.type = data.get('message_type', '') + '_' + data.get('post_type', '')
                    self.user = data.get('user_id', '')
                    self.content = data.get('raw_message', '')
                    self.source = data.get('message_type', '')
                else:
                    # 纯文本内容
                    self.content = self.pack
                    self.type = 'text'
            except json.JSONDecodeError:
                # 无法解析为JSON的纯文本
                self.content = self.pack
                self.type = 'text'
        return self

    

class CoreOutput(IOPack):
    '''
    基本的输出数据包,原始数据来自模型生成内容, 记录了SKA / 程序逻辑选择的操作与目标
    '''
    def __init__(self, pack) -> None:
        super().__init__(pack, 'output')
        self.target = ''

    def normalize(self):
        '''
        解析数据包并标准化Output类结构
        '''
        if isinstance(self.pack, dict):
            # 处理Ollama API响应格式
            if 'response' in self.pack:
                self.content = self.pack.get('response', '')
                self.time = self.pack.get('created_at', time.time())
                self.type = 'ollama_response'
                
            else:
                # 处理其他字典格式
                self.time = self.pack.get('time', time.time())
                self.type = self.pack.get('type', 'output')
                self.user = self.pack.get('user', '')
                self.content = self.pack.get('content', '')
                self.target = self.pack.get('target', '')
        elif isinstance(self.pack, str):
            # 处理纯文本格式
            self.content = self.pack
            self.type = 'text'
        return self

class ExpandOutput(CoreOutput):
    '''
    扩增的输出操作,在需要调用工具等时使用
    '''

