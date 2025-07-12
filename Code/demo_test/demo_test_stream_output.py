# -*- coding: utf-8 -*-
# @Author: Fang Peng
# @Wechat Account: 77 Data
# @Date:   2025-07-10
# @Last Modified by: Fang Peng
# @Last Modified time: 2025-07-10 21:25:00
# @Description: 流式调用 的功能测试
# 参考文档：https://open.bigmodel.cn/dev/api/normal-model/glm-4

from zhipuai import ZhipuAI
from model_config import model_conf

client = ZhipuAI(api_key=model_conf.zhipu_ak)

messages = [
    {"role": "user", "content": "你能夸夸我的女朋友 77 吗？"},
]

response = client.chat.completions.create(
    model=model_conf.model_name,
    messages=messages,
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content.replace('\n', ''), end="")
