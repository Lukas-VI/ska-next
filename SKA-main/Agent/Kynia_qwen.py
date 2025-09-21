"""SKA的qwen-agaent实现"""
import os  # noqa
import json

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.utils.output_beautify import typewriter_print


def init_agent_service():

    llm_cfg = {
        # Use your own model service compatible with OpenAI API by vLLM/SGLang:
        'model': 'qwen3:30b-a3b-instruct-2507-q4_K_M',
        'model_server': 'http://192.168.30.13:11434/v1',  # api_base
        'api_key': 'EMPTY',
    
        'generate_cfg': {
            # When using vLLM/SGLang OAI API, pass the parameter of whether to enable thinking mode in this way
            'extra_body': {
                'chat_template_kwargs': {'enable_thinking': False}
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
    ]

    bot = Assistant(llm=llm_cfg,
                    function_list=tools,
                    system_message='',
                    name='SKA',
                    description="我是SKA，大家的好帮手，快来让我使用工具吧！")

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
        for response in bot.run(messages=messages):
            response_plain_text = typewriter_print(response, response_plain_text)
        print(response)
        messages.extend(response)


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
    app_tui()
