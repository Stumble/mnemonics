# -*- coding: utf-8 -*-

import vcb_db
import time
import mnemonic as mnc
import datetime
def do_remember(word, word_time):
    last_remember = datetime.datetime.fromtimestamp(word_time).strftime('%m-%d %H:%M:%S');
    review_cnt = vcb_db.get_word_review_cnt(word);
    print("---------------------")
    print (">>" +last_remember + "(" + str(review_cnt) + ")" + ":" + word);
    while True:
        is_remember = raw_input();
        if is_remember == 'y':
            return True;
        elif is_remember == 'n':
            return False;
        elif is_remember == 'b':
            vcb_db.ban_this_word(word);
            return True;
        else:
            print ("input error");


def active_insert(words_que, to_insert):
    i = 0;
    for word_t in words_que:
        i += 1;
        if to_insert[1] <= word_t[1]:
            words_que.insert(i, to_insert);
            return True;

    words_que.insert(i, to_insert);

def remember_act(words_que, word):
    # words_que.append(word);
    word_tuple = vcb_db.remember_word(word);
    active_insert(words_que, word_tuple);
    pass;


def not_remember_act(words_que, word):
    # words_que.append(word);
    word_tuple = vcb_db.not_remember_word(word);
    active_insert(words_que, word_tuple);
    pass;

def review_mode():
    words_queue = vcb_db.get_need_words_queue();
    turn_rest = len(words_queue);
    while len(words_queue) > 0 :

        turn_rest -= 1;
        if turn_rest <= 0:
            print ("new turn: ");
            turn_rest = len (words_queue);

        word_t = words_queue.pop(0);
        word = word_t[0];
        word_time = word_t[1];
        if int(time.time()) < word_time:
            continue;
        if do_remember(word, word_time):
            remember_act(words_queue, word);
        else:
            not_remember_act(words_queue, word);
        mnc.show_mnc(word);
        print ("rest: ~ " + str(turn_rest));


def insert_mode():
    nlist = raw_input("please input the list number: ");
    while True:
        word = raw_input(">>>> input the word:");
        if word == 'ou':
            break;
        vcb_db.insert_word(word, nlist);
        mnc.show_mnc(word);


# funciton start here
choice = raw_input("please choose the working mode:\nr:review.\ni:insert\nm:domore\n")
if choice == 'r':
    review_mode();
elif choice == 'i':
    insert_mode();
else:
    print ("error input");
