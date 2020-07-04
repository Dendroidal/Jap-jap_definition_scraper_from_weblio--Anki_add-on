import unittest
from definition_formatter import WordData


class TestDefinitions(unittest.TestCase):

    def test_yomikata(self):
        data = WordData('地平')
        data.fetch_def()
        self.assertEqual(data.definitions[0].yomikata, "ちへい")


if __name__ == "__main__":
    unittest.main()
