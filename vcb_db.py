#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import time
import sys
import random

# to use utf-8 decode
reload(sys)
sys.setdefaultencoding('utf-8')

conn = sqlite3.connect('vcb_data.db')
conn.isolation_level = None
cursor = conn.cursor()

remember_interval = [15, 60, 300, 1800, 12600, 100800, 100800*2, 100800*3, 100800 * 5];
remember_max = 8;
shuffle_group = 7;
# print("opened");

# def get_all_words():
#     try:
#         cursor.execute("select * from words;");
#     except sqlite3.Error as e:
#         print ("An error occurred:", e.args[0]);
#     return (cursor.fetchall());

# 获得当前在复习计划中的单词，sadfsadf
# 满足以下条件：
# 已知次数 (1,2,3,4,5,6,7,8,9)
# 对应间隔时间(秒) (15, 60, 300, 1800, 12600, 100800, 100800*2, 100800*3, 100800 * 5)
# 返回一个队列

def close():
    conn.close();


def group_shuffle(lst):
    n_words = len(lst);
    for i in xrange(0, n_words, shuffle_group):
        copy = lst[i: i + shuffle_group];
        random.shuffle(copy)
        lst[i: i + shuffle_group] = copy;

    return lst;


def get_need_words_queue(thelist=None):
    words_que = [];
    if thelist == None:
        words = cursor.execute("select *  from words;");
    else:
        words = cursor.execute("select * from words where list = ?", [thelist]);
    now_time = int(time.time());
    for word in words:
        n_remember = word[1];
        last_know = word[2];
        if n_remember == remember_max:
            continue;
        if last_know + remember_interval[n_remember] <= now_time:
            words_que.append((word[0], last_know + remember_interval[n_remember]));

    rtn_que = sorted(words_que, key = lambda x: x[1]);

    rtn_que = group_shuffle(rtn_que);

    return rtn_que;

def get_word_review_cnt(word):
    cursor.execute("select review_cnt from words where word = ?", [word]);
    review_cnt = cursor.fetchone();
    if len(review_cnt) == 1:
        return review_cnt[0];
    else:
        return False;

def remember_word(word):
    now_time = int(time.time());
    try:
        cursor.execute("UPDATE words SET review_cnt = min(review_cnt + 1, 8), last_know = ? WHERE word = ?;", [now_time, word]);
        cursor.execute("select review_cnt from words where word = ?", [word]);
        review_cnt = cursor.fetchone()[0];
        conn.commit();
        return (word, remember_interval[review_cnt] + int(time.time()));
    except sqlite3.Error as e:
        print ("sql error", e.args[0]);
        return False;

def ban_this_word(word):
    now_time = int(time.time());
    try:
        cursor.execute("UPDATE words SET review_cnt = 8, last_know = ? WHERE word = ?;", [now_time, word]);
        cursor.execute("select review_cnt from words where word = ?", [word]);
        review_cnt = cursor.fetchone()[0];
        conn.commit();
        return (word, remember_interval[review_cnt] + int(time.time()));
    except sqlite3.Error as e:
        print ("sql error", e.args[0]);
        return False;

def not_remember_word(word):
    now_time = int(time.time());
    try:
        cursor.execute("UPDATE words SET review_cnt = max(review_cnt - 3, 0), last_know = ? WHERE word = ?;", [now_time, word]);
        cursor.execute("select review_cnt from words where word = ?", [word]);
        review_cnt = cursor.fetchone()[0];
        conn.commit();
        return (word, remember_interval[review_cnt] + int(time.time()));
    except sqlite3.Error as e:
        print ("sql error", e.args[0]);
        return False;


def insert_word(word, list_number):
    word_data = (word, 0, int(time.time()), list_number, 0);
    try:
        cursor.execute("INSERT INTO words VALUES (?,?,?,?,?)", word_data);
        conn.commit();
        return True;
    except sqlite3.Error as e:
        print ("sql error:", e.args[0]);
        return False;



# data = get_need_words_queue();
# word = raw_input();
# print not_remember_word(word);

# word = raw_input();
# nlist = raw_input();

# insert_word_db(word, nlist);



