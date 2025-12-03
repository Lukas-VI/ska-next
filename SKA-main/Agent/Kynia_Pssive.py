"""
SKA的qwen-agaent-被动实现
初版由于采用Agent主动策略，导致过于激进输出无意义歇斯底里内容
本版通过单一模型输出进行回复，废弃

"""
import os  # noqa


from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.utils.output_beautify import typewriter_print
# 修复导入路径问题
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


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
    ]

    """加载提示词模板"""
    try:
        prompt_templatet_path = os.path.join(os.path.dirname(__file__), 'prompt-p.json')
        with open(prompt_templatet_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        print("Prompt template loaded successfully")
    except Exception as e:
        print(f"Failed to load prompt template: {e}")
        prompt_template = "you are a helpful agent"
    # print(prompt_template)
    bot = Assistant(llm=llm_cfg,
                    function_list=tools,
                    system_message=prompt_template,
                    name='SKA-P',
                    description="我是SKA2，大家的好帮手，快来使用我吧！")
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