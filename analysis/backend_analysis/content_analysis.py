# -*- coding:utf-8 -*-

import pymysql
import math

#浏览量统计
def get_pv_map():
    pv_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select newsId, count(1) as cnt from pv_news_log  group by newsId '
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

#转发量统计
def get_transmit_map():
    transmit_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select newsId, count(1) as cnt from transmit_news group by newsId '
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

#新闻ID去重
def get_all_news_id():
    newsId_set = []
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select distinct newsId  from news '
        cursor.execute(sql)
        result = cursor.fetchall()
        for newsId in result:
            newsId_set.append(newsId[0])
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return newsId_set

#新闻传播热度计算
def compute_news_hot():
    rst = []
    news_hot_map = {}
    newsId_set = get_all_news_id()
    transmit_map = get_transmit_map()
    pv_map = get_pv_map()
    for newsId in newsId_set:
        news_transmit_cnt = 0
        if newsId in transmit_map:
            news_transmit_cnt = transmit_map[newsId]
        news_pv_cnt = 0
        if newsId in pv_map:
            news_pv_cnt = pv_map[newsId]
        hot_value = 0.6*math.log(news_transmit_cnt+1, 10) + 0.4*math.log(news_pv_cnt+1, 10)#pv权重0.4，transmit权重0.6
        hot_value = float('%.2f' % hot_value)
        print (newsId, news_transmit_cnt, news_pv_cnt, hot_value)
        rst.append([newsId, news_transmit_cnt, news_pv_cnt, hot_value])
    return rst


#转发路径跟踪
def transmit_tree():
    print('todo')



#compute_news_hot()

