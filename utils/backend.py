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
Base_Url = "http://pecg.hust.edu.cn/"
session = Session()
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
"""
时间格式:
08:00:00   10:00:00   12:00:00  14:00:00    16:00:00   18:00:00  20:00:00  # 22:00:00

zt: 2：已预约；4：不开放；1：可预约；3：使用中；5：预约中，''：不可预约。
pian: 场地代码。300：7号，299：6号，298：5号，297：4号，301：8号，134：1号
"""
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
    global session
    session.headers.update(
        {"Host": "pecg.hust.edu.cn", "Referer": "http://pecg.hust.edu.cn/cggl/"}
    )
    url = Base_Url + "cggl/front/huiyuandetail"
    requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    r = session.get(url, allow_redirects=False)
    if "退出" in r.text or r.status_code == 200:
        return True
    else:
        return False


def force_update_cookie(Cookie_Path, infos, verify=False):
    """使用学号与统一认证密码更新cookie"""
    global session
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
    读取、验证、更新 cookie，并保存 至文件下次使用
    """
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
            return False
    return True


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


def appointment(Config_Path, Cookie_Path, item, date_str, start_time, infos, days):
    """
    参数： 1.预约场地代号，2.预约日期，3.预约时间段开始点，4.同伴信息字典，返回  bool 值
    """
    global session
    r, url2 = step2_post_form(
        Config_Path, Cookie_Path, date_str, start_time, infos, item, days
    )
    if r.status_code != 200:
        raise UserWarning("step2 error:" + r.text)
    if "表单验证失败" in r.text:
        # 更新token，再试一次
        print("表单验证失败")
        r, url2 = step2_post_form(
            Config_Path, Cookie_Path, date_str, start_time, infos, item, days
        )
        if r.status_code != 200:
            raise UserWarning("step2 error again:" + r.text)
        if "表单验证失败" in r.text:
            raise UserWarning("step2 表单再次验证失败:" + r.text)
    # 确认预定
    url3 = Base_Url + "cggl/front/step3"
    data3 = get_confirm_data(r.text)
    token = match_token(r)
    data3.update({"token": (token, token)})
    session.headers.update({"Referer": url2, "X-Requested-With": None})
    # 开放系统前等待
    if judge_time():
        while strftime("%H:%M:%S", localtime()) <= "08:00:00":
            sleep(1)

    r = session.post(url3, data3)
    if "表单验证失败" in r.text:
        cancel_and_release(start_time, item, date_str)
        raise UserWarning("step3 error:" + r.text)

    if "在线预约扣费失败" in r.text:
        err_info = search(r"alert.HTMLDecode[^;]+", r.text)
        if err_info:
            err_info = err_info.group().split("'")[1]
        cancel_and_release(start_time, item, date_str)
        raise Warning(err_info)

    if r.status_code != 200:
        raise Warning(r.status_code, "step3 error:" + r.text)
    return True


def cancel_and_release(start_time, item, date_str):
    """预定失败，释放场地"""
    end_time = search(r"(\d+):00:00", start_time).group(1)
    end_time = int(end_time) + 2
    end_time = str(end_time) + ":00:00"
    params = {
        "spaceid": item,
        "cdbh": "69",
        "date": date_str,
        "starttime": start_time,
        "endtime": end_time,
    }
    session.get(Base_Url + "cggl/front/cancelreserve", params=params)


def step2_token(days, start_time):
    global session
    header_patch = {
        "Referer": Base_Url + "cggl/front/yuyuexz",
        "Host": "pecg.hust.edu.cn",
    }
    session.headers.update(header_patch)

    # 调日期
    current_day = date.today()
    _day = 0
    while _day <= days:
        date_str = (current_day + timedelta(days=_day)).strftime("%Y-%m-%d")
        if _day == 0:
            url = Base_Url + "cggl/front/syqk?cdbh=69"
        else:
            session.headers.update({"Referer": url})
            url = Base_Url + "cggl/front/syqk?date=" + date_str + "&type=1&cdbh=69"
        r = session.get(url)
        if r.status_code != 200:
            raise Warning(r.status_code, "get step2 [date] token error:" + r.text)
        token_in = match_token(r)
        _, token_out = get_zt_and_token(token_in, date_str, start_time, url)
        _day += 1
    # 调时间
    if start_time != "08:00:00":
        session.headers.update({"Referer": url})
        url = (
            Base_Url
            + "cggl/front/syqk?cdbh=69&date="
            + date_str
            + "&starttime="
            + start_time
            + "&endtime="
        )
        r = session.get(url)
        if r.status_code != 200:
            raise Warning(r.status_code, "get step2 [time] token error:" + r.text)
        token_in = match_token(r)
        _, token_out = get_zt_and_token(token_in, date_str, start_time, url)

    return token_out, r.url


def step2_post_form(Config_Path, Cookie_Path, date_str, start_time, infos, item, days):
    """方法独立，方便重复调用"""
    global session
    update_cookie(Config_Path, Cookie_Path)
    token, ref_url = step2_token(days, start_time)
    session.headers.update({"X-Requested-With": None, "Referer": ref_url})
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
        "date": date_str,
        "token": (token, token),
    }
    r = session.post(url2, data2, allow_redirects=False)
    return r, url2


def get_random_day_and_time(infos):
    """返回合法的随机日期以及时间，用于更新 token"""
    days = []
    times = []
    _today = date.today()
    for i in range(7):
        _day = _today + timedelta(days=i)
        _day = _day.strftime("%Y-%m-%d")
        if _day != infos[0]:
            days.append(_day)
        _time = "{0:02d}:00:00".format(8 + 2 * i)
        if _time != infos[1]:
            times.append(_time)
    day_ = days[randint(0, len(days) - 1)]
    time_ = times[randint(0, len(times) - 1)]
    return (day_, time_)


def get_token_by_refresh(param):
    """刷新当前页面"""
    params = {"cdbh": "69"}
    tok_url = Base_Url + "cggl/front/syqk"
    date_str = param[0]
    stime = param[1]
    ref_url = (
        tok_url + "?cdbh=69&date=" + date_str + "&starttime=" + stime + "&endtime="
    )
    params.update({"date": date_str, "starttime": stime, "endtime": ""})
    session.headers.update(
        {"X-Requested-With": None, "Upgrade-Insecure-Requests": "1", "Referer": ref_url}
    )
    r = session.get(tok_url, params=params, allow_redirects=False)

    return tok_url, match_token(r)


def get_token_by_random_refresh(param):
    """先去其他页面，再返回当前页面"""
    infos_other = get_random_day_and_time(param)
    params = {"cdbh": "69"}
    date_str = param[0]
    stime = param[1]
    date_2 = infos_other[0]
    stime_2 = infos_other[1]
    params.update({"date": date_2, "starttime": stime_2, "endtime": ""})
    tok_url = Base_Url + "cggl/front/syqk"
    ref_url = (
        tok_url + "?cdbh=69&date=" + date_str + "&starttime=" + stime + "&endtime="
    )
    session.headers.update(
        {"X-Requested-With": None, "Upgrade-Insecure-Requests": "1", "Referer": ref_url}
    )
    r = session.get(tok_url, params=params, allow_redirects=False)
    target_url = r.url
    session.headers.update({"Referer": target_url})
    r = session.get(ref_url, params=params, allow_redirects=False)

    return ref_url, match_token(r)


def get_token_normal(param=None):
    """
    获取 token；param: 0 日期，1 时间；refparam与param类似，表示上一次的param
    注意：时间在 22点至8点间，token需要使用其他url地址获取。
    """
    params = {"cdbh": "69"}
    tok_url = Base_Url + "cggl/front/syqk"
    session.headers.update({"X-Requested-With": None, "Upgrade-Insecure-Requests": "1"})

    # Referer 与 token 不匹配，第二次则会返回“表单验证失败，请重新返回提交”
    session.headers.update({"Referer": Base_Url + "cggl/front/yuyuexz"})

    r = session.get(tok_url, params=params, allow_redirects=False)
    # print("token---->>1", r.status_code, r.request.headers)
    if r.status_code != 200:
        # 非预定时间，只能用于查询，该token不能用于预定
        tok_url = Base_Url + "cggl/front/yuyuexz"
        r = session.get(tok_url, allow_redirects=False)
        # print("token---->>2", r.status_code, r.request.headers.get("Referer"))
    return tok_url, match_token(r)


def get_status(Config_Path, Cookie_Path, infos, refresh=False, rand_refresh=False):
    """
    infos 为 日期(info[0]) 与 时间(info[1])，返回 场地状态信息字典
    """
    res = {}
    token_out = ""

    update_cookie(Config_Path, Cookie_Path)
    if rand_refresh:
        tok_url, token_in = get_token_by_random_refresh(infos)
    elif refresh:
        tok_url, token_in = get_token_by_refresh(infos)
    else:
        tok_url, token_in = get_token_normal(infos)

    if token_in:
        date_str = str(infos[0])
        start_time = str(infos[1])
        res, token_out = get_zt_and_token(token_in, date_str, start_time, tok_url)

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


def get_zt_and_token(token_in, date_str, start_time, ref_url):
    global session
    header_patch = {
        "Upgrade-Insecure-Requests": None,
        "Referer": ref_url,
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://pecg.hust.edu.cn",
    }
    session.headers.update(header_patch)

    url = Base_Url + "cggl/front/ajax/getsyzt"
    end_time = search(r"(\d+):00:00", start_time).group(1)
    end_time = int(end_time) + 2
    end_time = str(end_time) + ":00:00"
    _data_ = [str(i) + "@" + start_time + "-" + end_time for i in pian_status.keys()]
    datas = {
        "changdibh": 69,
        "data": ",".join(_data_),
        "date": date_str,
        "token": token_in,
    }
    r = session.post(url, datas, allow_redirects=False)
    res = {}
    token_out = ""
    received = r.text
    if r.status_code == 200 and "message" in received:
        received = loads(received)
        token_out = received[0]["token"]
        status = received[0]["message"]
        for item in status:
            key, value, note = item["pian"], item["zt"], item["note"]
            res[key] = (value, note)
    return res, token_out


def add_partner(infos):
    """添加同伴信息"""
    global session
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
    r = session.post(add_url, data=datas)
    return True if pa_name in r.text and pa_num in r.text else False


def have_partner(pa_name, pa_num):
    """删除已经添加的相同同伴，并返回表单数据"""
    global session
    data = {}
    detail_url = Base_Url + "cggl/front/huiyuandetail"
    del_url = Base_Url + "cggl/front/delPartner"
    regx = r"'([\d]+)','{}','{}'".format(pa_name, pa_num)
    r = session.get(detail_url)
    id_pre = search(regx, r.text)
    if id_pre:
        id_pre = id_pre.group(1)
        r = session.get(del_url, params={"id": id_pre})
    token = match_token(r)
    data = get_hidden_form(r)
    data.update({"token": (token, token)})
    return data
