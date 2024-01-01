class ChunkedTransfer:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_chunks(self, chunk_size=1024):
        chunks = []  # 初始化一个空列表来存储数据块
        try:
            with open(self.file_path, "rb") as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)  # 将每个数据块添加到列表中
        except FileNotFoundError:
            return None
        return chunks  # 返回包含所有数据块的列表


if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
