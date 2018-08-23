# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import codecs #完成文件打开和写入
import json,datetime,MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

class Articalspider2Pipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('artical.json','w',encoding="utf-8")
    def process_item(self,item,spider):
        lines = json.dumps(dict(item), ensure_ascii=False)+ "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open("articalexport.json","wb")
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item

class ArticalImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
            return item

class MysqlPipeline(object):#同步机制写入数据库
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1','root','930822','artical_spider',charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_artical2(title, url, create_date, url_object_id, front_image_url, praise_nums, comment_nums, favor_nums, tags, content)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["url_object_id"], item["front_image_url"],
                                         item["praise_nums"], item["comment_nums"], item["favor_nums"], item["tags"], item["content"]))
        self.conn.commit()

class MysqlTwistedPipeline(object):#改变对应的pipeline，异步机制写入数据库
    def __init__(self, dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],  #可以直接读取settings中的值
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = "utf8",
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    def process_item(self,item,spider):#使用twist讲mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item)#处理异常

    def handle_error(self, failure):#处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):#执行具体插入
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class ElasticsearchPipeline(object):
    #将数据写入到es中
    def process_item(self,item,spider):
        #将item转换为es的数据
        item.save_to_es()
        return item