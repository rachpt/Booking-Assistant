#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import pickle
import tkinter as tk
from tkinter import StringVar, Label, E, Button
from tkinter.filedialog import askopenfilename

from . import backend

Config_Path = "config/user_info.pickle"


class SettingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.is_checking = tk.BooleanVar()
        self.is_checking.set(False)
        self.var_id = StringVar()
        self.var_pwd = StringVar()
        self.var_browser = StringVar()
        self.var_browser_path = StringVar()

        self.label_id = Label(self, text="学号：", anchor=E)
        self.label_pwd = Label(self, text="统一身份认证密码：", anchor=E)
        self.label_browser = Label(self, text="选择浏览器：", anchor=E)
        self.label_browser_path = Label(self, text="浏览器路径：", anchor=E)

        self.entry_id = tk.Entry(
            self,
            textvariable=self.var_id,
            width=60,
            borderwidth=3,
            font=("Helvetica", "10"),
        )
        self.entry_pwd = tk.Entry(
            self,
            textvariable=self.var_pwd,
            width=60,
            borderwidth=3,
            font=("Helvetica", "10"),
        )
        self.entry_pwd["show"] = "*"

        self.choose_firefox = tk.Radiobutton(
            self,
            text="Firefox",
            variable=self.var_browser,
            value="Firefox",
            command=self.set_browser,
        )
        self.choose_chrome = tk.Radiobutton(
            self,
            text="Chrome",
            variable=self.var_browser,
            value="Chrome",
            command=self.set_browser,
        )

        self.entry_browser_path = tk.Entry(
            self,
            textvariable=self.var_browser_path,
            width=60,
            borderwidth=3,
            font=("Helvetica", "10"),
        )

        self.button_path = Button(self, text="...", command=self.select_brower_path)
        self.button_login = Button(self, text="验证并保存", command=self.verification)
        self.button_checking = Button(
            self, text="正在后台验证用户，请稍等 ...", bg="LightGreen", fg="Red"
        )

        self.frame = tk.LabelFrame(self, text="更多配置", height=200, width=200)
        self.var_pa_name = tk.StringVar()
        self.label_pa_name = tk.Label(self.frame, text="同伴姓名：", anchor=tk.W)
        self.ertry_pa_name = tk.Entry(self.frame, textvariable=self.var_pa_name)

        self.var_pa_num = tk.StringVar()
        self.label_pa_num = tk.Label(self.frame, text="同伴学号：", anchor=tk.W)
        self.ertry_pa_num = tk.Entry(self.frame, textvariable=self.var_pa_num)

        self.var_pa_pwd = tk.StringVar()
        self.label_pa_pwd = tk.Label(self.frame, text="同伴场馆密码：", anchor=tk.W)
        self.ertry_pa_pwd = tk.Entry(self.frame, textvariable=self.var_pa_pwd)
        self.ertry_pa_pwd["show"] = "*"
        self.label_notice = Label(
            self.frame, text="**该部分目前无法验证是否有效**", fg="red", font=("Helvetica", 12)
        )

        self.create_page()

    def update_button_bar(self):
        top = 50
        height = 30
        hspace = 20
        middle = 270
        f_y = 16
        if self.is_checking.get():
            self.button_login.place_forget()
            self.button_checking.place(
                x=middle - 25,
                y=top
                + (height + hspace) * 4
                + height * 3
                + f_y * 4
                + hspace
                + height
                + 10,
                width=250,
                height=height + 10,
            )
        else:
            self.button_login.place(
                x=middle,
                y=top + (height + hspace) * 4 + height * 3 + f_y * 4 + hspace,
                width=200,
                height=height + 10,
            )
            self.button_checking.place_forget()

    def create_page(self):
        top = 50
        height = 30
        hspace = 20
        middle = 270

        self.label_id.place(x=190, y=top, width=middle - 190, height=height)
        self.label_pwd.place(
            x=160, y=top + (height + hspace), width=middle - 160, height=height
        )
        # self.label_browser.place(
        #     x=190, y=top + (height + hspace) * 2, width=middle - 190, height=height
        # )

        self.entry_id.place(x=middle, y=top, width=250, height=height)
        self.entry_pwd.place(
            x=middle, y=top + (height + hspace), width=250, height=height
        )
        # self.choose_firefox.place(
        #     x=middle, y=top + (height + hspace) * 2, width=80, height=height
        # )
        # self.choose_chrome.place(
        #     x=middle + 90, y=top + (height + hspace) * 2, width=80, height=height
        # )
        # if self.var_browser.get() == "Firefox":
        #     self.choose_firefox.select()
        # elif self.var_browser.get() == "Chrome":
        #     self.choose_chrome.select()
        # else:
        #     self.choose_firefox.select()

        # if backend.is_win:
        if False:
            self.label_browser_path.place(
                x=190 - 70,
                y=top + (height + hspace) * 3,
                width=middle - 190,
                height=height,
            )
            self.entry_browser_path.place(
                x=middle - 70,
                y=top + (height + hspace) * 3,
                width=250 + 70 * 2,
                height=height,
            )

            self.button_path.place(
                x=middle + 260 + 70,
                y=top + (height + hspace) * 3,
                width=40,
                height=height,
            )

        f_x = 30
        f_y = 16
        f_w1 = 90
        f_w2 = 160
        f_spx = 26
        self.frame.place(
            x=50, y=top + (height + hspace) * 4, width=630, height=height * 3 + f_y * 4
        )

        self.label_pa_name.place(x=f_x, y=f_y, width=f_w1, height=height)
        self.ertry_pa_name.place(x=f_x + f_w1, y=f_y, width=f_w2, height=height)
        self.label_pa_num.place(
            x=f_x + f_w1 + f_w2 + f_spx, y=f_y, width=f_w1, height=height
        )
        self.ertry_pa_num.place(
            x=f_x + f_w1 * 2 + f_w2 + f_spx, y=f_y, width=f_w2, height=height
        )
        self.label_pa_pwd.place(x=f_x, y=f_y * 2 + height, width=f_w1, height=height)
        self.ertry_pa_pwd.place(
            x=f_x + f_w1, y=f_y * 2 + height, width=f_w2, height=height
        )
        self.label_notice.place(
            x=f_x + f_w1 + f_w2 + f_spx,
            y=f_y * 2 + height - 5,
            width=f_w1 + f_w2,
            height=height + 10,
        )
        self.update_button_bar()
        try:
            with open(Config_Path, "rb") as _file:
                usrs_info = pickle.load(_file)
                self.var_id.set(usrs_info["student_id"])
                self.var_pwd.set(usrs_info["student_pwd"])
                self.var_browser.set(usrs_info["browser"])
                self.var_browser_path.set(usrs_info["browser_path"])
                self.var_pa_name.set(usrs_info["pa_name"])
                self.var_pa_num.set(usrs_info["pa_num"])
                self.var_pa_pwd.set(usrs_info["pa_pwd"])
        except FileNotFoundError:
            pass

    def select_brower_path(self):
        path_ = askopenfilename()
        self.var_browser_path.set(path_)
        self.entry_browser_path.configure(textvariable=self.var_browser_path)

    def set_browser(self):
        default_firefox_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
        default_chrome_path = "C:/Program Files/Google Chrome/chrome.exe"
        if self.var_browser.get() == "Firefox":
            if (
                not self.var_browser_path.get()
                or self.var_browser_path.get() == default_chrome_path
            ):
                self.var_browser_path.set(default_firefox_path)
        elif self.var_browser.get() == "Chrome":
            if (
                not self.var_browser_path.get()
                or self.var_browser_path.get() == default_firefox_path
            ):
                self.var_browser_path.set(default_chrome_path)
        self.entry_browser_path.configure(textvariable=self.var_browser_path)

    def verification(self, auto=False):
        if auto:
            self.is_checking.set(True)
            self.update_button_bar()
        try:
            student_id = self.var_id.get()
            student_pwd = self.var_pwd.get()
            browser = self.var_browser.get()
            browser_path = self.var_browser_path.get()
            pa_name = self.var_pa_name.get()
            pa_num = self.var_pa_num.get()
            pa_pwd = self.var_pa_pwd.get()
            param_ok = self.controller.param_ok

            user_info = {
                "student_id": student_id,
                "student_pwd": student_pwd,
                "browser": browser,
                "browser_path": browser_path,
                "pa_name": pa_name,
                "pa_num": pa_num,
                "pa_pwd": pa_pwd,
                "param_ok": param_ok,
            }
            # print(user_info)
            old_cookie = backend.update_cookie()
            if auto and old_cookie:
                # 旧配置 与 cookie 有效
                self.controller.param_ok = True
            if not old_cookie:
                if not student_id and not student_pwd:
                    raise Warning("请输入学号与统一身份认证密码！")
                if backend.force_update_cookie(user_info):
                    self.controller.param_ok = True
                    with open(Config_Path, "wb") as _file:
                        pickle.dump(user_info, _file)
                else:
                    raise RuntimeError("登录失败！")
        except Warning:
            pass
        except Exception as exc:
            tk.messagebox.showerror("Error", "--" * 28 + "\n身份验证失败：%s" % exc)
        else:
            # tk.messagebox.showinfo('提示', '--'*28+'\n   =_=用户信息配置有效=_=   ')
            self.controller.show_frame("RunPage")
        if auto:
            self.is_checking.set(False)
            self.update_button_bar()
