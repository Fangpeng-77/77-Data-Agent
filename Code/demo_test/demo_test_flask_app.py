from flask import Flask, request, render_template_string, session
from datetime import datetime
from zhipuai import ZhipuAI
from src import main
from model_config import model_conf
user_message = []
app = Flask(__name__)
app.secret_key = 'supersecretkey123!@#'

# 定义HTML模板（内联）
CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>77 Data Agent</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* 样式保持不变 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            width: 100%;
            max-width: 900px;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 90vh;
        }

        .header {
            background: linear-gradient(to right, #4b6cb7, #182848);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .header-left {
            display: flex;
            align-items: center;
        }

        .ai-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 24px;
            color: white;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }

        .header-info h1 {
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 3px;
        }

        .header-info p {
            font-size: 0.9rem;
            opacity: 0.9;
            display: flex;
            align-items: center;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 8px #4ade80;
        }

        .chat-container {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            background: #f9fafb;
        }

        .chat-log {
            flex: 1;
            overflow-y: auto;
            padding-right: 10px;
        }

        .message {
            max-width: 85%;
            margin-bottom: 25px;
            position: relative;
        }

        .user {
            align-self: flex-end;
            margin-left: auto;
        }

        .bot {
            align-self: flex-start;
            margin-right: auto;
        }

        .message-content {
            padding: 15px 20px;
            border-radius: 18px;
            line-height: 1.5;
            position: relative;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .user .message-content {
            background: linear-gradient(to right, #3494e6, #ec6ead);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .user .message-header {
            justify-content: flex-end;
            color: #3b82f6;
        }

        .bot .message-header {
            color: #10b981;
        }

        .bot .message-header i {
            margin-right: 8px;
            color: #10b981;
        }

        .user .message-header i {
            margin-left: 8px;
            color: #3b82f6;
        }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
        }

        .input-area form {
            display: flex;
            width: 100%;
            gap: 12px;
        }

        .input-area input[type="text"] {
            flex: 1;
            padding: 16px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
            background: #f9fafb;
        }

        .input-area input[type="text"]:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }

        .input-area input[type="submit"] {
            background: linear-gradient(to right, #4b6cb7, #182848);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 0 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(75, 108, 183, 0.3);
        }

        .input-area input[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(75, 108, 183, 0.4);
        }

        .input-area input[type="submit"]:active {
            transform: translateY(0);
        }

        .typing-indicator {
            display: none;
            padding: 15px 20px;
            background: white;
            border-radius: 18px;
            border: 1px solid #e5e7eb;
            margin-bottom: 25px;
            width: fit-content;
            align-self: flex-start;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .typing-indicator span {
            height: 10px;
            width: 10px;
            background: #9ca3af;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            animation: typing 1.4s infinite;
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        .welcome-message {
            text-align: center;
            padding: 30px 0;
            color: #6b7280;
            font-size: 1.1rem;
        }

        .timestamp {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-top: 5px;
            text-align: right;
        }

        .bot .timestamp {
            text-align: left;
        }

        @media (max-width: 768px) {
            .container {
                height: 95vh;
                border-radius: 15px;
            }

            .header {
                padding: 15px;
            }

            .ai-avatar {
                width: 42px;
                height: 42px;
                font-size: 20px;
            }

            .header-info h1 {
                font-size: 1.3rem;
            }

            .chat-container {
                padding: 15px;
            }

            .message {
                max-width: 90%;
            }

            .input-area {
                padding: 15px;
            }

            .input-area input[type="text"] {
                padding: 14px;
            }

            .input-area input[type="submit"] {
                padding: 0 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="chat-container">
            <div class="chat-log" id="chat-box">
                {% if not session.chat_log %}
                <div class="welcome-message">
                    <p>您好！我是77 Data Agent，一个专注于数据库智能操作的助手</p>
                    <p>请问有什么可以帮您的吗？</p>
                </div>
                {% endif %}

                {% for msg in session.chat_log %}
                <div class="message {{ msg.role }}">
                    {% if msg.role == 'bot' %}
                    <div class="message-header">
                        <i class="fas fa-robot"></i> 77 Data Agent
                    </div>
                    {% else %}
                    <div class="message-header">
                        用户 <i class="fas fa-user"></i>
                    </div>
                    {% endif %}
                    <div class="message-content">{{ msg.text }}</div>
                    <div class="timestamp">{{ msg.time }}</div>
                </div>
                {% endfor %}
            </div>

            <div class="typing-indicator" id="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>

        <div class="input-area">
            <form method="POST" id="chat-form">
                <input type="text" name="user_input" placeholder="输入您的问题..." autocomplete="off" />
                <input type="submit" value="发送" />
            </form>
            <button id="clear-chat" style="margin-left: 10px; background: #ff6b6b; color: white; border: none; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease;">清空聊天记录</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatBox = document.getElementById('chat-box');
            const typingIndicator = document.getElementById('typing-indicator');
            const clearButton = document.getElementById('clear-chat');

            // 滚动到聊天框底部
            function scrollToBottom() {
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            scrollToBottom();

            // 表单提交时显示"正在输入"效果
            document.querySelector('form').addEventListener('submit', function() {
                typingIndicator.style.display = 'block';
                scrollToBottom();

                // 2秒后自动隐藏（实际应用中应由服务器响应后隐藏）
                setTimeout(function() {
                    typingIndicator.style.display = 'none';
                }, 2000);
            });
            
            // 清空聊天按钮
            clearButton.addEventListener('click', function() {
                if(confirm('确定要清空聊天记录吗？')) {
                    fetch('/clear', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }).then(() => {
                        location.reload();
                    });
                }
            });
        });
    </script>
</body>
</html>
'''

def chat_with_model(user_input):
    client = ZhipuAI(api_key=model_conf.zhipu_ak)
    response = client.chat.completions.create(
        model = model_conf.model_name,
        messages = [
            {"role": "user", "content": f"{user_input}"},
        ]
    )
    return response.choices[0].message.content

def get_model_response(user_input):
    return chat_with_model(user_input)
@app.route('/', methods=['GET', 'POST'])
def chat():
    # 初始化聊天记录
    if 'chat_log' not in session:
        session['chat_log'] = []

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input:

            # bot_response = get_model_response(user_input)
            bot_response = main.ai_assistant(user_input)
            current_time = datetime.now().strftime('%H:%M')

            # 添加到聊天记录
            session['chat_log'].append({
                "role": "user",
                "text": user_input,
                "time": current_time
            })

            session['chat_log'].append({
                "role": "bot",
                "text": bot_response,
                "time": current_time
            })

            # 保存修改后的会话
            session.modified = True

    return render_template_string(CHAT_TEMPLATE)


@app.route('/clear', methods=['POST'])
def clear_chat():
    """清空聊天记录"""
    session['chat_log'] = []
    session.modified = True
    return '', 204

# 剩下开发任务
"""
1. Flask APP 代码需要进行合并整理。
2. 初试化的对话信息还需要进行完善。
3. 能不能换成流式调用的信息？

"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=52177, debug=True)