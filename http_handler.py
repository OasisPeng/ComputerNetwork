import os
import mimetypes
import base64
import urllib.parse
import cgi
from io import BytesIO

from chunked_transfer import ChunkedTransfer
from file_manager import FileManager
from session_manager import SessionManager
from chunked_transfer import ChunkedTransfer
# 用于存储用户的用户名和密码信息
# 实际项目中应该使用更安全的存储方式，例如数据库
user_credentials = {"client1": "123", "client2": "123", "client3": "123"}

# 创建 SessionManager 实例
session_manager = SessionManager()


def handle_http_request(http_request):
    # 解析HTTP请求
    request_lines = http_request.split("\r\n")
    request_method, request_path, _ = request_lines[0].split(" ")
    # 检查是否包含 Authorization 头部信息
    authorization_header = get_authorization_header(request_lines)
    # 获取请求的 Cookie 头部信息
    cookie_header = get_cookie_header(request_lines)

    # 获取请求体
    if authorization_header:
        # 解码 Authorization 头部信息
        decoded_info = decode_authorization_header(authorization_header)
        # 检查用户提供的授权信息是否有效
        if validate_credentials(decoded_info):
            # 用户提供的授权信息有效，可以继续处理请求
            # 获取用户的会话信息
            username, _ = decoded_info.split(":")
            session_info = session_manager.get_session_info(username)

            # 获取请求中的 Cookie
            session_cookie = get_cookie_value(cookie_header, "session-id")

            if session_info and session_cookie and session_manager.is_session_valid(username, session_cookie):
                # 用户有有效的会话信息且请求中包含有效的 session-id Cookie
                if request_method == "GET":
                    return handle_get_request(request_path)
                elif request_method == "HEAD":
                    return handle_head_request(request_path)
                elif request_method == "POST":
                    # 获取请求主体
                    return handle_post_request(request_path, decoded_info, http_request)
                else:
                    return generate_response(405, "Method Not Allowed")
            elif session_info and session_cookie:  # 请求中的 session-id 无效或过期
                return generate_response(401, "Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                           'Required"'})
            else:
                # 用户没有有效的会话信息，生成新的 session-id
                new_session_id = session_manager.create_session(username)
                # 返回响应时设置 Set-Cookie 头部，包含新的 session-id
                headers = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
                return generate_response(200, "OK", headers=headers)
        else:
            # 用户提供的授权信息无效，返回 401 Unauthorized
            return generate_response(401, "Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                       'Required"'})

    else:
        # 未提供 Authorization 头部信息，返回 401 Unauthorized
        return generate_response(401, "Unauthorized", headers={"WWW-Authenticate": 'Basic realm="Authorization '

                                                                                   'Required"'})


def get_cookie_value(cookie_header, cookie_name):
    # 从 Cookie 头部信息中获取指定名称的 Cookie 值
    if cookie_header:
        cookies = cookie_header.split(";")
        for cookie in cookies:
            name, value = cookie.split("=")
            if name.strip() == cookie_name:
                return value.strip()
    return None


def get_cookie_header(request_lines):
    # 从请求头部获取 Cookie 头部信息
    for line in request_lines[1:]:
        if line.startswith("Cookie:"):
            return line[len("Cookie:"):].strip()
    return None


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


def get_request_body(request_lines):
    # 查找空行，之后的内容为请求主体
    empty_line_index = request_lines.index("")
    request_body = "\r\n".join(request_lines[empty_line_index + 1:])
    return request_body


def handle_get_request(request_path):
    # 检查路径并执行相应的操作
    try:
        access_path = urllib.parse.unquote(request_path[1:])
    except UnicodeDecodeError:
        return generate_response(400, "Bad Request")

    # 初始化文件管理器
    file_manager = FileManager(base_path="./data")

    # 如果是目录，则列出目录内容
    if file_manager.is_directory(access_path):
        files = file_manager.list_directory(access_path)
        if files is not None:
            response_body = generate_directory_listing(access_path, files)
            return generate_response(200, "OK", response_body)
        else:
            return generate_response(404, "Not Found")

    # 如果是文件，则使用分块传输
    elif file_manager.is_file(access_path):
        # 确定文件路径
        file_path = file_manager.get_full_path(access_path)

        # 使用分块传输
        chunked_transfer = ChunkedTransfer(file_path)
        if chunked_transfer is not None:
            headers = {
                "Transfer-Encoding": "chunked",
                "Content-Type": "application/octet-stream",  # 或其他合适的 MIME 类型
            }
            response = generate_response(200, "OK", headers=headers)

            # 对于分块传输，您需要发送每个块的大小，然后是块内容，最后是块结束标志
            for chunk in chunked_transfer:
                if chunk is None:
                    return generate_response(404, "Not Found")
                response += f"{len(chunk):X}\r\n"
                response += chunk.decode('latin-1')  # 用 latin-1 解码二进制数据
                response += "\r\n"
            response += "0\r\n\r\n"  # 发送结束块
            return response
        else:
            return generate_response(404, "Not Found")

    else:
        # 如果既不是目录也不是文件，则返回 404
        return generate_response(404, "Not Found")
        # # 请求路径为文件，返回文件内容
        # file_content = file_manager.read_file(access_path)
        #
        # if file_content is not None:
        #     # 获取文件的 MIME 类型
        #     mime_type, _ = mimetypes.guess_type(access_path)
        #
        #     response_headers = {
        #         "Content-Type": mime_type,
        #         "Content-Disposition": f"attachment; filename={os.path.basename(access_path)}"
        #     }
        #     return generate_response(200, "OK", file_content, response_headers)
        # else:
        #     # 文件不存在，返回 404 Not Found
        #     return generate_response(404, "Not Found")


def handle_head_request(request_path):
    # 处理HEAD请求
    # 返回HTTP头信息，但不返回实际内容
    return generate_response(200, "OK")


def handle_post_request(request_path, decoded_info, http_request):
    # 处理POST请求
    # 根据 request_path 处理文件上传或删除等操作
    # 这里需要根据你的项目具体需求进行处理

    # 检查是否是上传请求
    if request_path.startswith("/upload"):
        return handle_upload_request(request_path, decoded_info, http_request)
    elif request_path.startswith("/delete"):
        return handle_delete_request(request_path, decoded_info)
    else:
        # 如果不是上传请求，返回 405 Method Not Allowed
        return generate_response(405, "Method Not Allowed")


def handle_upload_request(request_path, decoded_info, http_request):
    # 获取上传目录路径
    upload_path = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query).get("path", [""])[0]

    # 获取用户权限信息
    username, _ = decoded_info.split(":")

    # 检查用户是否有权限上传到目标目录
    if username != upload_path.strip("/"):
        return generate_response(403, "Forbidden")

    # 构建完整的上传目录路径
    if upload_path.startswith('/'):  # 防止upload_path是绝对路径
        upload_path = upload_path[1:]
    full_upload_path = os.path.join("./data", upload_path)
    # 检查目录是否存在，不存在则返回 404 Not Found
    if not os.path.exists(full_upload_path):
        return generate_response(404, "Not Found")

    # 解析请求主体
    body_start = http_request.find('\r\n\r\n') + 4
    request_body = http_request[body_start:]

    # 解析 Content-Type 中的 boundary 值
    content_type_start = http_request.find('Content-Type:') + len('Content-Type:')
    content_type_end = http_request.find('\r\n', content_type_start)
    content_type_line = http_request[content_type_start:content_type_end]
    boundary_start = content_type_line.find('boundary=') + len('boundary=')
    boundary = content_type_line[boundary_start:].strip()

    # 解析multipart/form-data格式的请求主体
    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': f'multipart/form-data; boundary={boundary}'}
    input_stream = BytesIO(request_body.encode())
    form = cgi.FieldStorage(fp=input_stream, environ=environ)

    # 获取上传的文件内容
    uploaded_file = form['file']
    file_content = uploaded_file.file.read()

    # 处理文件上传逻辑，调用 FileManager 类的 upload_file 方法
    file_manager = FileManager(base_path="./data")
    file_manager.upload_file(upload_path, file_content)

    # 返回上传成功的响应
    return generate_response(200, "OK", "File uploaded successfully")


def handle_delete_request(request_path, decoded_info):
    # 获取删除文件的路径
    delete_path = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query).get("path", [""])[0]

    # 获取用户权限信息
    username, _ = decoded_info.split(":")
    # 检查用户是否有权限删除目标文件
    if username != delete_path.strip("/").split("/")[0]:
        return generate_response(403, "Forbidden")

    # 构建完整的删除文件路径
    if delete_path.startswith('/'):  # 防止delete_path是绝对路径
        delete_path = delete_path[1:]
    full_delete_path = os.path.join("./data", delete_path)

    # 检查文件是否存在，不存在则返回 404 Not Found
    if not os.path.exists(full_delete_path):
        return generate_response(404, "Not Found")

    # 删除文件，调用 FileManager 类的 delete_file 方法
    file_manager = FileManager(base_path="./data")
    file_manager.delete_file(delete_path)

    # 返回删除成功的响应
    return generate_response(200, "OK", "File deleted successfully")


def generate_response(status_code, reason_phrase, body=None, headers=None):
    # 生成HTTP响应
    response = f"HTTP/1.1 {status_code} {reason_phrase}\r\n"

    if headers:
        for key, value in headers.items():
            response += f"{key}: {value}\r\n"

    if body:
        response += f"Connection: keep-alive\r\nAccess-Control-Allow-Origin: http://localhost:8080\r\nContent-Length: {len(body)}\r\n\r\n{body}\r\n"
    else:
        response += "\r\n"

    return response


def generate_directory_listing(current_path, files):
    full_path = os.path.join('./data', current_path)
    # 生成目录列表的HTML页面
    listing = f"<html><body><h1>Directory Listing: {full_path}</h1><ul>"

    # 添加链接到当前目录
    listing += f'<li><a href="/{current_path}">/</a></li>'

    # 添加链接到上一级目录
    parent_path = os.path.join(current_path, "..")
    listing += f'<li><a href="/{parent_path}">../</a></li>'  # 使用斜杠 / 开始路径，表示从网站的根目录开始。

    for file in files:
        file_path = os.path.join(current_path, file)
        listing += f'<li><a href="{file_path}">{file}</a></li>'

    listing += "</ul></body></html>"
    return listing


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
