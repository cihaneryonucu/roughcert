import unittest
import Crypto


class CryptoTesting(unittest.TestCase):

    # Test whether the generated key is an RSA private key or not
    def test_is_private_key(self):
        self.assertIsInstance(Crypto.generate_private_key('testKey.pem'), Crypto.rsa.RSAPrivateKey)

    # Test the import function whether it is a RSA private key, meaning it importaed correctly or not
    def test_is_imported_key_private_key(self):
        Crypto.generate_private_key('testKey.pem')
        self.assertIsInstance(Crypto.import_private_key('testKey.pem'), Crypto.rsa.RSAPrivateKey)

    # Test is the created self signed certificate is done properly
    def test_is_self_signed_certificate(self):
        private = Crypto.generate_private_key('testKey.pem')
        details = {'country': 'Se', 'region': 'Skane', 'city': 'stockholm', 'org': 'someCo', 'hostname': 'somesite.com'}
        cert = Crypto.generate_self_signed_cert(private, 'testSelfSigned.pem', details, 10)
        self.assertIsInstance(cert, Crypto.x509.Certificate)  # Is it a certificate?
        self.assertGreater(Crypto.datetime.utcnow() + Crypto.timedelta(days=10),
                           cert.not_valid_before)  # Is validity expires after the creation plus 10 days?

    # This is to test program does not crash if imports wrong key. Also to assert imported file is always private key
    def test_wrong_imported_private_key(self):
        private = Crypto.generate_private_key('testKey.pem')
        details = {'country': 'Se', 'region': 'Skane', 'city': 'stockholm', 'org': 'someCo', 'hostname': 'somesite.com'}
        cert = Crypto.generate_self_signed_cert(private, 'testSelfSigned.pem', details, 10)
        self.assertNotIsInstance(Crypto.import_private_key('testSelfSigned.pem'), Crypto.rsa.RSAPrivateKey)

    # This test whether we import the certificate or not.
    def test_imported_certificate(self):
        private = Crypto.generate_private_key('testKey.pem')
        details = {'country': 'Se', 'region': 'Skane', 'city': 'stockholm', 'org': 'someCo', 'hostname': 'somesite.com'}
        cert = Crypto.generate_self_signed_cert(private, 'testSelfSigned.pem', details, 10)
        self.assertIsInstance(Crypto.import_certificate('testSelfSigned.pem'), Crypto.x509.Certificate)
        # Also verify the signature. Verify returns nothing if verified and raises exception if not verified
        try:
            private.public_key().verify(cert.signature, cert.tbs_certificate_bytes,
                                    Crypto.padding.PKCS1v15(), Crypto.hashes.SHA256())
        except Crypto.cryptography.exceptions.InvalidSignature:
            self.fail('Verification of signature failed')

    # This is to test program does not crash if imports cert. Also to assert imported file is always certificate
    def test_wrong_imported_cert(self):
        private = Crypto.generate_private_key('testKey.pem')
        self.assertNotIsInstance(Crypto.import_certificate('testKey.pem'), Crypto.x509.Certificate)

    # This is to check if the generating CSR works and returns the corresponding class
    def test_is_csr(self):
        private = Crypto.generate_private_key('testKey.pem')
        details = {'country': 'Se', 'region': 'Skane', 'city': 'stockholm', 'org': 'someCo', 'hostname': 'somesite.com'}
        csr = Crypto.create_csr(private, details)
        self.assertIsInstance(csr, Crypto.x509.CertificateSigningRequest)  # Is it a csr?


if __name__ == '__main__':
    unittest.main()
