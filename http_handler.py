import os
import mimetypes
import base64
import urllib.parse
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

    # 获取请求体
    if request.authorization_header:
        # 解码 Authorization 头部信息
        decoded_info = decode_authorization_header(request.authorization_header)
        # 检查用户提供的授权信息是否有效
        if validate_credentials(decoded_info):
            # 用户提供的授权信息有效，可以继续处理请求
            # 获取用户的会话信息
            username, _ = decoded_info.split(":")
            session_info = session_manager.get_session_info(username)

            # 获取请求中的 Cookie
            session_cookie = get_cookie_value(request.cookie_header, "session-id")

            if session_info and session_cookie and session_manager.is_session_valid(username, session_cookie):
                # 用户有有效的会话信息且请求中包含有效的 session-id Cookie
                if request.method == "GET":
                    return handle_get_request(request.path, request.request_lines, None)
                elif request.method == "HEAD":
                    return handle_head_request(request.path, None)
                elif request.method == "POST":
                    # 获取请求主体
                    return handle_post_request(request.path, decoded_info, http_request, None)
                else:
                    return HttpResponse(405, "Method Not Allowed", '', None).response
            elif session_info and session_cookie:  # 请求中的 session-id 无效或过期
                return HttpResponse(401, "Unauthorized", '', headers={"WWW-Authenticate": 'Basic '
                                                                                          'realm="Authorization'
                                                                                          'Required"'}).response
            else:
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
                    return handle_post_request(request.path, decoded_info, http_request, new_session_id)
                else:
                    return HttpResponse(405, "Method Not Allowed", '', headers).response
        else:
            # 用户提供的授权信息无效，返回 401 Unauthorized
            return HttpResponse(401, "Unauthorized", '', headers={"WWW-Authenticate": 'Basic realm="Authorization '
                                                                                      'Required"'}).response

    else:
        # 未提供 Authorization 头部信息，返回 401 Unauthorized
        return HttpResponse(401, "Unauthorized", '', headers={"WWW-Authenticate": 'Basic realm="Authorization '

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
            if "," in range_header:  # 多重范围请求
                return handle_multiple_range_request(access_path, range_header)
            else:  # 单一范围请求
                return handle_range_request(access_path, range_header)
        else:
            # 确定文件路径
            file_path = file_manager.get_full_path(access_path)

            if chunk_param == 1:
                # 使用分块传输
                chunked_transfer = ChunkedTransfer(file_path)
                if chunked_transfer is not None:
                    headers = {
                        "Transfer-Encoding": "chunked",
                        "Content-Type": "application/octet-stream",  # 或其他合适的 MIME 类型
                    }
                    response = HttpResponse(200, "OK", '', headers=headers).response

                    # 对于分块传输，您需要发送每个块的大小，然后是块内容，最后是块结束标志
                    for chunk in chunked_transfer:
                        if chunk is None:
                            return HttpResponse(404, "Not Found", '', head).response
                        response += f"{len(chunk):X}\r\n"
                        response += chunk.decode('latin-1')  # 用 latin-1 解码二进制数据
                        response += "\r\n"
                    response += "0\r\n\r\n"  # 发送结束块
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
                                "Content-Type":  mime_type,
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


def handle_post_request(request_path, decoded_info, http_request, new_session_id):
    if new_session_id is not None:
        head = {"Set-Cookie": f"session-id={new_session_id}; HttpOnly"}
    else:
        head = None
    # 处理POST请求
    # 根据 request_path 处理文件上传或删除等操作
    # 这里需要根据你的项目具体需求进行处理

    # 检查是否是上传请求
    if request_path.startswith("/upload"):
        return handle_upload_request(request_path, decoded_info, http_request, head)
    elif request_path.startswith("/delete"):
        return handle_delete_request(request_path, decoded_info, head)
    else:
        # 如果不是上传请求，返回 405 Method Not Allowed
        return HttpResponse(405, "Method Not Allowed", '', head).response


def handle_upload_request(request_path, decoded_info, http_request, head):
    # 获取上传目录路径
    query_param = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
    if query_param == {}:
        return HttpResponse(400, "Bad Request", '', head).response
    upload_path = query_param.get("path", None)[0]
    if upload_path is None:
        return HttpResponse(400, "Bad Request", '', head).response
    # 获取用户权限信息
    username, _ = decoded_info.split(":")

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


def handle_delete_request(request_path, decoded_info, head):
    # 获取删除文件的路径

    query_param = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
    if query_param == {}:
        return HttpResponse(400, "Bad Request", '', head).response
    delete_path = query_param.get("path", None)[0]
    if delete_path is None:
        return HttpResponse(400, "Bad Request", '', head).response

    # 获取用户权限信息
    username, _ = decoded_info.split(":")
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

    start_byte, end_byte = parse_range_header(range_header)
    file_path = file_manager.get_full_path(access_path)
    file_size = os.path.getsize(file_path)

    if start_byte is None or end_byte is None or start_byte > end_byte or end_byte >= file_size:
        return HttpResponse(416, "Range Not Satisfiable", '', None).response

    with open(file_path, 'rb') as file:
        file.seek(start_byte)
        content = file.read(end_byte - start_byte + 1)

    content_range_header = f"bytes {start_byte}-{end_byte}/{file_size}"
    headers = {
        "Content-Range": content_range_header,
        "Content-Length": str(len(content)),
        "Content-Type": "application/octet-stream"
    }

    return HttpResponse(206, "Partial Content", content, headers).response


def get_range_header(request_lines):
    # 从请求头部获取Range头部信息
    for line in request_lines:
        if line.startswith("Range:"):
            return line[len("Range:"):].strip()
    return None


def parse_range_header(range_header):
    if range_header:
        # 解析范围格式，例如 "bytes=0-499"
        range_type, range_values = range_header.split('=')
        if range_type == 'bytes':
            start_str, end_str = range_values.split('-')
            start_byte = int(start_str) if start_str else None
            end_byte = int(end_str) if end_str else None
            return start_byte, end_byte
    return None, None


def handle_multiple_range_request(file_path, range_header):
    # 分析 Range 头以获得多个范围
    ranges = parse_multiple_ranges(range_header)
    file_size = os.path.getsize(file_path)
    boundary = "3d6b6a416f9b5"  # 边界字符串，可以是任意唯一字符串
    content_parts = []

    for start, end in ranges:
        if start > end or end >= file_size:
            continue  # 忽略无效范围

        # 读取并存储每个范围的内容
        with open(file_path, 'rb') as file:
            file.seek(start)
            content = file.read(end - start + 1)
            content_range_header = f"bytes {start}-{end}/{file_size}"
            content_parts.append((content, content_range_header))

    # 创建多部分响应体
    multipart_content = create_multipart_content(content_parts, boundary)

    # 设置响应头
    headers = {
        "Content-Type": f"multipart/byteranges; boundary={boundary}",
        "Content-Length": str(len(multipart_content))
    }

    return HttpResponse(206, "Partial Content", multipart_content, headers).response


def create_multipart_content(content_parts, boundary):
    # 构建多部分响应体
    parts = []
    for content, content_range in content_parts:
        part = f"--{boundary}\r\n"
        part += "Content-Type: application/octet-stream\r\n"
        part += f"Content-Range: {content_range}\r\n\r\n"
        part += content.decode('latin-1')  # 用 latin-1 解码二进制数据
        part += "\r\n"
        parts.append(part)
    parts.append(f"--{boundary}--\r\n")
    return "".join(parts)


def parse_multiple_ranges(range_header):
    # 解析多重范围
    _, range_values = range_header.split('=')
    ranges = range_values.split(',')
    parsed_ranges = []
    for range in ranges:
        start_str, end_str = range.split('-')
        start_byte = int(start_str) if start_str else None
        end_byte = int(end_str) if end_str else None
        parsed_ranges.append((start_byte, end_byte))
    return parsed_ranges


# 手动解析 multipart/form-data 格式的请求主体
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


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
