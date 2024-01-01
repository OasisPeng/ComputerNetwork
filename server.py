import socket
import threading
import argparse
from http_handler import handle_http_request
from encryption import Server


def handle_client(client_socket):
    is_gain_key = False
    server = Server()
    print('new client')

    try:
        # 处理单个客户端连接
        while True:
            request_data = client_socket.recv(2048)

            if not request_data:
                # 如果没有数据，客户端可能已关闭连接
                break

            if "Symmetric key post" in request_data.decode():
                is_gain_key = True
                # symmetric_key是request_data中的body
                symmetric_key = request_data.decode().replace("Symmetric key post", "").split("\r\n")[-1]
                server.receive_encrypted_symmetric_key(eval(symmetric_key))
                # print(symmetric_key)

            # 解析HTTP请求
            http_request = request_data.decode('utf-8')
            print(http_request)

            # 处理HTTP请求并获取响应
            http_response = handle_http_request(http_request)
            print(http_response)

            if is_gain_key:
                # 将data加密
                old_data = http_response.split("\r\n")[-1].encode()
                old_response = http_response.split("\r\n")[:-1]
                data = server.encrypt_message(old_data)
                http_response = "\r\n".join(old_response) + "\r\n" + str(data)

            # 发送HTTP响应到客户端
            client_socket.send(http_response.encode('utf-8'))

            # # 检查是否需要关闭连接
            if "Connection: Close" in http_request:
                client_socket.close()
            # break
    except (ConnectionResetError, socket.error):
        # 客户端关闭连接引发异常
        print("Client closed the connection.")

    except Exception as e:  # 即使在处理某个客户端连接时发生异常，服务器仍会关闭该连接并继续处理其他客户端连接。
        print(f"Error handling client: {e}")

    finally:
        # 关闭客户端连接
        pass
        # client_socket.close()


def run_server(host, port):
    # 启动HTTP服务器
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(client_socket)  # 一个连接
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # 使用线程处理每个连接，实现并发处理
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("-i", "--host", default="localhost", help="Server IP address")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Server port")
    args = parser.parse_args()

    run_server(args.host, args.port)
