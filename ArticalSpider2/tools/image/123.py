# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/8/15 0015 16:18'

import re
import time
import hmac
from hashlib import sha1
import json
import base64
import requests
import PIL.Image as Image
try:
    import cookielib
except:
    import http.cookiejar as cookielib



session = requests.session()

session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")  # cookie存储文件，


try:
    session.cookies.load(ignore_discard=True)  # 从文件中读取cookie
except:
    print("cookie 未能加载")


agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
header = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    "User-agent":agent
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否登录
    # 通过allow_redirects 设置为不获取重定向后的页面

    response = session.get("https://www.zhihu.com/inbox", headers=header, allow_redirects=False)

    print(response.cookies)
    print(response.status_code)
    if response.status_code != 200:
        print("尚未登录")
        zhihu_login("+861563915****", "****")
    else:
        print("你已经登陆了")


def get_xsrf():
    response = session.post("https://www.zhihu.com/signup?next=%2F", headers=header)
    print(response.cookies['_xsrf'])
    return response.cookies['_xsrf']


def get_signature(time_str):
    h = hmac.new(key='d1b964811afb40118a12068ff74a12f4'.encode('utf-8'), digestmod=sha1)
    grant_type = 'password'
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    now = time_str
    h.update((grant_type + client_id + source + now).encode('utf-8'))
    return h.hexdigest()

def get_captcha():

    '''
    :authority: www.zhihu.com
    :method: GET
    :path: /api/v3/oauth/captcha?lang=cn
    :scheme: https
    accept: application/json, text/plain, */*
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9,en;q=0.8
    authorization: oauth c3cef7c66a1843f8b3a9e6a1e3160e20
    cookie: d_c0="AIDk5lsxrA2PTn6UE7w8ZXwIcLwr6s4V8TM=|1527673963"; q_c1=29e9198d965c42b4b4d13820bc7023db|1527673963000|1527673963000; _zap=a0bc8c13-50e7-484b-abde-db97010a065b; l_cap_id="YzIxYmFmNzg0YjViNGZmODljNTIwMjUwMTQ5NWY0NTY=|1527688563|f3bfccc25e61ab0e6c92295650f257e2f9cd779b"; r_cap_id="YTE3M2JlMWQ4NWQzNDA2NzllYThmMWYxNjMxZmRhMTY=|1527688563|be9b0cd7843bf090e5e0194ceb29a99fc60a1cce"; cap_id="ZWFjYTg3ODljMzI0NDVmOTgyYmE0NjRiMGQyZGRmYmU=|1527688563|4636e8decd51156afe879407f16e6c7f57e222ce"; tgw_l7_route=5bcc9ffea0388b69e77c21c0b42555fe; _xsrf=405b7e07-d4f5-4b35-8b70-3e129d97a4d8; capsion_ticket="2|1:0|10:1527727674|14:capsion_ticket|44:Y2M3YTcwYWQ3OGFiNGIxMjk3MWUwY2I5ZWQ0OWM0ZjQ=|ed0700eadd8466ffd6f4c61dfbce11a1f4d11483f32f1ae8262501a7fd859558"
    if-none-match: "fa4cf03c0ac47ca1c52ed2df2b71dfda86db6655"
    referer: https://www.zhihu.com/signup?next=%2F
    user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36
    x-udid: AIDk5lsxrA2PTn6UE7w8ZXwIcLwr6s4V8TM=
    '''

    header.update({
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"
    })
    captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
    response = session.get(captcha_url, headers=header)

    print(response.text)
    r = re.findall('"show_captcha":(\w+)', response.text)
    if r[0] == 'false':
        return ''
    else:
        print("需要输入验证码！")
        response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=cn', headers=header)
        show_captcha = json.loads(response.text)['img_base64']
        with open('captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(show_captcha))
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print("打开文件失败！")

        captcha = input('输入验证码:')

        return captcha

def zhihu_login(account, password):
    # 知乎登录
    time_str = str(int(time.time()))
    xsrf = get_xsrf()
    header.update({
        "X-Xsrftoken": xsrf
    })
    post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
    post_data = {
        "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
        "grant_type": "password",
        "timestamp": time_str,
        "source": "com.zhihu.web",
        "signature": get_signature(time_str),
        "username": account,
        "password": password,
        "captcha": get_captcha(),
        "lang": "cn",
        "ref_source": "homepage",
        "utm_source": ""
    }

    response = session.post(post_url, data=post_data, headers=header, cookies=session.cookies)
    if response.status_code == 201:
        # 保存cookie，下次直接读取保存的cookie，不用再次登录
        print("登录成功")

        response = session.post("https://www.zhihu.com", headers=header, cookies=session.cookies)
        print(response.text)
        session.cookies.save()
    else:
        print("登录失败")

if __name__ == '__main__':
    is_login()