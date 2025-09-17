from pycqBot.cqHttpApi import cqHttpApi, cqLog
from pycqBot.data import Message
from waifu.Waifu import Waifu
from waifu.Tools import divede_sentences
import logging
import json
import os
import time

from pycqBot.cqCode import image, record

# 加载配置文件，返回用户ID列表
def load_config():
    with open(f'./qqbot/bot.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['user_id_list']


# 创建QQ机器人，设置消息处理回调，并实现消息发送功能
def make_qq_bot(callback, waifu: Waifu, send_text, send_voice, tts):
    cqLog(level=logging.INFO, logPath='./qqbot/cqLogs')

    cqapi = cqHttpApi(download_path='./qqbot/download')

    # 处理私信消息的回调函数
    def on_private_msg(message: Message):
        if 'CQ' in message.message:
            return
        callback.set_sender(message.sender)
        try:
            waifu.ask(message.message)
        except Exception as e:
            logging.error(e)

    # 处理非流式私信消息的回调函数
    def on_private_msg_nonstream(message: Message):
        if 'CQ' in message.message:
            return
        try:
            reply = waifu.ask(message.message)
            sentences = divede_sentences(reply)
            for st in sentences:
                time.sleep(0.5)
                if st == '' or st == ' ':
                    continue
                if send_text:
                    message.sender.send_message(waifu.add_emoji(st))
                    logging.info(f'发送信息: {st}')
                if send_voice:
                    emotion = waifu.analyze_emotion(st)
                    tts.speak(st, emotion)
                    file_path = './output.wav'
                    abs_path = os.path.abspath(file_path)
                    mtime = os.path.getmtime(file_path)
                    local_time = time.localtime(mtime)
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    message.sender.send_message("%s" % record(file='file:///' + abs_path))
                    logging.info(f'发送语音({emotion} {time_str}): {st}')
            time.sleep(0.5)
            file_name = waifu.finish_ask(reply)
            if not file_name == '':
                file_path = './presets/emoticon/' + file_name
                abs_path = os.path.abspath(file_path)
                message.sender.send_message("%s" % image(file='file:///' + abs_path))
            time.sleep(0.5)
            waifu.brain.think('/reset 请忘记之前的对话')
        except Exception as e:
            logging.error(e)

    user = load_config()

    # 创建机器人实例并指定用户ID列表
    bot = cqapi.create_bot(
        group_id_list=[0],
        user_id_list=user
    )
    if callback is None:
        bot.on_private_msg = on_private_msg_nonstream
    else:
        bot.on_private_msg = on_private_msg

    # TODO: 指令功能
    # def echo(commandData, message: Message):
    #     # 回复消息
    #     message.sender.send_message(" ".join(commandData))
    # 设置指令为 echo
    # bot.command(echo, "echo", {
    #     # echo 帮助
    #     "help": [
    #         "#echo - 输出文本"
    #     ],
    #     "type": "all"
    # })
    bot.start(go_cqhttp_path='./qqbot/')