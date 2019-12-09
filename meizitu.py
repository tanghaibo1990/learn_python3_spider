# encoding = utf-8
import concurrent
import os
from concurrent.futures import ThreadPoolExecutor
import threadpool
import requests
import time
import asyncio
from aiohttp import ClientSession
from queue import Queue
from bs4 import BeautifulSoup

root_path = 'E:/meizitu/'

def header(referer):

    headers = {
        # 'Host': 'i.meizitu.net',
        # 'Pragma': 'no-cache',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }

    return headers


def request_page(url):
    try:
        headers=header('https://www.mzitu.com/')
        print('页面链接：%s' % url)
        # headers = {'user-agent':"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}
        response = requests.get(url,headers= headers)
        time.sleep(0.2)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


def get_page_urls():
    queue = Queue()

    urls = []
    for i in range(1, 237):
        baseurl = 'https://www.mzitu.com/page/{}/'.format(i)
        html = request_page(baseurl)
        soup = BeautifulSoup(html, 'lxml')
        list = soup.find(class_='postlist').find_all('li')
        for item in list:
            url = item.find('span').find('a').get('href')
            if url not in urls:
                print('页面链接：%s' % url)
                urls.append(url)
                queue.put(url)
    return urls
    # return queue


def download_Pic(title, image_list):
    # 新建文件夹
    if not os.path.exists(title):
        os.mkdir(title)
    j = 1
    # 下载图片
<<<<<<< HEAD
    # tasks=[]
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # loop = asyncio.get_event_loop()
    for item in image_list:
        filename = '%s/%s.jpg' % (title, str(j))
        print('downloading....%s : NO.%s' % (title, str(j)))
        download_pic_item(filename,item)
        # task = asyncio.ensure_future(async_download_pic_item(filename,item))
        # tasks.append(task)
        j += 1
    # loop.run_until_complete(asyncio.wait(tasks))
=======
    tasks=[]
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    for item in image_list:
        filename = '%s/%s.jpg' % (title, str(j))
        print('downloading....%s : NO.%s' % (title, str(j)))
        # download_pic_item(filename,item)
        task = asyncio.ensure_future(async_download_pic_item(filename,item))
        tasks.append(task)
        j += 1
    loop.run_until_complete(asyncio.wait(tasks))
>>>>>>> e187a063848fdfa27f60c708b872c7d8bfaaccec

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as exector:
    #     for item in image_list:
    #         filename = '%s/%s.jpg' % (title, str(j))
    #         exector.submit(download_pic_item, filename, item)

def download_pic_item(filename,pic_url):
    with open(filename, 'wb') as f:
        img = requests.get(pic_url, headers= header(pic_url)).content
        f.write(img)
        time.sleep(0.1)

async def async_download_pic_item(filename,pic_url):
    async with ClientSession() as session:
        async with session.get(pic_url , headers= header(pic_url)) as response:
            img = await response.read()
            # print(response)
            with open(filename, 'wb') as f:
                f.write(img)


def download( url):
    html = request_page(url)
    soup = BeautifulSoup(html, 'lxml')
    total = soup.find(class_='pagenavi').find_all('a')[-2].find('span').string
    title =root_path + soup.find('h2').string
    image_list = []
    # total = min(1, int(total))
    total = int(total)
    for i in range(total):
        html = request_page(url + '/%s' % (i + 1))
        soup = BeautifulSoup(html, 'lxml')
        img_url = soup.find('img').get('src')
        image_list.append(img_url)


    download_Pic(title, image_list)


def download_all_images(list_page_urls):
    # 获取每一个详情妹纸
    # works = len(list_page_urls)
    # with concurrent.futures.ProcessPoolExecutor(max_workers=3) as exector:
    #     for url in list_page_urls:
    #         exector.submit(download, url)

    task_pool = threadpool.ThreadPool(1)
    requests = threadpool.makeRequests(download, list_page_urls)
    for req in requests:
        task_pool.putRequest(req)
    task_pool.wait()
    # for url in list_page_urls:
    #     download(path, url)


if __name__ == '__main__':
    # 获取每一页的链接和名称
    list_page_urls = get_page_urls()
    download_all_images(list_page_urls)