import requests
from scrapy.selector import Selector
import MySQLdb
conn = MySQLdb.connect(host = "127.0.0.1", user = "root", passwd = "930822", db = "artical_spider", charset = "utf8")
cursor = conn.cursor()

def crawl_ips():
    #爬取西祠ip
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.7 Safari/537.36"}
    for i in range(1000):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers = headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []
        for tr in all_trs[1:]:
            all_texts = tr.css("td::text").extract()
            if all_texts[5] =='HTTP':
                ip = all_texts[0]
                port = all_texts[1]
                proxy_type = all_texts[5]
                speed_str = tr.css(".bar::attr(title)").extract()
                if speed_str:
                    speed_str = speed_str[0].split("秒")[0]
                    speed = float(speed_str)
                ip_list.append((ip, port, proxy_type,speed))
        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, 'HTTP')".format(
                    ip_info[0], ip_info[1], ip_info[3]
                )
            )
            conn.commit()
class GetIP(object):
    def delete_ip(self,ip):
        #删除无效ip
        delete_sql = """
            delete from proxy_ip where ip = '{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self,ip,port):
        #判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip,port)
        try:
            proxy_dict = {
                "http":proxy_url
            }
            response = requests.get(http_url, proxies = proxy_dict)
            return True
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        #随机从数据库随机获取一个ip
        random_sql = """
            SELECT ip,port FROM proxy_ip  
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_result = self.judge_ip(ip,port)
            if judge_result:
                return "http://{0}:{1}".format(ip,port)
            else:
                return self.get_random_ip()

# print(crawl_ips())
if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()