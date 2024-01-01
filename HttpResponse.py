class HttpResponse:
    def __init__(self, status_code, reason_phrase, body=None, headers=None):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.body = body
        self.headers = headers
        self.response = self.generate_response_string()
        self.boundary = 'boundary'
        self.multipart_respond = self.generate_multipart_body()

    def generate_response_string(self):
        response = f"HTTP/1.1 {self.status_code} {self.reason_phrase}\r\n"

        if self.headers is not None:
            for key, value in self.headers.items():
                response += f"{key}: {value}\r\n"

        if self.body is not None:
            # 注意：此处不再需要发送body内容，因为在分块传输中，内容将在之后发送
            response += f"Connection: keep-alive\r\nAccess-Control-Allow-Origin: " \
                        f"http://localhost:8080\r\nContent-Length: {len(self.body)}\r\n\r\n"
        else:
            response += "\r\n"

        return response

    def generate_multipart_body(self):
        response = f"HTTP/1.1 {self.status_code} {self.reason_phrase}\r\n"

        if self.headers is not None:
            for key, value in self.headers.items():
                response += f"{key}: {value}\r\n"

        response += '\r\n'

        if self.body is not None:
            for body in self.body:
                response += body.decode() + "\r\n"
        else:
            response += "\r\n"

        return response
