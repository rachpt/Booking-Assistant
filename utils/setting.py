#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from os import path
from pickle import dump, load
from re import match
from tkinter import (
    StringVar,
    Label,
    E,
    Button,
    Frame,
    BooleanVar,
    Entry,
    LabelFrame,
    Label,
    messagebox,
    PhotoImage,
)

from .backend import update_cookie, force_update_cookie


class SettingPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.is_checking = BooleanVar()
        self.is_checking.set(False)
        self.var_id = StringVar()
        self.var_pwd = StringVar()
        self.ctrl_show_pwd = False
        self.ctrl_show_pa_pwd = False
        self.Config_Path = self.controller.Config_Path
        self.Cookie_Path = self.controller.Cookie_Path
        self.ROOT = self.controller.ROOT

        logo_path = path.join(self.ROOT, "config/logo.gif")
        if not path.isfile(logo_path):
            from .pic import logo_gif, get_pic

            get_pic(logo_gif, logo_path)
        global logo_img
        logo_img = PhotoImage(file=logo_path)
        self.label_logo = Label(self, image=logo_img, width=237, height=80)
        # except Exception:
        #     pass
        self.label_id = Label(self, text="学号：", anchor=E)
        self.label_pwd = Label(self, text="统一身份认证密码：", anchor=E)

        self.entry_id = Entry(
            self,
            textvariable=self.var_id,
            width=60,
            borderwidth=3,
            font=("Helvetica", "10"),
        )
        self.entry_pwd = Entry(
            self,
            textvariable=self.var_pwd,
            width=60,
            borderwidth=3,
            font=("Helvetica", "10"),
        )
        self.entry_pwd["show"] = "*"
        self.entry_pwd_eye = Button(
            self, bitmap="error", width=10, command=self.show_pwd
        )

        self.button_login = Button(self, text="验证并保存", command=self.verification)
        self.button_checking = Button(
            self, text="正在后台验证用户，请稍等 ...", bg="LightGreen", fg="Red"
        )

        self.frame = LabelFrame(self, text="更多配置", height=200, width=200)
        self.var_pa_name = StringVar()
        self.label_pa_name = Label(self.frame, text="同伴姓名：", anchor=E)
        self.ertry_pa_name = Entry(self.frame, textvariable=self.var_pa_name)

        self.var_pa_num = StringVar()
        self.label_pa_num = Label(self.frame, text="同伴学号：", anchor=E)
        self.ertry_pa_num = Entry(self.frame, textvariable=self.var_pa_num)

        self.var_pa_pwd = StringVar()
        self.label_pa_pwd = Label(self.frame, text="同伴场馆密码：", anchor=E)
        self.ertry_pa_pwd = Entry(self.frame, textvariable=self.var_pa_pwd)
        self.ertry_pa_pwd["show"] = "*"
        self.entry_pa_pwd_eye = Button(
            self.frame, bitmap="error", width=10, command=self.show_partner_pwd
        )

        self.var_sort = StringVar()
        self.place_sort_prompt = "1至8，空格分割"
        self.var_sort.set(self.place_sort_prompt)
        self.label_sort = Label(self.frame, text="预定顺序：", anchor=E)
        self.entry_sort = Entry(self.frame, textvariable=self.var_sort)

        self.create_page()

    def update_button_bar(self):
        top = 30
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
        top = 30
        height = 30
        hspace = 20
        middle = 270
        logo_h = 80
        logo_w = 237

        self.label_logo.place(x=(750 - logo_w) / 2, y=0, width=logo_w, height=logo_h)

        self.label_id.place(x=190, y=top + logo_h, width=middle - 190, height=height)
        self.label_pwd.place(
            x=160, y=top + logo_h + (height + hspace), width=middle - 160, height=height
        )

        self.entry_id.place(x=middle, y=top + logo_h, width=250, height=height)
        self.entry_pwd.place(
            x=middle, y=top + logo_h + (height + hspace), width=230, height=height
        )
        self.entry_pwd_eye.place(
            x=middle + 220,
            y=top + logo_h + (height + hspace),
            width=height,
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
            x=f_x + f_w1, y=f_y * 2 + height, width=f_w2 - height, height=height
        )
        self.entry_pa_pwd_eye.place(
            x=f_x + f_w1 + f_w2 - height,
            y=f_y * 2 + height,
            width=height,
            height=height,
        )
        self.label_sort.place(
            x=f_x + f_w1 + f_w2 + f_spx, y=f_y * 2 + height, width=f_w1, height=height
        )
        self.entry_sort.place(
            x=f_x + f_w1 * 2 + f_w2 + f_spx,
            y=f_y * 2 + height,
            width=f_w2,
            height=height,
        )
        self.entry_sort.bind("<FocusIn>", self.place_sort_click)
        self.entry_sort.bind("<FocusOut>", self.place_sort_out)
        self.entry_sort.config(fg="grey")

        self.update_button_bar()
        try:
            with open(self.Config_Path, "rb") as _file:
                usrs_info = load(_file)
                self.var_id.set(usrs_info["student_id"])
                self.var_pwd.set(usrs_info["student_pwd"])
                self.var_pa_name.set(usrs_info["pa_name"])
                self.var_pa_num.set(usrs_info["pa_num"])
                self.var_pa_pwd.set(usrs_info["pa_pwd"])
                self.var_sort.set(usrs_info["place_sort"])
        except (FileNotFoundError, KeyError):
            pass

    def place_sort_click(self, event):
        if self.var_sort.get() == self.place_sort_prompt:
            self.var_sort.set("")
            self.entry_sort.config(fg="black")

    def place_sort_out(self, enent):
        if self.var_sort.get() == "":
            self.var_sort.set(self.place_sort_prompt)
            self.entry_sort.config(fg="grey")

    def verification(self, auto=False):
        if auto:
            self.is_checking.set(True)
            self.update_button_bar()
        try:
            student_id = self.var_id.get()
            student_pwd = self.var_pwd.get()
            pa_name = self.var_pa_name.get()
            pa_num = self.var_pa_num.get()
            pa_pwd = self.var_pa_pwd.get()
            param_ok = self.controller.param_ok
            place_sort = self.var_sort.get().strip()
            if place_sort == self.place_sort_prompt:
                place_sort = ""

            user_info = {
                "student_id": student_id,
                "student_pwd": student_pwd,
                "pa_name": pa_name,
                "pa_num": pa_num,
                "pa_pwd": pa_pwd,
                "place_sort": place_sort,
                "param_ok": param_ok,
            }
            # print(user_info)
            old_cookie = update_cookie(self.Config_Path, self.Cookie_Path)
            if auto and old_cookie:
                # 旧配置 与 cookie 有效
                self.controller.param_ok = True
            if not auto:
                if pa_num:
                    match_pa_num = match(r"^\w20[\d]{7}$", pa_num)
                    if not match_pa_num:
                        raise Exception("同伴学号格式不对！")
                if not student_id:
                    raise Exception("请输入学号！")
                else:
                    # 匹配学号
                    _match = match(r"^\w20[\d]{7}$", student_id)
                    if not _match:
                        raise Exception("学号格式不对！")
                if not student_pwd:
                    raise Warning("请输入统一身份认证密码！")
                if force_update_cookie(self.Cookie_Path, user_info, verify=True):
                    self.controller.param_ok = True
                    with open(self.Config_Path, "wb") as _file:
                        dump(user_info, _file)
                else:
                    raise RuntimeError("登录失败！")
        except Warning:
            pass
        except Exception as exc:
            messagebox.showerror("Error", "--" * 28 + "\n身份验证失败：%s" % exc)
        else:
            # messagebox.showinfo('提示', '--'*28+'\n   =_=用户信息配置有效=_=   ')
            self.controller.show_frame("RunPage")
        if auto:
            self.is_checking.set(False)
            self.update_button_bar()

    def show_pwd(self):
        if self.ctrl_show_pwd:
            self.ctrl_show_pwd = False
            self.entry_pwd.configure(show="")
        else:
            self.ctrl_show_pwd = True
            self.entry_pwd.configure(show="*")

    def show_partner_pwd(self):
        if self.ctrl_show_pa_pwd:
            self.ctrl_show_pa_pwd = False
            self.ertry_pa_pwd.configure(show="")
        else:
            self.ctrl_show_pa_pwd = True
            self.ertry_pa_pwd.configure(show="*")
