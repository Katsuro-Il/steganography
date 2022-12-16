import unittest
from main import *


class StegaTest(unittest.TestCase):
    def testEncodeByteLSB(self):
        self.assertEqual(EncodeByteLSB(120, '1'), 121)
        self.assertEqual(EncodeByteLSB(121, '1'), 121)
        self.assertEqual(EncodeByteLSB(120, '0'), 120)
        self.assertEqual(EncodeByteLSB(121, '0'), 120)
        self.assertEqual(EncodeByteLSB(0, '1'), 1)
        self.assertEqual(EncodeByteLSB(0, '0'), 0)
        self.assertEqual(EncodeByteLSB(255, '1'), 255)
        self.assertEqual(EncodeByteLSB(255, '0'), 254)

    def testEncodeBytePM1(self):
        res = EncodeBytePM1(120, '1')
        self.assertTrue(res == 121 or res == 119)
        self.assertEqual(EncodeBytePM1(121, '1'), 121)
        self.assertEqual(EncodeBytePM1(120, '0'), 120)
        res = EncodeBytePM1(121, '0')
        self.assertTrue(res == 120 or res == 122)
        self.assertEqual(EncodeBytePM1(0, '1'), 1)
        self.assertEqual(EncodeBytePM1(0, '0'), 0)
        self.assertEqual(EncodeBytePM1(255, '1'), 255)
        self.assertEqual(EncodeBytePM1(255, '0'), 254)

    def testEncodeByteQIM(self):
        q = 12
        self.assertEqual(EncodeByteQIM(120, '1', q), 126)
        self.assertEqual(EncodeByteQIM(121, '1', q), 126)
        self.assertEqual(EncodeByteQIM(120, '0', q), 120)
        self.assertEqual(EncodeByteQIM(121, '0', q), 120)
        self.assertEqual(EncodeByteQIM(0, '1', q), 6)
        self.assertEqual(EncodeByteQIM(0, '0', q), 0)
        self.assertEqual(EncodeByteQIM(255, '1', q), 255)
        self.assertEqual(EncodeByteQIM(255, '0', q), 252)

if __name__ == "__main__":
    unittest.main()
#print(testEncodeByteLSB())