import unittest
from prymate import objects


class TestObjects(unittest.TestCase):
    def test_string_hashkey(self):
        hello1 = objects.String("Hello World")
        hello2 = objects.String("Hello World")
        diff1 = objects.String("My name is johnny")
        diff2 = objects.String("My name is johnny")

        self.assertEqual(
            hello1.hashkey(),
            hello2.hashkey(),
            "strings with same content have different hash keys",
        )

        self.assertEqual(
            diff1.hashkey(),
            diff2.hashkey(),
            "strings with same content have different hash keys",
        )

        self.assertNotEqual(
            hello1.hashkey(),
            diff1.hashkey(),
            "strings with different content have same hash keys",
        )


if __name__ == "__main__":
    unittest.main()
