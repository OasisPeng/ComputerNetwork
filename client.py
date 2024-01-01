# import requests
# import base64
#
# # 你的服务器地址
# server_url = 'http://localhost:8080/upload?path=/client1/'
#
# # 你的用户名和密码
# username = 'client1'
# password = '123'
#
# # 构建认证信息
# auth_info = f"{username}:{password}"
# encoded_auth_info = base64.b64encode(auth_info.encode()).decode('utf-8')
# headers = {
#     'Authorization': f'Basic {encoded_auth_info}',
#     'Cookie': 'session-id=f85dfecd-e4bf-4a2f-8217-eedb15cdf3a0; HttpOnly'
# }
#
# # 构建文件上传的数据
# files = {'file': ('123.txt', open('./data/121115xx/123.txt', 'rb'))}  # 请替换为实际文件路径
#
# # 发送 POST 请求
# response = requests.head(server_url, headers=headers, files=files)
#
# # 打印响应内容
# print(response.text)


import requests
import base64

# 你的服务器地址
# server_url = 'http://localhost:8080/delete?path=client1'
#
# # 你的用户名和密码
# username = 'client1'
# password = '123'
#
# # 构建认证信息
# auth_info = f"{username}:{password}"
# encoded_auth_info = base64.b64encode(auth_info.encode()).decode('utf-8')
# headers = {'Authorization': f'Basic {encoded_auth_info}',
#            # 'Cookie': 'session-id=1c36a689-c66a-4e38-ac43-9bda3d174352; HttpOnly'
#            }
#
# # 发送 POST 请求
# response = requests.post(server_url, headers=headers)
#
# # 打印响应内容
# print(response.text)


# ################# 测试持久连接
# import socket
#
#
# def send_http_request():
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect(('localhost', 8080))
#
#     for _ in range(1):
#         # 发送简单的HTTP请求
#         http_request = "GET / HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: " \
#                        "python-requests/2.31.0\r\nAccept-Encoding: gzip, deflate, br\r\nAccept: */*\r\nConnection: " \
#                        "keep-alive\r\nAuthorization: Basic Y2xpZW50MToxMjM=\r\n\r\n"
#         client_socket.send(http_request.encode('utf-8'))
#
#         # 接收并打印服务器的响应
#         response_data = client_socket.recv(1024)
#         print(response_data.decode('utf-8'))
#
#     # 关闭连接
#     client_socket.close()
#
#
# if __name__ == "__main__":
#     send_http_request()
# import requests
#
# headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
# q = requests.get('http://localhost:8080/', headers=headers)
# print(q.text)
# print(q)
# import requests
#
#
# def test_chunked_transfer(server_url, username, password):
#     # Construct authorization information
#     auth_info = f"{username}:{password}"
#     encoded_auth_info = base64.b64encode(auth_info.encode()).decode('utf-8')
#     headers = {
#         'Authorization': f'Basic {encoded_auth_info}',
#         'Accept-Encoding': 'chunked'
#     }
#
#     # Sending GET request with chunked transfer
#     response = requests.get(server_url, headers=headers, stream=True)
#     print(response.text)
#
#     # Check if the server response is chunked
#     if response.headers.get('Transfer-Encoding') == 'chunked':
#         print("Chunked transfer encoding detected. Reading chunks:")
#
#         # Read the response in chunks
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:  # filter out keep-alive new chunks
#                 print(chunk)
#     else:
#         print("Server did not use chunked transfer encoding.")
#
#     return response
#
#
# if __name__ == "__main__":
#     # Your server URL with chunked parameter
#     server_url = 'http://localhost:8080/example.txt?chunked=1'
#
#     # Your username and password
#     username = 'client1'
#     password = '123'
#
#     # Test chunked transfer
#     test_chunked_transfer(server_url, username, password)
# url='http://127.0.0.1:8080/client1/a.txt'
#
# data={}
# headers={"Authorization": "Basic Y2xpZW50MToxMjM=",
#          "Range": "bytes=2-3"}
# r=requests.get(url=url, data=data, headers=headers)
# print(r.content.decode())

# url='http://127.0.0.1:8080/client1/a.txt'
#
# data={}
# headers={"Authorization": "Basic Y2xpZW50MToxMjM=",
#          "Range": "bytes=0-1,1-2,2-3"}
# r=requests.get(url=url, data=data, headers=headers)
# print(r.content.decode())

# headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
# response = requests.get('http://localhost:8080/get_public_key', headers=headers)
# print(response.content.decode())
# 给我完整的回复



# client = Client(server_public_key)
url1='http://127.0.0.1:8080/?SUSTech-HTTP=1'

headers={"Authorization": "Basic Y2xpZW50MToxMjM="}
r=requests.get(url=url1, headers=headers)
print(r)
print(r.content.decode())
