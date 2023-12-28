class HttpRequest:
    def __init__(self, request_string):
        self.request_lines = request_string.split("\r\n")
        self.method, self.path, _ = self.request_lines[0].split(" ")

        self.authorization_header = self.get_authorization_header()
        self.cookie_header = self.get_cookie_header()
        self.body = self.get_request_body()

    def get_authorization_header(self):
        for line in self.request_lines[1:]:
            if line.startswith("Authorization:"):
                return line[len("Authorization:"):].strip()
        return None

    def get_cookie_header(self):
        for line in self.request_lines[1:]:
            if line.startswith("Cookie:"):
                return line[len("Cookie:"):].strip()
        return None

    def get_request_body(self):
        empty_line_index = self.request_lines.index("")
        if empty_line_index + 1 < len(self.request_lines):
            return "\r\n".join(self.request_lines[empty_line_index + 1:])
        return None
