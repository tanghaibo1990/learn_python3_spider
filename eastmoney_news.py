# coding=utf-8
import requests
from bs4 import BeautifulSoup
import pymysql
import time
import sys
import imp
imp.reload(sys)

# python 3 以前版本默认非utf8编码，中文会出错
sys.setdefaultencoding('utf8')

host = 'http://finance.eastmoney.com'

db_host = 'localhost'
db_port = 3306
db_user = 'root'
db_password = 'root'
db_database = 'rong'


class NewsModel:
    def __init__(self, title, url, short_title):
        self.title = title
        self.url = url
        self.short_title = short_title

    def get_title(self):
        return self.title

    def get_url(self):
        return self.url

    def get_short_title(self):
        return self.short_title

    def __str__(self):
        return 'title: %s ,info : %s ,url: %s' % (self.title, self.short_title, self.url)


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
        headers = header(host)
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


def get_page_news():
    urls = []
    base_url = host + '/a/ccjdd.html'
    html = request_page(base_url)
    soup = BeautifulSoup(html, 'lxml')
    news = soup.find(id='newsListContent').find_all('li')
    if len(news) > 5:
        news = news[0:5]

    for item in news:
        text_div = item.find('div', class_='text')
        title = text_div.find(class_='title').find('a').get_text().strip()
        url = text_div.find(class_='title').find('a').get('href').strip()
        info = text_div.find(class_='info').get_text().strip()
        data = NewsModel(title, url, info)
        urls.append(data)
    return urls
    # return queue


def download_html(item):
    title = item.get_title()
    try:
        cus = db_conn.cursor()
        sql = "select count(1) from `rong`.`cms_document` where title= '%s'" % title
        cus.execute(sql)
        count = cus.fetchone()[0]
        if count > 0:
            return None
    finally:
        cus.close()
    url = item.get_url()
    html = request_page(url)
    soup = BeautifulSoup(html, 'lxml')
    content_body = soup.find(id='ContentBody')

    # 删除摘要
    tmp1 = content_body.find(class_='abstract')
    if tmp1:
        tmp1.decompose()
    tmp2 = content_body.find(class_='b-review')
    if tmp2:
        tmp2.decompose()

    # 清理广告
    tmp3 = content_body.find(class_='reading')
    if tmp3:
        tmp3.decompose()

    # 段落样式
    for p_tag in content_body.find_all('p'):
        if not p_tag.parent.get('id') == 'ContentBody':
            continue
        style = p_tag.get('style')
        style = '''margin-top: 12px; margin-bottom: 12px; padding: 0px 20px 0px 17px; line-height: 28px; font-family: 宋体, Helvetica, sans-serif; font-size: 14px; 
        white-space: normal; background-color: rgb(255, 255, 255);''' + ('' if style == None else '')
        p_tag['style'] = style

    # a标签处理：禁止跳转，颜色
    for a in content_body.find_all('a'):
        a['href'] = 'javascript:void(0)'
        style = a.get('style')
        style = 'color:black;' + ('' if style == None else '')
        a['style'] = style

    # 处理图片宽高
    for img in content_body.find_all('img'):
        style = img.get('style')
        style = 'width:100%;height:100%;' + ('' if style == None else '')
        img['style'] = style

    # 时间
    # create_time = soup.find(class_='Info').find(class_='time').get_text()
    # create_time = time.mktime(time.strptime(create_time, "%Y年%m月%d日 %H:%M"))
    create_time = time.time()
    # print(content_body.prettify())
    short_title = item.get_short_title()
    try:
        cursor = db_conn.cursor()
        sql = """INSERT INTO `rong`.`cms_document`( `cid`, `model`, `title`, `shorttitle`, `uid`, `flag`, `view`, `comment`, `good`, `bad`, `mark`, `create_time`, `update_time`, `sort`, `status`, `trash`) 
        VALUES ( 11, 2, '%s', '%s', 2, '', 9, 0, 0, 0, 0, %d, %d, 100, 1, 0);""" % (
            title, title, create_time, create_time)
        cursor.execute(sql)
        row_id = cursor.lastrowid
        str_body = content_body.prettify()
        sql = """INSERT INTO `rong`.`cms_document_news`(`aid`, `content`, `summary`) 
        VALUES (%d, '%s', '%s');""" % (row_id, str_body, title)
        cursor.execute(sql)
        db_conn.commit()
    except BaseException as ex:
        db_conn.rollback()
    finally:
        cursor.close()


if __name__ == '__main__':
    # 获取每一页的链接和名称
    global db_conn
    try:
        db_conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_database,
            charset="utf8"
        )
        list_page_news = get_page_news()
        for item in list_page_news:
            download_html(item)
        print('ok')
    except BaseException as ex:
        print('同步失败')
        print(str(ex))
    finally:
        db_conn.close()
