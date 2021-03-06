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

remember_interval = [15, 300, 12 * 3600, 24 * 3600, 2 * 24 * 3600,
                     4 * 24 * 3600, 7 * 24 * 3600, 15 * 24 * 3600]
remember_max = 7
shuffle_group = 20

# 单词队列状态
WORD_STATUS_NOT_IN_QUEUE = 0
WORD_STATUS_IN_QUEUE = 1
WORD_STATUS_KNOWN = 2

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
    conn.close()


def group_shuffle(lst):
    n_words = len(lst)
    for i in xrange(0, n_words, shuffle_group):
        copy = lst[i:i + shuffle_group]
        random.shuffle(copy)
        lst[i:i + shuffle_group] = copy

    return lst


def get_all_words():
    words_arr = []
    words = cursor.execute("select *  from words;")
    for word in words:
        words_arr.append(word[0])
    return words_arr


def update_word_def(word, chn_def, mnc_def):
    try:
        cursor.execute("INSERT OR REPLACE INTO chn VALUES (?,?)", [word,
                                                                   chn_def])
        cursor.execute("INSERT OR REPLACE INTO mnc VALUES (?,?)", [word,
                                                                   mnc_def])
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("[update_word_def]: insert or replace error", e.args[0])
        return False


def is_def_in_db(word):
    rtn = cursor.execute("select count(*) AS rtn from chn where word = ?;",
                         [word]).fetchone()[0]
    if rtn == 1:
        return True
    else:
        return False


def get_word_def_from_db(word):
    chn_def = cursor.execute("select * from chn where word = ?;",
                             [word]).fetchone()[1]
    mnc_def = cursor.execute("select * from mnc where word = ?;",
                             [word]).fetchone()[1]
    return chn_def, mnc_def


def get_need_words_queue(thelist=None, nGroup=500):
    words_que = []
    if thelist == None:
        words = cursor.execute("select *  from words where status = ?;",
                               [WORD_STATUS_IN_QUEUE])
    else:
        words = cursor.execute(
            "select * from words where list = ? and status = ?",
            [thelist, WORD_STATUS_IN_QUEUE])
    now_time = int(time.time())
    for word in words:
        n_remember = min(word[1], remember_max)
        last_know = word[2]
        if n_remember == remember_max:
            continue
        if last_know + remember_interval[n_remember] <= now_time:
            words_que.append((word[0], last_know + remember_interval[
                n_remember]))

    rtn_que = sorted(words_que, key=lambda x: x[1])

    rtn_que = group_shuffle(rtn_que)

    return rtn_que[0:nGroup]


def get_word_review_cnt(word):
    cursor.execute("select review_cnt from words where word = ?", [word])
    review_cnt = cursor.fetchone()
    if len(review_cnt) == 1:
        return review_cnt[0]
    else:
        return False


def remember_word(word):
    now_time = int(time.time())
    try:
        cursor.execute(
            "UPDATE words SET review_cnt = min(review_cnt + 1, ?), last_know = ? WHERE word = ?;",
            [remember_max, now_time, word])
        cursor.execute("select review_cnt from words where word = ?", [word])
        conn.commit()
        review_cnt = cursor.fetchone()[0]
        if review_cnt == remember_max:
            ban_this_word(word)
        return (word, remember_interval[review_cnt] + int(time.time()))
    except sqlite3.Error as e:
        print("sql error", e.args[0])
        return False


def ban_this_word(word):
    now_time = int(time.time())
    try:
        cursor.execute(
            "UPDATE words SET status = ?, last_know = ? WHERE word = ?;",
            [WORD_STATUS_KNOWN, now_time, word])
        cursor.execute("select review_cnt from words where word = ?", [word])
        review_cnt = cursor.fetchone()[0]
        conn.commit()
        return (word, remember_interval[review_cnt] + int(time.time()))
    except sqlite3.Error as e:
        print("sql error", e.args[0])
        return False


def not_remember_word(word):
    now_time = int(time.time())
    try:
        cursor.execute(
            "UPDATE words SET review_cnt = max(review_cnt / 2, 0), last_know = ? WHERE word = ?;",
            [now_time, word])
        cursor.execute("select review_cnt from words where word = ?", [word])
        review_cnt = cursor.fetchone()[0]
        conn.commit()
        return (word, remember_interval[review_cnt] + int(time.time()))
    except sqlite3.Error as e:
        print("sql error", e.args[0])
        return False


def insert_word(word, list_number):
    word_data = (word, 0, int(time.time()), list_number, WORD_STATUS_IN_QUEUE)
    try:
        cursor.execute("INSERT INTO words VALUES (?,?,?,?,?)", word_data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("sql error:", e.args[0])
        re_enable_single_word(word, list_number)
        return False


def re_enable_single_word(word, list_number):
    try:
        cursor.execute("UPDATE words SET status = ?, list = ? WHERE word = ?;",
                       [WORD_STATUS_IN_QUEUE, list_number, word])
        conn.commit()
    except sqlite3.Error as e:
        print("sql error:", e.args[0])


def enable_word(count=20):
    cursor.execute("UPDATE words SET status = ? WHERE status = ? LIMIT ?;",
                   [WORD_STATUS_IN_QUEUE, WORD_STATUS_NOT_IN_QUEUE, count])
    conn.commit()


def get_inqueue_number():
    rtn = cursor.execute("select count(*) AS rtn from words where status = ?;",
                         [WORD_STATUS_IN_QUEUE]).fetchone()[0]
    return rtn

# data = get_need_words_queue();
# word = raw_input();
# print not_remember_word(word);

# word = raw_input();
# nlist = raw_input();

# insert_word_db(word, nlist);
