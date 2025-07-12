from zhipuai import ZhipuAI
from model_config import model_conf

def chat_with_zhipu(messages, tools=None, tool_choice=None, model=model_conf.model_name):
    """
    创建请求示例
    :param messages:
    :param tools:
    :param tool_choice:
    :param model:
    :return:
    """
    client = ZhipuAI(api_key=model_conf.zhipu_ak)
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
    )
    return response
