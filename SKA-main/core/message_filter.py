import json
import os
import re
from typing import List, Set, Optional


class MessageFilter:
    """
    聊天消息过滤器，用于过滤不当内容并支持自定义违禁词典
    """
    
    def __init__(self, banned_words_file: Optional[str] = None):
        """
        初始化消息过滤器
        
        Args:
            banned_words_file: 违禁词文件路径
        """
        self.banned_words_file = banned_words_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'config', 'banned_words.json'
        )
        self.banned_words: Set[str] = set()
        self.banned_patterns: List[re.Pattern] = []
        self.load_banned_words()
    
    def load_banned_words(self):
        """
        从文件加载违禁词
        """
        try:
            if os.path.exists(self.banned_words_file):
                with open(self.banned_words_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    words = data.get('words', [])
                    patterns = data.get('patterns', [])
                    
                    self.banned_words = set(words)
                    self.banned_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            else:
                # 创建默认的违禁词文件
                self.create_default_banned_words_file()
        except Exception as e:
            print(f"加载违禁词文件失败: {e}")
            # 使用默认违禁词
            self.banned_words = {
                '违禁词1', '违禁词2', '非法内容'
            }
            self.banned_patterns = []
    
    def create_default_banned_words_file(self):
        """
        创建默认的违禁词文件
        """
        default_data = {
            "words": [
                "违禁词1",
                "违禁词2", 
                "非法内容"
            ],
            "patterns": [
                r"[\d]{11}",  # 匹配11位数字(如手机号)
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  # 匹配邮箱
            ]
        }
        
        # 确保config目录存在
        config_dir = os.path.dirname(self.banned_words_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        with open(self.banned_words_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        
        self.banned_words = set(default_data['words'])
        self.banned_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in default_data['patterns']]
    
    def add_banned_word(self, word: str):
        """
        添加单个违禁词
        
        Args:
            word: 要添加的违禁词
        """
        self.banned_words.add(word)
        self.save_banned_words()
    
    def add_banned_words(self, words: List[str]):
        """
        添加多个违禁词
        
        Args:
            words: 要添加的违禁词列表
        """
        self.banned_words.update(words)
        self.save_banned_words()
    
    def remove_banned_word(self, word: str):
        """
        移除单个违禁词
        
        Args:
            word: 要移除的违禁词
        """
        self.banned_words.discard(word)
        self.save_banned_words()
    
    def save_banned_words(self):
        """
        保存违禁词到文件
        """
        try:
            # 读取现有文件内容
            if os.path.exists(self.banned_words_file):
                with open(self.banned_words_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"words": [], "patterns": []}
            
            # 更新违禁词列表
            data['words'] = list(self.banned_words)
            
            # 确保config目录存在
            config_dir = os.path.dirname(self.banned_words_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 写入文件
            with open(self.banned_words_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存违禁词文件失败: {e}")
    
    def filter_message(self, message: str) -> str:
        """
        过滤消息中的违禁内容
        
        Args:
            message: 原始消息
            
        Returns:
            过滤后的消息
        """
        filtered_message = message
        
        # 检查是否包含违禁词
        for word in self.banned_words:
            if word in filtered_message:
                # 用*替换违禁词
                filtered_message = filtered_message.replace(word, '*' * len(word))
        
        # 检查是否匹配违禁模式
        for pattern in self.banned_patterns:
            if pattern.search(filtered_message):
                # 用*替换匹配的内容
                filtered_message = pattern.sub(lambda m: '*' * len(m.group()), filtered_message)
        
        return filtered_message
    
    def contains_banned_content(self, message: str) -> bool:
        """
        检查消息是否包含违禁内容
        
        Args:
            message: 要检查的消息
            
        Returns:
            如果包含违禁内容返回True，否则返回False
        """
        # 检查是否包含违禁词
        for word in self.banned_words:
            if word in message:
                return True
        
        # 检查是否匹配违禁模式
        for pattern in self.banned_patterns:
            if pattern.search(message):
                return True
        
        return False
    
    def update_banned_patterns(self, patterns: List[str]):
        """
        更新违禁模式
        
        Args:
            patterns: 正则表达式模式列表
        """
        self.banned_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        self.save_banned_words()


def test_message_filter():
    """
    测试消息过滤器功能
    """
    # 创建过滤器实例
    filter_obj = MessageFilter()
    
    # 测试过滤功能
    test_messages = [
        "这是一条正常消息",
        "这是一条包含违禁词1的消息",
        "这是手机号13812345678",
        "这是邮箱test@example.com",
        "混合内容：违禁词1和手机号13812345678"
    ]
    
    print("=== 消息过滤测试 ===")
    for msg in test_messages:
        filtered = filter_obj.filter_message(msg)
        contains_banned = filter_obj.contains_banned_content(msg)
        print(f"原始消息: {msg}")
        print(f"过滤后消息: {filtered}")
        print(f"是否包含违禁内容: {contains_banned}")
        print("-" * 30)


if __name__ == "__main__":
    test_message_filter()