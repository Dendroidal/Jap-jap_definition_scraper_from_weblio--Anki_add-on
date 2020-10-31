import os
import json
import threading
import unittest
import io

from definition_formatter import WordData


class TestDefinitions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__), "test_def_form.json")
        with io.open(path, 'r', encoding="utf-8") as data:
            cls.data = json.load(data)
            print(f"Starting the tests. {len(cls.data.keys())} words to be tested.")
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
                    self.data[w]['definitions'][i]['yomikata'],
                    'Issue with definition {} of word "{}"'.format(
                        i, self.data[w]['romaji'])
                )

    def test_kanji(self):
        for w in self.data:
            for i, _ in enumerate(self.data[w]['definitions']):
                self.assertEqual(
                    self.data[w]['worddata'].definitions[i].kanji,
                    self.data[w]['definitions'][i]['kanji'],
                    'Issue with definition {}'.format(i)
                )

    def test_stem(self):
        for w in self.data:
            for i, _ in enumerate(self.data[w]['definitions']):
                self.assertEqual(
                    self.data[w]['worddata'].definitions[i].stem,
                    self.data[w]['definitions'][i]['stem'],
                    'Issue with definition {}'.format(i)
                )

    def test_text(self):
        for w in self.data:
            for i, _ in enumerate(self.data[w]['definitions']):
                self.assertEqual(
                    self.data[w]['worddata'].definitions[i].display_def(),
                    self.data[w]['definitions'][i]['text'],
                    'Issue with definition {} of word "{}"'.format(
                        i, self.data[w]['romaji'])
                )


if __name__ == "__main__":
    unittest.main()
