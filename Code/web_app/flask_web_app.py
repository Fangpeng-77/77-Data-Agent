from flask import Flask, request, render_template_string, session, Response, jsonify
from datetime import datetime
from zhipuai import ZhipuAI
import json
import time
from src import main
from model_config import model_conf
user_message = []
app = Flask(__name__)
app.secret_key = 'supersecretkey123!@#'

# 定义HTML模板（内联）- 增加了流式输出的JavaScript处理
CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>77 Data Agent</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.5/dist/purify.min.js"></script>
    
    <style>
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
        
        /* Markdown样式增强 */
        .message-content p {
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .message-content h1, 
        .message-content h2, 
        .message-content h3, 
        .message-content h4, 
        .message-content h5, 
        .message-content h6 {
            margin-top: 15px;
            margin-bottom: 10px;
            font-weight: 600;
            color: #2d3748;
        }
        
        .message-content h1 {
            font-size: 1.6rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 5px;
        }
        
        .message-content h2 {
            font-size: 1.4rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 3px;
        }
        
        .message-content h3 {
            font-size: 1.2rem;
        }
        
        .message-content blockquote {
            border-left: 4px solid #4299e1;
            padding-left: 15px;
            margin: 15px 0;
            color: #4a5568;
        }

        .message-content pre {
            background-color: #1e293b; /* 改为深蓝色背景 */
            color: #f8fafc;           /* 改为浅灰色字体 */
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
            line-height: 1.5;
            font-family: 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', Courier, monospace;
        }

        .message-content code {
            background-color: #334155; /* 改为中蓝色背景 */
            color: #e2e8f0;           /* 改为浅蓝色字体 */
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', Courier, monospace;
        }

        .message-content ul, 
        .message-content ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        .message-content li {
            margin-bottom: 8px;
        }
        
        .message-content table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            background-color: white;
            border: 1px solid #cbd5e0;
        }
        
        .message-content th, 
        .message-content td {
            padding: 10px;
            text-align: left;
            border: 1px solid #cbd5e0;
        }
        
        .message-content th {
            background-color: #edf2f7;
            font-weight: 600;
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
            
            .message-content pre {
                padding: 10px;
                font-size: 0.9rem;
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
                    <!-- 直接渲染已转换的HTML内容 -->
                    <div class="message-content">{{ msg.html|safe }}</div>
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
            const chatForm = document.getElementById('chat-form');
            let eventSource = null;

            // 滚动到聊天框底部
            function scrollToBottom() {
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            scrollToBottom();

            // 创建新的机器人消息元素
            function createBotMessage() {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot';
                
                const header = document.createElement('div');
                header.className = 'message-header';
                header.innerHTML = '<i class="fas fa-robot"></i> 77 Data Agent';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                content.id = 'streaming-content';
                
                const timestamp = document.createElement('div');
                timestamp.className = 'timestamp';
                timestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                messageDiv.appendChild(header);
                messageDiv.appendChild(content);
                messageDiv.appendChild(timestamp);
                
                chatBox.appendChild(messageDiv);
                scrollToBottom();
                
                return content;
            }

            // 安全渲染Markdown内容
            function safeRenderMarkdown(markdown) {
                try {
                    if (!markdown) return '';
                    
                    // 将Markdown转换为HTML
                    let rawHtml = marked.parse(markdown);
                    
                    // 使用DOMPurify消毒HTML
                    let cleanHtml = DOMPurify.sanitize(rawHtml);
                    
                    return cleanHtml;
                } catch (e) {
                    console.error('Markdown渲染错误:', e);
                    return markdown; // 出错时返回原始文本
                }
            }

            // 表单提交时显示"正在输入"效果
            chatForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const userInput = chatForm.user_input.value.trim();
                if (!userInput) return;
                
                // 禁用表单
                chatForm.querySelector('input[type="submit"]').disabled = true;
                
                // 显示用户消息
                const userMessageDiv = document.createElement('div');
                userMessageDiv.className = 'message user';
                
                const userHeader = document.createElement('div');
                userHeader.className = 'message-header';
                userHeader.innerHTML = '用户 <i class="fas fa-user"></i>';
                
                const userContent = document.createElement('div');
                userContent.className = 'message-content';
                
                // 用户消息也使用Markdown渲染（可选）
                userContent.innerHTML = safeRenderMarkdown(userInput);
                
                const userTimestamp = document.createElement('div');
                userTimestamp.className = 'timestamp';
                userTimestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                userMessageDiv.appendChild(userHeader);
                userMessageDiv.appendChild(userContent);
                userMessageDiv.appendChild(userTimestamp);
                chatBox.appendChild(userMessageDiv);
                scrollToBottom();
                
                // 显示正在输入指示器
                typingIndicator.style.display = 'block';
                scrollToBottom();
                
                // 清空输入框
                chatForm.user_input.value = '';
                
                // 创建机器人消息容器
                const botContent = createBotMessage();
                
                // 使用EventSource获取流式响应
                if (eventSource) eventSource.close();
                
                eventSource = new EventSource(`/stream?q=${encodeURIComponent(userInput)}`);
                let responseText = '';
                let lastRenderTime = Date.now();
                
                eventSource.onmessage = function(event) {
                    if (event.data === '[DONE]') {
                        eventSource.close();
                        typingIndicator.style.display = 'none';
                        chatForm.querySelector('input[type="submit"]').disabled = false;
                        
                        // 保存完整响应到会话
                        fetch('/save_response', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                user_input: userInput,
                                bot_response: responseText  // 保存原始Markdown内容
                            })
                        });
                    } else {
                        const data = JSON.parse(event.data);
                        if (data.content) {
                            responseText += data.content;
                            
                            // 增量渲染优化：每150ms渲染一次以提高性能
                            const now = Date.now();
                            if (now - lastRenderTime > 150) {
                                botContent.innerHTML = safeRenderMarkdown(responseText);
                                lastRenderTime = now;
                                scrollToBottom();
                            }
                        }
                    }
                };
                
                // 最后确保渲染最终内容
                eventSource.addEventListener('end', function() {
                    botContent.innerHTML = safeRenderMarkdown(responseText);
                    scrollToBottom();
                });
                
                eventSource.onerror = function() {
                    eventSource.close();
                    typingIndicator.style.display = 'none';
                    chatForm.querySelector('input[type="submit"]').disabled = false;
                    if (!responseText) {
                        botContent.textContent = "抱歉，响应生成出错，请重试。";
                    }
                };
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
            
            // 初始化滚动到底部
            scrollToBottom();
        });
    </script>
</body>
</html>
'''


def chat_with_model_stream(user_input):
    """流式调用AI模型"""
    client = ZhipuAI(api_key=model_conf.zhipu_ak)
    response = client.chat.completions.create(
        model=model_conf.model_name,
        messages=[{"role": "user", "content": user_input}],
        stream=True
    )

    for chunk in response:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content


# app.py (修改后的流式响应部分)
@app.route('/stream')
def stream_response():
    """流式响应路由 - 适配统一的事件格式"""
    user_input = request.args.get('q', '')
    def generate():
        try:
            # 创建流式响应
            for event in main.ai_assistant_stream(user_input):
                # 统一使用content字段传输
                event_data = {
                    "type": event["type"],
                    "content": event["data"]
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            # 发送结束标志
            yield "data: [DONE]\n\n"
        except Exception as e:
            # 错误处理
            yield f"data: {json.dumps({'type': 'error', 'content': f'错误: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/save_response', methods=['POST'])
def save_response():
    """保存完整响应到session"""
    data = request.json
    user_input = data.get('user_input', '')
    bot_response = data.get('bot_response', '')
    if 'chat_log' not in session:
        session['chat_log'] = []
    current_time = datetime.now().strftime('%H:%M')
    # 添加用户消息
    session['chat_log'].append({
        "role": "user",
        "text": user_input,
        "time": current_time
    })
    # 添加AI响应
    session['chat_log'].append({
        "role": "bot",
        "text": bot_response,
        "time": current_time
    })
    session.modified = True
    return jsonify({"status": "success"})
@app.route('/', methods=['GET', 'POST'])
def chat():
    """主聊天路由"""
    if 'chat_log' not in session:
        session['chat_log'] = []

    return render_template_string(CHAT_TEMPLATE)


@app.route('/clear', methods=['POST'])
def clear_chat():
    """清空聊天记录"""
    session['chat_log'] = []
    session.modified = True
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=52177, debug=True)