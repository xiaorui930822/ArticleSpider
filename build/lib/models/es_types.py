# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/8/7 0007 11:07'

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, InnerDoc, Completion, Keyword, Text, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticalType(DocType):
    # 伯乐在线文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    favor_nums = Integer()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')

    class Meta:
        index = "artical"
        doc_type = 'jobbole'


class LagouType(DocType):
    # 拉勾网职位类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    salary = Text(analyzer='ik_max_word')
    job_city = Text(analyzer='ik_max_word')
    work_years = Text(analyzer='ik_max_word')
    degree_need = Text(analyzer='ik_max_word')
    job_type = Text(analyzer='ik_max_word')
    tags = Text(analyzer='ik_max_word')
    publish_time = Text(analyzer='ik_max_word')
    job_advantage = Text(analyzer='ik_max_word')
    job_desc = Text(analyzer='ik_max_word')
    job_addr = Text(analyzer='ik_max_word')
    company_name = Text(analyzer='ik_max_word')
    company_url = Keyword()


    class Meta:
        index = "lagou2"
        doc_type = 'lagou'


if __name__ == "__main__":

    # ArticalType.init()
    LagouType.init()
