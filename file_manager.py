import os
import mimetypes


class FileManager:
    def __init__(self, base_path):
        self.base_path = base_path

    def list_directory(self, relative_path):
        # 返回指定目录的文件列表
        absolute_path = os.path.join(self.base_path, relative_path)
        if os.path.isdir(absolute_path):
            files = os.listdir(absolute_path)
            return files
        else:
            return None

    def read_file(self, relative_path):
        # 读取指定文件的内容
        absolute_path = os.path.join(self.base_path, relative_path)

        if os.path.isfile(absolute_path):
            with open(absolute_path, "rb") as file:
                content = file.read()
            return content
        else:
            return None

    def upload_file(self, relative_path, content):
        # 上传文件到指定路径
        absolute_path = os.path.join(self.base_path, relative_path)

        # 创建目录
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        # 写入文件内容
        with open(absolute_path, "wb") as file:
            file.write(content)

    def delete_file(self, relative_path):
        # 删除指定文件
        absolute_path = os.path.join(self.base_path, relative_path)

        if os.path.isfile(absolute_path):
            os.remove(absolute_path)


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
