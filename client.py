import ast

import requests
from encryption import Client

import requests

symmetric_key = b'B`\x92(\xa9\xa4\xd0\xf8\x18l\x9d\x16\x90\xe8[\xe4'
encrypted_symmetric_key = b'%\x9d\xbb\x8f\x91k\xfaSk\\\x9c7\xc7\xfb\xef\xe3\xda\x81\xfde\xe0\x84\xe8\xaf\xbd\xd5\r36+W\xa40\xdb\xd4\x07\x85\xaa-o\xe5\x8e\x13\xdb\x9e\x1c\x07\xd8\xac\x0cV\xdew\x94\xaaQ\xe8\xe8\x1a\xb9\xf1-\xbc?B0\xba\xb9\xc2.\xe4\x95\xac\xd05\xc3uk\x84\x93y\x9b\xda\xea|\xa4\xb9\x18\\D4\xa4\x85\x07v\x8b\xad\xe5\x8d\r\xff\xf0k%\xf2\r\rSq\xf7\x07M\xc3an0tk\x02\xb4\xae\xccD\xa9S\x1f\xcaz\xcaFi)\xb1P\xbaTv\x80\xc7\x9a\xa3\x8e\x92\xce\xf9w\xcb\x15\xdc~-n\xb1\xd4\x8e&\xe1*\x06Ad\xbd\x80 E?\xe5\xb7\x9a\xa3\xea\'2J\xcb\xa89W|\xae\xad\xc5\xef\xfb\'\x9b\x07\xf0\xe3\xf77\xc4\xd0\xe2\x17nI\xbd\xe3,\x9c\x1f\xc9.s\x14\xefH\x01pV\x16\xe1\xf27\xe1\x9dsS\x84\x19\xbb\xde\x88\x9f\xd5g~R\x06\x86"Fp\x0c\xad!\x06\xc7\xa7k|\x14\xf4\xf39\xe2\xcd\xea|Y\x9cX\xd3,\x8b'
server_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxercqhZgLoDbeiBIRat2
A/cHBdmXzwnsn7tfIyMPHkVJHzLs9wHRFIbpl67XcOhW/Sr8gj0CgVOPfGWR5Vj2
GNsnCTbTi0qIdc7iCrD0me+2eIMiXyDnYJvNlhEAHv4uirtw8CoGkNHO5CWx8ROI
guf5f6DhV/q4xC1J5fdUcEEfR8zMQ4WeUAM7AWL8dGTQTh+1ASWm9kIxTN2oGhDy
WWg0Cosi98WrrNNRPoU6UHm8yeQ4GZPtjWC/HuyX8d9Enasro/aEOfH6bLXFfFKS
LW40P8g2HTn92hoyNx6gONtTkolx0S6fWgL28sSxKbRkMXyXgcbHtxyCSd0u2J9G
4wIDAQAB
-----END PUBLIC KEY-----"""
client = Client(server_public_key)


def exchange_key(session, headers):
    global symmetric_key
    # 获取服务器公钥
    response = session.get('http://localhost:8080/get_public_key', headers=headers)

    server_public_key = response.content.decode()

    # 创建客户端实例并生成对称密钥
    client = Client(server_public_key)
    # symmetric_key = client.generate_symmetric_key()
    # print(symmetric_key)

    encrypted_symmetric_key = client.encrypt_symmetric_key(symmetric_key)
    print(encrypted_symmetric_key)

    # 创建POST请求的数据和头部
    post_data = "Symmetric key post" + str(encrypted_symmetric_key)

    # 发送POST请求
    session.post('http://localhost:8080/send_symmetric_key', data=post_data, headers=headers)


# 创建 session 对象
# session = requests.Session()
# headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
# session.headers.update({'Connection': 'keep-alive'})
# # 执行 key 交换
# # exchange_key(session, headers)
#
# # 执行后续请求
# r = session.get(url='http://127.0.0.1:8080/client1/a.txt?chunked=1', headers=headers)
# print(r.content.decode())

def decode_response(response):
    content = response.content.decode()
      # 转化为元组
    response_tuple = ast.literal_eval(content)
    decrepted_response = client.decrypt_message(response_tuple, symmetric_key)
    return decrepted_response


headers={"Authorization": "Basic Y2xpZW50MToxMjM="}
q=requests.get('http://localhost:8080/',headers=headers)
print((q))

# headers = {"Authorization": "Basic Y2xpZW50MToxMjM="}
# session = requests.Session()
# session.headers.update({'Connection': 'keep-alive'})
#
# response1 = session.get('http://127.0.0.1:8080', headers=headers)
# response2 = session.get('http://127.0.0.1:8080', headers=headers)
#
# print(response1)
# print(response2)
