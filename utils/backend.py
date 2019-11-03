#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import os
import re
import datetime
import json
import pickle
import requests
from selenium import webdriver
from platform import system
from time import sleep
from . import setting

# 全局变量
Cookie_Path = "config/cookie.pickle"

headers = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Referer': 'http://pecg.hust.edu.cn/cggl/front/yuyuexz'
}

test_user_info = {
    "student_id": "M201770172",
    'student_pwd': "111111111",
    'browser': 'Chrome',
    'browser_path': 'C:/Program Files/Google Chrome/chrome.exe'
}

'''时间格式
08:00:00   10:00:00   12:00:00  14:00:00    16:00:00   18:00:00  20:00:00  # 22:00:00
'''


'''
zt: 2：已预约；4：不开放；1：可预约；3：使用中；5：预约中，''：不可预约。
pian: 场地代码。300：7号，299：6号，298：5号，297：4号，301：8号，134：1号
'''
zt_status = {2: '已预约', 4: '不开放', 1: '可预约', 3: '使用中', 5: '预约中', '': '不可预约'}
pian_status = {
    '300': '7',
    '299': '6',
    '298': '5',
    '297': '4',
    '301': '8',
    '134': '1',
    '295': '2',
    '296': '3'
}

is_win = 'windows' in system().lower()


def load_config():
    res = {}
    try:
        with open(setting.Config_Path, "rb") as _file:
            res = pickle.load(_file)
    except KeyError:
        pass
    return res


def get_cookie(infos):
    '''
    通过 学号、密码 统一登录，返回cookie，支持 Firefox、Chrome
    '''
    username = infos['student_id']
    password = infos['student_pwd']
    browser = infos['browser']
    browser_path = infos['browser_path']
    url = 'https://pass.hust.edu.cn/cas/login?service=http://pecg.hust.edu.cn/cggl/index1'
    cookies = {}
    if browser == 'Firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        if is_win:
            options.binary_location = browser_path
            driver = webdriver.Firefox(options=options,
                                       executable_path='bin/geckodriver.exe')
        else:
            driver = webdriver.Firefox(options=options,
                                       executable_path='bin/geckodriver')
    elif browser == 'Chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        if is_win:
            options.binary_location = browser_path
            driver = webdriver.Chrome(executable_path='bin/chromedriver.exe',
                                      options=options)
        else:
            driver = webdriver.Chrome(executable_path='bin/chromedriver',
                                      options=options)

    driver.get(url)
    # print('0000000000')
    if "统一身份认证系统" in driver.title:
        driver.find_element_by_id("username_text").send_keys(username)
        driver.find_element_by_id("password_text").send_keys(password)
        driver.find_element_by_class_name("login_box_landing_btn").click()
        # sleep(30)
        # print('f111111111')
        if "华中科技大学体育场馆管理系统" in driver.title:
            cookies = driver.get_cookies()
    driver.quit()

    cookie = {}

    for item in cookies:
        # cookie 只需要下面两个字段的 值
        if item['name'] == 'JSESSIONID' or item[
                'name'] == 'BIGipServerpool-tyb-cggl-yysf':
            cookie[item['name']] = item['value']
    if cookie:
        cookie = list("{}={}".format(key, cookie[key])
                      for key in cookie.keys())
        cookie = ";".join(cookie)
    return cookie if cookie else None


def get_token(cookie):
    '''
    获取 token，并用于验证 cookie 是否有效
    '''
    global headers
    tok_url = 'https://pecg.hust.edu.cn/cggl/front/yuyuexz'
    headers.update(Cookie=cookie)
    r = requests.get(tok_url, headers=headers)
    token = ''
    if r.status_code == 200:
        token = re.findall('"token[^,}]+', r.text)
        if token:
            token = re.search('([0-9a-z]{30,})', token[0])
            if token:
                token = token.group(1)
    return token


def update_cookie():
    '''
    更新 cookie，返回并保存 至文件下次使用
    '''
    cookie = ''
    try:
        with open(Cookie_Path, "rb") as _file:
            cookie = pickle.load(_file)
        if cookie and not get_token(cookie):
            raise UserWarning('Cookie 无效')

    except (FileNotFoundError, UserWarning):
        try:
            cookie = get_cookie(load_config())
            if cookie:
                with open(Cookie_Path, "wb") as _file:
                    pickle.dump(cookie, _file)
        except (FileNotFoundError, Exception):
            pass
    return cookie


def appointment(item, date, start_time, infos):
    '''
    参数： 1.预约场地代号，2.预约日期，3.预约时间段开始点，4.同伴信息字典，返回  bool 值
    '''
    global headers
    token = get_token(update_cookie())

    url = 'http://pecg.hust.edu.cn/cggl/front/step2'
    data = {
        'starttime': start_time,
        'endtime':
        str(int(re.search(r'(\d+):00:00', start_time).group(1)) + 2) +
        ':00:00',
        'partnerCardType': 1,
        'partnerName': infos['pa_name'],
        'partnerSchoolNo': infos['pa_num'],
        'partnerPwd': infos['pa_pwd'],
        'choosetime': item,
        'changdibh': 69,
        'date': date,
        'token': [token, token]
    }
    r = requests.post(url, data, headers=headers, allow_redirects=False)
    # print(r.status_code, r.text)
    if r.status_code != 200:
        raise Warning(r.status_code, r.text)
    return True if r.status_code == 200 else False


def get_status(infos):
    '''
    infos 为 日期(info[0]) 与 时间(info[1])，返回 场地状态信息字典
    '''
    res = {}
    token = get_token(update_cookie())
    if token:
        url = 'http://pecg.hust.edu.cn/cggl/front/ajax/getsyzt'
        end_time = str(int(re.search(r'(\d+):00:00', infos[1]).group(1)) +
                       2) + ':00:00'
        datas = {
            'changdibh':
            69,
            'data':
            ','.join(
                list(
                    str(i) + '@' + infos[1] + '-' + end_time
                    for i in pian_status.keys())),
            'date':
            infos[0],
            'token':
            token
        }
        r = requests.post(url, datas, headers=headers)
        received = r.text
        if r.status_code == 200 and 'message' in received:
            received = json.loads(received)
            received = received[0]['message']
            for item in received:
                key, value = item['pian'], item['zt']
                res[key] = value
    return res
