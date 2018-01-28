from django.shortcuts import render
from django.http import HttpResponse
from .backend_analysis import content_analysis
from .backend_analysis import user_analysis
from .backend_analysis import user_in_news_analysis


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