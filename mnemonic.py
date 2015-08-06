import urllib
from bs4 import BeautifulSoup
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

web_url = 'http://mnemonicdictionary.com/';

query_string = "?word=";

save_dir = "/home/stumble/.mnemonic/"

def readfile(fname):
    file_object = open(fname)
    try:
        html_doc = file_object.read()
    finally:
        file_object.close()
    return html_doc

def get_page_of_word(word):
    # open(save_dir , word).close()
    path_and_name = save_dir + word;
    if os.path.isfile(path_and_name):
        print ("cached word");
        pass;
    else:
        urllib.urlretrieve(web_url + query_string + word, path_and_name);
    return readfile(path_and_name);

def get_soup(data):
    return BeautifulSoup(data, from_encoding='utf-8')

# query_word = str(raw_input("remenber this word: "));
query_word = sys.argv[1];
word_page = get_page_of_word(query_word);
soup = get_soup(word_page);
texts = soup.findAll(text=True);

# for string in soup.stripped_strings:
    # print(repr(string))

def print_string(x):
    print (x.string.strip());

def print_mnemonics(mnemonics):
    print ('------------------mnemonics-----------------');
    for i_cursor in mnemonics:
        sentence = i_cursor.next_sibling;
        print_string(sentence);
        print ('>>>>>>>>>>><<<<<<<<<<');



for link in soup.findAll('u'):
    if link.string == 'Definition':
        dict_def = link.next_sibling.next_sibling;
        print ("Def:" + dict_def.strip());
    elif link.string == 'Synonyms':
        synonyms = link.parent.find_all('a');
        # map(lambda x: print_string(x, "Synonyms"), synonyms);
    elif link.string == 'Example Sentence':
        examples = link.parent.find_all('li');
        # map(lambda x: print_string(x), examples);
    elif link.string.find('Mnemonics (Memory Aids) for') is not -1:
        print_mnemonics(link.parent.find_all('i','icon-lightbulb'));
        pass;
    else:
        pass;
