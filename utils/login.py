#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    : login.py
@Time    : 2019/11/16 16:07:52
@Author  : rachpt
@Version : 0.1
@Contact : rachpt@126.com
"""

# here put the import lib
from re import findall, search, match
from binascii import hexlify
from Crypto.PublicKey import RSA


def encr_pw(pw, rsa_value, rsa_len):
    """RSA加密；参数：要加密的内容，加密key，key len"""
    key = RSA.construct([rsa_value, rsa_len])
    return key.encrypt(bytes(pw[::-1], "us-ascii"), 0)[0]


def find_token(r):
    """参数 r requests请求，返回 token"""
    token = findall('"token[^>;)]+', r.text)
    if token:
        token = search("([0-9a-z]{30,})", token[0])
        if token:
            token = token.group(1)
    return token


def get_hidden_form(r):
    """获取隐藏表单数据"""
    data = {}
    res = findall(r'<input type="hidden"[^>]+>', r.text)
    if res:
        for i in res:
            pattern1 = search(r'.*name="([^"]+)"', i)
            pattern2 = search(r'value="([^"]+)".*', i)
            if pattern1 and pattern2:
                name = pattern1.group(1)
                value = pattern2.group(1)
                data.update({name: value})
    return data


def get_dict_cookie(r):
    """将header中的cookie转成字典形式"""
    cookies = r.request.headers.get("Cookie")
    if cookies:
        cookies = cookies.split(";")  # 字符串到列表
        cookies = set([i.strip() for i in cookies])  # 去重，注意前后空格
        cookies = {i.split("=")[0]: i.split("=")[1] for i in cookies}  # 字典
    return cookies


def get_new_cookie(s, user, pwd, target_url):
    """
    参数：用户名，密码，认证网站地址
    返回：cookie字典，token
    通过统一认证登录，获取cookie
    """

    pass_url = "https://pass.hust.edu.cn/cas/login"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN, en-US q=0.8, zh q=0.5, en q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # 获取 表单信息
    params = {"service": target_url}
    r = s.get(pass_url, params=params, headers=headers)
    data = get_hidden_form(r)
    if not data:
        # 当前 cookie 有效
        cookies = get_dict_cookie(r)
        return cookies if "您好" in r.text else None
    # RSA 加密参数
    rsakeys = findall("RSAKeyPair[^;]+", r.text)
    pattern2 = match(r'RSAKeyPair.*"([\d]+)".*"([\w]{256})".*', rsakeys[0])
    if pattern2:
        rsa_len = int(pattern2.group(1), 16)
        rsa_value = int(pattern2.group(2), 16)
    # 使用 RSA 对用户名、密码加密
    user = hexlify(encr_pw(user, rsa_value, rsa_len)).decode("ascii")
    pwd = hexlify(encr_pw(pwd, rsa_value, rsa_len)).decode("ascii")
    data.update({"username": user, "password": pwd})

    # 获取 ticket
    r = s.post(
        pass_url, params=params, data=data, headers=headers, allow_redirects=False
    )
    # Location 中包含 ticket
    url2 = r.headers.get("Location")
    # 获取 cookie
    if not url2:
        raise Exception("学号或者统一身份认证密码有误")
    r = s.get(url2, headers=headers, allow_redirects=False)
    cookies = dict(r.cookies)

    # 必须使用带 jsessionid 参数的 get 请求访问一次，否则cookie无效。
    url3 = r.headers["Location"]
    s.get(url3, headers=headers, allow_redirects=False)
    # 验证 是否有登录成功才有的问候语
    r = s.get(target_url, headers=headers, cookies=cookies)
    cookies = get_dict_cookie(r)
    # 登录成功，cookie有效
    return cookies if "您好" in r.text else None


if __name__ == "__main__":
    # 测试
    user = ""  # 学号
    pwd = ""  # 统一认证密码
    target_url = "http://pecg.hust.edu.cn/cggl/index1"
    from requests import Session

    s = Session()

    cookies = get_new_cookie(s, user, pwd, target_url)
    print("Cookie:", cookies)

    url = "http://pecg.hust.edu.cn/cggl/index"
    r = s.get(url)
    if "退出" in r.text:
        print(r.request.headers)
