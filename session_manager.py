# session_manager.py
import uuid
import time


class SessionManager:
    def __init__(self):
        # 存储用户会话信息的字典，以用户名为键，值为 (session_id, expiration_time) 的元组
        self.sessions = {}

    def create_session(self, username):
        # 生成一个新的 session_id
        session_id = str(uuid.uuid4())

        # 设置会话过期时间为一定的时间后（例如，3600秒）
        expiration_time = time.time() + 3600

        # 存储会话信息
        self.sessions[username] = (session_id, expiration_time)

        return session_id

    def get_session_info(self, username):
        # 获取用户的会话信息
        return self.sessions.get(username)

    def is_session_valid(self, session_id):
        # 检查会话是否有效
        valid_sessions = [info for info in self.sessions.values() if info[0] == session_id and info[1] > time.time()]
        return len(valid_sessions) > 0

    def get_username_by_session_id(self, session_id):
        # 通过 session_id 获取用户名
        for username, (existing_session_id, _) in self.sessions.items():
            if existing_session_id == session_id:
                return username
        return None
