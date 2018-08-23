# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/7/11 0011 21:03'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector

# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
browser = webdriver.Chrome(executable_path="H:/chromedriver.exe")
# browser.maximize_window()

"""
browser.get('https://detail.tmall.com/item.htm?id=570283990461&spm=875.7931836/B.2017077.9.148d4265VvafR2&scm=1007.12144.81309.73263_0&pvid=7e409aca-7602-45a1-afcd-583d41cabb46&utparam={%22x_hestia_source%22:%2273263%22,%22x_mt%22:8,%22x_object_id%22:570283990461,%22x_object_type%22:%22item%22,%22x_pos%22:8,%22x_pvid%22:%227e409aca-7602-45a1-afcd-583d41cabb46%22,%22x_src%22:%2273263%22}')
print(browser.page_source)
t_selector = Selector(text=browser.page_source)
print(t_selector.css('.tm-promo-price .tm-price::text').extract())
"""

"""selenium完成微博模拟登录

browser.get('https://weibo.com/')
import time
time.sleep(10)
browser.find_element_by_css_selector('#loginname').send_keys('个人账号')
browser.find_element_by_css_selector('.info_list.password .Input').send_keys('个人密码')
browser.find_element_by_css_selector('.info_list.login_btn a[node-type="submitBtn"]').click()

"""
"""
browser.get('https://www.oschina.net/blog')
import time
time.sleep(5)
for i in range(3):
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight); var lenOfPage = document.body.scrollHeight; return lenOfPage;')
    time.sleep(3)
"""
"""
# 设置Chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {'profile.manage_default_content_settings.images':2}
chrome_opt.add_experimental_option('prefs',prefs)
browser = webdriver.Chrome(executable_path="H:/chromedriver.exe", chrome_options=chrome_opt)
browser.get('https://www.taobao.com')
"""
# browser.quit()

"""
# phantomjs无界面浏览器的使用，多进程下phantomjs性能下载严重

browser = webdriver.PhantomJS(executable_path="E:/phantomjs-2.1.1-windows/bin/phantomjs.exe")
browser.get('https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w10921125-15478044004.23.716d6839zEVMgR&id=544541272577&sku_properties=5919063:6536025&scene=taobao_shop')

print(browser.page_source)
browser.quit()
"""