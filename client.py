import requests
from encryption import Client

headers={"Authorization": "Basic Y2xpZW50MToxMjM="}
r=requests.get(url='http://127.0.0.1:8080/client1/a.txt?chunked=1', headers=headers)
print(r)
# def exchange_key():
#     headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
#     # 获取服务器公钥
#     response = requests.get('http://localhost:8080/get_public_key', headers=headers)
#     server_public_key = response.content.decode('utf-8').replace('\\n', '\n').replace("b'", "").replace("'",
#                                                                                                         "") + 'C KEY-----'
#
#     # 创建客户端实例并生成对称密钥
#     client = Client(server_public_key)
#     symmetric_key = client.generate_symmetric_key()
#
#     encrypted_symmetric_key = client.encrypt_symmetric_key(symmetric_key)
#
#     # 创建POST请求的数据和头部
#     post_data = "Symmetric key post" + str(encrypted_symmetric_key)
#     post_headers = {
#         'Authorization': headers['Authorization'],
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#
#     # 发送POST请求
#     post_response = requests.post('http://localhost:8080/send_symmetric_key', data=post_data, headers=post_headers)
#     print(post_response.text)
#
#
# exchange_key()
#5
# headers={"Authorization": "Basic Y2xpZW50MToxMjM="}
# r=requests.get(url='http://127.0.0.1:8080/client1/a.txt?chunked=1', headers=headers)
# print(r)