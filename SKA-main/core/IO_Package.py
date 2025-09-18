import time

class IOPack():
    '''
    与SKA交互的标准数据包的基类
    '''
    def __init__(self, pack, type) -> None:
        self.time = time.time
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
        super().__init__(pack, self.type)
        self.source = ''

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

