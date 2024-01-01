import requests
from encryption import Client

import requests


def exchange_key(session, headers):
    # 获取服务器公钥
    response = session.get('http://localhost:8080/get_public_key', headers=headers)

    server_public_key = response.content.decode()

    # 创建客户端实例并生成对称密钥
    client = Client(server_public_key)
    symmetric_key = client.generate_symmetric_key()

    encrypted_symmetric_key = client.encrypt_symmetric_key(symmetric_key)

    # 创建POST请求的数据和头部
    post_data = "Symmetric key post" + str(encrypted_symmetric_key)

    # 发送POST请求
    session.post('http://localhost:8080/send_symmetric_key', data=post_data, headers=headers)


# 创建 session 对象
session = requests.Session()
headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
session.headers.update({'Connection': 'keep-alive'})
# 执行 key 交换
exchange_key(session, headers)

# 执行后续请求
r = session.get(url='http://127.0.0.1:8080/client1/a.txt?chunked=1', headers=headers)
print(r.content.decode())
