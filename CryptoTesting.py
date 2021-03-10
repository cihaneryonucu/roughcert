import unittest
import Crypto

class CryptoTesting(unittest.TestCase):

    #Test whether the generated key is an RSA private key or not
    def test_is_private_key(self):
        self.assertIsInstance(Crypto.generate_private_key('testKey.pem'),Crypto.rsa.RSAPrivateKey)

    # Test the import function whether it is a RSA private key, meaning it importaed correctly or not
    def test_is_imported_key_private_key(self):
        Crypto.generate_private_key('testKey.pem')
        self.assertIsInstance(Crypto.import_private_key('testKey.pem'),Crypto.rsa.RSAPrivateKey)

    

if __name__ == '__main__':
    unittest.main()