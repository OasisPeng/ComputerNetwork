import os
import mimetypes
import base64
import urllib.parse
import uuid
import encryption
from uuid import uuid4

from HttpRequest import HttpRequest
from HttpResponse import HttpResponse
# from io import BytesIO

# from chunked_transfer import ChunkedTransfer
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
    request = HttpRequest(http_request)
    # 获取请求中的 Cookie
    session_cookie = get_cookie_value(request.cookie_header, "session-id")

    # 第一次登录，没有cookie
    if request.authorization_header and session_cookie is None:
        # 解码 Authorization 头部信息
        decoded_info = decode_authorization_header(request.authorization_header)
        # 获取用户的会话信息
        username, _ = decoded_info.split(":")

        if validate_credentials(decoded_info):
            # 用户没有有效的会话信息，生成新的 session-id
            new_session_id = session_manager.create_session(username)
            # # 返回响应时设置 Set-Cookie 头部，包含新的 session-id
            headers = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
            if request.method == "GET":
                return handle_get_request(request.path, request.request_lines, new_session_id)
            elif request.method == "HEAD":
                return handle_head_request(request.path, new_session_id)
            elif request.method == "POST":
                # 获取请求主体
                return handle_post_request(request.path, username, http_request, new_session_id)
            else:
                return HttpResponse(405, "Method Not Allowed", '', headers).response
        else:
            return HttpResponse(401, "Unauthorized", '', headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                      'Required"'}).response
    # cookie登录
    elif session_manager.is_session_valid(session_cookie):
        username = session_manager.get_username_by_session_id(session_cookie)
        # 用户有有效的会话信息且请求中包含有效的 session-id Cookie
        if request.method == "GET":
            return handle_get_request(request.path, request.request_lines, None)
        elif request.method == "HEAD":
            return handle_head_request(request.path, None)
        elif request.method == "POST":
            # 获取请求主体
            return handle_post_request(request.path, username, http_request, None)
        else:
            return HttpResponse(405, "Method Not Allowed", '', None).response
    # cookie无效或过期
    else:
        return HttpResponse(401, "Unauthorized", login_page(),
                            headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                         'Required"'}).response


def get_cookie_value(cookie_header, cookie_name):
    # 从 Cookie 头部信息中获取指定名称的 Cookie 值
    if cookie_header:
        cookies = cookie_header.split(";")
        for cookie in cookies:
            name, value = cookie.split("=")
            if name.strip() == cookie_name:
                return value.strip()
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


def handle_get_request(request_path, request_lines, new_session_id):
    if new_session_id is not None:
        head = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
    else:
        head = None

    if request_path.startswith("/upload") or request_path.startswith("/delete"):
        return HttpResponse(405, "Method Not Allowed", '', head).response
    elif 'get_public_key' in request_path:
        # 返回服务器的公钥
        return HttpResponse(200, "OK", str(encryption.server_public_key), head).response + str(
            encryption.server_public_key) + '\r\n'
        # 检查路径并执行相应的操作
    try:
        access_path = urllib.parse.unquote(urllib.parse.urlparse(request_path).path)[1:]
    except UnicodeDecodeError:
        return HttpResponse(400, "Bad Request", '', head).response

    # 初始化文件管理器
    file_manager = FileManager(base_path="./data")

    # 如果是目录，则列出目录内容
    if file_manager.is_directory(access_path):
        # Check for the SUSTech-HTTP query parameter
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
        sustech_http_param = query_params.get("SUSTech-HTTP", ["0"])[0]

        # List items in the directory
        if sustech_http_param == "1":
            items = file_manager.list_directory(access_path)
            print(items + '\r\n' + str(items))
            return HttpResponse(200, "OK", str(items), head).response
        elif query_params == {} or sustech_http_param == '0':  # 没有参数
            # Show HTML page with file tree
            response_body = generate_directory_listing(access_path, file_manager.list_directory(access_path))
            return HttpResponse(200, "OK", response_body, head).response
        else:
            return HttpResponse(400, "Bad Request", '', head).response

    # 如果是文件，传输文件内容
    elif file_manager.is_file(access_path):
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
        chunk_param = query_params.get("chunked", ["0"])[0]
        # 检查是否有 Range 请求头
        range_header = get_range_header(request_lines)
        if range_header:
            return handle_range_request(access_path, range_header)
        else:
            # 确定文件路径
            file_path = file_manager.get_full_path(access_path)

            if chunk_param == "1":
                # Use chunked transfer
                chunked_transfer = ChunkedTransfer(file_path).read_chunks()
                if chunked_transfer is not None:
                    headers = {
                        "Transfer-Encoding": "chunked",
                        "Content-Type": "application/octet-stream",  # Or other appropriate MIME type
                    }
                    response = HttpResponse(200, "OK", '', headers=headers).response

                    # Send each chunk's size followed by the chunk content, and end with an empty chunk
                    for chunk in chunked_transfer:
                        if chunk:
                            response += f"{len(chunk):X}\r\n"
                            response += chunk.decode('utf-8', 'ignore')  # 将字节块转换为字符串
                            response += "\r\n"
                    response += "0\r\n\r\n"  # 结束分块传输

                    return response
                else:
                    return HttpResponse(404, "Not Found", '', head).response

            else:
                # 直接传输
                # 请求路径为文件，返回文件内容
                file_content = file_manager.read_file(access_path)

                if file_content is not None:
                    # # 获取文件的 MIME 类型
                    mime_type, _ = mimetypes.guess_type(access_path)

                    # 如果是文本文件，则直接返回内容
                    if mime_type and mime_type.startswith('text'):
                        if new_session_id:
                            response_headers = {
                                "Content-Type": mime_type,
                                "Content-Disposition": f"attachment; filename={os.path.basename(access_path)}",
                                "Set-Cookie": f"session-id={new_session_id}; HttpOnly"
                            }
                        else:
                            response_headers = {
                                "Content-Type": mime_type,
                                "Content-Disposition": f"attachment; filename={os.path.basename(access_path)}"
                            }
                        return HttpResponse(200, "OK", file_content.decode(), response_headers).response
                    else:
                        # 对于其他类型的文件，可以使用base64编码并以数据URL的形式返回，以便在前端直接显示
                        base64_content = base64.b64encode(file_content).decode('utf-8')
                        data_url = f"data:{mime_type};base64,{base64_content}"
                        # 在HTML页面中通过img标签等元素直接显示，并提供下载链接
                        response_body = f"<html><body><img src='{data_url}' /><br><a href='{data_url}' download>Download</a></body></html>"
                        if new_session_id:
                            response_headers = {
                                "Content-Type": "text/html",
                                "Set-Cookie": f"session-id={new_session_id}; HttpOnly"
                            }
                        else:
                            response_headers = {
                                "Content-Type": "text/html",
                            }
                        return HttpResponse(200, "OK", response_body, response_headers).response
                else:
                    # 文件不存在，返回 404 Not Found
                    return HttpResponse(404, "Not Found", '', head).response
    else:
        # 如果既不是目录也不是文件，则返回 404
        return HttpResponse(404, "Not Found", '', head).response


def handle_head_request(request_path, new_session_id):
    if new_session_id is not None:
        head = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
    else:
        head = None

    access_path = urllib.parse.unquote(urllib.parse.urlparse(request_path).path)[1:]
    if access_path != '' and (request_path.startswith("/upload") or request_path.startswith("/delete") or FileManager(
            base_path="./data").is_file(access_path) or FileManager(base_path="./data").is_directory(access_path)):
        return HttpResponse(405, "Method Not Allowed", '', head).response
    # 处理HEAD请求
    # 返回HTTP头信息，但不返回实际内容
    return HttpResponse(200, "OK", '', head).response


def handle_post_request(request_path, username, http_request, new_session_id):
    if new_session_id is not None:
        head = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
    else:
        head = None
    # 处理POST请求
    # 根据 request_path 处理文件上传或删除等操作
    # 这里需要根据你的项目具体需求进行处理

    # 检查是否是上传请求
    if request_path.startswith("/upload"):
        return handle_upload_request(request_path, username, http_request, head)
    elif request_path.startswith("/delete"):
        return handle_delete_request(request_path, username, head)
    else:
        # 如果不是上传请求，返回 405 Method Not Allowed
        return HttpResponse(405, "Method Not Allowed", '', head).response


def handle_upload_request(request_path, username, http_request, head):
    # 获取上传目录路径
    query_param = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
    if query_param == {}:
        return HttpResponse(400, "Bad Request", '', head).response
    upload_path = query_param.get("path", None)[0]
    if upload_path is None:
        return HttpResponse(400, "Bad Request", '', head).response

    # 检查用户是否有权限上传到目标目录
    if username != upload_path.strip("/"):
        return HttpResponse(403, "Forbidden", '', head).response

    # 构建完整的上传目录路径
    if upload_path.startswith('/'):  # 防止upload_path是绝对路径
        upload_path = upload_path[1:]
    full_upload_path = os.path.join("./data", upload_path)
    # 检查目录是否存在，不存在则返回 404 Not Found
    if not os.path.exists(full_upload_path):
        return HttpResponse(404, "Not Found", '', head).response

    # 解析请求主体
    body_start = http_request.find('\r\n\r\n') + 4
    request_body = http_request[body_start:]

    # 通过表单上传包含二进制数据的内容
    # 解析 Content-Type 中的 boundary 值
    content_type_start = http_request.find('Content-Type:') + len('Content-Type:')
    content_type_end = http_request.find('\r\n', content_type_start)
    content_type_line = http_request[content_type_start:content_type_end]
    boundary_start = content_type_line.find('boundary=') + len('boundary=')
    boundary = content_type_line[boundary_start:].strip()

    # 解析multipart/form-data格式的请求主体
    form_data = parse_multipart_body(request_body, boundary)

    # 获取上传的文件内容
    uploaded_file = form_data.get('file')
    if uploaded_file:
        filename = uploaded_file['filename']
        file_content = uploaded_file['content'].encode('utf-8')

        # 处理文件上传逻辑，调用 FileManager 类的 upload_file 方法
        file_manager = FileManager(base_path="./data")
        file_manager.upload_file(upload_path, file_content, filename)

    # 返回上传成功的响应
    return HttpResponse(200, "OK", "File uploaded successfully", head).response


def handle_delete_request(request_path, username, head):
    # 获取删除文件的路径

    query_param = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
    if query_param == {}:
        return HttpResponse(400, "Bad Request", '', head).response
    delete_path = query_param.get("path", None)[0]
    if delete_path is None:
        return HttpResponse(400, "Bad Request", '', head).response

    # 检查用户是否有权限删除目标文件
    if username != delete_path.strip("/").split("/")[0]:
        return HttpResponse(403, "Forbidden", '', head).response

    # 构建完整的删除文件路径
    if delete_path.startswith('/'):  # 防止delete_path是绝对路径
        delete_path = delete_path[1:]
    full_delete_path = os.path.join("./data", delete_path)

    # 检查文件是否存在，不存在则返回 404 Not Found
    if not os.path.exists(full_delete_path):
        return HttpResponse(404, "Not Found", '', head).response

    # 删除文件，调用 FileManager 类的 delete_file 方法
    file_manager = FileManager(base_path="./data")
    file_manager.delete_file(delete_path)

    # 返回删除成功的响应
    return HttpResponse(200, "OK", "File deleted successfully", head).response


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
        listing += f'<li><a href="/{file_path}">{file}</a></li>'

    listing += "</ul></body></html>"
    return listing


def handle_range_request(access_path, range_header):
    file_manager = FileManager(base_path="./data")

    # 解析范围请求，可能有多个范围
    ranges = parse_range_header(range_header)
    file_path = file_manager.get_full_path(access_path)
    file_size = os.path.getsize(file_path)

    boundary = uuid.uuid4().hex  # 生成唯一边界字符串
    content_parts = []

    for start_byte, end_byte in ranges:
        if start_byte is None or end_byte is None or start_byte > end_byte or end_byte >= file_size:
            continue  # 跳过无效范围

        with open(file_path, 'rb') as file:
            file.seek(start_byte)
            content = file.read(end_byte - start_byte + 1)

        content_range_header = f"bytes {start_byte}-{end_byte}/{file_size}"
        part_headers = (
            f"--{boundary}\r\n"
            "Content-Type: application/octet-stream\r\n"
            f"Content-Range: {content_range_header}\r\n\r\n"
        )
        content_parts.append(part_headers.encode() + content)

    content_parts.append(f"--{boundary}--\r\n".encode())
    multipart_content = b''.join(content_parts)
    headers = {
        "Content-Type": f"multipart/byteranges; boundary={boundary}",
        "Content-Length": str(len(multipart_content))
    }

    return HttpResponse(206, "Partial Content", content_parts, headers).generate_multipart_respond()


def parse_range_header(range_header):
    # 从头部解析多个范围
    ranges = []
    if range_header:
        _, range_values = range_header.split('=')
        for range_value in range_values.split(','):
            start_str, end_str = range_value.split('-')
            start_byte = int(start_str) if start_str else None
            end_byte = int(end_str) if end_str else None
            ranges.append((start_byte, end_byte))
    return ranges


def get_range_header(request_lines):
    # 从请求头部获取Range头部信息
    for line in request_lines:
        if line.startswith("Range:"):
            return line[len("Range:"):].strip()
    return None


def parse_multipart_body(request_body, boundary):
    parts = request_body.split(f'--{boundary}')
    form_data = {}

    for part in parts:
        if not part or part == '--\r\n':
            continue

        headers_end = part.find('\r\n\r\n') + 4
        headers = part[:headers_end].strip().split('\r\n')
        content = part[headers_end:]

        # Extracting content disposition to identify form fields and files
        content_disposition = [header for header in headers if header.startswith('Content-Disposition')][0]
        disposition, name, filename = parse_content_disposition(content_disposition)

        if filename:  # File field
            form_data[name] = {'filename': filename, 'content': content}
        else:  # Regular form field
            form_data[name] = content

    return form_data


def parse_content_disposition(content_disposition):
    parts = content_disposition.split(';')
    disposition = parts[0].strip()
    name = None
    filename = None

    for part in parts[1:]:
        key, value = part.strip().split('=')
        if key == 'name':
            name = urllib.parse.unquote(value.strip('\"'))
        elif key == 'filename':
            filename = urllib.parse.unquote(value.strip('\"'))

    return disposition, name, filename


def login_page():
    return """
    <html>
    <head>
        <title>Login Page</title>
    </head>
    <body>
        <h2>Login</h2>
        <form method="post" action="/login">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
