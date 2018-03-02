from django.shortcuts import render
from django.http import HttpResponse
from .backend_analysis import content_analysis
from .backend_analysis import single_content_analysis
from .backend_analysis import single_user_analysis
from .backend_analysis import user_analysis
from .backend_analysis import user_in_news_analysis
from analysis.models import News
from analysis.models import TransmitNews
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import connection
import jieba.analyse
import math
import datetime
import pandas as pd


def index(request):
    return render(request, 'frontend/index.html')


#传播路径分析，生成转发路径树
def get_transmit_tree(request, news_id=0):
    rst = user_in_news_analysis.get_transmit_tree(news_id)
    return HttpResponse(rst)

#传播路径分析，关键传播节点
def find_important_user(request, news_id=0, top=10):
    rst_list = user_in_news_analysis.find_important_user_django(news_id)
    if len(rst_list) >= top:
        rst_list = rst_list[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)

#传播路径分析，发现转发重点路径
def find_important_path(request, news_id=0):
    rst_list = user_in_news_analysis.find_important_path(news_id)
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


#最新内容
def get_latest_news(request, top=3):
    rst_list = News.objects.all().order_by("-createdAt").values("title", "writerName", "introduction","newsId","createdAt")
    if len(rst_list) >= top:
        rst_list = rst_list[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    # rst = serializers.serialize("json",rst_list)
    return HttpResponse(rst)


#最新内容分页
def get_latest_news_by_page(request, page_number=1, page_size=10):
    rst = {}
    rst_list = News.objects.all().order_by("-createdAt").values("title", "writerName", "introduction","newsId","createdAt")
    rst['total_count'] = len(rst_list)
    if len(rst_list) >= page_size:
        rst_list = rst_list[page_size*(page_number-1):page_size*page_number]
    rst['content_list'] = list(rst_list)
    rst = json.dumps(rst, cls=DjangoJSONEncoder)
    return HttpResponse(rst)

#最新活跃用户
def get_latest_users(request, top=3):
    rst_list = TransmitNews.objects.all().order_by("-updatedAt").values("viewerId","viewerName","viewerHeadImg", "updatedAt")
    if len(rst_list) >= top:
        rst_list = rst_list[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


#最新活跃用户分页
def get_latest_users_by_page(request, page_number=1, page_size=10):
    rst = {}
    rst_list = TransmitNews.objects.all().order_by("-updatedAt").values("viewerId","viewerName","viewerHeadImg", "updatedAt")
    rst['total_count'] = len(rst_list)
    if len(rst_list) >= page_size:
        rst_list = rst_list[page_size*(page_number-1):page_size*page_number]
    rst['user_list'] = list(rst_list)
    rst = json.dumps(rst, cls=DjangoJSONEncoder)
    return HttpResponse(rst)

# 用户行为日志
def get_user_log(request, viewer_id='',top=3):
    rst_list = TransmitNews.objects.filter(viewerId=viewer_id).order_by("-updatedAt").values("viewerId","viewerName", "updatedAt", "title", "introduction", "newsId")
    if len(rst_list) >= top:
        rst_list = rst_list[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


# 总分享
def get_total_transmit_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(1) as cnt FROM transmit_news  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


# 总阅读
def get_total_read_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(1) as cnt FROM pv_news_log  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


# 总覆盖用户
def get_total_user_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(DISTINCT viewerId) as cnt FROM pv_news_log  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


# 用户地域分析
def get_user_area(request):
    area_lang_lat = single_user_analysis.get_user_area()
    return HttpResponse(json.dumps(area_lang_lat, cls=DjangoJSONEncoder))


# 用户数量分析
def get_user_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(DISTINCT userId) as cnt FROM user  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


#取最近10篇文章的介绍生成词云图
def get_word_cloud(request):
    content_txt = ''
    cursor = connection.cursor()
    cursor.execute('SELECT introduction from news order by createdAt limit 10' )
    rst_list = cursor.fetchall()
    for rst_txt in rst_list:
        content_txt += rst_txt[0]
    jieba.analyse.set_stop_words('./analysis/chineseStopWords.txt')
    tags = jieba.analyse.extract_tags(content_txt, topK=100, withWeight=True)
    rst = json.dumps(list(tags), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


#取文章的标题及摘要
def get_news_info(request, news_id=0):
    rst = {}
    cursor = connection.cursor()
    cursor.execute('SELECT title,introduction from news where newsId = %d'% news_id )
    result = cursor.fetchall()
    if result is not None and len(result) > 0:
        title = result[0][0]
        rst['title'] = title
        introduction = result[0][1]
        rst['introduction'] = introduction
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))


# 文章当前热度分析 参数：新闻ID，当前时间
def get_now_news_hot(request, news_id=0):
    rst={}
    pv_cnt = single_content_analysis.get_pv(news_id)
    transmit_cnt = single_content_analysis.get_transmit(news_id)
    user_cover_cnt = single_content_analysis.get_user_cover(news_id)
    hot_value = 0.4 * math.log(transmit_cnt + 1, 10) + 0.3 * math.log(pv_cnt + 1, 10) + 0.3 * math.log(
        user_cover_cnt + 1, 10)  # user_cover权重0.3，pv权重0.3，transmit权重0.4
    hot_value = float('%.2f' % hot_value)
    rst['pv_cnt']=pv_cnt
    rst['transmit_cnt']=transmit_cnt
    rst['user_cover_cnt']=user_cover_cnt
    rst['hot_value']=hot_value
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))


# 文章热度曲线分析 参数：新闻ID，时间范围，默认7天
def get_history_news_hot(request, news_id=0, day_limit=7):
    rst={}
    max_news_day = single_content_analysis.get_max_news_time(news_id)
    compute_time_str = max_news_day+' 59:59:59'
    log_hot = single_content_analysis.compute_news_hot(news_id, compute_time_str)
    rst[max_news_day] = log_hot
    start_day = datetime.datetime.strptime(max_news_day, "%Y-%m-%d")
    delta = datetime.timedelta(days=1)
    next_day = start_day - delta
    day_index=1
    while (day_index < day_limit):
        next_day_str = datetime.date.strftime(next_day, '%Y-%m-%d')
        compute_time_str = next_day_str + ' 59:59:59'
        log_hot = single_content_analysis.compute_news_hot(news_id, compute_time_str)
        rst[next_day_str]=log_hot
        #print(next_day_str)
        day_index += 1
        next_day = next_day - delta
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))


#用户当前影响力分析
def get_now_user_effect(request, user_id='0'):
    rst = single_user_analysis.compute_now_users_hot(user_id)
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))

#用户影响力趋势曲线
def get_history_user_effect(request, user_id='0', day_limit=7):
    rst = {}
    max_news_day = single_user_analysis.get_max_user_time(user_id)
    compute_time_str = max_news_day + ' 59:59:59'
    log_hot = single_user_analysis.compute_history_users_hot(user_id, compute_time_str)
    rst[max_news_day] = log_hot
    start_day = datetime.datetime.strptime(max_news_day, "%Y-%m-%d")
    delta = datetime.timedelta(days=1)
    next_day = start_day - delta
    day_index = 1
    while (day_index < day_limit):
        next_day_str = datetime.date.strftime(next_day, '%Y-%m-%d')
        compute_time_str = next_day_str + ' 59:59:59'
        log_hot = single_user_analysis.compute_history_users_hot(user_id, compute_time_str)
        rst[next_day_str] = log_hot
        print(next_day_str)
        day_index += 1
        next_day = next_day - delta
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))

#取用户的基本信息
def get_user_info(request, user_id=0):
    rst = {}
    cursor = connection.cursor()
    cursor.execute('SELECT userId,userName,sex,province,city,country,headImgUrl from user where userId =\'%s\''% user_id )
    result = cursor.fetchall()
    if result is not None and len(result) > 0:
        userId = result[0][0]
        rst['userId'] = userId
        userName = result[0][1]
        rst['userName'] = userName
        sex = result[0][2]
        if sex==1:
            rst['sex'] = '男'
        if sex==2:
            rst['sex'] = '女'
        province = result[0][3]
        rst['province'] = province
        city = result[0][4]
        rst['city'] = city
        country = result[0][5]
        rst['country'] = country
        headImgUrl = result[0][6]
        rst['headImgUrl'] = headImgUrl
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))


#TODO 用户活跃度分析
def get_user_active(request, user_id='0', day_limit=7):
    rst = {}
    pv_date_cnt_map = single_user_analysis.get_pv_date_cnt_map(user_id)
    transmit_date_cnt_map = single_user_analysis.get_transmit_date_cnt_map(user_id)
    max_news_day = single_user_analysis.get_max_user_time(user_id)
    start_day = datetime.datetime.strptime(max_news_day, "%Y-%m-%d")
    pv_cnt = 0
    if max_news_day in pv_date_cnt_map:
        pv_cnt = pv_date_cnt_map[max_news_day]
    transmit_cnt = 0
    if max_news_day in transmit_date_cnt_map:
        transmit_cnt = transmit_date_cnt_map[max_news_day]
    rst[max_news_day] = pv_cnt + transmit_cnt
    delta = datetime.timedelta(days=1)
    next_day = start_day - delta
    day_index = 1
    while (day_index < day_limit):
        next_day_str = datetime.date.strftime(next_day, '%Y-%m-%d')
        pv_cnt = 0
        if next_day_str in pv_date_cnt_map:
            pv_cnt = pv_date_cnt_map[next_day_str]
        transmit_cnt = 0
        if next_day_str in transmit_date_cnt_map:
            transmit_cnt = transmit_date_cnt_map[next_day_str]
        rst[next_day_str] = pv_cnt + transmit_cnt
        day_index += 1
        next_day = next_day - delta
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))

