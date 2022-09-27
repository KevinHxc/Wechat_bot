# -*- coding: utf-8 -*-
import sys
import ntchat
import requests
import json
import common_const

SERVICE_ADD = 'http://localhost:8888/rocketqa'

wechat = ntchat.WeChat()

# 打开pc微信, smart: 是否管理已经登录的微信
wechat.open(smart=True)

# 注册消息回调
@wechat.msg_register(ntchat.MT_RECV_TEXT_MSG)
def on_recv_text_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    room_wxid = data["room_wxid"]

    # 判断消息不是自己发的并且不是群消息时，回复对方
    if from_wxid != self_wxid and not room_wxid:

        # 判断是否是QA问答关键字，形式为"QA XXXX"，关键字与所咨询的问题之间以一个空格间隔
        queryQA = data["msg"].split(' ')

        if len(queryQA) == 0 or len(queryQA) == 1:
            return

        if queryQA[0] == 'QA':
            keyword_input = queryQA[1]
            wechat_str = ''

            input_data = {}
            input_data['query'] = keyword_input
            input_data['topk'] = common_const.TOPK

            # 通过RocketQA，按照匹配度由高到低，获取所咨询问题的相关话题
            result = requests.post(SERVICE_ADD, json=input_data)
            res_json = json.loads(result.text)

            if res_json['answer'] is None or len(res_json['answer']) == 0:
                wechat_instance.send_text(to_wxid=from_wxid, content="未查询到与之匹配的问题，请重新输入咨询内容。")
                return res_json

            i = 0
            for queryIndex in res_json['answer']:
                # 在每套话题之间加上分割线
                if i > 0:
                    wechat_str = wechat_str + "------------------------\r\n"

                wechat_str = wechat_str + "问题" + str(i+1) + ": " + queryIndex['title'] + '\n'
                wechat_str = wechat_str + "回答" + str(i+1) + ": " + queryIndex['para'] + '\n'

                i = i + 1

            # 将结果回复对方
            wechat_instance.send_text(to_wxid=from_wxid, content=wechat_str)

try:
    while True:
        pass
except KeyboardInterrupt:
    ntchat.exit_()
    sys.exit()
