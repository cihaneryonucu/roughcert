import cryptography
import zmq
import sys
import secrets
# from pyroughtime import RoughtimeClient, RoughtimeServer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.hazmat.primitives import hashes


def initiate_key_derivation(target_addr, target_port, client_cert):
    # Connect
    tx_sock = zmq.Context().instance().socket(zmq.PAIR)
    tx_sock.connect('tcp://{}:{}'.format(target_addr, target_port))

    # TLS like key derivation: Round 1    
    client_secret = secrets.token_urlsafe(16)
    tx_sock.send_string('hey', flags=zmq.NOBLOCK)
    tx_sock.send_string(client_secret, flags=zmq.NOBLOCK)

    # Round 2 listen
    message = tx_sock.recv()
    print(message)
    message = tx_sock.recv()
    print(message)
    message = tx_sock.recv()
    print(message)


def listen_key_derivation(addr, port, server_cert):
    # Connect
    rx_sock = zmq.Context().instance().socket(zmq.PAIR)
    rx_sock.bind('tcp://{}:{}'.format(addr, port))

    # Round 1 listen
    message = rx_sock.recv()
    print(message)
    message = rx_sock.recv()
    print(message)

    #Round 2 send cert, response and secret
    server_secret = secrets.token_urlsafe(16)
    rx_sock.send_string('hej back', flags=zmq.NOBLOCK)
    rx_sock.send_string(server_secret, flags=zmq.NOBLOCK)
    rx_sock.send(server_cert.public_bytes(serialization.Encoding.PEM), flags=zmq.NOBLOCK)


def generate_private_key(filename):
    # Gen private key, n=65537, 2048 keysize
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Write key to a file
    with open(filename, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(b"password")  # todo: Change this with param
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
    public_key = builder.sign(private_key, hashes.SHA256(), default_backend()
                              )

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
    cert = open(filename, "rb")
    cert = x509.load_pem_x509_certificate(cert.read(), default_backend())
    return cert


def import_private_key(filename):
    key_file = open(filename, "rb")
    private_key = serialization.load_pem_private_key(key_file.read(), b'password',
                                                     default_backend())  # todo: replace password with getpass().encode("utf-8")
    return private_key

key = generate_private_key('priv')
details = {'country': 'Se', 'region': 'Skane', 'city': 'stockholm', 'org': 'someCo', 'hostname': 'somesite.com'}
cert = generate_self_signed_cert(key, 'pub', details, 10)
# key = import_private_key('priv')
# cert = import_certificate('pub')
# csr = create_csr(key,details)

# print(sign_csr(csr,cert,key,10))

if sys.argv[1] == 's':
    listen_key_derivation(sys.argv[2], sys.argv[3], cert)
else:
    initiate_key_derivation(sys.argv[2], sys.argv[3], '')