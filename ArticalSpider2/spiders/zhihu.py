# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
import datetime, time
from urllib import parse
from scrapy.loader import ItemLoader
from fake_useragent import UserAgent
from ArticalSpider2.items import ZhihuAnswerItem, ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    cookies1 = {
        'z_c0': '"2|1:0|10:1534937757|4:z_c0|92:Mi4xWUdHV0F3QUFBQUFBZ0djX0RUY1lEaVlBQUFCZ0FsVk5uWmhxWEFDa3JTakVqMWVJYjg3MXZjeXNNcnNoOUp1VDd3|c136f6d55e65fa16fe94be9d941129d4486f2c544cc80b4f16f3629c3ad4c7ec"'
    }
    cookies2 = {
        'z_c0': '"2|1:0|10:1534849837|4:z_c0|92'
                ':Mi4xbnRXSEFnQUFBQUFBVUtjcUNEcnFEU1lBQUFCZ0FsVk5MRUZwWEFDai00aUt4ZV9INlo4emg5ZXhKYW0yUkxRdERB'
                '|248084ce4f9e4f526e2be77da4dc5cb3ba5caa3796578be48fe4113f5d1150d3"'
    }
    ua = UserAgent()
    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            # 'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            # 'Connection': 'keep-alive',
            'cookies': cookies2,
            'host': 'www.zhihu.com',
            # 'Origin': 'https://www.zhihu.com',
            # 'Referer': 'https://www.zhihu.com/',
            'user-agent': ua.random,
        }
    }

    # host = "https://www.zhihu.com/"
    # headers = {
    #     'user-agent': ua.random
    # }

    # response = requests.get(host, headers=headers, cookies=cookies1, callback=parse)
    # res = scrapy.Request('https://www.zhihu.com/', callback=parse)
    # question的第一页answer请求url
    # start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    # ua = UserAgent()
    # headers = {
    # "HOST": "www.zhihu.com",
    # "Referer": "https://www.zhihu.com",
    # "user-agent": ua.random,
    # "cookies":cookies
    # }
    # custom_settings = {
    #     "COOKIES_ENABLED": True
    # }
    session = requests.session()

    def parse(self, response):
        """
        提取出html页面中的所有url，并跟踪这些url进行下一步爬取
        如果提取的url格式为/question/xxx就下载之后直接进入解析函数
        :param response:
        :return:
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        all_urls = [x for x in all_urls if x.startswith("https")]
        for url in all_urls:
            if url.startswith("https"):
                match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
                if match_obj:
                    # 提取到question相关的页面则下载后给提取函数进行提取
                    request_url = match_obj.group(1)
                    question_id = match_obj.group(2)
                    yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
                    break
                else:
                    # pass
                    # 不是question页面则返回进一步跟踪
                    yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面，从页面提取出具体的question  item
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", ".QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeaderActions .Button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        # totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    # def start_requests(self):
    # return [scrapy.Request('https://www.zhihu.com/', callback=self.check_login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ""
        if match_obj:
            xsrf = (match_obj.group(1))
        # if xsrf:
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": xsrf,
            "phone_num": "电话",
            "password": "密码",
            "captcha": ""
        }
        import time
        t = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
        yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data": post_data},
                             callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        with open("captcha.png", "wb") as f:
            f.write(response.body)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.png')
            im.show()
            im.close()
        except:
            pass

        lang = input("输入验证码类别cn/en：")
        if lang == "cn":
            captcha = {
                'img_size': [200, 44],
                'input_points': [],
            }
            points = [[22.796875, 22], [42.796875, 22], [63.796875, 21], [84.796875, 20], [107.796875, 20],
                      [129.796875, 22],
                      [150.796875, 22]]
            seq = input('请输入倒立字的位置：')
            for i in seq:
                captcha['input_points'].append(points[int(i) - 1])
            captcha = json.dumps(captcha)
        else:
            captcha = input("输入英文验证码：")

        im.close()
        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data["captcha"] = captcha

        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    # def check_login(self, response):
    # 验证服务器的返回数据是否成功
    # text_json = json.loads(response.text)
    # if "msg" in text_json and text_json["msg"] == "登录成功":
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, dont_filter=True, headers=self.headers)
