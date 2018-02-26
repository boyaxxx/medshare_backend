# -*- coding:utf-8 -*-

import pymysql
import math
import time


#浏览量统计
def get_pv(newsId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    pv = 0
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from pv_news_log where newsId=%d and createdAt<=\'%s\'  ' %(newsId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            pv = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return pv

#转发量统计
def get_transmit(newsId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    transmit = 0
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from transmit_news where newsId=%d and createdAt<=\'%s\'  ' %(newsId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            transmit = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit


#覆盖用户统计
def get_user_cover(newsId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    user_cover_cnt = 0
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT DISTINCT viewerId FROM transmit_news WHERE newsId=%d and createdAt<=\'%s\' UNION SELECT DISTINCT viewerId FROM pv_news_log WHERE newsId=%d and createdAt<=\'%s\'  ' %(newsId, time_limit,newsId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            user_cover_cnt = len(result)
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return user_cover_cnt


#新闻最新传播时间
def get_max_news_time(newsId):
    max_news_time = time.strftime("%Y-%m-%d")
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT DATE_FORMAT((SELECT GREATEST(MAX(a.createdAt),MAX(b.createdAt)) FROM transmit_news a,pv_news_log b WHERE a.newsId='+str(newsId)+' AND a.newsId=b.newsId), \'%Y-%m-%d\') '
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            max_news_time = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return max_news_time



#新闻传播热度计算
def compute_news_hot(newsId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    news_transmit_cnt = get_transmit(newsId, time_limit)
    news_pv_cnt = get_pv(newsId, time_limit)
    user_cover_cnt = get_user_cover(newsId, time_limit)
    hot_value = 0.4*math.log(news_transmit_cnt+1, 10) + 0.3*math.log(news_pv_cnt+1, 10) + 0.3*math.log(user_cover_cnt+1, 10)#user_cover权重0.3，pv权重0.3，transmit权重0.4
    hot_value = float('%.2f' % hot_value)
    #print (newsId, news_transmit_cnt, news_pv_cnt, hot_value)
    return hot_value


