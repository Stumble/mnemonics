import urllib
from bs4 import BeautifulSoup
import os
import sys

# to use utf-8 decode
reload(sys)
sys.setdefaultencoding('utf-8')

web_url = 'http://mnemonicdictionary.com/'

query_string = "?word="

save_dir = "/home/stumble/.mnemonic/"


def chinese_def(word):
    chn_def_str = ""
    yd_web_url = "http://dict.youdao.com/search?q="
    path_and_name = save_dir + word + '.yd'
    if os.path.isfile(path_and_name):
        pass
    else:
        urllib.urlretrieve(yd_web_url + word, path_and_name)
    yd_page = readfile(path_and_name)
    soup = get_soup(yd_page)
    trans_div = soup.findAll("div", {"class": "trans-container"})
    if len(trans_div) <= 0:
        return False
    for trans in trans_div[0].findAll("li"):
        if trans.string == None:
            continue
        print(trans.string)
        chn_def_str += trans.string.strip()
        chn_def_str += "\n"
    return chn_def_str


def readfile(fname):
    file_object = open(fname)
    try:
        html_doc = file_object.read()
    finally:
        file_object.close()
    return html_doc


def get_page_of_word(word):
    # open(save_dir , word).close()
    path_and_name = save_dir + word
    if os.path.isfile(path_and_name):
        # print ("cached word");
        pass
    else:
        urllib.urlretrieve(web_url + query_string + word, path_and_name)
    return readfile(path_and_name)


def get_soup(data):
    return BeautifulSoup(data, from_encoding='utf-8')


def print_string(x):
    print(x.string.strip())
    return x.string.strip()


def print_mnemonics(mnemonics):
    mnc_str = ""
    mnc_str += '------------------mnemonics-----------------\n'
    print('------------------mnemonics-----------------')
    limit = 0
    for i_cursor in mnemonics:
        limit += 1
        if limit > 5:
            break
        sentence = i_cursor.next_sibling
        mnc_str += print_string(sentence) + "\n"
        mnc_str += '>>>>>>>>>>><<<<<<<<<<\n'
        print('>>>>>>>>>>><<<<<<<<<<')
    return mnc_str


def show_mnc(query_word):

    chinese_def_str = chinese_def(query_word)
    mnc_str = ""
    word_page = get_page_of_word(query_word)
    soup = get_soup(word_page)
    # texts = soup.findAll(text=True);

    for link in soup.findAll('u'):
        if link.string == 'Definition':
            pass
            # dict_def = link.next_sibling.next_sibling;
            # print ("Def:" + dict_def.strip());
        elif link.string == 'Synonyms':
            pass
            # synonyms = link.parent.find_all('a');
            # map(lambda x: print_string(x), synonyms[0:3]);
        elif link.string == 'Example Sentence':
            pass
            # examples = link.parent.find_all('li');
            # map(lambda x: print_string(x), examples);
        elif link.string.find('Mnemonics (Memory Aids) for') is not -1:
            mnc_str = print_mnemonics(
                link.parent.find_all('i', 'icon-lightbulb')
            )
            pass
        else:
            pass
    return chinese_def_str, mnc_str


def main():
    query_word = sys.argv[1]
    show_mnc(query_word)


if __name__ == "__main__":
    main()
