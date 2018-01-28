# -*- coding:utf-8 -*-

import pymysql
import json
import math
from .UserTransmitTree import TreeNode


#用户单篇被浏览量统计
def get_re_pv_map(newsId):
    pv_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select shareId, count(1) as cnt from pv_news_log where newsId=%s  group by shareId '
        cursor.execute(sql, newsId)
        result = cursor.fetchall()
        for newsId, cnt in result:
            pv_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return pv_map


#用户单篇被转发量统计
def get_re_transmit_map(newsId):
    transmit_map = {}
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select shareId, count(1) as cnt from transmit_news where newsId=%s  and shareId<>\'0\'  group by shareId '
        cursor.execute(sql, newsId)
        result = cursor.fetchall()
        for newsId, cnt in result:
            transmit_map[newsId] = cnt
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_map



#用户单篇被转发量统计
def get_all_transmit_user_list(newsId):
    transmit_user_list = []
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select distinct viewerId as cnt from transmit_news where newsId=%s '
        cursor.execute(sql, newsId)
        result = cursor.fetchall()
        for viewerId in result:
            transmit_user_list.append(viewerId[0])
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_user_list


#用户单篇转发量统计
def get_transmit_list(newsId):
    transmit_list = []
    db = pymysql.connect(host="localhost", user="root", passwd="123456", db="virus_source",charset='utf8')
    cursor = db.cursor()
    try:
        sql = 'select viewerId,viewerName, shareId, shareName  from transmit_news where newsId=%s   '
        cursor.execute(sql,newsId)
        result = cursor.fetchall()
        for viewerId,viewerName, shareId, shareName in result:
            node = TreeNode(viewerId,viewerName, shareId, shareName)
            transmit_list.append(node)
    except Exception as err:
        print(err)
    finally:
        cursor.close()
        db.close()
    return transmit_list


#转发路径跟踪
def build_transmit_tree(newsId):
    node_list = []
    transmit_list = get_transmit_list(newsId)
    for each_node in transmit_list:
        mark = False
        for second_node in transmit_list:
            if((each_node.share_id is not None or each_node.share_id != 0) and each_node.share_id == second_node.viewer_id):
                mark = True
                second_node.children.append(each_node)
                break
        if (mark is False):
            node_list.append(each_node)
    return node_list


#文章重点用户发现-django调用
def find_important_user_django(newsId):
    user_power = {}
    all_transmit_user_list = get_all_transmit_user_list(newsId)
    user_re_pv = get_re_pv_map(newsId)
    user_re_transmit = get_re_transmit_map(newsId)
    for user_id in all_transmit_user_list:
        transmit_cnt = 0
        if user_id in user_re_transmit:
            transmit_cnt = user_re_transmit[user_id]
        pv_cnt = 0
        if user_id in user_re_pv:
            pv_cnt = user_re_pv[user_id]
        #hot_value = 0.6*math.log(transmit_cnt+2, 10)+0.4*math.log(pv_cnt+1, 10)
        hot_value = transmit_cnt
        user_power[user_id] = hot_value
    sorted_user_power = sorted(user_power.items(),key = lambda x:x[1],reverse = True)
    #return sorted_user_power
    print(sorted_user_power)
    return sorted_user_power


#文章重点用户发现-内部调用
def find_important_user(newsId):
    user_power = {}
    all_transmit_user_list = get_all_transmit_user_list(newsId)
    user_re_pv = get_re_pv_map(newsId)
    user_re_transmit = get_re_transmit_map(newsId)
    for user_id in all_transmit_user_list:
        transmit_cnt = 0
        if user_id in user_re_transmit:
            transmit_cnt = user_re_transmit[user_id]
        pv_cnt = 0
        if user_id in user_re_pv:
            pv_cnt = user_re_pv[user_id]
        #hot_value = 0.6*math.log(transmit_cnt+2, 10)+0.4*math.log(pv_cnt+1, 10)
        hot_value = transmit_cnt
        user_power[user_id] = hot_value
    sorted_user_power = sorted(user_power.items(),key = lambda x:x[1],reverse = True)
    #return sorted_user_power
    print(sorted_user_power)
    return user_power

#文章重点转发路径发现
def find_important_path(newsId):
    rst = []
    node_list = build_transmit_tree(newsId)
    sorted_user_power = find_important_user(newsId)
    #一级转发节点遍历
    for node in node_list:
        sum_child_important_cnt(node,sorted_user_power)
    s_sorted_user_power = sorted(sorted_user_power.items(),key = lambda x:x[1],reverse = True)
    print(s_sorted_user_power)#############
    max_node_list = []
    find_max_important_user(node_list,sorted_user_power, max_node_list)
    print("最具影响力转发路径：")
    for node in max_node_list:
        print(node.viewer_id, sorted_user_power[node.viewer_id])
        rst.append([node.viewer_id, sorted_user_power[node.viewer_id]])
    return rst


 #递归将子节点影响力加到父节点上
def sum_child_important_cnt(node, user_power):
    cnt = user_power[node.viewer_id]
    if(len(node.children)>0):
        for child_node in node.children:
            child_node_cnt = sum_child_important_cnt(child_node, user_power)
            cnt += child_node_cnt
    user_power[node.viewer_id] = cnt
    return cnt

#寻找同层级节点中影响力最大的节点
def find_max_important_user(node_list, user_power, max_node_list):
    max_cnt = 0
    max_node = None
    for node in node_list:
        user_id = node.viewer_id
        cnt = user_power[user_id]
        if(cnt>=max_cnt):
            max_cnt = cnt
            max_node = node
    max_node_list.append(max_node)
    if(len(max_node.children)>0):
        find_max_important_user(max_node.children,user_power,max_node_list)




def get_transmit_tree(newsId):
    node_list = build_transmit_tree(newsId)
    for node in node_list:
        print(node)
    json_str = json.dumps(node_list, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    print(json_str)
    return json_str


def test2():
    sorted_user_power = find_important_user(6)
    print(sorted_user_power)



#test1()
#find_important_path(6)