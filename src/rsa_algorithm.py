from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class RsaAlgorithm:
    def __init__(self):
        self.key_pair = RSA.generate(3072)
        self.public_key = self.key_pair.publickey()

    def get_public_key(self):
        """ Método que retorna a chave pública da classe instânciada """
        return self.public_key

    def encrypt(self, msg, pub_key):
        """ Método que recebe a mensagem e uma public_key, e retorna a mensagem cifrada """

        encryptor = PKCS1_OAEP.new(pub_key)
        msg_encrypted = encryptor.encrypt(bytes(msg, encoding='utf8'))
        return msg_encrypted

    def decrypt(self, msg_cifrada):
        """ Método que recebe a mensagem cifrada, e retorna ela decifrada """

        decryptor = PKCS1_OAEP.new(self.key_pair)
        decrypted = decryptor.decrypt(msg_cifrada)
        return str(decrypted, encoding="utf8")


# TESTANDO A CLASSE
if __name__ == '__main__':
    algo = RsaAlgorithm()
    r_msg = algo.encrypt("Chave que vai ser passada", algo.get_public_key())
    print(algo.decrypt(r_msg))
