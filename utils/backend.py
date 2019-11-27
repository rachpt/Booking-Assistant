#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from re import findall, search
from json import loads
from pickle import dump, load
from random import randint
from datetime import date, timedelta, datetime
from time import sleep, strftime, localtime
import requests
from requests import Session

from .login import find_token as match_token
from .login import get_hidden_form, get_new_cookie


# 全局变量
# Config_Path = "config/user_info.pickle"
# Cookie_Path = "config/cookie.pickle"
Base_Url = "http://pecg.hust.edu.cn/"
session = Session()
cookies = {}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Referer": Base_Url,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
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


def judge_time(delta_time=30):
    """参数：与目标时间(8点)之差，单位秒；返回布尔值"""
    target_time = "08:00:00"  # 系统开放时间
    current_time = strftime("%H:%M:%S", localtime())
    d1_ = datetime.strptime(target_time, "%H:%M:%S")
    d2_ = datetime.strptime(current_time, "%H:%M:%S")
    if target_time >= current_time:
        time_diff = (d1_ - d2_).seconds
    else:
        time_diff = (d2_ - d1_).seconds
    return True if time_diff <= delta_time else False


def load_config(Config_Path):
    res = {}
    try:
        with open(Config_Path, "rb") as _file:
            res = load(_file)
    except KeyError:
        pass
    return res


def check_cookie(cookies):
    """验证cookie是否有效，返回bool值"""
    global session, token, headers
    headers.update(
        {"Host": "pecg.hust.edu.cn", "Referer": "http://pecg.hust.edu.cn/cggl/"}
    )
    url = Base_Url + "cggl/front/huiyuandetail"
    r = session.get(url, headers=headers, cookies=cookies, allow_redirects=False)
    if "退出" in r.text or r.status_code == 200:
        token = match_token(r)
        return True
    else:
        return False


def force_update_cookie(Cookie_Path, infos, verify=False):
    """使用学号与统一认证密码更新cookie"""
    global cookies, session
    if verify:
        session.close()
        session = Session()
    username = infos["student_id"]
    password = infos["student_pwd"]
    target_url = Base_Url + "cggl/index1"
    cookies = get_new_cookie(session, username, password, target_url)
    successed = check_cookie(cookies)
    if not successed:
        raise Exception("无法登录获取Cookie")
    if verify:
        _partner = add_partner(infos)
        if not _partner:
            raise Exception("同伴信息有误")
    with open(Cookie_Path, "wb") as _file:
        dump(cookies, _file)
    return True


def update_cookie(Config_Path, Cookie_Path):
    """
    读取、验证、更新 cookie，返回并保存 至文件下次使用
    """
    cookies = ""
    try:
        with open(Cookie_Path, "rb") as _file:
            cookies = load(_file)
            # 验证旧的 Cookie 是否有效
            if not check_cookie(cookies):
                raise UserWarning("Cookie 无效")
    except (FileNotFoundError, UserWarning):
        try:
            infos = load_config(Config_Path)
            _ = force_update_cookie(Cookie_Path, infos)
        except (FileNotFoundError, Exception):
            pass
    return cookies


def get_confirm_data(html):
    """获取预定确认表单数据"""
    data = {}
    pattern = r'input[^>]name[^>]+value[^>]+"'
    infos = findall(pattern, html)
    for item in infos:
        name = search(r'name="([^"]+)"', item).group(1)
        value = search(r'value="([^"]+)"', item).group(1)
        if name and value:
            data.update({name: value})
    return data


def appointment(Config_Path, Cookie_Path, item, date, start_time, infos):
    """
    参数： 1.预约场地代号，2.预约日期，3.预约时间段开始点，4.同伴信息字典，返回  bool 值
    """
    r, url2, cookies = step2_post_form(
        Config_Path, Cookie_Path, date, start_time, infos, item
    )
    # print("appoint: step2(第一次):", r.status_code, r.text)
    if r.status_code != 200:
        raise UserWarning(
            r.status_code, "{},step2 error:{}".format(r.status_code, r.text)
        )
    if "表单验证失败" in r.text:
        # 更新token，再试一次
        r, url2, cookies = step2_post_form(
            Config_Path, Cookie_Path, date, start_time, infos, item
        )
        # print("appoint: step2:", r.status_code, r.text)
        if r.status_code != 200:
            raise UserWarning(
                r.status_code, "{},step2 error:{}".format(r.status_code, r.text)
            )
        if "表单验证失败" in r.text:
            raise UserWarning(r.status_code, "step2 表单再次验证失败" + r.text)
    # 确认预定
    url3 = Base_Url + "cggl/front/step3"
    data3 = get_confirm_data(r.text)
    token = match_token(r)
    data3.update({"token": (token, token)})
    headers.update({"Referer": url2, "Origin": "http://pecg.hust.edu.cn"})
    # print(data3)
    # 开放系统前等待
    if judge_time():
        while strftime("%H:%M:%S", localtime()) <= "08:00:00":
            sleep(1)

    # 调试代码
    # if False:
    if True:
        r = session.post(
            url3, data3, headers=headers, cookies=cookies, allow_redirects=False
        )
        if r.status_code != 200:
            raise Warning(r.status_code, "step3 error" + r.text)
    return True if r.status_code == 200 else False


def step2_post_form(Config_Path, Cookie_Path, date, start_time, infos, item):
    """方法独立，方便重复调用"""
    global headers, cookies
    cookies = update_cookie(Config_Path, Cookie_Path)
    _, token = get_status(Config_Path, Cookie_Path, [date, start_time])

    url2 = Base_Url + "cggl/front/step2"
    data2 = {
        "starttime": start_time,
        "endtime": str(int(search(r"(\d+):00:00", start_time).group(1)) + 2) + ":00:00",
        "partnerCardType": 1,
        "partnerName": infos["pa_name"],
        "partnerSchoolNo": infos["pa_num"],
        "partnerPwd": infos["pa_pwd"],
        "choosetime": item,
        "changdibh": 69,
        "date": date,
        "token": (token, token),
    }
    r = session.post(
        url2, data2, headers=headers, cookies=cookies, allow_redirects=False
    )
    return r, url2, cookies


def get_random_day_and_time(infos):
    """返回合法的随机日期以及时间，用于更新 token"""
    days = []
    times = []
    for i in range(7):
        _day = date.today() + timedelta(days=i)
        _day = _day.strftime("%Y-%m-%d")
        if _day != infos[0]:
            days.append(_day)
        _time = "{0:02d}:00:00".format(8 + 2 * i)
        if _time != infos[1]:
            times.append(_time)
    day_ = days[randint(0, len(days) - 1)]
    time_ = times[randint(0, len(times) - 1)]
    return (day_, time_)


def get_token_by_refresh(cookies, param):
    """刷新当前页面"""
    params = {"cdbh": "69"}
    tok_url = Base_Url + "cggl/front/syqk"
    date = param[0]
    stime = param[1]
    ref_url = tok_url + "?cdbh=69&date=" + date + "&starttime=" + stime + "&endtime="
    params.update({"date": date, "starttime": stime, "endtime": ""})
    session.headers.update(
        {"X-Requested-With": None, "Upgrade-Insecure-Requests": "1", "Referer": ref_url}
    )
    r = session.get(tok_url, params=params, cookies=cookies, allow_redirects=False)

    return tok_url, match_token(r)


def get_token_by_random_refresh(cookies, param):
    """先去其他页面，再返回当前页面"""
    infos_other = get_random_day_and_time(param)
    params = {"cdbh": "69"}
    date = param[0]
    stime = param[1]
    date_2 = infos_other[0]
    stime_2 = infos_other[1]
    params.update({"date": date_2, "starttime": stime_2, "endtime": ""})
    tok_url = Base_Url + "cggl/front/syqk"
    ref_url = tok_url + "?cdbh=69&date=" + date + "&starttime=" + stime + "&endtime="
    session.headers.update(
        {"X-Requested-With": None, "Upgrade-Insecure-Requests": "1", "Referer": ref_url}
    )
    r = session.get(tok_url, params=params, cookies=cookies, allow_redirects=False)
    target_url = r.url
    session.headers.update({"Referer": target_url})
    r = session.get(ref_url, params=params, cookies=cookies, allow_redirects=False)

    return ref_url, match_token(r)


def get_token_normal(cookies, param=None):
    """
    获取 token；param: 0 日期，1 时间；refparam与param类似，表示上一次的param
    注意：时间在 22点至8点间，token需要使用其他url地址获取。
    """
    params = {"cdbh": "69"}
    tok_url = Base_Url + "cggl/front/syqk"
    session.headers.update({"X-Requested-With": None, "Upgrade-Insecure-Requests": "1"})

    # Referer 与 token 不匹配，第二次则会返回“表单验证失败，请重新返回提交”
    session.headers.update({"Referer": Base_Url + "cggl/front/yuyuexz"})

    r = session.get(tok_url, params=params, cookies=cookies, allow_redirects=False)
    # print("token---->>1", r.status_code, r.request.headers)
    if r.status_code != 200:
        # 非预定时间，只能用于查询，该token不能用于预定
        tok_url = Base_Url + "cggl/front/yuyuexz"
        r = session.get(tok_url, cookies=cookies, allow_redirects=False)
        # print("token---->>2", r.status_code, r.request.headers.get("Referer"))
    return tok_url, match_token(r)


def get_status(Config_Path, Cookie_Path, infos, refresh=False, rand_refresh=False):
    """
    infos 为 日期(info[0]) 与 时间(info[1])，返回 场地状态信息字典
    """
    global cookies
    res = {}
    token_out = ""

    cookies = update_cookie(Config_Path, Cookie_Path)
    if rand_refresh:
        tok_url, token_in = get_token_by_random_refresh(cookies, infos)
    elif refresh:
        tok_url, token_in = get_token_by_refresh(cookies, infos)
    else:
        tok_url, token_in = get_token_normal(cookies, infos)

    if token_in:
        date = str(infos[0])
        start_time = str(infos[1])
        header_patch = {
            "Upgrade-Insecure-Requests": None,
            "Referer": tok_url,
            "Host": "pecg.hust.edu.cn",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://pecg.hust.edu.cn",
        }
        session.headers.update(header_patch)

        url = Base_Url + "cggl/front/ajax/getsyzt"
        end_time = search(r"(\d+):00:00", start_time).group(1)
        end_time = int(end_time) + 2
        end_time = str(end_time) + ":00:00"
        _data_ = [
            str(i) + "@" + start_time + "-" + end_time for i in pian_status.keys()
        ]
        datas = {
            "changdibh": 69,
            "data": ",".join(_data_),
            "date": date,
            "token": token_in,
        }
        r = session.post(url, datas, cookies=cookies, allow_redirects=False)

        received = r.text
        if r.status_code == 200 and "message" in received:
            received = loads(received)
            token_out = received[0]["token"]
            status = received[0]["message"]
            for item in status:
                key, value, note = item["pian"], item["zt"], item["note"]
                res[key] = (value, note)

    if not token_out and not refresh:
        # 自更新，“表单验证失败，请重新返回提交”
        # print("--" * 10, "自更新")
        return get_status(Config_Path, Cookie_Path, infos, refresh=True)

    if not token_out and not rand_refresh:
        # 自更新无效，再出去转一下再回来
        # print("--" * 13, "出去转一圈")
        return get_status(Config_Path, Cookie_Path, infos, rand_refresh=True)

    # 正常情况
    return res, token_out


def add_partner(infos):
    """添加同伴信息"""
    global cookies, session
    add_url = Base_Url + "cggl/front/addPartner"
    pa_name = infos["pa_name"]
    pa_num = infos["pa_num"]
    pa_pwd = infos["pa_pwd"]
    datas = {
        "partner_name": pa_name,
        "partner_type": "1",
        "partner_schoolno": pa_num,
        "partner_passwd": pa_pwd,
    }
    data = have_partner(pa_name, pa_num)
    datas.update(data)
    r = session.post(add_url, data=datas, headers=headers, cookies=cookies)
    return True if pa_name in r.text and pa_num in r.text else False


def have_partner(pa_name, pa_num):
    """删除已经添加的相同同伴，并返回表单数据"""
    global cookies, session
    data = {}
    detail_url = Base_Url + "cggl/front/huiyuandetail"
    del_url = Base_Url + "cggl/front/delPartner"
    regx = r"'([\d]+)','{}','{}'".format(pa_name, pa_num)
    r = session.get(detail_url, cookies=cookies, headers=headers)
    id_pre = search(regx, r.text)
    if id_pre:
        id_pre = id_pre.group(1)
        r = session.get(
            del_url, params={"id": id_pre}, headers=headers, cookies=cookies
        )
    token = match_token(r)
    data = get_hidden_form(r)
    data.update({"token": (token, token)})
    return data
