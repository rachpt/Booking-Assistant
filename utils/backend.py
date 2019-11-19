#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import os
import re
import json
import pickle
import requests
from . import setting
from . import login

# 全局变量
Config_Path = setting.Config_Path
Cookie_Path = "config/cookie.pickle"
Base_Url = "http://pecg.hust.edu.cn/"
session = requests.Session()
cookies = {}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Referer": Base_Url,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    # "Cache-Control": "max-age=0",
}
session.headers.update(headers)
"""时间格式
08:00:00   10:00:00   12:00:00  14:00:00    16:00:00   18:00:00  20:00:00  # 22:00:00
"""

"""
zt: 2：已预约；4：不开放；1：可预约；3：使用中；5：预约中，''：不可预约。
pian: 场地代码。300：7号，299：6号，298：5号，297：4号，301：8号，134：1号
"""
zt_status = {2: "已预约", 4: "不开放", 1: "可预约", 3: "使用中", 5: "预约中", "": "不可预约"}
pian_status = {
    "300": "7",
    "299": "6",
    "298": "5",
    "297": "4",
    "301": "8",
    "134": "1",
    "295": "2",
    "296": "3",
}


def load_config():
    res = {}
    try:
        with open(Config_Path, "rb") as _file:
            res = pickle.load(_file)
    except KeyError:
        pass
    return res


def match_token(html):
    """参数 html 页面，返回 token"""
    token = re.findall('"token[^,}]+', html)
    if token:
        token = re.search("([0-9a-z]{30,})", token[0])
        if token:
            token = token.group(1)
    # print("match token:", token)
    return token


def check_cookie(cookies):
    """验证cookie是否有效，返回bool值"""
    global session, token
    url = Base_Url + "cggl/index"
    r = session.get(url, cookies=cookies)
    if "退出" in r.text:
        token = match_token(r.text)
        # print(r.request.headers)
        return True
    else:
        return False


def get_token(cookies, param=None):
    """
    获取 token；param: 0 日期，1 时间
    """
    params = {"cdbh": "69"}
    tok_url = Base_Url + "cggl/front/syqk"
    if param:
        params.update({"date": param[0], "starttime": param[1], "endtime": ""})
        session.headers.update(
            {"Referer": tok_url + "?date={}&type=1&cdbh=69".format(param[0])}
        )
    else:
        session.headers.update({"Referer": Base_Url + "cggl/front/yuyuexz"})
    r = session.get(tok_url, params=params, cookies=cookies)
    return match_token(r.text)


def force_update_cookie(infos):
    """使用学号与统一认证密码更新cookie"""
    username = infos["student_id"]
    password = infos["student_pwd"]
    target_url = Base_Url + "cggl/index1"
    cookies, token = login.get_new_cookie(username, password, target_url)
    successed = check_cookie(cookies)
    if successed:
        with open(Cookie_Path, "wb") as _file:
            pickle.dump(cookies, _file)
        return True
    return False


def update_cookie():
    """
    读取、验证、更新 cookie，返回并保存 至文件下次使用
    """
    cookies = ""
    try:
        with open(Cookie_Path, "rb") as _file:
            cookies = pickle.load(_file)
            # 验证旧的 Cookie 是否有效
            if not check_cookie(cookies):
                print("旧Cookie无效")
                raise UserWarning("Cookie 无效")
    except (FileNotFoundError, UserWarning):
        try:
            infos = load_config()
            force_update_cookie(infos)
        except (FileNotFoundError, Exception):
            pass
    return cookies


def appointment(item, date, start_time, infos):
    """
    参数： 1.预约场地代号，2.预约日期，3.预约时间段开始点，4.同伴信息字典，返回  bool 值
    """
    global headers, cookies
    cookies = update_cookie()
    _, token = get_status([date, start_time])

    url = "http://pecg.hust.edu.cn/cggl/front/step2"
    data = {
        "starttime": start_time,
        "endtime": str(int(re.search(r"(\d+):00:00", start_time).group(1)) + 2)
        + ":00:00",
        "partnerCardType": 1,
        "partnerName": infos["pa_name"],
        "partnerSchoolNo": infos["pa_num"],
        "partnerPwd": infos["pa_pwd"],
        "choosetime": item,
        "changdibh": 69,
        "date": date,
        "token": (token, token),
    }
    r = session.post(url, data, headers=headers, cookies=cookies, allow_redirects=False)
    print("#" * 15)
    print(r.request.headers)
    print(r.status_code, r.text)
    if r.status_code != 200:
        raise Warning(r.status_code, r.text)
    return True if r.status_code == 200 else False


def get_status(infos):
    """
    infos 为 日期(info[0]) 与 时间(info[1])，返回 场地状态信息字典
    """
    global cookies
    res = {}
    cookies = update_cookie()
    token = get_token(cookies, infos)
    if token:
        ref = Base_Url + "cggl/front/syqk?cdbh=69&date={}&starttime={}&endtime=".format(
            infos[0], infos[1]
        )
        session.headers.update(
            {
                "Referer": ref,
                "Host": "pecg.hust.edu.cn",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "http://pecg.hust.edu.cn",
            }
        )

        url = "http://pecg.hust.edu.cn/cggl/front/ajax/getsyzt"
        end_time = str(int(re.search(r"(\d+):00:00", infos[1]).group(1)) + 2) + ":00:00"
        datas = {
            "changdibh": 69,
            "data": ",".join(
                list(
                    str(i) + "@" + infos[1] + "-" + end_time for i in pian_status.keys()
                )
            ),
            "date": infos[0],
            "token": token,
        }
        r = session.post(url, datas, cookies=cookies)
        # print("+" * 10)
        # print("get status:", r.request.headers)
        received = r.text
        # print(received)
        if r.status_code == 200 and "message" in received:
            received = json.loads(received)
            token = received[0]["token"]
            status = received[0]["message"]
            for item in status:
                key, value = item["pian"], item["zt"]
                res[key] = value
    # print("return token:", token)
    return res, token
