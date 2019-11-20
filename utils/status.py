#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import threading
import datetime
import time
import random
from tkinter import StringVar, E, W, Label, Button, Radiobutton
from tkinter import messagebox
import tkinter as tk
from time import sleep
from . import backend
from . import mymessage


class RunPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.reserve_time = StringVar()
        self.reserve_date = StringVar()
        self.success = StringVar()
        self.success.set("No")
        self.counter = tk.IntVar()
        self.counter.set(0)
        self.run_flag = tk.IntVar()
        self.run_flag.set(0)
        self.T = {}
        self.message_count_down = False
        self.frame_1 = tk.LabelFrame(
            self, text="选择预定日期与开始时间（点击自动选择并查询）", height=100, width=630
        )

        self.days = {}
        self.choose_days = {}
        for i in range(7):
            self.days[i] = StringVar()
            _day = datetime.date.today() + datetime.timedelta(days=i)
            _day = _day.strftime("%Y-%m-%d")
            self.days[i].set(_day)
            self.choose_days[i] = Radiobutton(
                self.frame_1,
                text=self.days[i].get(),
                variable=self.reserve_date,
                value=self.days[i].get(),
                command=self.set_reserve_date,
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

        self.frame_2 = tk.LabelFrame(self, height=150, width=630)
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
        self.is_sucessed = Label(
            self.frame_2, bg="Red", textvariable=self.success)
        self.button_start = Button(
            self.frame_2, text="开始监控", bg="SpringGreen", command=self.start_job
        )
        self.button_stop = Button(
            self.frame_2,
            text="结束",
            state=tk.DISABLED,
            bg="LightGray",
            command=self.stop_job,
        )
        self.frame_3 = tk.LabelFrame(self, text="场地状态", height=600, width=630)

        self.courts = {}
        self.show_courts = {}
        for i in range(8):
            self.courts[i] = tk.IntVar()
            self.courts[i].set("")
            self.show_courts[i] = Button(
                self.frame_3,
                # state=tk.DISABLED,
                text="{}号场地".format(i + 1),
            )

        self.create_page()

    def create_page(self):
        f_x = 56
        height = 30
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
        if not self.reserve_time.get():
            self.choose_times[6].select()
        self.frame_2.place(
            x=f_x,
            y=space + height * 4 + space,
            width=630,
            height=height * 2 + space * 3,
        )
        self.label_date_1.place(x=space, y=space, width=120, height=height)
        self.label_date_2.place(x=space + 120, y=space,
                                width=80, height=height)
        self.label_time_1.place(x=space, y=space * 2 +
                                height, width=120, height=height)
        self.label_time_2.place(
            x=space + 120, y=space * 2 + height, width=80, height=height
        )
        self.button_start.place(x=space + 100 + 100,
                                y=space, width=180, height=height)
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
        self.frame_3.place(x=f_x, y=150 + 100 + space * 3,
                           width=630, height=height * 6)
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

    def judge_time(self):
        target_time = "08:00"  # 系统开放时间
        delta_time = 2
        current_time = time.strftime("%H:%M", time.localtime())
        d1_ = datetime.datetime.strptime(target_time, "%H:%M")
        d2_ = datetime.datetime.strptime(current_time, "%H:%M")
        if target_time >= current_time:
            time_diff = (d1_ - d2_).seconds / 60
        else:
            time_diff = (d2_ - d1_).seconds / 60
        return True if time_diff <= delta_time else False

    def job(self):
        i = 1
        infos = backend.load_config()
        while True:
            if self.run_flag.get() == 0:
                break
            else:
                self.counter.set(i)
                if self.judge_time():
                    dt = 2
                    if i != 1:
                        sleep(dt)
                else:
                    dt = 4
                    if i != 1:
                        sleep(dt)
                    self.update_status(True, infos, dt)
                self.couner_num.configure(textvariable=self.counter)
                i += 1

    def start_job(self):
        if self.run_flag.get() == 0 and self.success.get() == "No":
            self.run_flag.set(1)
            self.button_start.configure(
                bg="LightGray", state=tk.ACTIVE, text="正在运行 ...", fg="Green"
            )
            self.button_stop.configure(
                bg="Tomato", state=tk.NORMAL, text="结束", fg="Black"
            )
            ct = int(random.random() * 10000)
            self.T[ct] = threading.Thread(target=self.job, args=())
            self.T[ct].daemon = True
            self.T[ct].start()

        elif self.success.get() == "Yes":
            messagebox.showinfo("提示", "   =_=已经预定到啦=_=   \n\n   请网页上查看!   \n")
        else:
            messagebox.showinfo("提示", "   =_=已经在运行啦=_=   \n\n   不要重复点击!   \n")

    def stop_job(self):
        if self.run_flag.get() == 1:
            self.run_flag.set(0)
            self.button_stop.configure(
                bg="Gray", state=tk.ACTIVE, text="已经停止", fg="White"
            )
            self.button_start.configure(
                bg="SpringGreen", state=tk.NORMAL, text="开始监控", fg="Black"
            )
        else:
            messagebox.showinfo(
                "提示", "   =_=当前没有后台监控任务=_=   \n\n   不要重复点击!   \n   ")

    def update_status(self, doit=False, infos=None, dt=0):
        _date = self.reserve_date.get()
        _time = self.reserve_time.get()
        if _date and _time:
            res = {}
            court = backend.pian_status
            res, _ = backend.get_status((_date, _time))
            # print(res)
            for key in res.keys():
                # 2：已预约；4：不开放；1：可预约；3：使用中；5：预约中，''：不可预约
                ii = int(court[key])
                if res[key] == 1:
                    self.try_to_reverse(doit, infos, key, ii, _date, _time, dt)
                elif res[key] == 2:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n已被预约".format(ii),
                        background="Black",
                        highlightbackground="Gold",
                        foreground="Gold",
                    )
                elif res[key] == 3:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n使用中".format(ii),
                        background="Yellow",
                        highlightbackground="Gold",
                        foreground="Gold",
                    )
                elif res[key] == 4:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n不开放".format(ii),
                        background="Gray",
                        highlightbackground="Gold",
                        foreground="Red",
                    )
                elif res[key] == 5:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n预约中".format(ii),
                        background="Green",
                        highlightbackground="Gold",
                        foreground="Cyan",
                    )
                else:
                    self.show_courts[ii - 1].configure(
                        text="{}号场地\n不可预约".format(ii),
                        background="LightGray",
                        highlightbackground="Gold",
                        foreground="Gold",
                    )
            if doit and infos:
                print(res.values())
                if res and 1 not in res.values():
                    self.stop_job()  # 退出线程
                    messagebox.showinfo(
                        "提示",
                        "--" * 28
                        + "\n   =_=没有可预约的场地=_=   \n\n   请选择其他时间和日期的场地预约!   \n   ",
                    )

    def try_to_reverse(self, doit, infos, key, ii, _date, _time, dt):
        '''尝试预定单个场地'''
        if doit and infos and self.success.get() != 'Yes':
            print('appoint------->', key, ii)
            is_ok = False
            try:
                sleep(1)
                is_ok = backend.appointment(key, _date, _time, infos)
            except UserWarning as UW:
                msg = ("-" * 28 + "\n{}\n".format(UW) +
                       "-" * 28 + "\n{}秒后重试".format(dt), )
                # messagebox.showinfo("提示", msg)
                if not self.message_count_down:
                    mymessage.CountDownMessageBox(self, msg)
            except Warning as War:
                msg = ("--" * 28 + "\n返回码 与 返回信息\n{}\n".format(War) +
                       "--" * 28 + "\n{}秒后重试".format(dt), )
                messagebox.showerror("警告", msg)
                # if not self.message_count_down:
                #     mymessage.CountDownMessageBox(self)
                # print('后台运行...', i)
            if is_ok:
                self.success.set("Yes")
                self.is_sucessed.configure(
                    textvariable=self.success, bg="LightGray", fg="Magenta"
                )
                self.stop_job()  # 退出线程
                self.show_courts[ii - 1].configure(
                    text="{}号场地\n程序预约了该场地".format(ii),
                    background="Magenta",
                    highlightbackground="Green",
                    foreground="Gold",
                )
            else:
                self.show_courts[ii - 1].configure(
                    text="{}号场地\n尝试预约，已失败".format(ii),
                    background="Green",
                    highlightbackground="Gold",
                    foreground="Gold",
                )
                # raise UserWarning("预约失败 д，同伴错误或者是未到时间？")
        else:
            self.show_courts[ii - 1].configure(
                text="{}号场地\n可预约".format(ii),
                background="Green",
                highlightbackground="Gold",
                foreground="Gold",
            )

    def set_reserve_date(self):
        self.update_status()

    def set_reserve_time(self):
        self.update_status()
