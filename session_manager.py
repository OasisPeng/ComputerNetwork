import uuid
import time

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, username):
        # 创建一个新的会话，并返回会话ID
        session_id = str(uuid.uuid4())
        expiration_time = time.time() + 3600  # 会话有效期为1小时

        self.sessions[session_id] = {"username": username, "expiration_time": expiration_time}
        return session_id

    def get_username(self, session_id):
        # 根据会话ID获取用户名
        if session_id in self.sessions:
            session = self.sessions[session_id]

            # 检查会话是否过期
            if time.time() < session["expiration_time"]:
                return session["username"]

        return None

if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
