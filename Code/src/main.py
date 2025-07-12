from function_tools.sql_tools import tools, parse_response
from model_init import zhipu_model


def ai_assistant(input_string):
    messages = [{
        "role": "system",
        "content": "您是一名SQL专家，根据用户需求，生成准确的SQL语句，负责查询MySQL中的数据库表信息。"
    }, {
        "role": "user",
        "content": f"{input_string}"
    }]
    # 第一轮对话，生成相应的SQL语句
    response = zhipu_model.chat_with_zhipu(
        messages,
        tools=tools,
        tool_choice="auto"
    )
    # 解析模型响应
    assistant_message = response.choices[0].message
    function_name = response.choices[0].message.tool_calls[0].function.name
    function_id = response.choices[0].message.tool_calls[0].id
    # 让大模型执行相应的SQL语句
    function_response = parse_response(response)
    # 第二轮对话，让大模型生成自然语言回答
    messages.append(assistant_message.model_dump())
    messages.append({
        "role": "tool",
        "tool_call_id": function_id,
        "name": function_name,
        "content": str(function_response)
    })
    messages.append({
        "role": "user",
        "content": f"请结合用户的实际需求：{input_string}，给出一个合理的回答。"
    })
    ended_response = zhipu_model.chat_with_zhipu(
        messages,
        tools=tools,
        tool_choice="auto"
    )
    print(f"{ended_response.choices[0].message.content}")


if __name__ == '__main__':
    input_str = """
        现在我想选一名同学去参加数学竞赛，你认为选哪一位同学比较合适？
    """
    ai_assistant(input_str)
