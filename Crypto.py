import ed25519, cryptography
from pyroughtime import RoughtimeClient, RoughtimeServer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography import x509
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

# key = generate_private_key('a')
# cert = generate_cert(key,'b',{'country':'Se','region':'Skane','city':'stockholm','org':'someCo','hostname':'somesite.com'},10)
# print(cert)