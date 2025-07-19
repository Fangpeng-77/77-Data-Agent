import json
from function_tools import sql_tools
from model_init import zhipu_model
from model_config import model_conf
from zhipuai import ZhipuAI

def remove_duplicate_sentences(text):
    """简单句子级去重"""
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    seen = set()
    unique = []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return '。'.join(unique)

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
        tools=sql_tools.tools,
        tool_choice="auto"
    )
    # 解析模型响应
    assistant_message = response.choices[0].message
    # 让大模型执行相应的SQL语句
    function_response = sql_tools.parse_response(response)
    # 第二轮对话，让大模型生成自然语言回答
    messages.append(assistant_message.model_dump())
    # 是否需要调用工具
    if assistant_message.tool_calls:
        function_name = response.choices[0].message.tool_calls[0].function.name
        function_id = response.choices[0].message.tool_calls[0].id
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
            tools=sql_tools.tools,
            tool_choice="auto"
        )
        # print(f"{ended_response.choices[0].message.content}")
        return ended_response.choices[0].message.content
    return assistant_message.content


def ai_assistant_stream(input_string):
    """流式版本的AI助手，支持工具调用 - 优化所有输出均为流式"""
    client = ZhipuAI(api_key=model_conf.zhipu_ak)

    # 初始化消息
    messages = [{
        "role": "system",
        "content": "您是一名SQL专家，根据用户需求，生成准确的SQL语句，负责查询MySQL中的数据库表信息。"
    }, {
        "role": "user",
        "content": f"{input_string}"
    }]

    # 第一轮对话（流式），生成SQL语句
    response_stream = client.chat.completions.create(
        model=model_conf.model_name,
        messages=messages,
        tools=sql_tools.tools,
        tool_choice="auto",
        stream=True
    )

    # 收集第一轮响应（同时流式输出内容）
    assistant_message = {"role": "assistant", "content": "", "tool_calls": []}
    tool_calls_detected = False

    for chunk in response_stream:
        if chunk.choices and chunk.choices[0].delta:
            delta = chunk.choices[0].delta

            # 收集并输出内容
            if delta.content:
                content = delta.content
                assistant_message["content"] += content
                yield {"type": "content", "data": content}

            # 收集工具调用
            if delta.tool_calls:
                tool_calls_detected = True
                for tool_call in delta.tool_calls:
                    # 初始化新的工具调用
                    if len(assistant_message["tool_calls"]) <= tool_call.index:
                        assistant_message["tool_calls"].append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments or ""
                            }
                        })
                    else:
                        # 追加参数
                        assistant_message["tool_calls"][tool_call.index]["function"][
                            "arguments"] += tool_call.function.arguments or ""

    # 添加到消息历史
    messages.append(assistant_message)

    # 如果需要调用工具
    if assistant_message["tool_calls"]:
        # 执行工具调用
        function_mapping = {
            "query_database": sql_tools.query_database,
            "insert_database": sql_tools.insert_database,
            "delete_data": sql_tools.delete_data,
            "update_database": sql_tools.update_database
        }

        tool_responses = []
        for tool_call in assistant_message["tool_calls"]:
            func_name = tool_call["function"]["name"]
            try:
                func_args = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError:
                # 返回错误信息作为内容
                yield {"type": "content", "data": "参数解析失败"}
                return

            if func_name in function_mapping:
                func = function_mapping[func_name]
                # 执行函数并获取结果
                try:
                    result = func(query=func_args.get("query"))
                    tool_responses.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": str(result)
                    })
                except Exception as e:
                    tool_responses.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": f"执行错误: {str(e)}"
                    })

        # 添加工具响应到消息历史
        for response in tool_responses:
            messages.append(response)

        # 添加用户提示
        messages.append({
            "role": "user",
            "content": "请根据数据库操作结果给出专业回答。"
        })

        # 第二轮对话（流式），获取最终回答
        final_response_stream = client.chat.completions.create(
            model=model_conf.model_name,
            messages=messages,
            stream=True
        )

        # 流式输出最终回答
        for chunk in final_response_stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield {"type": "content", "data": content}

    elif not tool_calls_detected:
        # 如果没有检测到工具调用，并且也没有工具调用信息
        # 直接流式输出第一轮收集的内容（已经在前面的循环中输出过了）
        pass
    else:
        # 如果没有工具调用，但内容还没有完全输出（安全处理）
        # 这种情况理论上不会发生，但为了完整性保留
        if assistant_message["content"]:
            yield {"type": "content", "data": assistant_message["content"]}

def test_ai_assistant_stream(input_str):
    """测试函数，用于查看流式输出"""
    print(f"测试输入: '{input_str}'")
    print("=" * 80)

    # 创建输出收集器
    output = {
        "content_parts": [],
        "tool_calls": [],
        "tool_results": [],
        "tool_errors": [],
        "final_output": ""
    }

    try:
        # 调用流式函数
        for event in ai_assistant_stream(input_str):
            if event["type"] == "content":
                print(f"[内容] {event['data']}")
                output["content_parts"].append(event['data'])
            elif event["type"] == "tool_call":
                print(f"[工具调用] {event['data']}")
                output["tool_calls"].append(event['data'])
            elif event["type"] == "tool_result":
                print(f"[工具结果] {event['data']}")
                output["tool_results"].append(event['data'])
            elif event["type"] == "tool_error":
                print(f"[工具错误] {event['data']}")
                output["tool_errors"].append(event['data'])
            elif event["type"] == "final":
                print(f"[最终输出] {event['data']}")
                output["final_output"] = event['data']
            elif event["type"] == "error":
                print(f"[错误] {event['data']}")
                output["errors"].append(event['data'])

    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")

    print("\n" + "=" * 80)
    print("测试摘要:")
    print(f"内容片段数量: {len(output['content_parts'])}")
    print(f"工具调用次数: {len(output['tool_calls'])}")
    print(f"工具成功执行次数: {len(output['tool_results'])}")
    print(f"工具执行错误次数: {len(output['tool_errors'])}")
    print(f"最终输出长度: {len(output['final_output'])} 字符")

    if output["final_output"]:
        print("\n最终输出内容:")
        print(output["final_output"])

    return output


if __name__ == '__main__':
    input_str = """
        现在我想选一名同学去参加数学竞赛，你认为选哪一位同学比较合适？
    """
    test_ai_assistant_stream(input_str)