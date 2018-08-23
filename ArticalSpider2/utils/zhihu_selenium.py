# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/8/22 0022 16:28'

from selenium import webdriver
import os
from os import path
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector

# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# # browser = webdriver.Chrome(executable_path="H:/chromedriver.exe")
# chrome_opt = webdriver.ChromeOptions()
# prefs = {'profile.manage_default_content_settings.images':2}
# chrome_opt.add_experimental_option('prefs',prefs)
# browser = webdriver.Chrome(executable_path="H:/chromedriver3.exe", chrome_options=chrome_opt)

browser = webdriver.PhantomJS(executable_path="E:/phantomjs-2.1.1-windows/bin/phantomjs.exe")
browser.get('https://www.zhihu.com/signup?next=%2F')
import time
time.sleep(2)

browser.find_element_by_css_selector('.SignContainer-switch span').click()
time.sleep(2)
browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys('13554046083')
time.sleep(2)
browser.find_element_by_css_selector('.Input-wrapper input[type="password"]').send_keys('wan331957577')
time.sleep(2)
browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
zhihu_cookie = browser.get_cookies()
res = browser.get('www.zhihu.com')
res = browser.page_source
cookie_dict = {}
# index = 5
# while True :
#     page_source = browser.page_source
#     if 'Captcha-englishContainer' in page_source:
#         print('英文验证码：')
#         if index < 5:
#             a = input()
#             browser.find_element_by_css_selector('.Captcha.SignFlow-captchaContainer input[name="captcha]').send_keys(a)
#     elif 'Captcha-chineseOperator' in page_source:
#         print('倒立的文字')
#     browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
#     index = index - 1
#     if browser.title != '知乎 - 发现更大的世界':
#         break
# zhihu_cookies = browser.get_cookies()
import pickle
for cookie in zhihu_cookie:
    aa = os.path.abspath(__file__)
    bb = os.path.dirname(aa)
    cc = os.path.dirname(bb)
    dd = path.join(cc, 'cookies')
    base_path = path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookies')
    ee = dd + "/zhihu/" + cookie['name'] + '.zhihu'
    f = open(base_path + "/zhihu/" + cookie['name'] + '.zhihu', 'wb')
    pickle.dump(cookie, f)
    f.close()
    cookie_dict[cookie['name']] = cookie['value']
browser.close()

'H:\\pyprojects\\ArticalSpider2\\ArticalSpider2\\cookies/zhihu/capsion_ticket.zhihu'


