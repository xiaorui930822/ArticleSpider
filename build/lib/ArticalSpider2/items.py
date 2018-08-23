# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re,redis
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from ArticalSpider2.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticalSpider2.utils.common import extract_num, get_md5
from w3lib.html import remove_tags
from models.es_types import ArticalType, LagouType
from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticalType._doc_type.using)  # 单独指向ArticalType？LagouType未指向？

redis_cli = redis.StrictRedis()

class Articalspider2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串    analyzer="ik_max_word"
            words = es.indices.analyze(index=index, body={'text': text, 'analyzer': "ik_max_word"},
                                       params={"filter": ["lowercase"]})
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests


def date_convert(value):
    try:
        creat_date = datetime.datetime.strptime(value, "%Y%m%d").date()
    except Exception as e:
        creat_date = datetime.datetime.now().date()
    return creat_date


def return_value(value):
    return value


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


class ArticalItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def get_nums(value):
    match_re = re.match('.*(\d+).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_splash(value):  # 删除斜杠
    return value.replace("/", "")


class JobBoleArticalItem(scrapy.Item):
    # title = scrapy.Field()
    # create_date = scrapy.Field(
    #     input_processor=MapCompose(date_convert),
    #     # output_processor=TakeFirst()
    # )
    # url = scrapy.Field()
    # url_object_id = scrapy.Field()
    # front_image_url = scrapy.Field(
    #     output_processor=MapCompose(return_value)  # 注意！！！
    # )
    # front_image_path = scrapy.Field()
    # praise_nums = scrapy.Field(
    #     input_processor=MapCompose(get_nums)
    # )
    # comment_nums = scrapy.Field(
    #     input_processor=MapCompose(get_nums)
    # )
    # favor_nums = scrapy.Field(
    #     input_processor=MapCompose(get_nums)
    # )
    # tags = scrapy.Field(
    #     input_processor=MapCompose(remove_comment_tags),
    #     output_processor=Join(",")
    # )
    # content = scrapy.Field()

    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    favor_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                  insert into jobbole_artical2(title, url, create_date, url_object_id, front_image_url, praise_nums, comments_nums, fav_nums, tags, content)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                  ON DUPLICATE KEY UPDATE praise_nums = VALUES(praise_nums), comments_nums = VALUES(comments_nums), fav_nums = VALUES(fav_nums)
                """
        params = (self["title"], self["url"], self["create_date"], self["url_object_id"], self["front_image_url"],
                  self["praise_nums"], self["comments_nums"], self["fav_nums"], self["tags"], self["content"])
        return insert_sql, params

    def save_to_es(self):
        artical = ArticalType()
        artical.title = self['title']
        artical.create_date = self["create_date"]
        artical.content = remove_tags(self["content"])
        artical.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            artical.front_image_path = self["front_image_path"]
        artical.praise_nums = self["praise_nums"]
        artical.favor_nums = self["favor_nums"]
        artical.comment_nums = self["comment_nums"]
        artical.url = self["url"]
        artical.tags = self["tags"]
        artical.meta.id = self["url_object_id"]
        artical.suggest = gen_suggests(ArticalType._doc_type.index, ((artical.title, 10), (artical.tags, 7)))
        artical.save()
        redis_cli.incr("artical_count")
        return


class ZhihuQuestionItem(scrapy.Item):
    # 知乎问题的item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎的question
        insert_sql = """
                insert into zhihu_question2(zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content = VALUES(content), answer_num = VALUES(answer_num), 
                  comments_num = VALUES(comments_num), watch_user_num = VALUES(watch_user_num), click_num = VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["title"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = int(self["watch_user_num"][1].replace(",", ""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    # crawl_update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎的question
        insert_sql = """
                insert into zhihu_answer2(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
                  create_time, update_time, crawl_time) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE content = VALUES(content), comments_num = VALUES(comments_num), praise_num = VALUES(praise_num), update_time = VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self["create_time"])
        create_time = create_time.strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"])
        update_time = update_time.strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    job_addr = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job2(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params

    def save_to_es(self):
        artical = LagouType()
        artical.title = self['title']
        artical.create_date = self["crawl_time"]
        artical.url = self["url"]
        artical.url_object_id = self["url_object_id"]
        artical.salary = self["salary"]
        artical.job_city = self["job_city"]
        artical.work_years = self["work_years"]
        artical.degree_need = self["degree_need"]
        artical.job_type = self["job_type"]
        artical.tags = self["tags"]
        artical.publish_time = self["publish_time"]
        artical.job_advantage = self["job_advantage"]
        artical.job_desc = self["job_desc"]
        artical.job_addr = self["job_addr"]
        artical.company_name = self["company_name"]
        artical.company_url = self["company_url"]
        artical.suggest = gen_suggests(LagouType._doc_type.index, ((artical.title, 10), (artical.tags, 7)))
        artical.save()
        redis_cli.incr("lagou_count")

        return
