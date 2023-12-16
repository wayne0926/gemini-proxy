# 导入Flask、request模块
from flask import Flask, request
import requests
import base64

# 创建Flask应用
app = Flask(__name__)

# 定义生成内容的模型的API地址和请求头信息
url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": "YOUR_TOKEN",
}

# 用于验证令牌的密钥（替换为您的密钥）
SECRET_KEY = "YOUR_SECRET_KEY"

# 创建会话对象，用于发送HTTP请求并保持连接池
session = requests.Session()

# 验证令牌的函数
def verify_token(token):
    # 在此处实现令牌验证逻辑
    return token == SECRET_KEY

# 定义根路由，接受GET和POST请求
@app.route('/', methods=['GET', 'POST'])
def generate_content():
    try:
        # 从查询参数或请求体中获取令牌
        token = request.args.get('token') or request.json.get('token')

        # 验证令牌
        if not token or not verify_token(token):
            return "Unauthorized", 401

        # 从请求体或URL参数中提取文本
        text = request.json.get('text') or request.args.get('text', '')

        # 准备用于POST请求的数据
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": text}
                    ]
                }
            ]
        }

        # 使用连接池发送带有数据的POST请求
        with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
            result = response.json()
            content_text = result.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text")

            # 对内容进行Base64编码
            encoded_content = base64.b64encode(content_text.encode()).decode()

            return encoded_content

    except Exception as e:
        # 记录异常并返回错误响应
        app.logger.error(f"Error processing request: {e}")
        return "Internal Server Error", 500

# 如果是主程序，则运行Flask应用在指定的主机和端口上
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
