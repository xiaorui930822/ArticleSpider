# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/8/22 0022 19:37'


import requests
from lxml import etree
from fake_useragent import UserAgent



def login_zhihu():
    # 使用已经登录的cookies信息来登录知乎
        ua = UserAgent()
        headers = {
            'user-agent': ua.random
        }
        # 传入cookie
        cookies = {
            # 'z_c0': '"2|1:0|10:1534849837|4:z_c0|92'
            #         ':Mi4xbnRXSEFnQUFBQUFBVUtjcUNEcnFEU1lBQUFCZ0FsVk5MRUZwWEFDai00aUt4ZV9INlo4emg5ZXhKYW0yUkxRdERB'
            #         '|248084ce4f9e4f526e2be77da4dc5cb3ba5caa3796578be48fe4113f5d1150d3"'
            'z_c0': '"2|1:0|10:1534937757|4:z_c0|92:Mi4xWUdHV0F3QUFBQUFBZ0djX0RUY1lEaVlBQUFCZ0FsVk5uWmhxWEFDa3JTakVqMWVJYjg3MXZjeXNNcnNoOUp1VDd3|c136f6d55e65fa16fe94be9d941129d4486f2c544cc80b4f16f3629c3ad4c7ec"'
        }
        host = "https://www.zhihu.com/"
        response = requests.get(host, headers=headers, cookies=cookies)
        # with open("index_page.html", "wb") as f:
        #     f.write(response.text.encode("utf-8"))
        return response.text


def parse_html(html):
    data = etree.HTML(html)
    total = data.xpath('//*[@id="root"]/div/main/div/div/div[1]/div[2]/div/div')
    for info in total:
        if len(info.xpath('./div/div[2]/h2/div/a/text()')) != 0:
            title = info.xpath('./div/div[2]/h2/div/a/text()')
        else:
            title = info.xpath('./div/div[2]/h2/a/text()')
        topic = info.xpath('./div/div[1]/div[1]/span/a/div/div/text()')
        if len(info.xpath('./div/div[1]/div[2]/div/div[1]/span/div/div/a/text()')) != 0:
            answerer = info.xpath('./div/div[1]/div[2]/div/div[1]/span/div/div/a/text()')
        else:
            answerer = info.xpath('./div/div[1]/div[2]/div/div[1]/span/text()')
        answerer_info = info.xpath('./div/div[1]/div[2]/div/div[2]/div/div/text()')
        if len(info.xpath('./div/div[2]/div/div[2]/span/text()')) != 0:
            content = info.xpath('./div/div[2]/div/div[2]/span/text()')
        else:
            content = info.xpath('./div/div[2]/div[2]/div[1]/span/b[1]/text()')
        # 字典
        """
        summary = {
            '标题': title[0],
            '标签': topic[0],
            '回答者': answerer[0],
            '回答者简介': answerer_info[0]
        }
        """
        print("标题:", title[0])
        print("标签:", topic[0])
        print("回答者:", answerer[0], end='')
        print("|", answerer_info[0])
        print("概要:", content[0])
        # print(summary)
        print('-' * 120)
    """
    for title in titles:
        i = i + 1
        print("问题描述:", title)
        print("话题:", topics[i-1])
        print("回答者:", answerers[i - 1], "/", answerers_info[i-1])
        print("-"*100)
"""


if __name__ == '__main__':
    html = login_zhihu()
    parse_html(html)