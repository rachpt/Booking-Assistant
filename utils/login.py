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
import re
import json
import binascii
import requests
from Crypto.PublicKey import RSA


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN, en-US q=0.8, zh q=0.5, en q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def encr_pw(pw, rsa_value, rsa_len):
    """RSA加密；参数：要加密的内容，加密key，key len"""
    key = RSA.construct([rsa_value, rsa_len])
    return key.encrypt(bytes(pw[::-1], "us-ascii"), 0)[0]


def find_token(html):
    """参数 html 页面，返回 token"""
    token = re.findall('"token[^>;)]+', html)
    if token:
        token = re.search("([0-9a-z]{30,})", token[0])
        if token:
            token = token.group(1)
    return token


def get_new_cookie(user, pwd, target_url):
    """
    参数：用户名，密码，认证网站地址
    返回：cookie字典，token
    通过统一认证登录，获取cookie
    """
    s = requests.session()

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
    data = {}
    r = s.get(pass_url, params=params, headers=headers)
    ress = re.findall(r'<input type="hidden"[^>]+>', r.text)
    for i in ress:
        pattern1 = re.match('.*name="([^"]+)" value="([^"]+)".*', i)
        if pattern1:
            name = pattern1.group(1)
            value = pattern1.group(2)
            data.update({name: value})
    # RSA 加密参数
    rsakeys = re.findall("RSAKeyPair[^;]+", r.text)
    pattern2 = re.match(r'RSAKeyPair.*"([\d]+)".*"([\w]{256})".*', rsakeys[0])
    if pattern2:
        rsa_len = int(pattern2.group(1), 16)
        rsa_value = int(pattern2.group(2), 16)
    # 使用 RSA 对用户名、密码加密
    user = binascii.hexlify(encr_pw(user, rsa_value, rsa_len)).decode("ascii")
    pwd = binascii.hexlify(encr_pw(pwd, rsa_value, rsa_len)).decode("ascii")
    data.update({"username": user, "password": pwd})

    # 获取 ticket
    r = s.post(
        pass_url, params=params, data=data, headers=headers, allow_redirects=False
    )
    # Location 中包含 ticket
    url2 = r.headers.get("Location")
    # 获取 cookie
    r = s.get(url2, headers=headers, allow_redirects=False)

    cookies = dict(r.cookies)
    cookies.pop("BIGipServerpool-tyb-cggl-yysf")

    # 必须使用带 jsessionid 参数的 get 请求访问一次，否则cookie无效。
    url3 = r.headers["Location"]
    s.get(url3, headers=headers, cookies=cookies, allow_redirects=False)
    # 验证 是否有登录成功才有的问候语
    r = s.get(target_url, headers=headers, cookies=cookies,)

    # 登录成功，cookie有效
    return (cookies, find_token(r.text)) if "您好" in r.text else (None, None)


if __name__ == "__main__":
    # 测试
    user = ""  # 学号
    pwd = ""  # 统一认证密码
    target_url = "http://pecg.hust.edu.cn/cggl/index1"
    cookies, token = get_new_cookie(user, pwd, target_url)
    print("Cookie:", cookies, "initaial:", token)
