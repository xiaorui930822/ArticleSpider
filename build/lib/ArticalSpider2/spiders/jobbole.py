# -*- coding: utf-8 -*-
import scrapy, datetime
import re
from scrapy.http import Request
from urllib import parse
from ArticalSpider2.items import JobBoleArticalItem, ArticalItemLoader
from ArticalSpider2.utils.common import get_md5
from scrapy.loader import ItemLoader
from selenium import webdriver
from scrapy.xlib import pydispatch
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # def __init__(self):
    #     self.browser = webdriver.Chrome(executable_path="H:/chromedriver.exe")
    #     super(JobboleSpider, self).__init__()
    #     pydispatch.dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     print('spider closed')# 爬虫退出时关闭Chrome
    #     self.browser.quit()

    # 收集伯乐在线的所有404的url以及404页面数
    handle_httpstatus_list = [404]

    def __init__(self,**kwargs):
        self.fail_urls = []

    def parse(self, response):
        # 1获取下一页的URL并交给scrapy进行下载，下载完成后交给parse函数
        # 2获取文章列表的文章URL并进行具体字段解析
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value('failed_url')

        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first("")
            post_url = post_node.css('::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        artical_item = JobBoleArticalItem()
        # 提取文章具体字段
        # 通过xpath提取数据
        # title = response.xpath('//*[@id="post-113315"]/div[1]/h1/text()').extract()[0]
        # creat_date =  response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·','')
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # favor_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*(\d+).*", favor_nums)    #有问题空数组
        # if match_re:
        #     favor_nums = match_re.group(1)
        # else:
        #     favor_nums = '0'
        #
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match(".*(\d+).*", comment_nums)    #有问题
        # if match_re:
        #     comment_nums = match_re.group(1)
        # else:
        #     comment_nums = '0'
        #
        # content =  response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)

        # 通过css选择器选取
        front_image_url = response.meta.get("front_image_url","")#文章封面图
        title = response.css(".entry-header h1::text").extract()[0]
        create_date = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace(" ·","")
        praise_nums = response.css(".vote-post-up h10::text").extract()
        if praise_nums:
            praise_nums = int(praise_nums[0])
        else:
            praise_nums = 0
        favor_nums = response.css(".bookmark-btn::text").extract()[0]
        match_re = re.match(".*?(\d+).*", favor_nums)
        if match_re:
            favor_nums = int(match_re.group(1))
        else:
            favor_nums = 0
        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.css(".entry").extract()[0]
        tag_list = response.css(".entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        artical_item["url_object_id"] = get_md5(response.url)
        artical_item["title"] = title
        artical_item["url"] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        artical_item["create_date"] = create_date
        artical_item["front_image_url"] = [front_image_url]
        artical_item["praise_nums"] = praise_nums
        artical_item["comment_nums"] = comment_nums
        artical_item["favor_nums"] = favor_nums
        artical_item["tags"] = tags
        artical_item["content"] = content

        yield artical_item
"""
        # 通过itemloader加载item
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticalItemLoader(item=JobBoleArticalItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("favor_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        artical_item = item_loader.load_item()
"""


