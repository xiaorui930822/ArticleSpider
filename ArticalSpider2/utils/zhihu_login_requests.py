import requests, json
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")


agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
header = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    "User-agent":agent
}

def is_login():
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url,headers = header,allow_redirects = False)
    if response.status_code !=200:
        return False
    else:
        return True

def get_xsrf():
    response = session.get("https://www.zhihu.com/signup?next=%2F",headers=header)
    print(response.text)
    print(response.cookies['_xsrf'])
    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text, re.S)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""

def get_index():
    response = session.get("https://www.zhihu.com",headers=header)
    with open("index_page.html","wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")

def get_captcha():
    import time
    t = str(int(time.time() * 1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    t = session.get(captcha_url, headers=header)
    with open("captcha.jpg", "wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    lang = input("输入验证码类别：cn/en：")
    if lang == "cn":
        captcha = {
            'img_size': [200, 44],
            'input_points': [],
        }
        points = [[22.796875, 22], [42.796875, 22], [63.796875, 21], [84.796875, 20], [107.796875, 20],
                  [129.796875, 22],
                  [150.796875, 22]]
        seq = input('请输入倒立字的位置\n>')
        for i in seq:
            captcha['input_points'].append(points[int(i) - 1])
        return json.dumps(captcha)
    else:
        captcha = input("输入验证码\n>")
        return captcha


def zhihu_login(account,password):
    #知乎登录
    if re.match("^1\d{10}",account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
        post_data = {
            "_xsrf":get_xsrf(),
            "phone_num":account,
            "password":password,
            "captcha_type":get_captcha()
        }

    else:
        if "@"in account:
            #判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
            post_data = {
                "_xsrf": get_xsrf(),
                "phone_num": account,
                "password": password,
                # "captcha_type":get_captcha_type
            }
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()
    # res_text = response_text.text.replace('\n', '')
    # response_text = json.loads(res_text)
    # if 'msg' in response_text and response_text['msg'] == '登录成功':
    #     print('登录成功！')
    # else:
    #     print('登录失败')

zhihu_login("13554046083","wan331957577")
# get_index()
is_login()