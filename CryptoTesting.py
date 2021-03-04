import unittest
import Crypto

class CryptoTesting(unittest.TestCase):

    #Test whether the generated key is a private key or not
    def test_is_private_key(self):
        self.assertIsInstance(Crypto.generate_private_key('testKey.pem'),Crypto.rsa.RSAPrivateKey)

if __name__ == '__main__':
    unittest.main()