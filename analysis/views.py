from django.shortcuts import render
from django.http import HttpResponse
from .backend_analysis import content_analysis
from .backend_analysis import user_analysis
from .backend_analysis import user_in_news_analysis
from analysis.models import News
from analysis.models import TransmitNews
import json
from django.core import serializers


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
    rst_list = News.objects.all().order_by("-createdAt").values("title", "writerName", "introduction","createdAt")[0:top]
    #rst = json.dumps(rst_list)
    #rst = serializers.serialize("json",rst_list)
    return HttpResponse(rst_list)


#最新活跃用户
def get_latest_users(request, top=3):
    rst_list = TransmitNews.objects.all().order_by("-updatedAt").values("viewerName", "updatedAt")[0:top]
    return HttpResponse(rst_list)


#TODO 总分享
def get_total_transmit_number(request):
    rst_list = None
    return HttpResponse(rst_list)


#TODO 总阅读
def get_total_read_number(request):
    rst_list = None
    return HttpResponse(rst_list)


#TODO 总覆盖用户
def get_total_user_number(request):
    rst_list = None
    return HttpResponse(rst_list)