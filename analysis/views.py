from django.shortcuts import render
from django.http import HttpResponse
from .backend_analysis import content_analysis
from .backend_analysis import user_analysis
from .backend_analysis import user_in_news_analysis
from analysis.models import News
from analysis.models import TransmitNews
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import connection
import jieba.analyse


def index(request):
    return render(request, 'frontend/index.html')

#计算文章热度
def compute_news_hot(request):
    rst = content_analysis.compute_news_hot()
    return HttpResponse(rst)

#计算用户热度
def compute_users_hot(request):
    rst = user_analysis.compute_users_hot()
    return HttpResponse(rst)

#生成转发路径树
def get_transmit_tree(request):
    rst = user_in_news_analysis.get_transmit_tree(6)
    return HttpResponse(rst)

#发现转发重点用户
def find_important_user(request):
    rst = user_in_news_analysis.find_important_user_django(6)
    return HttpResponse(rst)

#发现转发重点路径
def find_important_path(request):
    rst = user_in_news_analysis.find_important_path(6)
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
