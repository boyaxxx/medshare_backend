# -*- coding:utf-8 -*-

import pymysql
import math
import time
import pandas as pd


#用户全局浏览量统计
def get_pv(viewerId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    pv = 0
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from pv_news_log  where viewerId = \'%s\' and createdAt<=\'%s\' ' %  (viewerId, time_limit)
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

#用户全局转发量统计
def get_transmit(viewerId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    transmit_cnt = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from transmit_news  where viewerId = \'%s\' and createdAt<=\'%s\' ' % (viewerId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) > 0:
            transmit_cnt = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_cnt


#用户全局被浏览量统计
def get_re_pv(shareId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    re_pv_cnt = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from pv_news_log  where shareId = \'%s\' and createdAt<=\'%s\' ' % (shareId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) > 0:
            re_pv_cnt = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return re_pv_cnt


#用户全局被转发量统计
def get_re_transmit(shareId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    re_transmit_cnt = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select count(1) as cnt from transmit_news  where shareId = \'%s\' and createdAt<=\'%s\' ' % (shareId, time_limit)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) > 0:
            re_transmit_cnt = result[0][0]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return re_transmit_cnt


#用户平均、最大被浏览量统计
def get_avg_max_pv(now_shareId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    rst = (0,0)
    pv_avg_max_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT shareId,AVG(cnt) as pv_avg,MAX(cnt) as pv_max FROM (SELECT newsId,shareId,  COUNT(1) AS cnt FROM pv_news_log where  createdAt<=\'%s\' GROUP BY newsId,shareId) AS total GROUP BY shareId ' % time_limit
        cursor.execute(sql)
        result = cursor.fetchall()
        for shareId, pv_avg,pv_max  in result:
            pv_avg_max_map[shareId] = (pv_avg,pv_max)
        if shareId in pv_avg_max_map:
            rst = pv_avg_max_map[now_shareId]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return rst


#用户平均、最大被转发量统计
def get_avg_max_transmit(now_shareId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    rst = (0,0)
    transmit_avg_max_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT shareId,AVG(cnt) as transmit_avg,MAX(cnt) as transmit_max FROM (SELECT newsId,shareId,  COUNT(1) AS cnt FROM transmit_news where  createdAt<=\'%s\' GROUP BY newsId,shareId) AS total GROUP BY shareId  ' % time_limit
        cursor.execute(sql)
        result = cursor.fetchall()
        for shareId, transmit_avg,transmit_max  in result:
            transmit_avg_max_map[shareId] = (transmit_avg,transmit_max)
        if shareId in transmit_avg_max_map:
            rst = transmit_avg_max_map[now_shareId]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return rst



#用户当前全局传播影响力计算，返回各项详情
def compute_now_users_hot(userId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    user_transmit_cnt = get_transmit(userId, time_limit)
    user_pv_cnt = get_pv(userId, time_limit)
    user_re_transmit_cnt = get_re_transmit(userId, time_limit)
    user_re_pv_cnt = get_re_pv(userId, time_limit)
    avg_max_pv_map = get_avg_max_pv(userId, time_limit)
    avg_max_transmit_map = get_avg_max_transmit(userId, time_limit)
    user_avg_pv_cnt = avg_max_pv_map[0]
    user_max_pv_cnt = avg_max_pv_map[1]
    user_avg_transmit_cnt = avg_max_transmit_map[0]
    user_max_transmit_cnt = avg_max_transmit_map[1]
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
    rst = {}
    rst['user_transmit_cnt'] = user_transmit_cnt
    rst['user_pv_cnt'] = user_pv_cnt
    rst['user_re_transmit_cnt'] = user_re_transmit_cnt
    rst['user_re_pv_cnt'] = user_re_pv_cnt
    rst['user_avg_transmit_cnt'] = user_avg_transmit_cnt
    rst['user_avg_pv_cnt'] = user_avg_pv_cnt
    rst['user_max_transmit_cnt'] = user_max_transmit_cnt
    rst['user_max_pv_cnt'] = user_max_pv_cnt
    rst['hot_value'] = hot_value
    #print (userId, user_transmit_cnt, user_pv_cnt, user_re_transmit_cnt, user_re_pv_cnt, user_avg_transmit_cnt, user_avg_pv_cnt, user_max_transmit_cnt,user_max_pv_cnt, hot_value)
    return rst


#用户历史全局传播影响力计算
def compute_history_users_hot(userId, time_limit=time.strftime("%Y-%m-%d %H:%M:%S")):
    user_transmit_cnt = get_transmit(userId, time_limit)
    user_pv_cnt = get_pv(userId, time_limit)
    user_re_transmit_cnt = get_re_transmit(userId, time_limit)
    user_re_pv_cnt = get_re_pv(userId, time_limit)
    avg_max_pv_map = get_avg_max_pv(userId, time_limit)
    avg_max_transmit_map = get_avg_max_transmit(userId, time_limit)
    user_avg_pv_cnt = avg_max_pv_map[0]
    user_max_pv_cnt = avg_max_pv_map[1]
    user_avg_transmit_cnt = avg_max_transmit_map[0]
    user_max_transmit_cnt = avg_max_transmit_map[1]
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
    #print (userId, user_transmit_cnt, user_pv_cnt, user_re_transmit_cnt, user_re_pv_cnt, user_avg_transmit_cnt, user_avg_pv_cnt, user_max_transmit_cnt,user_max_pv_cnt, hot_value)
    return hot_value


#用户最新活跃时间
def get_max_user_time(viewerId):
    max_news_time = time.strftime("%Y-%m-%d")
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT DATE_FORMAT((SELECT GREATEST(MAX(a.createdAt),MAX(b.createdAt)) FROM transmit_news a,pv_news_log b WHERE a.viewerId=\''+str(viewerId)+'\' AND a.viewerId=b.viewerId), \'%Y-%m-%d\') '
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


#用户当天转发行为统计
def get_transmit_date_cnt_map(viewerId):
    date_cnt_map ={}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\'),COUNT(1) FROM transmit_news WHERE viewerId=\''+viewerId+'\' GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\')'
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            for rst in result:
                date_cnt_map[rst[0]] = rst[1]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return date_cnt_map


#用户当天浏览行为统计
def get_pv_date_cnt_map(viewerId):
    date_cnt_map ={}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\'),COUNT(1) FROM pv_news_log WHERE viewerId=\''+viewerId+'\' GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\')'
        cursor.execute(sql)
        result = cursor.fetchall()
        if result is not None and len(result) >0:
            for rst in result:
                date_cnt_map[rst[0]] = rst[1]
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return date_cnt_map

def get_user_area():
    area_lang_lat = []
    df = pd.read_csv('./analysis/backend_analysis/area_long_lat.csv', sep='\t')
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    cursor.execute(
        'SELECT city,COUNT(DISTINCT userId) AS cnt FROM USER WHERE country = \'中国\' GROUP BY city ORDER BY cnt DESC ')
    result_list = cursor.fetchall()
    for result in result_list:
        #province = result[0]
        city = result[0]
        user_cnt = result[1]
        area_info = df.loc[df['country'].str.contains(city)]
        longitude = area_info['longitude'].values[0]
        latitude = area_info['latitude'].values[0]
        rst = {}
        rst['city'] = city
        rst['user_cnt'] = user_cnt
        rst['longitude'] = longitude
        rst['latitude'] = latitude
        area_lang_lat.append(rst)
    return area_lang_lat

