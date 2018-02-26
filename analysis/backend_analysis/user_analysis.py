# -*- coding:utf-8 -*-

import pymysql
import math

#用户全局浏览量统计
def get_pv_map():
    pv_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select viewerId, count(1) as cnt from pv_news_log  group by viewerId '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId, cnt in result:
            pv_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return pv_map

#用户全局转发量统计
def get_transmit_map():
    transmit_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select viewerId, count(1) as cnt from transmit_news group by viewerId '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId, cnt in result:
            transmit_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_map


#用户全局被浏览量统计
def get_re_pv_map():
    pv_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select shareId, count(1) as cnt from pv_news_log  group by shareId '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId, cnt in result:
            pv_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return pv_map


#用户全局被转发量统计
def get_re_transmit_map():
    transmit_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select shareId, count(1) as cnt from transmit_news group by shareId '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId, cnt in result:
            transmit_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_map


#用户平均、最大被浏览量统计
def get_avg_max_pv_map():
    pv_avg_max_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT shareId,AVG(cnt) as pv_avg,MAX(cnt) as pv_max FROM (SELECT newsId,shareId,  COUNT(1) AS cnt FROM pv_news_log GROUP BY newsId,shareId) AS total GROUP BY shareId '
        cursor.execute(sql)
        result = cursor.fetchall()
        for shareId, pv_avg,pv_max  in result:
            pv_avg_max_map[shareId] = [pv_avg,pv_max]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return pv_avg_max_map


#用户平均、最大被转发量统计
def get_avg_max_transmit_map():
    transmit_avg_max_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT shareId,AVG(cnt) as transmit_avg,MAX(cnt) as transmit_max FROM (SELECT newsId,shareId,  COUNT(1) AS cnt FROM transmit_news GROUP BY newsId,shareId) AS total GROUP BY shareId  '
        cursor.execute(sql)
        result = cursor.fetchall()
        for shareId, transmit_avg,transmit_max  in result:
            transmit_avg_max_map[shareId] = [transmit_avg,transmit_max]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_avg_max_map


#用户ID去重
def get_all_user_id():
    userId_set = []
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select distinct userId  from user '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId in result:
            userId_set.append(newsId[0])
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return userId_set

#用户全局传播影响力计算
def compute_users_hot():
    rst = []
    user_hot_map = {}
    userId_set = get_all_user_id()
    transmit_map = get_transmit_map()
    pv_map = get_pv_map()
    re_transmit_map = get_re_transmit_map()
    re_pv_map = get_re_pv_map()
    avg_max_pv_map = get_avg_max_pv_map()
    avg_max_transmit_map = get_avg_max_transmit_map()

    for userId in userId_set:
        user_transmit_cnt = 0
        if userId in transmit_map:
            user_transmit_cnt = transmit_map[userId]
        user_pv_cnt = 0
        if userId in pv_map:
            news_pv_cnt = pv_map[userId]
        user_re_transmit_cnt = 0
        if userId in re_transmit_map:
            user_re_transmit_cnt = re_transmit_map[userId]
        user_re_pv_cnt = 0
        if userId in re_pv_map:
            user_re_pv_cnt = re_pv_map[userId]
        user_avg_pv_cnt = 0
        user_max_pv_cnt = 0
        if userId in avg_max_pv_map:
            user_avg_pv_cnt = avg_max_pv_map[userId][0]
            user_max_pv_cnt = avg_max_pv_map[userId][1]
        user_avg_transmit_cnt = 0
        user_max_transmit_cnt = 0
        if userId in avg_max_transmit_map:
            user_avg_transmit_cnt = avg_max_transmit_map[userId][0]
            user_max_transmit_cnt = avg_max_transmit_map[userId][1]
        hot_value = 0.1*(0.8*math.log(user_transmit_cnt+1, 10)+0.2*math.log(user_pv_cnt+1, 10))+\
                    0.2 * (0.8 * math.log(user_re_transmit_cnt + 1, 10) + 0.2 * math.log(user_re_pv_cnt + 1, 10)) +\
                    0.3 * (0.8 * math.log(user_avg_transmit_cnt + 1, 10) + 0.2 * math.log(user_avg_pv_cnt + 1, 10)) +\
                    0.4 * (0.8 * math.log(user_max_transmit_cnt + 1, 10) + 0.2 * math.log(user_max_pv_cnt + 1, 10))
        #阅读、转发权重分摊为0.2、0.8，
        # 用户主动阅读量、转发量权重0.1，
        # 全局被阅读、被转发量权重0.2，
        # 用户平均被阅读、被转发量权重各0.3，
        # 用户最大被阅读、被转发量权重各0.4，
        hot_value = float('%.2f' % hot_value)
        print (userId, user_transmit_cnt, user_pv_cnt, user_re_transmit_cnt, user_re_pv_cnt, user_avg_transmit_cnt, user_avg_pv_cnt, user_max_transmit_cnt,user_max_pv_cnt, hot_value)
        rst.append([userId, user_transmit_cnt, user_pv_cnt, user_re_transmit_cnt, user_re_pv_cnt, user_avg_transmit_cnt, user_avg_pv_cnt, user_max_transmit_cnt,user_max_pv_cnt, hot_value])
    return rst


#compute_users_hot()

