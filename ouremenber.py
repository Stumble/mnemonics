# -*- coding: utf-8 -*-

import vcb_db
import time
import mnemonic as mnc
import datetime
import os
import sys
from libs import getch

# to use utf-8 decode
reload(sys)
sys.setdefaultencoding('utf-8')


def show_def(word):
    if vcb_db.is_def_in_db(word):
        chn_def, mnc_def = vcb_db.get_word_def_from_db(word)
        print(word + ":")
        # print (chn_def.encode('utf8'));
        print(chn_def)
        print(mnc_def)
    else:
        chn_def, mnc_def = mnc.show_mnc(word)
        vcb_db.update_word_def(word, chn_def, mnc_def)


def do_remember(word, word_time):
    last_remember = datetime.datetime.fromtimestamp(word_time).strftime(
        '%m-%d %H:%M:%S')
    review_cnt = vcb_db.get_word_review_cnt(word)
    print("")
    print("---------------------")
    while True:
        print(">>" + last_remember + "(" + str(review_cnt) + ")" + " " + word +
              ":")
        is_remember = getch.getch()
        if is_remember == 'u':  # yes
            return True
        elif is_remember == 'i':  # no
            return False
        elif is_remember == 'j':  # show
            show_def(word)
            continue
        elif is_remember == 'b':  # ban
            vcb_db.ban_this_word(word)
            return True
        elif is_remember == 'k':  # clear
            os.system('clear')
            continue
        elif is_remember == 'q':  # quit
            exit(0)
        else:
            print("input error")


def active_insert(words_que, to_insert, is_hotword=False):
    i = 0
    for word_t in words_que:
        i += 1
        if is_hotword and i >= 15:
            words_que.insert(i, to_insert)
            return True
        if to_insert[1] <= word_t[1]:
            words_que.insert(i, to_insert)
            return True

    words_que.insert(i, to_insert)


def remember_act(words_que, word):
    # words_que.append(word);
    word_tuple = vcb_db.remember_word(word)
    active_insert(words_que, word_tuple)
    pass


def not_remember_act(words_que, word):
    # words_que.append(word);
    word_tuple = vcb_db.not_remember_word(word)
    active_insert(words_que, word_tuple, True)
    pass


def review_mode(lst_num=None):
    words_queue = vcb_db.get_need_words_queue(lst_num)
    do_review(words_queue)


def challenge_mode():
    words_queue = vcb_db.get_need_words_queue(None, 20)
    do_review(words_queue)


def do_review(words_queue):
    turn_rest = len(words_queue)
    while len(words_queue) > 0:

        turn_rest -= 1
        if turn_rest <= 0:
            print("new turn: ")
            turn_rest = len(words_queue)

        word_t = words_queue.pop(0)
        word = word_t[0]
        word_time = word_t[1]
        if int(time.time()) < word_time:
            continue
        if do_remember(word, word_time):
            remember_act(words_queue, word)
        else:
            not_remember_act(words_queue, word)
        show_def(word)
        print("rest: ~ " + str(turn_rest))


def insert_mode():
    nlist = raw_input("please input the list number: ")
    while True:
        word = raw_input(">>>> input the word:")
        word = word.strip()
        if word == '':
            os.system('clear')
            continue
        if word == 'ou':
            break
        vcb_db.insert_word(word, nlist)
        show_def(word)


def update_word_def():
    words_arr = vcb_db.get_all_words()
    for word in words_arr:
        if vcb_db.is_def_in_db(word):
            continue
        print(word)
        chn_def, mnc_def = mnc.show_mnc(word)
        vcb_db.update_word_def(word, chn_def, mnc_def)
    pass


def spelling_closest(word):
    words_arr = vcb_db.get_all_words()

# funciton start here
words_in_queue = vcb_db.get_inqueue_number()
print("words in queue:" + str(words_in_queue))
choice = raw_input(
    "please choose the working mode:\nr:review.\ni:insert\nm:domore\nc:challenge-Mode(20)\n")
if choice == 'r':
    review_mode()
elif choice == 'i':
    insert_mode()
elif choice == 'lr':
    lst_num = raw_input("please input the list id:")
    review_mode(lst_num)
elif choice == 'update':
    update_word_def()
elif choice == 'c':
    challenge_mode()
elif choice == 'e':
    enable_number = raw_input(
        "please input the number of words you want to fuck today:")
    vcb_db.enable_word(int(enable_number))
else:
    print("error input")
