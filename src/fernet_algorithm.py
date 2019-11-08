import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FernetAlgorithm():
    def __init__(self):
        # Seta o tamanho do SALT
        self.salt = os.urandom(16)
        # Configuração do KDF conforme os parametros
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        # Senha raiz gerada automaticamente
        self.password = bytes(Fernet.generate_key())
        # KEY gerada apartir da Senha
        self.key = base64.urlsafe_b64encode(kdf.derive(self.password))

        # Instancia do Algoritmo
        self.f = Fernet(self.key)

    def get_key(self):
        """ Função que retorna a KEY """
        return self.key

    def encrypt(self, text):
        """ Função que Cifra o texto e retorna o token"""
        # TOKEN gerado da cifragem
        token = self.f.encrypt(bytes(text, encoding='utf8'))
        return token

    @staticmethod
    def decrypt(token, new_key):
        """ Função que Decifra o tpken e retorna o texto """
        f = Fernet(new_key)
        return f.decrypt(token)
