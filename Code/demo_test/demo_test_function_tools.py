# -*- coding: utf-8 -*-
# @Author: Fang Peng
# @Wechat Account: 77 Data
# @Date:   2025-07-10
# @Last Modified by: Fang Peng
# @Last Modified time: 2025-07-10 22:29:00
# @Description: function_tools 的功能测试
# 参考文档：https://open.bigmodel.cn/dev/api/search-tool/websearch-in-chat

from zhipuai import ZhipuAI
from model_config import model_conf

client = ZhipuAI(api_key=model_conf.zhipu_ak)

tools = [
    {
        # 指明这是一个web搜索工具
        "type": "web_search",
        # 定义具体的参数列表
        "web_search": {
            # 是否启动web搜索
            "enable": "True",
            # 搜索引擎类型
            "search_engine": "search_pro",
            # 是否返回获取网页搜索来源的相信信息
            "search_result": "True",
            "search_prompt": "你是一名高铁车票查询员，请用简洁的语言总结网络搜索中：{{search_result}}中的关键信息，以供用户选择合理的车次购票。",
            # 返回结果的条数
            "count": "10",
            "search_domain_filter": "www.sohu.com",
            # 搜索指定时间范围内的网页
            "search_recency_filter": "noLimit",
            "content_size": "high"
        }
    }
]

messages = [{
    "role": "user",
    "content": "你能帮我查一下2025年7月9日从北京南到合肥南的高铁吗？"
}]

response = client.chat.completions.create(
    model=model_conf.model_name_web_search,
    messages=messages,
    tools=tools
)
print(response)
