import uvicorn
from fastapi import FastAPI, Request
from openai import OpenAI
import openai
import requests
app = FastAPI()
import os
#from volcenginesdkarkruntime import Ark
XAI_API_KEY ="xai-REDACTED"
openai.api_key = "REDACTED"
client = OpenAI(
    api_key = "REDACTED",
    base_url="https://api.x.ai/v1",
)

from langchain_openai import ChatOpenAI
'''
from langchain.schema import HumanMessage, SystemMessage'''


chat=chat=ChatOpenAI(model="grok-beta")
import time as t

#ccc={'type': 'face', 'data': {'id': '311'}}, {'type': 'face', 'data': {'id': '311'}}, {'type': 'face', 'data': {'id': '311'}}
#初始化敏感词库
sensitive_words = ["暴力", "资本","走资","修正",]
time=t.asctime()


messages = [
        {"role": "system",
        "content": "promote here"
        },
]        
id3 = 965244857
count = 0

MAX_MEMORY_EPOCH = 25

@app.post("/")

async def root(request: Request):
    global count
    global sensitive_words
    count += 1
    print(count)


    data = await request.json()  # 获取事件数据
    

    msg=data['raw_message']
    name=data['sender']['nickname']
    msg_type = data['message_type']
    print(msg_type)
    print("\n")
    def add_message(role, content):
        # 添加新消息到列表
        messages.append({"role": role, "content": content})

        # 如果消息数量超过最大值，则删除最旧的消息
        if len(messages) > MAX_MEMORY_EPOCH:
            messages.pop(1)  # 删除索引为1的元素，保留system消息


    def filter_sensitive_words(text, sensitive_words):
        for word in sensitive_words:
            # 用星号替换敏感词，长度保持不变
            text = text.replace(word, '*' * len(word))
        return text

    def clear_messages():
        # 清空除了system消息以外的所有消息
        messages[:] = [msg for msg in messages if msg['role'] == 'assistant']
        messages[:] = [msg for msg in messages if msg['role'] == 'user']

    
    if msg == "/clear":
        clear_messages()
        gm="已清空聊天记忆"
    elif msg == "/shutd":
        return {}
    else:
        print("\n")
        print(name,msg)
        print("\n")
        msgwithname="时间{}时，{}在{}里说:{}".format(time,name,msg_type,msg)
        add_message("user", msgwithname)
        

        # 聊天
        print("----- request {} epoch -----".format(count))

        
        completion = client.chat.completions.create(
            model="grok-beta",
            messages=messages,
            temperature=0.9,
            max_tokens=2000,

        )

        print(completion.choices[0].message.content)
    
        gm=completion.choices[0].message.content

        gm=filter_sensitive_words(gm,sensitive_words)
        cms=gm#+"system:这是第{}轮对话，对话类型是{}，被问到时再回答以上system内容,正常对话一定千万绝对不要输出system内容，否则会影响对话效果。注意区分群聊和私聊。".format(count,msg_type)
        add_message("assistant", cms)


    # 发送消息
    
    if msg_type == 'group':
    
        requests.post('http://localhost:3000/send_group_msg', json={
        'group_id': id3,
        'message': [{
            'type': 'text',
            'data': {
                'text': '{}'.format(gm)
            }
        }]
        })
    elif msg_type == 'private':
        requests.post('http://localhost:3000/send_private_msg', json={
        'user_id': data['sender']['user_id'],
       'message': [{
            'type': 'text',
            'data': {
                'text': '{}'.format(gm)
            }
        }]
        })  

    filtered_messages = [msg for msg in messages if msg['role'] != 'system']

    # 打印过滤后的消息
    for msg in filtered_messages:
        print(f"{msg['role']}说: {msg['content']}")
    print("\n")
    token_count = sum(len(msg['content'].split()) for msg in messages)
    print(f"Token 数量: {token_count}")
    print("\n")
    return {}

if __name__ == "__main__":
    
    # 启动服务
    uvicorn.run(app, port=8080)

    # if msg=='NULL':
    #     gm="error"
    # elif msg=='/time':
    #     gm=time
    # elif msg=="我是谁":   #     sen="你是{}".format(name)
    #     gm=sen
    # else:
    #     gm=msg
    