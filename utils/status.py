#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from random import random
from threading import Thread
from functools import partial
from datetime import date, timedelta
from time import sleep, strftime, localtime
from tkinter import (
    StringVar,
    E,
    W,
    Label,
    Button,
    Radiobutton,
    Frame,
    IntVar,
    LabelFrame,
    DISABLED,
    ACTIVE,
    NORMAL,
    messagebox,
)
from . import backend
from . import mymessage


class RunPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.reserve_time = StringVar()
        self.reserve_date = StringVar()
        self.success = StringVar()
        self.success.set("No")
        self.counter = IntVar()
        self.counter.set(0)
        self.run_flag = IntVar()
        self.run_flag.set(0)
        self.T = {}
        self.message_count_down = False
        self.show_notice = True
        self.successed_info = []
        self.Config_Path = self.controller.Config_Path
        self.Cookie_Path = self.controller.Cookie_Path
        self.frame_1 = LabelFrame(
            self, text="选择预定日期与开始时间（点击自动选择并查询）", height=100, width=630
        )
        self.day = 0
        self.days = {}
        self.choose_days = {}
        for i in range(7):
            _today = date.today()
            self.days[i] = StringVar()
            _day = _today + timedelta(days=i)
            _day = _day.strftime("%Y-%m-%d")
            self.days[i].set(_day)
            self.choose_days[i] = Radiobutton(
                self.frame_1,
                text=self.days[i].get(),
                variable=self.reserve_date,
                value=self.days[i].get(),
                command=partial(self.set_reserve_date, i),
            )

        self.times = {}
        self.choose_times = {}
        for i in range(7):
            self.times[i] = StringVar()
            _time = "{0:02d}:00:00".format(8 + 2 * i)
            self.times[i].set(_time)
            self.choose_times[i] = Radiobutton(
                self.frame_1,
                text=self.times[i].get(),
                variable=self.reserve_time,
                value=self.times[i].get(),
                command=self.set_reserve_time,
            )
        # -------------------
        self.frame_2 = LabelFrame(self, height=150, width=630)
        self.label_date_1 = Label(self.frame_2, text="预定日期：", anchor=E)
        self.label_date_2 = Label(
            self.frame_2, textvariable=self.reserve_date, anchor=W
        )
        self.label_time_1 = Label(self.frame_2, text="预定时间段(2小时)：", anchor=E)
        self.label_time_2 = Label(
            self.frame_2, textvariable=self.reserve_time, anchor=W
        )
        self.label_couner = Label(self.frame_2, text="刷新次数：", anchor=E)
        self.couner_num = Label(self.frame_2, textvariable=self.counter)
        self.label_sucessed = Label(self.frame_2, text="是否预定成功？：", anchor=E)
        self.is_sucessed = Label(self.frame_2, bg="Red", textvariable=self.success)
        self.button_start = Button(
            self.frame_2, text="开始监控", bg="SpringGreen", command=self.start_job
        )
        self.button_stop = Button(
            self.frame_2,
            text="结束",
            state=DISABLED,
            bg="LightGray",
            command=self.stop_job,
        )
        self.label_notice = Label(self.frame_2, text="显示警告与提示？", anchor=E)
        self.button_notice = Button(
            self.frame_2, text="是", bg="Pink", command=self.turn_on_notice
        )
        self.label_sucessed_place = Label(self.frame_2, text="预定成功的场地：", anchor=E)
        self.label_successed_place_info = Label(self.frame_2)
        # -------------------
        self.frame_3 = LabelFrame(self, text="场地状态（点击刷新）", height=600, width=630)

        self.courts = {}
        self.show_courts = {}
        for i in range(8):
            self.courts[i] = IntVar()
            self.courts[i].set("")
            self.show_courts[i] = Button(
                self.frame_3,
                font=("Helvetica 10"),
                text="{}号场地".format(i + 1),
                command=self.get_status,
            )

        self.create_page()

    def create_page(self):
        f_x = 56
        height = 28
        space = 20
        f1_width = 98
        f3_width = 120
        self.frame_1.place(
            x=f_x - 30, y=space, width=700, height=height * 2 + space * 3
        )
        for i in range(7):
            self.choose_days[i].place(
                x=5 + f1_width * i, y=10, width=f1_width, height=height
            )
            self.choose_times[i].place(
                x=5 + f1_width * i, y=20 + height, width=f1_width, height=height
            )
        if not self.reserve_date.get():
            self.choose_days[2].select()
            self.day = 2
        if not self.reserve_time.get():
            self.choose_times[6].select()
        self.frame_2.place(
            x=f_x,
            y=space + height * 4 + space,
            width=630,
            height=height * 3 + space * 4,
        )
        self.label_date_1.place(x=space, y=space, width=120, height=height)
        self.label_date_2.place(x=space + 120, y=space, width=80, height=height)
        self.label_time_1.place(x=space, y=space * 2 + height, width=120, height=height)
        self.label_time_2.place(
            x=space + 120, y=space * 2 + height, width=80, height=height
        )
        self.button_start.place(x=space + 100 + 100, y=space, width=180, height=height)
        self.button_stop.place(
            x=space + 120 + 80, y=space * 2 + height, width=180, height=height
        )
        self.label_couner.place(
            x=space * 2 + 100 + 100 + 180, y=space, width=100, height=height
        )
        self.couner_num.place(
            x=space * 2 + 100 + 100 + 180 + 100, y=space, width=80, height=height
        )
        self.label_sucessed.place(
            x=space * 2 + 100 + 100 + 180,
            y=space * 2 + height,
            width=100,
            height=height,
        )
        self.is_sucessed.place(
            x=space * 2 + 100 + 100 + 180 + 100,
            y=space * 2 + height,
            width=80,
            height=height,
        )
        self.label_notice.place(
            x=space, y=space * 3 + height * 2, width=120, height=height
        )
        self.button_notice.place(
            x=space + 120, y=space * 3 + height * 2, width=50, height=height
        )
        # -------------------
        self.frame_3.place(x=f_x, y=150 + 100 + space * 4, width=630, height=height * 6)
        for i in range(8):
            self.show_courts[i].place(
                x=10 + (f3_width + 40) * (i % 4),
                y=10 + (height * 2 + space) * (i // 4),
                width=f3_width,
                height=height * 2,
            )
            self.show_courts[i].configure(
                background="LightGray", highlightbackground="Gold", foreground="Black"
            )

    def job(self):
        _st = "07:59:30"  # 开始时间
        _end = "22:00:00"  # 结束时间
        i = 1  # 刷新次数计数器
        infos = backend.load_config(self.Config_Path)
        while True:
            if self.run_flag.get() == 0:
                break
            elif _st <= strftime("%H:%M:%S", localtime()) < _end:
                if backend.judge_time():
                    dt = 2
                else:
                    dt = 20
                self.update_status(True, infos, dt)
            else:
                dt = 40
                self.update_status(False, infos, dt)
            sleep(dt)
            self.counter.set(i)
            self.couner_num.configure(textvariable=self.counter)
            i += 1

    def start_job(self):
        if self.run_flag.get() == 0 and self.success.get() == "No":
            self.run_flag.set(1)
            for i in range(7):
                self.choose_days[i].config(state=DISABLED)
                self.choose_times[i].config(state=DISABLED)
            self.button_start.configure(
                bg="LightGray", state=ACTIVE, text="正在运行 ...", fg="Green"
            )
            self.button_stop.configure(bg="Tomato", state=NORMAL, text="结束", fg="Black")
            # sort_place_order(self.controller)
            ct = int(random() * 10000)
            self.T[ct] = Thread(target=self.job, args=())
            self.T[ct].daemon = True
            self.T[ct].start()

        elif self.success.get() == "Yes":
            messagebox.showinfo("提示", "   =_=已经预定到啦=_=   \n\n   请网页上查看!   \n")
        else:
            messagebox.showinfo("提示", "   =_=已经在运行啦=_=   \n\n   不要重复点击!   \n")

    def stop_job(self):
        if self.run_flag.get() == 1:
            self.run_flag.set(0)
            for i in range(7):
                self.choose_days[i].config(state=NORMAL)
                self.choose_times[i].config(state=NORMAL)
            self.button_stop.configure(bg="Gray", state=ACTIVE, text="已经停止", fg="White")
            self.button_start.configure(
                bg="SpringGreen", state=NORMAL, text="开始监控", fg="Black"
            )
        else:
            messagebox.showinfo("提示", "   =_=当前没有后台监控任务=_=   \n\n   不要重复点击!   \n   ")

    def update_status(self, doit=False, infos=None, dt=0, mark=True):
        """doit 预定 flag，infos 同伴信息，dt 睡眠时间，秒；mark 用于防止递归。"""
        _date = self.reserve_date.get()
        _time = self.reserve_time.get()
        if _date and _time:
            res = {}
            court = backend.pian_status
            res, _ = backend.get_status(
                self.Config_Path, self.Cookie_Path, (_date, _time)
            )
            if infos and infos["place_sort"]:
                sorted_keys = sort_place_order(court, infos["place_sort"])
            else:
                sorted_keys = res.keys()
            for key in sorted_keys:
                # 2：已预约；4：不开放；1：可预约；3：使用中；5：预约中，''：不可预约
                ii = int(court[key])
                res_status = res[key][0]
                res_note = res[key][1]
                if res_status == 1:
                    self.try_to_reverse(doit, infos, key, ii, _date, _time, dt)
                elif res_status == 2:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n已被预约".format(ii),
                        background="Black",
                        highlightbackground="Gold",
                        foreground="Gold",
                        font=("Helvetica 10"),
                    )
                elif res_status == 3:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n使用中".format(ii),
                        background="Yellow",
                        highlightbackground="Gold",
                        foreground="Gold",
                        font=("Helvetica 10"),
                    )
                elif res_status == 4:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n不开放".format(ii),
                        background="Gray",
                        highlightbackground="Gold",
                        foreground="White",
                        font=("Helvetica 10"),
                    )
                    if res_note:
                        if len(res_note) >= 10:
                            self.show_courts[ii - 1].configure(
                                text="{}号场地(不开放)\n{}".format(ii, res_note),
                                font=("Helvetica 8"),
                            )
                        else:
                            self.show_courts[ii - 1].configure(
                                text="{}号场地(不开放)\n{}".format(ii, res_note)
                            )

                elif res_status == 5:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n预约中".format(ii),
                        background="Green",
                        highlightbackground="Gold",
                        foreground="Cyan",
                        font=("Helvetica 10"),
                    )
                else:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n不可预约".format(ii),
                        background="LightGray",
                        highlightbackground="Gold",
                        foreground="Gold",
                        font=("Helvetica 10"),
                    )
            if mark:
                self.mark_successed_place(court, _date, _time)
            if doit and infos:
                # 没有可预定或正在预定的场地，则退出预定
                if res and (1, "") not in res.values() and (5, "") not in res.values():
                    self.stop_job()  # 退出线程
                    messagebox.showinfo(
                        "提示",
                        "-" * 20
                        + "\n   =_=没有可预约的场地=_=   \n\n   请选择其他时间和日期的场地预约!   \n   ",
                    )

    def try_to_reverse(self, doit, infos, key, ii, _date, _time, dt):
        """尝试预定单个场地"""
        _text = "{}号场地\n可预约".format(ii)
        if doit and infos and self.success.get() != "Yes" and self.run_flag.get() == 1:
            is_ok = False
            try:
                is_ok = backend.appointment(
                    self.Config_Path,
                    self.Cookie_Path,
                    key,
                    _date,
                    _time,
                    infos,
                    self.day,
                )
            except UserWarning as UW:
                msg = (
                    "-" * 20 + "\n{}\n".format(UW) + "-" * 20 + "\n{}秒后重试".format(dt),
                )
                if not self.message_count_down and self.show_notice:
                    mymessage.CountDownMessageBox(self, msg)
            except Warning as War:
                _text = "{}号场地\n尝试预约，已失败".format(ii)
                self.stop_job()  # 退出线程
                msg = "-" * 20 + "\n错误信息：\n{}\n".format(War) + "-" * 20
                if self.show_notice:
                    messagebox.showerror("发生错误", msg)

            if is_ok:
                self.success.set("Yes")
                self.successed_info = [key, _date, _time]
                self.stop_job()  # 退出线程

        self.color_target_court(ii, _text)

    def color_target_court(self, ii, _text):
        """上色 可预约场地"""
        self.show_courts[ii - 1].configure(
            text=_text,
            background="Green",
            highlightbackground="Gold",
            foreground="Gold",
            font=("Helvetica 10"),
        )

    def mark_successed_place(self, court, _date, _time):
        """标记已经预定了的场地"""
        if (
            self.successed_info
            and _date == self.successed_info[1]
            and _time == self.successed_info[2]
        ):
            # 更新场地状态，如果显示已被预定，就表示成功预定该场地。
            self.update_status(mark=False)
            res, _ = backend.get_status(
                self.Config_Path, self.Cookie_Path, (_date, _time)
            )
            key = self.successed_info[0]
            if res[key][0] == 2:
                ii = int(court[key])
                # 高亮 成功 YES
                self.is_sucessed.configure(
                    textvariable=self.success, bg="LightGray", fg="Magenta"
                )
                # 显示预定信息
                success_text = str(ii) + "号 " + _date + " " + _time
                self.label_successed_place_info.configure(
                    fg="Magenta", text=success_text
                )
                self.label_sucessed_place.place(
                    x=20 + 200, y=20 * 3 + 28 * 2, width=180, height=28
                )
                self.label_successed_place_info.place(
                    x=20 + 380, y=20 * 3 + 28 * 2, width=200, height=28
                )
                self.show_courts[ii - 1].configure(
                    text="{}号场地\n程序预约了该场地".format(ii),
                    background="Magenta",
                    highlightbackground="Green",
                    foreground="White",
                    font=("Helvetica 10"),
                )
            else:
                self.successed_info = []
                self.success.set("No")

    def set_reserve_date(self, day):
        self.update_status()
        self.day = day

    def set_reserve_time(self):
        self.update_status()

    def get_status(self):
        if self.run_flag.get() != 1:
            self.update_status()

    def turn_on_notice(self):
        if self.show_notice:
            self.show_notice = False
            self.button_notice.configure(text="否", bg="LightGray")
        else:
            self.show_notice = True
            self.button_notice.configure(text="是", bg="Pink")


def sort_place_order(place_dict, order_str):
    if order_str:
        reversed_place_dict = {v: k for k, v in place_dict.items()}
        ret_list = []
        order_str_list = order_str.split()
        for i in order_str_list:
            if "0" <= i <= "8":
                ret_list.append(reversed_place_dict[str(i)])
        # 补全
        for i in range(1, 9):
            i = str(i)
            if i not in order_str_list:
                ret_list.append(reversed_place_dict[i])
        return ret_list
    else:
        return place_dict.keys()
