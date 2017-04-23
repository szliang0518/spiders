# -*- coding:utf8 -*-

'''
http://www.xieemanhuaba.com/xieedontaitu/

sudo -H pip install requests beautifulsoup
'''

import os               # path, makedirs
import requests         # 网络请求
import urllib           # 下载文件
from bs4 import BeautifulSoup # 网页分析
import re               # 正则表达式
import thread
import multiprocessing
from multiprocessing import Pool
import time

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDRE = 'xeba1'

def download_url(url):
    if len(url) < 1: return
    path = os.path.join(CURR_DIR, FOLDRE, os.path.basename(url))
    print url, path
    mkdir(os.path.dirname(path))
    if os.path.exists(path): return
    urllib.urlretrieve(url, path)

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fixUrl(url):
    return 'http://www.xieemanhuaba.com' + url

def get_image_url(soup):
    item = soup.find('li', id='imgshow')
    img_url = ''
    try:
        title, img_url = item.img.get('alt'), item.img.get('src')
        print title, img_url
    except Exception,e:
        print '解析图片失败 %s' % e.message
    return img_url

def get_pagelist(url, soup):
    ret = []
    pagelist = soup.find('ul', class_='pagelist').find_all('li')
    if len(pagelist):
        # 使用正则表达式获取 分页
        pagecount = re.findall("\d+", pagelist[0].a.text)[0]
        pagecount = int(pagecount)
        print '子页面数量:', pagecount
        baseurl = url.replace('.html', '')
        for index in xrange(2, pagecount+1):
            nexturl = '%s_%d.html' % (baseurl, index)
            ret.append(nexturl)
    return ret

def get_all_img_urls():
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

    url = 'http://www.xieemanhuaba.com/xieedontaitu/'
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')
    item = soup.find('div', class_='kg')
    count = int(item.span.text)
    print '已有%d集漫画.' % count


    title = item.a.get('title')
    url = fixUrl(item.a.get('href'))
    print title, url

    urls = []

    for x in xrange(1,count+1):
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')
        # 下载页面中的动图
        urls.append(get_image_url(soup))

        # 下载页面中子页面的动图
        pagelist = get_pagelist(url, soup)
        for page in pagelist:
            print 'page', page
            html = requests.get(page, headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')
            urls.append(get_image_url(soup))

        # 获取到下一章链接
        url = re.findall("var str = \S+<a href='(\S+)'", html.text)[1]
        url = fixUrl(url)
    return urls

def download(urls, processes=10):
    """ 并发下载所有图片 """
    print u'开始下载所有图片'
    start_time = time.time()
    pool = Pool(processes)
    for img_url in urls:
        pool.apply_async(download_url, (img_url,))

    pool.close()
    pool.join()
    print('下载完毕，用时: %s 秒' % (time.time() - start_time))

btime = time.time()
download(get_all_img_urls())
print '总共花了多久:', time.time()-btime
