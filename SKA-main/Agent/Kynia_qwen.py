"""SKA的qwen-agaent实现"""
import os  # noqa
import json5

import json
import http.client
import json

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.tools.base import BaseTool, register_tool

# Add a custom tool named my_image_gen：
@register_tool('private_msg')
class PrivateMsg(BaseTool):
    description = '私信发送服务, 输入目标用户昵称与内容, 返回状态码'
    parameters = [
        {
            'name': 'user_card',
            'type': 'string',
            'description': '用户的昵称',
            'required': True,
        },
        {
            'name': 'text',
            'type': 'string',
            'description': '将要输出的信息',
            'required': True,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        data = ''
        try:
            user_card = json5.loads(params)['user_card']
            text = json5.loads(params)['text']
            conn = http.client.HTTPSConnection("127.0.0.1", 3000)
            payload = json.dumps({
                "user_id": 1029797287,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": text
                        }
                    }
                ]
            })
            headers = {
            'Content-Type': 'application/json'
            }
            conn.request("POST", "/send_private_msg", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
        except Exception as e:
            print(f"发送消息 send_private_msg 失败: {str(e)}")    
        return data

@register_tool('group_msg')
class GroupMsg(BaseTool):
    description = '私信发送服务, 输入目标用户昵称与内容, 返回状态码'
    parameters = [
        {
            'name': 'user_card',
            'type': 'string',
            'description': '用户的昵称',
            'required': True,
        },
        {
            'name': 'text',
            'type': 'string',
            'description': '将要输出的信息',
            'required': True,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        data = ''
        try:
            user_card = json5.loads(params)['user_card']
            text = json5.loads(params)['text']
            conn = http.client.HTTPSConnection("127.0.0.1", 3000)
            payload = json.dumps({
                "user_id": 965244857,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": text
                        }
                    }
                ]
            })
            headers = {
            'Content-Type': 'application/json'
            }
            conn.request("POST", "/send_group_msg", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
        except Exception as e:
            print(f"发送消息 private_msg 失败: {str(e)}")    
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
    
            # Add: When the content is `<think>this is the thought</think>this is the answer`
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
                'fetch': {
                    'command': 'uvx',
                    'args': ['mcp-server-fetch']
                }
            }
        },
        'code_interpreter',  # Built-in tools
        'private_msg',
        'group_msg'
    ]

    """加载提示词模板"""
    try:
        with open('SKA-main/Agent/prompt.json', 'r', encoding='utf-8') as f:
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
