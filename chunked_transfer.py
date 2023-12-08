class ChunkedTransfer:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_chunks(self, chunk_size=1024):
        with open(self.file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break

                yield chunk

if __name__ == "__main__":
    # 在这里可以添加一些测试代码
    pass
