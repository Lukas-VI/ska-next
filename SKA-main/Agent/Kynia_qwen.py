"""SKA的qwen-agaent实现"""
import os  # noqa
import json5

import json
import http.client
from typing import Any, Dict

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.tools.base import BaseTool, register_tool
# 修复导入路径问题
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.message_filter import MessageFilter


@register_tool('qq_message', True)
class QQMessageSender(BaseTool):
    description = '统一消息发送服务，支持私聊和群聊消息'
    parameters = [
        {
            'name': 'type',
            'type': 'string',
            'description': '消息类型: private(私聊消息), group(群聊消息)',
            'required': True,
        },
        {
            'name': 'text',
            'type': 'string',
            'description': '将要输出的信息',
            'required': True,
        },
        {
            'name': 'user_card',
            'type': 'string',
            'description': '用户的昵称（私聊时必需）',
            'required': False,
        },
    ]

        
    def call(self, params: str, **kwargs) -> str:  # type: ignore
        self.message_filter = MessageFilter()
        data = ''
        try:
            # 修复类型问题
            params_dict: Dict[str, Any] = json5.loads(params)  # type: ignore
            msg_type = params_dict.get('type', '')
            text = params_dict.get('text', '')
            user_card = params_dict.get('user_card', '')
            
            # 过滤消息内容
            filtered_text = self.message_filter.filter_message(text)
            
            # # 检查是否包含违禁内容
            # if self.message_filter.contains_banned_content(text):
            #     print("消息包含违禁内容，已过滤")
            #     filtered_text = "[消息包含敏感内容，已被过滤]"
            
            conn = http.client.HTTPConnection("127.0.0.1", 3000)
            headers = {'Content-Type': 'application/json'}
            
            if msg_type == 'private':
                # 私聊消息
                if not user_card:
                    return "发送私聊消息需要提供用户昵称(user_card)"
                    
                user_id = 1029797287
                # 安全加载用户id
                user_id_dict_path = os.path.join(os.path.dirname(__file__), 'user_id_dict.json')
                with open(user_id_dict_path, 'r', encoding='utf-8') as f:
                    user_id_dict = json5.load(f)
                    user_id = user_id_dict.get(user_card, user_id)
                    
                payload = json.dumps({
                    "user_id": user_id,
                    "message": [
                        {
                            "type": "text",
                            "data": {
                                "text": filtered_text
                            }
                        }
                    ]
                })
                conn.request("POST", "/send_private_msg", payload, headers)
                res = conn.getresponse()
                data = res.read().decode("utf-8")
                
            elif msg_type == 'group':
                # 群聊消息
                payload = json.dumps({
                    "group_id": 965244857,
                    "message": [
                        {
                            "type": "text",
                            "data": {
                                "text": filtered_text
                            }
                        }
                    ]
                })
                conn.request("POST", "/send_group_msg", payload, headers)
                res = conn.getresponse()
                data = res.read().decode("utf-8")
            else:
                return "不支持的消息类型，请使用 private 或 group"
                
        except FileNotFoundError as e:
            data = f"文件未找到: {str(e)}"
            print(data)
        except KeyError as e:
            data = f"配置错误: {str(e)}"
            print(data)
        except Exception as e:
            data = f"发送消息失败: {str(e)}"
            print(data)
        return data  


def init_agent_service():

    llm_cfg = {
        # Use your own model service compatible with OpenAI API by vLLM/SGLang:
        'model': 'qwen3:30b-a3b-instruct-2507-q4_K_M',
        'model_server': 'http://192.168.30.13:11434/v1',  # api_base
        'api_key': 'EMPTY',
    
        'generate_cfg': {
            # When using vLLM/SGLang OAI API, pass the parameter of whether to enable thinking mode in this way
            'extra_body': {
                # 'chat_template_kwargs': {'enable_thinking': False},
                "max_input_tokens": 100
            },
    
            # Add: When the content is ```
            # Do not add: When the response has been separated by reasoning_content and content
            # This parameter will affect the parsing strategy of tool call
            # 'thought_in_content': True,
        },
    }

    tools = [
        {
            'mcpServers': {  # You can specify the MCP configuration file
                'time': {
                    'command': 'uvx',
                    'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
                },
                "fetch": {
                    "args": ["mcp-server-fetch"],
                    "command": "uvx"
                },
                "playwright": {
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"]
                },
                "bingcn": {
                    "args": ["bing-cn-mcp"],
                    "command": "npx"
                },
                "memory": {
                    "args": ["-y","@modelcontextprotocol/server-memory"],"command": "npx"
                },
                "12306-mcp": {
                    "args": ["-y","12306-mcp"],
                    "command": "npx"
                },
                 "howtocook-mcp": {
                    "args": ["-y","howtocook-mcp"],
                    "command": "npx"
                }, 
                "calculator": {
                    "args": ["mcp-calculator"],
                    "command": "npx"
                    }
            }
        },
        'code_interpreter',  # Built-in tools
        'qq_message'
    ]

    """加载提示词模板"""
    try:
        prompt_templatet_path = os.path.join(os.path.dirname(__file__), 'prompt2.json')
        with open(prompt_templatet_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
            '''try:
                with open('SKA-main/Agent/card.json', 'r', encoding='utf-8') as f:
                    prompt_template += f.read()
            except Exception as e:
                print(f"Failed to load card: {e}")'''
        print("Prompt template loaded successfully")
    except Exception as e:
        print(f"Failed to load prompt template: {e}")
        prompt_template = ""
    # print(prompt_template)
    bot = Assistant(llm=llm_cfg,
                    function_list=tools,
                    system_message=prompt_template,
                    name='SKA2',
                    description="我是SKA2，大家的好帮手，快来让我使用工具吧！")
    return bot


'''def test(query: str = 'What time is it?'):
    # Define the agent
    bot = init_agent_service()

    # Chat
    messages = [{'role': 'user', 'content': query}]
    response_plain_text = ''
    for response in bot.run(messages=messages):
        response_plain_text = typewriter_print(response, response_plain_text)'''


def app_tui():
    # Define the agent
    bot = init_agent_service()

    # Chat
    messages = [{'role': 'system', 'content': '你是SKAgent'}]
    while True:
        query = input('user question: ')
        messages.append({'role': 'user', 'content': query})
        response = []
        response_plain_text = ''
        for response in bot.run(messages=messages): # type: ignore
            response_plain_text = typewriter_print(response, response_plain_text) # type: ignore
        print(response)
        messages.extend(response) # type: ignore


def app_gui():
    # Define the agent
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            'What time is it?',
            'https://github.com/orgs/QwenLM/repositories Extract markdown content of this page, then draw a bar chart to display the number of stars.'
        ]
    }
    WebUI(
        bot,
        chatbot_config=chatbot_config,
    ).run()


if __name__ == '__main__':
    # test()
    # app_tui()
    app_gui()