import os
import json
import threading
import unittest

from definition_formatter import WordData


class TestDefinitions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__), "test_def_form.json")
        with open(path, 'r', encoding="utf-8") as data:
            cls.data = json.load(data)
            for w in cls.data:
                cls.data[w]['worddata'] = WordData(cls.data[w]["word"])
                cls.data[w]['thread'] = \
                    threading.Thread(target=cls.data[w]['worddata'].fetch_def)
                cls.data[w]['thread'].start()

            for w in cls.data:
                cls.data[w]['thread'].join()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_yomikata(self):
        for w in self.data:
            for i, _ in enumerate(self.data[w]['definitions']):
                self.assertEqual(
                    self.data[w]['worddata'].definitions[i].yomikata,
                    self.data[w]['definitions'][i]['yomikata']
                )

    def test_text(self):
        for w in self.data:
            for i, _ in enumerate(self.data[w]['definitions']):
                self.assertEqual(
                    self.data[w]['worddata'].definitions[i].display_def(),
                    self.data[w]['definitions'][i]['text']
                )


if __name__ == "__main__":
    unittest.main()
