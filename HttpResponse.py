class HttpResponse:
    def __init__(self, status_code, reason_phrase, body=None, headers=None):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.body = body
        self.headers = headers
        self.response = self.generate_response_string()

    def generate_response_string(self):
        response = f"HTTP/1.1 {self.status_code} {self.reason_phrase}\r\n"

        if self.headers is not None:
            for key, value in self.headers.items():
                response += f"{key}: {value}\r\n"

        if self.body is not None:
            response += f"Connection: keep-alive\r\nAccess-Control-Allow-Origin: " \
                        f"http://localhost:8080\r\nContent-Length: {len(self.body)}\r\n\r\n{self.body}\r\n"
        else:
            response += "\r\n"

        return response
