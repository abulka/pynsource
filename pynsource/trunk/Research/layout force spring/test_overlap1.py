import unittest

class MathLibraryTests(unittest.TestCase):
    def test1Plus1Equals2(self):
        self.assertEqual(1+1, 2)
    
    def test1Plus1Equals2a(self):
        self.assertEqual(1+1, 2)
    
    def test1Plus1Equals2aaa(self):
        print 'aaa'
        self.assertEqual(1+1, 2)
        
    def test1Plus1Equals2aaaaaaa(self):
        self.assertEqual(1+1, 2)
        
if __name__ == "__main__":
    unittest.main()
