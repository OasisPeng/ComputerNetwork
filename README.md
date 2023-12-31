### server.py（服务器主程序）

包含服务器的主要逻辑。
使用argparse处理命令行参数，例如指定服务器的IP地址和端口号。
创建Socket服务器，监听客户端连接。
处理每个客户端连接，解析HTTP请求，调用相应的服务函数，构造HTTP响应并发送回客户端。
### http_handler.py（HTTP请求处理模块）

包含解析HTTP请求、构造HTTP响应的函数。
实现解析HTTP请求的函数，将请求转化为可处理的数据结构。
实现构造HTTP响应的函数，根据服务函数的执行结果构造响应。
### file_manager.py（文件管理模块）

包含处理文件相关操作的函数，如查看目录、下载文件、上传文件和删除文件。
实现验证用户授权的函数，处理HTTP Basic Authorization Scheme。
提供函数用于列出目录、获取文件内容、上传文件和删除文件。
### session_manager.py（会话管理模块）

包含处理用户会话的函数，生成和验证会话ID。
实现生成会话ID的函数，将会话ID与用户关联。
实现验证会话ID的函数，确保请求具有有效的会话。
### chunked_transfer.py（分块传输模块）

包含处理分块传输的函数。
实现分块传输文件的函数，根据HTTP/1.1 Chunked-transfer标准传输文件。
### encryption.py（加密通信模块，仅在Bonus Part中实现）

包含处理加密通信的函数，包括生成密钥、加密和解密通信内容。
实现通过非对称加密进行密钥交换的函数。
实现对称加密通信的函数
### client.py

模拟客户端发送请求

### HttpRequest和HttpResponse

对请求和响应进行了封装