from django.shortcuts import render
from django.http import HttpResponse
from .backend_analysis import content_analysis
from .backend_analysis import single_content_analysis
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


def index(request):
    return render(request, 'frontend/index.html')


#生成转发路径树
def get_transmit_tree(request, news_id=0):
    rst = user_in_news_analysis.get_transmit_tree(news_id)
    return HttpResponse(rst)

#发现转发重点用户
def find_important_user(request, news_id=0):
    rst = user_in_news_analysis.find_important_user_django(news_id)
    return HttpResponse(rst)

#发现转发重点路径
def find_important_path(request, news_id=0):
    rst = user_in_news_analysis.find_important_path(news_id)
    return HttpResponse(rst)


#最新内容
def get_latest_news(request, top=3):
    rst_list = News.objects.all().order_by("-createdAt").values("title", "writerName", "introduction","newsId","createdAt")[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    # rst = serializers.serialize("json",rst_list)
    return HttpResponse(rst)


#最新活跃用户
def get_latest_users(request, top=3):
    rst_list = TransmitNews.objects.all().order_by("-updatedAt").values("viewerId","viewerName", "updatedAt")[0:top]
    rst = json.dumps(list(rst_list), cls=DjangoJSONEncoder)
    return HttpResponse(rst)


# 用户行为
def get_user_log(request, viewer_id='',top=3):
    rst_list = TransmitNews.objects.filter(viewerId=viewer_id).order_by("-updatedAt").values("viewerId","viewerName", "updatedAt", "title", "introduction", "newsId")[0:top]
    return HttpResponse(rst_list)


# 总分享
def get_total_transmit_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(1) as cnt FROM transmit_news  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    return HttpResponse(rst_list)


# 总阅读
def get_total_read_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(1) as cnt FROM pv_news_log  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    return HttpResponse(rst_list)


# 总覆盖用户
def get_total_user_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(DISTINCT viewerId) as cnt FROM pv_news_log  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    return HttpResponse(rst_list)


# 用户地域分析
def get_user_area(request):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT city,COUNT(DISTINCT userId) AS cnt FROM USER WHERE country = \'中国\' GROUP BY city ORDER BY cnt DESC ')
    rst_list = cursor.fetchall()
    return HttpResponse(rst_list)


# 用户数量分析
def get_user_number(request ,top=7):
    cursor = connection.cursor()
    cursor.execute('SELECT DATE_FORMAT(createdAt, \'%Y-%c-%d\') as time_day,COUNT(DISTINCT userId) as cnt FROM user  GROUP BY DATE_FORMAT(createdAt, \'%Y-%c-%d\') ORDER BY createdAt DESC LIMIT ' + str(top))
    rst_list = cursor.fetchall()
    return HttpResponse(rst_list)


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
    return HttpResponse(tags)


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
        print(next_day_str)
        day_index += 1
        next_day = next_day - delta
    return HttpResponse(json.dumps(rst, cls=DjangoJSONEncoder))