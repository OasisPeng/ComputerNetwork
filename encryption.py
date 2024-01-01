from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

server_public_key = None


class Server:
    def __init__(self):
        self.symmetric_key = None
        key = RSA.generate(2048)
        self.private_key = key.export_key()

    def get_keys(self):
        global server_public_key
        key = RSA.generate(2048)
        self.public_key = key.publickey().export_key()
        self.private_key = key.export_key()
        server_public_key = self.public_key

        return self.public_key

    def receive_encrypted_symmetric_key(self, encrypted_key):
        private_key = RSA.import_key(self.private_key)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        self.symmetric_key = cipher_rsa.decrypt(encrypted_key)

    def decrypt_message(self, encrypted_data):
        nonce, ciphertext, tag = encrypted_data
        cipher = AES.new(self.symmetric_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    def encrypt_message(self, message):
        cipher = AES.new(self.symmetric_key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message)
        return nonce, ciphertext, tag


class Client:
    def __init__(self, server_public_key):
        self.server_public_key = server_public_key

    def generate_symmetric_key(self):
        return get_random_bytes(16)

    def encrypt_symmetric_key(self, symmetric_key):
        public_key = RSA.import_key(self.server_public_key)
        cipher_rsa = PKCS1_OAEP.new(public_key)
        return cipher_rsa.encrypt(symmetric_key)

    def encrypt_message(self, symmetric_key, message):
        cipher = AES.new(symmetric_key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message)
        return nonce, ciphertext, tag

    def decrypt_message(self, encrypted_data, symmetric_key):
        nonce, ciphertext, tag = encrypted_data
        cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)


# Simulate the communication
if __name__ == "__main__":
    # Create a server instance
    server = Server()

    # Simulate client requesting the public key from the server
    server_public_key = server.get_keys()

    # Create a client instance with the server's public key
    client = Client(server_public_key)

    # Client generates a symmetric key and encrypts it with the server's public key
    symmetric_key = client.generate_symmetric_key()
    encrypted_symmetric_key = client.encrypt_symmetric_key(symmetric_key)

    # Simulate sending the encrypted symmetric key to the server
    server.receive_encrypted_symmetric_key(encrypted_symmetric_key)

    # Client encrypts a message with the symmetric key
    message = "Hello, secure world!".encode()
    encrypted_message = client.encrypt_message(symmetric_key, message)
    print(f"Encrypted Message: {encrypted_message}")

    # Server decrypts the message
    decrypted_message = server.decrypt_message(encrypted_message)
    print(f"Decrypted Message: {decrypted_message.decode()}")

    # Server encrypts a response message
    response_message = "Hello from server!".encode()
    encrypted_response = server.encrypt_message(response_message)
    print(f"Encrypted Response: {encrypted_response}")

    # Client decrypts the server's message
    decrypted_response = client.decrypt_message(encrypted_response, symmetric_key)
    print(f"Decrypted Response: {decrypted_response.decode()}")
