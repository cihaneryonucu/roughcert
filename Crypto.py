import ed25519, cryptography
from pyroughtime import RoughtimeClient, RoughtimeServer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography import x509
from getpass import getpass
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def generate_private_key(filename):
    # Gen private key, n=65537, 2048 keysize
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Write key to a file
    with open(filename, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(b"password") # todo: Change this with param
            )
        )

    return key


def generate_self_signed_cert(private_key, filename, cert_details, validity):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, cert_details["country"]),# Sweden
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, cert_details["region"] # Skåne
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert_details["city"]), # Lund
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_details["org"]), # Cihan-Marco Co.
            x509.NameAttribute(NameOID.COMMON_NAME, cert_details["hostname"]), #ce-ms.com
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
            x509.NameAttribute(NameOID.COUNTRY_NAME, cert_details["country"]),# Sweden
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, cert_details["region"] # Skåne
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert_details["city"]), # Lund
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_details["org"]), # Cihan-Marco Co.
            x509.NameAttribute(NameOID.COMMON_NAME, cert_details["hostname"]), #ce-ms.com
        ]
    )

    builder = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
    )
    csr = builder.sign(private_key, hashes.SHA256(), default_backend())

    return csr

def sign_csr(csr, ca_public_key, ca_private_key, validity): #public key is not key.public_key() but the certificate.
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

def import_certificate(filename): # Cert containing public key. This is directly importing the 
    certFile = open(filename, "rb")
    cert = x509.load_pem_x509_certificate(cert.read(), default_backend())
    certFile.close()
    return cert

def import_private_key(filename):
    key_file = open(filename, "rb")
    private_key = serialization.load_pem_private_key(key_file.read(),b'password',default_backend()) #todo: replace password with getpass().encode("utf-8")
    key_file.close()
    return private_key

# key = generate_private_key('priv')
details = {'country':'Se','region':'Skane','city':'stockholm','org':'someCo','hostname':'somesite.com'}
# # cert = generate_self_signed_cert(key,'pub',details,10)
# key = import_private_key('priv')
# cert = import_certificate('pub')
# csr = create_csr(key,details)

# print(sign_csr(csr,cert,key,10))