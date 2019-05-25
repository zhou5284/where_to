# -*- coding: utf-8 -*-
"""
  @author :  Zero
  @contact :  375644652@qq.com
  @software : PyCharm
  @file : WhereTo.py
  @time : 2019-05-17 13:45
  目标地址:https://www.qunar.com/
  目标需求:爬取全国景点信息
"""

import requests
from bs4 import BeautifulSoup
import math
import numpy as np
import pandas as pd

'''
1.数据采集
'''


def get_url(u):
    # 构建请求信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    # 获取请求url的html
    html = BeautifulSoup(requests.get(u, headers=headers, timeout=500).text, 'lxml')
    # 定位
    urls = html.find('div', class_='contbox current').find_all('li')
    # 获取全国的景点URL
    list_urls = []
    for i in urls:
        # 拼接每个地区景点的url
        i = i.find('a')['href'] + '-jingdian'
        # 获取每个地区的html
        html = BeautifulSoup(requests.get(i, headers=headers, timeout=500).text, 'lxml')
        # 有些url中没有景点
        try:
            # 获取每个地区景点的总数
            mun = int(html.find('p', class_='nav_result').find('span').get_text()[1:-2])
            # 每个地区景点的页数,景点每页10个,页面最多显示200页
            if mun <= 2000:
                mun = math.ceil(mun / 10) + 1
            else:
                mun = 201
            # 拼接添加全国景点的url放到list中
            url = [i + '-1-' + str(j) for j in range(1, mun)]
            # print(url)
            list_urls.append(url)
        # 地区没有景点处理
        except:
            # 这里简单提示一下
            print(f"景点页面缺失:{i}")
    return list_urls


# 每个地区的元素提取
def get_informations(urls):
    data_list = []
    for lst in urls:
        for url in lst:
            html = BeautifulSoup(requests.get(url).text, 'lxml')
            infori = html.find('ul', class_='list_item clrfix').find_all('li')
            for i in infori:
                dic = {}
                dic['lat'] = i['data-lat']
                dic['lng'] = i['data-lng']
                dic['景点名称'] = i.find('span', class_='cn_tit').text
                dic['景点星级'] = i.find('span', class_="total_star").find('span')['style'].split(':')[1]
                dic['景点排名'] = i.find('span', class_='sum').text
                dic['景点攻略'] = i.find('div', class_="strategy_sum").text
                dic['景点简介'] = i.find('div', class_="desbox").text
                dic['景点点评'] = i.find('div', class_="comment_sum").text
                print(dic)
                data_list.append(dic)

    return data_list


'''
2.字段清洗/保存/可视化在excel中全选,点击插入,三维地图
'''


def data_clean(data_list):
    df = pd.DataFrame()
    dfi = pd.DataFrame(data_list)
    df = pd.concat([df, dfi])
    df.reset_index(inplace=True, drop=True)
    df['lat'] = df['lat'].astype(np.float)
    df['lng'] = df['lng'].astype(np.float)
    df['景点点评'] = df['景点点评'].astype(np.int)
    df['景点攻略'] = df['景点攻略'].astype(np.int)
    df['景点星级'] = df['景点星级'].str.replace('%', '').astype(np.float)
    df['景点排名'] = df['景点排名'].str.replace('%', '').astype(np.int)
    df.to_excel('./全国景点汇总.xlsx')


if __name__ == '__main__':
    url = 'https://travel.qunar.com/place/'
    urls = get_url(url)
    data = get_informations(urls)
    data_clean(data)
