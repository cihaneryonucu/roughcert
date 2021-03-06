import cryptography
import cryptography.hazmat.primitives.asymmetric.padding as padding
import zmq
import sys
import copy
import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.hazmat.primitives import hashes
import base64
from LogMixin import LogMixin


def generate_private_key(filename, password='password'):
    # Gen private key, n=65537, 2048 keysize
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Write key to a file
    with open(filename, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(bytes(password, 'utf-8'))
            )
        )

    return key


def generate_self_signed_cert(private_key, filename, cert_details, validity):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, cert_details["country"]),  # Sweden
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, cert_details["region"]  # Skåne
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert_details["city"]),  # Lund
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_details["org"]),  # Cihan-Marco Co.
            x509.NameAttribute(NameOID.COMMON_NAME, cert_details["hostname"]),  # ce-ms.com
        ]
    )

    # Valid for
    valid_from = datetime.utcnow()
    valid_to = valid_from + timedelta(days=validity)

    # Build the cert
    builder = (
        x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(valid_from)
            .not_valid_after(valid_to)
    )

    # Sign
    public_key = builder.sign(private_key, hashes.SHA256(), default_backend())

    # Write
    with open(filename, "wb") as f:
        f.write(public_key.public_bytes(serialization.Encoding.PEM))

    return public_key


def create_csr(private_key, cert_details):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, cert_details["country"]),  # Sweden
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, cert_details["region"]  # Skåne
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert_details["city"]),  # Lund
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_details["org"]),  # Cihan-Marco Co.
            x509.NameAttribute(NameOID.COMMON_NAME, cert_details["hostname"]),  # ce-ms.com
        ]
    )

    builder = (
        x509.CertificateSigningRequestBuilder()
            .subject_name(subject)
    )
    csr = builder.sign(private_key, hashes.SHA256(), default_backend())

    return csr


def sign_csr(csr, ca_public_key, ca_private_key, validity):  # public key is not key.public_key() but the certificate.
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=validity)

    builder = (
        x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_public_key.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(valid_from)
            .not_valid_after(valid_until)
    )

    for extension in csr.extensions:
        builder = builder.add_extension(extension.value, extension.critical)

    public_key = builder.sign(
        private_key=ca_private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend(),
    )
    return public_key


def import_certificate(filename):  # Cert containing public key. This is directly importing the
    certFile = open(filename, "rb")
    try:
        cert = x509.load_pem_x509_certificate(certFile.read(), default_backend())
    except ValueError:
        print('This is not a pem certificate')
        return None
    certFile.close()
    return cert


def import_private_key(filename, password='password'):
    key_file = open(filename, "rb")
    try:
        private_key = serialization.load_pem_private_key(key_file.read(), bytes(password, 'utf-8'),
                                                         default_backend())
    except ValueError:
        print('This is not a pem private key')
        return None
    return private_key


def export_cert(filename, cert):
    with open(filename, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


class CryptoPrimitives(LogMixin):
    def __init__(self, socket, private_key, cert, CA_pub_key):
        self.__socket = socket
        self.__private_key = private_key
        self.cert = cert
        self.CA_pub_key = CA_pub_key
        self.__session_key = None  # Can be a Dict: They should be filled with username as key and symmetric key as
        # value.
        self.__fernet = None
        self.peer_cert = None

    def establish_session_key(self, isClient):  # if client, you should specify the address and port
        if isClient:
            self.__fernet = self.__initiate_key_derivation(self.__private_key, self.cert, self.CA_pub_key)
        else:
            self.__fernet = self.__listen_key_derivation(self.__private_key, self.cert, self.CA_pub_key)

    def encrypt(self, message):  # Message type is byte
        return self.__fernet.encrypt(message)

    def decrypt(self, ciphertext):
        return self.__fernet.decrypt(ciphertext)

    def __initiate_key_derivation(self, client_private_key, client_cert, CA_pub_key):

        tx_sock = self.__socket

        client_secret, secret_byte_size = self.__client_round_1(tx_sock)
        server_cert, server_secret = self.__client_round_2(CA_pub_key, tx_sock)

        if server_cert is None:
            return None

        premaster_secret = self.__client_round_3(client_cert, client_private_key, secret_byte_size, server_cert,
                                                 tx_sock)
        fernet = self.__client_round_4(client_secret, premaster_secret, server_secret)
        finalize_client, finalize_server = self.__client_round_5(fernet, tx_sock)

        if finalize_client == finalize_server:
            self.logger.info('Finalized')
            return fernet
        else:
            self.logger.info('Problem with the derived key')
            return None

    def __listen_key_derivation(self, server_private_key, server_cert, CA_pub_key):
        rx_sock = self.__socket

        client_secret = self.__server_round_1(rx_sock)
        server_secret = self.__server_round_2(rx_sock, server_cert, server_private_key)
        premaster_secret = self.__server_round_3(CA_pub_key, rx_sock, server_private_key)
        if premaster_secret is None:
            return None

        fernet = self.__server_round_4(client_secret, premaster_secret, server_secret)
        finalize_client, finalize_server = self.__server_round_5(fernet, rx_sock)

        if finalize_client == finalize_server:
            self.logger.info('Finalized')
            return fernet
        else:
            self.logger.info('Problem with the derived key')
            return None

    def __server_round_5(self, fernet, rx_sock):
        # Round 5: Finalize by sending a message
        self.logger.info('-----Round 5 starts-----')
        finalize_server = b"Finalize!"
        ct_finalize_server = fernet.encrypt(finalize_server)
        rx_sock.send(ct_finalize_server, flags=zmq.NOBLOCK)
        ct_finalize_client = rx_sock.recv()
        finalize_client = fernet.decrypt(ct_finalize_client)
        return finalize_client, finalize_server

    def __server_round_4(self, client_secret, premaster_secret, server_secret):
        # Round 4: Key derivation by collected secrets. Hash first, use the hash for key
        self.logger.info('-----Round 4 starts-----')
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(client_secret)
        digest.update(server_secret)
        digest.update(premaster_secret)
        key = digest.finalize()
        key = base64.urlsafe_b64encode(key)
        self.__session_key = key
        fernet = Fernet(key)
        self.logger.info('-----Round 4 ends-----')
        return fernet

    def __server_round_3(self, CA_pub_key, rx_sock, server_private_key):
        # Round 3: Recieve client cert, signed and encrpyted secret and verify them
        self.logger.info('-----Round 3 starts-----')
        premaster_secret_encrypted = rx_sock.recv()
        premaster_secret_signed = rx_sock.recv()
        client_cert_raw = rx_sock.recv()
        client_cert = x509.load_pem_x509_certificate(client_cert_raw, default_backend())
        self.peer_cert = client_cert
        premaster_secret = server_private_key.decrypt(premaster_secret_encrypted, padding.PKCS1v15())
        try:
            CA_pub_key.public_key().verify(client_cert.signature, client_cert.tbs_certificate_bytes, padding.PKCS1v15(),
                                           hashes.SHA256())
            self.logger.info('Client certificate verified.')
        except cryptography.exceptions.InvalidSignature:
            self.logger.info("Certificate verification failed, invalid CA or certificate")
            return None
        try:
            client_cert.public_key().verify(premaster_secret_signed, premaster_secret, padding.PKCS1v15(),
                                            hashes.SHA256())
            self.logger.info('Premaster signature verified.')
        except cryptography.exceptions.InvalidSignature:
            self.logger.info("Premaster signature verification failed, invalid key or signature")
            return None
        self.logger.info('-----Round 3 ends-----')
        return premaster_secret

    def __server_round_2(self, rx_sock, server_cert, server_private_key):
        # Round 2 send cert, response and secret
        self.logger.info('-----Round 2 starts-----')
        secret_byte_size = 16
        server_secret = secrets.token_bytes(secret_byte_size)
        signed_server_secret = server_private_key.sign(server_secret, padding.PKCS1v15(), hashes.SHA256())
        rx_sock.send_string('hej back', flags=zmq.NOBLOCK)
        rx_sock.send(server_secret, flags=zmq.NOBLOCK)
        rx_sock.send(signed_server_secret, flags=zmq.NOBLOCK)
        rx_sock.send(server_cert.public_bytes(serialization.Encoding.PEM), flags=zmq.NOBLOCK)
        self.logger.info('-----Round 2 ends-----')
        return server_secret

    def __server_round_1(self, rx_sock):
        # Round 1 listen
        self.logger.info('----- Server Round 1 starts-----')
        client_hey = rx_sock.recv()
        client_secret = rx_sock.recv()
        self.logger.info('-----Round 1 ends-----')
        return client_secret

    def __client_round_5(self, fernet, tx_sock):
        # Round 5: Finalize by sending a message
        self.logger.info('-----Round 5 starts-----')
        ct_finalize_server = tx_sock.recv()
        finalize_server = fernet.decrypt(ct_finalize_server)
        finalize_client = b"Finalize!"
        ct_finalize_client = fernet.encrypt(finalize_client)
        tx_sock.send(ct_finalize_client, flags=zmq.NOBLOCK)
        return finalize_client, finalize_server

    def __client_round_4(self, client_secret, premaster_secret, server_secret):
        # Round 4: Key derivation by collected secrets. Hash first, use the hash for key
        self.logger.info('-----Round 4 starts-----')
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(client_secret)
        digest.update(server_secret)
        digest.update(premaster_secret)
        key = digest.finalize()
        key = base64.urlsafe_b64encode(key)  # Encode it to string
        self.__session_key = key
        fernet = Fernet(key)
        self.logger.info('-----Round 4 ends-----')
        return fernet

    def __client_round_3(self, client_cert, client_private_key, secret_byte_size, server_cert, tx_sock):
        # Round 3: Client sends the encrypted pre-master secret, signature, and his certificate for mutual auth.
        self.logger.info('-----Round 3 starts-----')
        premaster_secret = secrets.token_bytes(secret_byte_size)
        premaster_secret_encrypted = server_cert.public_key().encrypt(premaster_secret, padding.PKCS1v15())
        premaster_secret_signed = client_private_key.sign(premaster_secret, padding.PKCS1v15(), hashes.SHA256())
        tx_sock.send(premaster_secret_encrypted, flags=zmq.NOBLOCK)
        tx_sock.send(premaster_secret_signed, flags=zmq.NOBLOCK)
        tx_sock.send(client_cert.public_bytes(serialization.Encoding.PEM), flags=zmq.NOBLOCK)
        self.logger.info('-----Round 3 ends-----')
        return premaster_secret

    def __client_round_2(self, CA_pub_key, tx_sock):
        # Round 2 listen
        self.logger.info('-----Round 2 starts-----')
        server_hey = tx_sock.recv()
        server_secret = tx_sock.recv()
        server_secret_signed = tx_sock.recv()
        server_cert_raw = tx_sock.recv()
        server_cert = x509.load_pem_x509_certificate(server_cert_raw, default_backend())
        self.peer_cert = server_cert
        try:
            CA_pub_key.public_key().verify(server_cert.signature, server_cert.tbs_certificate_bytes, padding.PKCS1v15(),
                                           hashes.SHA256())
            # CA_pub_key.public_key().verify(server_cert.signature,server_cert.tbs_certificate_bytes,padding.PKCS1v15(),hashes.SHA256())
            self.logger.info('Server certificate verified.')
        except cryptography.exceptions.InvalidSignature:
            self.logger.info("Certificate verification failed, invalid CA")
            return None, None
        try:
            server_cert.public_key().verify(server_secret_signed, server_secret, padding.PKCS1v15(), hashes.SHA256())
            self.logger.info('Server signature verified')
        except cryptography.exceptions.InvalidSignature:
            self.logger.info("Server signature verification failed, invalid key or signature")
            return None, None
        self.logger.info('-----Round 2 ends-----')
        return server_cert, server_secret

    def __client_round_1(self, tx_sock):
        # TLS like key derivation: Round 1
        self.logger.info('-----Client Round 1 starts-----')
        secret_byte_size = 16
        client_secret = secrets.token_bytes(secret_byte_size)
        tx_sock.send_string('hej', flags=zmq.NOBLOCK)
        tx_sock.send(client_secret, flags=zmq.NOBLOCK)
        self.logger.info('-----Round 1 ends-----')
        return client_secret, secret_byte_size



# generate_private_key('a')
# For testing uncomment below and run as:
# server:python3 Crypto.py s [local_address] [local_port] - for example: python3 Crypto.py s 127.0.0.1 1111
# client:python3 Crypto.py c [target_address] [target_port] - for example: python3 Crypto.py c 127.0.0.1 1111
# You can use the example certificates and keys which can be found in credentials folder. 
# Note that these keys/cert should not be used for real world scenarios but used only for testing the system.

# if sys.argv[1] == 's':
#     key = import_private_key('credentials/client1_private_key.pem')
#     cert = import_certificate('credentials/client1_cert.pem')
#     CA_cert = import_certificate('credentials/CA_cert.pem')
#     crypto = Crypto_Primitives(sys.argv[2], sys.argv[3], key, cert, CA_cert)
#     crypto.establish_session_key(False)
#     c = crypto.encrypt(b'Folsom')
#     print(c)
#     print(crypto.decrypt(c))
# elif sys.argv[1] == 'c':
#     key = import_private_key('credentials/client2_private_key.pem')
#     cert = import_certificate('credentials/client2_cert.pem')
#     CA_cert = import_certificate('credentials/CA_cert.pem')
#     crypto = Crypto_Primitives(sys.argv[2], sys.argv[3], key, cert, CA_cert)
#     crypto.establish_session_key(True, sys.argv[2], sys.argv[3])
#     c = crypto.encrypt(b'Folsom')
#     print(c)
#     print(crypto.decrypt(c))
# else:
#     print('Nope')
