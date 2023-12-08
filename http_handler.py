import os
import mimetypes
import base64
import urllib.parse
from file_manager import FileManager

# 用于存储用户的用户名和密码信息
# 实际项目中应该使用更安全的存储方式，例如数据库
user_credentials = {"username": "password"}


def handle_http_request(http_request):
    # 解析HTTP请求
    request_lines = http_request.split("\r\n")
    request_method, request_path, _ = request_lines[0].split(" ")
    # 检查是否包含 Authorization 头部信息
    authorization_header = get_authorization_header(request_lines)

    if authorization_header:
        # 解码 Authorization 头部信息
        decoded_info = decode_authorization_header(authorization_header)
        # 检查用户提供的授权信息是否有效
        if validate_credentials(decoded_info):
            # 用户提供的授权信息有效，可以继续处理请求
            if request_method == "GET":
                return handle_get_request(request_path)
            elif request_method == "HEAD":
                return handle_head_request(request_path)
            elif request_method == "POST":
                return handle_post_request(request_path)
            else:
                return generate_response(405, "Method Not Allowed")
        else:
            # 用户提供的授权信息无效，返回 401 Unauthorized
            return generate_response(401, "Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                       'Required"'})

    else:
        # 未提供 Authorization 头部信息，返回 401 Unauthorized
        return generate_response(401, "Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                   'Required"'})


def get_authorization_header(request_lines):
    # 从请求头部获取 Authorization 头部信息
    for line in request_lines[1:]:
        if line.startswith("Authorization:"):
            return line[len("Authorization:"):].strip()
    return None


def decode_authorization_header(authorization_header):
    # 解码 Authorization 头部信息
    encoded_info = authorization_header.split(" ")[1]
    decoded_info = base64.b64decode(encoded_info).decode('utf-8')
    return decoded_info


def validate_credentials(decoded_info):
    # 验证用户提供的用户名和密码是否有效
    # 实际项目中应该从安全的存储中获取用户信息进行验证
    username, password = decoded_info.split(":")
    return user_credentials.get(username) == password


def handle_get_request(request_path):
    # 处理GET请求
    # 根据 request_path 处理文件查看或下载等操作
    # 解析请求路径
    try:
        access_path = urllib.parse.unquote(request_path[1:])
    except UnicodeDecodeError:
        # 请求路径不是有效的UTF-8编码，返回 400 Bad Request
        return generate_response(400, "Bad Request")
    # 初始化文件管理器
    file_manager = FileManager(base_path="./data")
    # 列出目录
    files = file_manager.list_directory(access_path)
    if files is not None:
        # 请求路径为目录，返回文件列表
        response_body = generate_directory_listing(access_path, files)
        return generate_response(200, "OK", response_body)
    else:
        # 请求路径为文件，返回文件内容
        file_content = file_manager.read_file(access_path)

        if file_content is not None:
            # 获取文件的 MIME 类型
            mime_type, _ = mimetypes.guess_type(access_path)
            # 将二进制文件内容以 UTF-8 编码
            content_text = file_content.decode('utf-8')
            response_headers = {
                "Content-Type": mime_type,
                "Content-Disposition": f"attachment; filename={os.path.basename(access_path)}"
            }
            return generate_response(200, "OK", content_text, response_headers)
        else:
            # 文件不存在，返回 404 Not Found
            return generate_response(404, "Not Found")


def handle_head_request(request_path):
    # 处理HEAD请求
    # 返回HTTP头信息，但不返回实际内容
    return generate_response(200, "OK")


def handle_post_request(request_path):
    # 处理POST请求
    # 根据 request_path 处理文件上传或删除等操作
    # 这里需要根据你的项目具体需求进行处理

    # 示例：返回一个简单的成功信息
    response_body = "Post request received successfully!"
    return generate_response(200, "OK", response_body)


def generate_response(status_code, reason_phrase, body=None, headers=None):
    # 生成HTTP响应
    response = f"HTTP/1.1 {status_code} {reason_phrase}\r\n"

    if headers:
        for key, value in headers.items():
            response += f"{key}: {value}\r\n"

    if body:
        response += f"Access-Control-Allow-Origin: http://localhost:8080\r\nContent-Length: {len(body)}\r\n\r\n{body}\r\n"
    else:
        response += "\r\n"

    return response


def generate_directory_listing(current_path, files):
    full_path = os.path.join('./data', current_path)
    # 生成目录列表的HTML页面
    listing = f"<html><body><h1>Directory Listing: {full_path}</h1><ul>"
    # 添加上级目录链接
    parent_dir = os.path.dirname(full_path)
    if parent_dir:
        parent_link = f'<li><a href="../">../</a></li>'
        listing += parent_link

    for file in files:  # file是文件名
        file_path = os.path.join(current_path, file)
        listing += f'<li><a href="{file_path}">{file}</a></li>'

    listing += "</ul></body></html>"
    return listing


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
