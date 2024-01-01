from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

server_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxercqhZgLoDbeiBIRat2
A/cHBdmXzwnsn7tfIyMPHkVJHzLs9wHRFIbpl67XcOhW/Sr8gj0CgVOPfGWR5Vj2
GNsnCTbTi0qIdc7iCrD0me+2eIMiXyDnYJvNlhEAHv4uirtw8CoGkNHO5CWx8ROI
guf5f6DhV/q4xC1J5fdUcEEfR8zMQ4WeUAM7AWL8dGTQTh+1ASWm9kIxTN2oGhDy
WWg0Cosi98WrrNNRPoU6UHm8yeQ4GZPtjWC/HuyX8d9Enasro/aEOfH6bLXFfFKS
LW40P8g2HTn92hoyNx6gONtTkolx0S6fWgL28sSxKbRkMXyXgcbHtxyCSd0u2J9G
4wIDAQAB
-----END PUBLIC KEY-----"""
private_key = b'-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAxercqhZgLoDbeiBIRat2A/cHBdmXzwnsn7tfIyMPHkVJHzLs\n9wHRFIbpl67XcOhW/Sr8gj0CgVOPfGWR5Vj2GNsnCTbTi0qIdc7iCrD0me+2eIMi\nXyDnYJvNlhEAHv4uirtw8CoGkNHO5CWx8ROIguf5f6DhV/q4xC1J5fdUcEEfR8zM\nQ4WeUAM7AWL8dGTQTh+1ASWm9kIxTN2oGhDyWWg0Cosi98WrrNNRPoU6UHm8yeQ4\nGZPtjWC/HuyX8d9Enasro/aEOfH6bLXFfFKSLW40P8g2HTn92hoyNx6gONtTkolx\n0S6fWgL28sSxKbRkMXyXgcbHtxyCSd0u2J9G4wIDAQABAoIBADy/W06bgpcTdwoz\nqWs09wq9gjrR8E4cgjP+63MZ+jR02L5KP8CLHrUZuc4UXM0rizO2w31oI4I1dyeb\n9115YkP71C34VZL95Aeg4fGdId6z3IJ94YloTIxzFfWXLz3UD84GPWKBy7UcqM+P\nIGBZ+f8QG50IcNIzww13xyReN10inQ7xoLRBNdImuVNAivJQjBa0CtGrs3VAVSyf\nw3AuD1sSKLC4y4byMGDbXC36MDsULtyG1iN5sRvt94psAxhm6U+YpBEwmjeTWyPD\np1LM9nA/dlDqRDyTQgV2tRsy7GaFdPpEaXvbc/A1GBsTx9i6mMTwfnm1qtM/OoO6\nXfh1XxkCgYEAy9mMyzEPMfJav7cBkZ5wc2ci1qHxEvsrAVYGtMz3s3QoEsA5KQoe\nb03ZQpXqkkEFFR/Ww3FXTZA/DP2FsZ3D1jBnIURQYamRO5n7jPyd2jAoCXbHQv7F\nRbXwETai/YAUgbsvnNBPMR7R5utFHlFKOiShp29llVbLQgIPPDsCE4sCgYEA+IzK\nj+c2cJljsFQck782XSDQufpNk9+Nlt8MWZqYwIhKITcpIJ0khIx9dt2EKOTMK2TF\n+AQkt5araOJuN50jW3U2zypssFJ+jfOsMEjTWs8//NMwspW6kug1A/rz8cKsXh9k\nBDPcwRdpIbEF70WAKxzHcr61G8msTk/f5VtcpQkCgYBuULrasx/v/aGSomzc6wsb\nyLKXyGd3yCjLvkw+x7U8jh2pmBDW3rz9qvlqCUs5/qnLdsF4XvvJ48fbNc+GAUSb\nwvHslNWTJHqN8JSrBYI/M1RXWsoWvVzwjrbt+c1WtltioXPwvuI8SNt6xdNPxtoO\ngQhiXexxVtkETa0FAUHsZQKBgDef8rlv6mwauAe/W0HpmjYPYQcuMGx2rI5mTrJC\n+gqktcpnOOoWoRSVCIMwoiIwykyv2epeqwT3UFdBzZ7eqQoP2ntUqExxueb08MVB\nlyOMnGptrUlaXw3/r9W7NRsXEVJjPhP+s1n3bkze/FAHQt7jKvPQIGIeqVRBZf9D\niiFZAoGALXD4M9Yhicj/SoA7htNqcth+yl2X2/x9+OsVcbkxyJw+vo5cRDddiLsr\nAgpyI4N2VP9h2/BXV75TGc3EM1hFWKnT+QtUEla37b0nCDM3IBz52HSv9c9yebvw\nGv5lGR8++2jMJJcsO6tOg2Ph9M9PFyK1rFj78nNAVkVbJ7gtGMc=\n-----END RSA PRIVATE KEY-----'
encrypted_symmetric_key = b'%\x9d\xbb\x8f\x91k\xfaSk\\\x9c7\xc7\xfb\xef\xe3\xda\x81\xfde\xe0\x84\xe8\xaf\xbd\xd5\r36+W\xa40\xdb\xd4\x07\x85\xaa-o\xe5\x8e\x13\xdb\x9e\x1c\x07\xd8\xac\x0cV\xdew\x94\xaaQ\xe8\xe8\x1a\xb9\xf1-\xbc?B0\xba\xb9\xc2.\xe4\x95\xac\xd05\xc3uk\x84\x93y\x9b\xda\xea|\xa4\xb9\x18\\D4\xa4\x85\x07v\x8b\xad\xe5\x8d\r\xff\xf0k%\xf2\r\rSq\xf7\x07M\xc3an0tk\x02\xb4\xae\xccD\xa9S\x1f\xcaz\xcaFi)\xb1P\xbaTv\x80\xc7\x9a\xa3\x8e\x92\xce\xf9w\xcb\x15\xdc~-n\xb1\xd4\x8e&\xe1*\x06Ad\xbd\x80 E?\xe5\xb7\x9a\xa3\xea\'2J\xcb\xa89W|\xae\xad\xc5\xef\xfb\'\x9b\x07\xf0\xe3\xf77\xc4\xd0\xe2\x17nI\xbd\xe3,\x9c\x1f\xc9.s\x14\xefH\x01pV\x16\xe1\xf27\xe1\x9dsS\x84\x19\xbb\xde\x88\x9f\xd5g~R\x06\x86"Fp\x0c\xad!\x06\xc7\xa7k|\x14\xf4\xf39\xe2\xcd\xea|Y\x9cX\xd3,\x8b'


symmetric_key = b'B`\x92(\xa9\xa4\xd0\xf8\x18l\x9d\x16\x90\xe8[\xe4'

class Server:
    def __init__(self):
        global encrypted_symmetric_key
        self.symmetric_key = None
        self.receive_encrypted_symmetric_key(encrypted_symmetric_key)

    def get_keys(self):
        global server_public_key
        # key = RSA.generate(2048)
        # private_key = key.export_key()
        # print(private_key)
        # server_public_key = key.publickey().export_key()

        return server_public_key

    def receive_encrypted_symmetric_key(self, encrypted_key):
        global private_key
        private_key_ = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(private_key_)
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
    # server_public_key = server.get_keys()
    # print(f"Server Public Key: {server_public_key}", "type" + str(type(server_public_key)))
    #
    # # Create a client instance with the server's public key
    client = Client(server_public_key)
    #
    # # Client generates a symmetric key and encrypts it with the server's public key
    # symmetric_key = client.generate_symmetric_key()
    # print(f"Symmetric Key: {symmetric_key}")
    #
    # encrypted_symmetric_key = client.encrypt_symmetric_key(symmetric_key)
    # print(f"Encrypted Symmetric Key: {encrypted_symmetric_key}")

    # Simulate sending the encrypted symmetric key to the server
    server.receive_encrypted_symmetric_key(encrypted_symmetric_key)

    # Client encrypts a message with the symmetric key
    message = "Hello, secure world!".encode()
    encrypted_message = client.encrypt_message(symmetric_key, message)
    print(f"Encrypted Message: {encrypted_message}")

    # Server decrypts the message
    decrypted_message = server.decrypt_message(encrypted_message)
    print(f"Decrypted Message: {decrypted_message.decode()}", "type")

    # Server encrypts a response message
    response_message = "Hello from server!".encode()
    encrypted_response = server.encrypt_message(response_message)
    print(f"Encrypted Response: {encrypted_response}")

    # Client decrypts the server's message
    decrypted_response = client.decrypt_message(encrypted_response, symmetric_key)
    print(f"Decrypted Response: {decrypted_response.decode()}")
