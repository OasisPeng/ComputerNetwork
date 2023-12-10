import requests
import base64

# 你的服务器地址
server_url = 'http://localhost:8080/upload?path=/12111548/'

# 你的用户名和密码
username = '12111548'
password = '111111'

# 构建认证信息
auth_info = f"{username}:{password}"
encoded_auth_info = base64.b64encode(auth_info.encode()).decode('utf-8')
headers = {'Authorization': f'Basic {encoded_auth_info}'}

# 构建文件上传的数据
files = {'file': ('123.txt', open('./data/121115xx/123.txt', 'rb'))}  # 请替换为实际文件路径

# 发送 POST 请求
response = requests.post(server_url, headers=headers, files=files)

# 打印响应内容
print(response.text)


# import requests
# import base64
#
# # 你的服务器地址
# server_url = 'http://localhost:8080/delete?path=/12111548/abc.py'
#
# # 你的用户名和密码
# username = '12111548'
# password = '111111'
#
# # 构建认证信息
# auth_info = f"{username}:{password}"
# encoded_auth_info = base64.b64encode(auth_info.encode()).decode('utf-8')
# headers = {'Authorization': f'Basic {encoded_auth_info}'}
#
# # 发送 POST 请求
# response = requests.post(server_url, headers=headers)
#
# # 打印响应内容
# print(response.text)

