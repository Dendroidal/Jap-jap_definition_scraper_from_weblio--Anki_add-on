# -*- coding: utf-8 -*-
#
# This module handles how the add-on
# processes and formats the definitions obtained from weblio.jp

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import urllib.error
import re


# sets the default number of subdefinitions displayed
sub_def_cnt = 3


# allows for sub_def_cnt to be changed when importing
def change_sub_def_cnt(n):
    global sub_def_cnt
    sub_def_cnt = n


# Builds and fetches the data for a word

######################################

class WordData:
    def __init__(self, word):
        self.word = word
        self.url = ("http://www.weblio.jp/content/"
                    + urllib.parse.quote(word.encode('utf-8')))

    def fetch_def(self):
        self.definitions = []
        self.source = urllib.request.urlopen(self.url)
        self.soup = BeautifulSoup(self.source, features="html.parser")

        kijis = self.soup.find_all('div', {'class': "kiji"})

        for kiji in kijis:
            if kiji.find('div', {'class': "Sgkdj"}):
                self.definitions.append(WordDefinition(kiji, self.word))


class WordDefinition:
    def __init__(self, kiji, word):
        self.head = kiji.find('h2', {'class': 'midashigo'})
        self.body = kiji.find('div', {'class': 'Sgkdj'})
        self.word = word
        self.kanji = word
        self.stem = word

        self.find_kanji_yomikata()
        self.find_lines()

    def find_kanji_yomikata(self):
        prekanji = re.findall(r"【(.*)】", self.head.get_text())
        if prekanji:
            self.kanji = re.sub(r"[（）×]", "", prekanji[0])
            self.kanji = re.sub(r"／", "・", self.kanji)
        preyomikata = re.match(r"[^〔〕【】]*", self.head.get_text())
        if preyomikata:
            self.yomikata = re.sub(r"‐", "", preyomikata[0])
            if '・' in self.yomikata:
                suff = self.yomikata.split('・')[-1]
                self.yomikata = re.sub(r'・', '', self.yomikata)
                self.stem = re.sub(suff+'$', '', self.kanji)

    def find_lines(self):
        pieces = self.body.find_all('p', {})
        self.sublines = [DefinitionLine(piece, self.stem) for piece in pieces]

    def display_def(self):
        return (f'{self.kanji}{f"[{self.yomikata}]" if self.yomikata else ""}' +
                ''.join(l.display_line()
                        for l in self.sublines[:sub_def_cnt] if l.display_line()
                        ).strip()
                ).replace(' ', '')


class DefinitionLine:

    def __init__(self, soup, stem):
        self.sublines = []
        self.raw_text = soup.text
        self.raw_text = re.sub(r'^［名］\(スル\)', '', self.raw_text)
        self.raw_text = re.sub(r'^［動ラ下一］.*［ラ下二］', '', self.raw_text)
        self.raw_text = re.sub(r'^［動サ変］.*［サ変］', '', self.raw_text)
        self.raw_text = re.sub(r'^［動ラ五（四）］', '', self.raw_text)
        self.marker = ''
        num = re.findall(r'^\d+', self.raw_text)
        if num and 0 < int(num[0]) < 10:
            self.marker = ' ①②③④⑤⑥⑦⑧⑨'[int(num[0])]

        self.main_text = re.sub(r'^\d+', '', self.raw_text)

        self.main_text = re.sub(r'「.*?―・?.*?」',
                                lambda ex: re.sub(r'―・?', stem, ex.group(0)),
                                self.main_text)

    def display_line(self):
        if not self.main_text:
            return ''
        text = '　' + self.marker + '：　' + \
            self.main_text + \
            '<br>' + \
            ''.join(sub.display_line() for sub in self.sublines[:sub_def_cnt])
        return text


# Extra code for barebones support for Chinese weblio
# (note: this feature is quite basic and "not official",
# and will receive no further support.)


class ChineseWordData:
    def __init__(self, word):
        self.word = word
        self.url = ("https://cjjc.weblio.jp/content/"
                    + urllib.parse.quote(word.encode('utf-8')))

    def fetch_def(self):
        self.definitions = []
        self.source = urllib.request.urlopen(self.url)
        self.soup = BeautifulSoup(self.source, features="html.parser")

        Midashigos = self.soup.find_all('h2', {'class': "midashigo"})
        Cgkgj = self.soup.find_all('div', {'class': "Cgkgj"})

        self.definitions = []
        for h, b in list(zip(Midashigos, Cgkgj)):
            self.definitions.append(ChineseWordDefinition(h, b, self.word))


class ChineseWordDefinition:
    def __init__(self, head, body, word):
        self.word = word
        self.body = body

    def display_def(self):
        pieces = self.body.find_all('div', {'class': 'level0'})
        if pieces:
            return self.word + '<br>' + '<br>'.join(p.get_text() for p in pieces)
        return 'KATTY KAT'


# Code below is auxiliary code used when debugging formatting issues

if __name__ == '__main__':
    import os
    import io
    path = os.path.dirname(__file__)

    data = WordData('手間取る')
    data.fetch_def()
    print(len(data.definitions))
    with io.open(os.path.join(path, 'test.txt'), 'w', encoding='utf-8') as f:
        f.write(data.definitions[0].yomikata + '\n')
        f.write(data.definitions[0].kanji + '\n')
        f.write(data.definitions[0].stem + '\n')
        f.write(data.definitions[0].display_def())
