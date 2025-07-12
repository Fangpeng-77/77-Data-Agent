import json
from model_config import model_conf

# todo 描述数据库表结构
database_schema_string = """
CREATE TABLE StudentGrades (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Course VARCHAR(50) NOT NULL,
    Grade DECIMAL(5, 2) NOT NULL
);
-- 示例数据
INSERT INTO StudentGrades (Name, Course, Grade) VALUES ('张三', '数学', 88.50);
)"""


tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "使用此函数查询数据库信息，输出必须是一个SQL查询语句",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"SQL查询提取信息以回答用户的问题。"
                        f"使用数据库模式：{database_schema_string}"
                        f"查询应该以纯文本返回，只包含MySQL支持的语法"
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_database",
            "description": "使用此函数向数据库插入新数据，输出必须是一个SQL插入语句",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"SQL插入语句，用于向数据库添加新纪录。"
                        f"使用数据库模式：{database_schema_string}"
                        f"语句应该以纯文本返回，只包含MySQL支持的语法"
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_data",
            "description": "使用此函数向数据库删除一条数据，输出必须是一个SQL删除语句",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"SQL删除语句，用于从数据库中删除一条记录。"
                        f"使用数据库模式：{database_schema_string}"
                        f"语句应该以纯文本返回，只包含MySQL支持的语法"
                    }
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_database",
            "description": "使用此函数更新数据库信息，输出必须一个SQL更新语句",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"SQL更新语句，用于更新数据库中的数据。"
                        f"使用数据库模式：{database_schema_string}"
                        f"语句应该以纯文本返回，只包含MySQL支持的语法"
                    }
                },
                "required": ["query"],
            }
        }
    }
]

def query_database(query):
    """查询数据库并返回结果"""
    cursor = model_conf.conn.cursor()
    print(f"执行查询: {query}")
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    model_conf.conn.close()
    return result

def insert_database(query):
    """向数据库插入数据并返回操作状态"""
    cursor = model_conf.conn.cursor()
    print(f"执行插入: {query}")
    try:
        cursor.execute(query)
        model_conf.conn.commit()
        affected_rows = cursor.rowcount
        return {"status": "success", "affected_rows": affected_rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        model_conf.conn.close()

def delete_data(query):
    """从数据中删除某条数据并返回操作状态"""
    cursor = model_conf.conn.cursor()
    print(f"执行删除: {query}")
    try:
        cursor.execute(query)
        model_conf.conn.commit()
        affected_rows = cursor.rowcount
        return {"status": "success", "affected_rows": affected_rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        model_conf.conn.close()

def update_database(query):
    """更新数据库并返回操作状态"""
    cursor = model_conf.conn.cursor()
    print(f"执行更新: {query}")
    try:
        cursor.execute(query)
        model_conf.conn.commit()
        affected_rows = cursor.rowcount
        return {"status": "success", "affected_rows": affected_rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

def parse_response(response):
    """解析模型响应并执行对应的数据库操作"""
    response_message = response.choices[0].message
    # 判断需不需要执行function_tool
    if response_message.tool_calls:
        # 可以使用的函数
        function_mapping = {
            "query_database": query_database,
            "insert_database": insert_database,
            "delete_data": delete_data,
            "update_database": update_database
        }
        results = []
        # 查询匹配
        for tool_call in response_message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            if func_name in function_mapping:
                func = function_mapping[func_name]
                # 执行函数并获取结果
                result = func(query = func_args.get("query"))
                results.append({
                    "function": func_name,
                    "result": result
                })
        return results
    return None


if __name__ == "__main__":
    query = """select count(1) as cnt from StudentGrades"""
    a = query_database(query)