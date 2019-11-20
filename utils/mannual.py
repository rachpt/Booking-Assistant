#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import tkinter as tk


class HowToUsePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.content = tk.StringVar()
        self.frame_1 = tk.LabelFrame(self, text="使用说明", height=500, width=500)
        self.text_1 = tk.Text(self.frame_1, height=5)

        self.create_page()

    def create_page(self):
        cont = """
支持 Windows、Linux 系统，依赖见 requirement.txt。

源代码更新地址： https://github.com/rachpt/Booking-Assistant

二进制文件更新地址： https://github.com/rachpt/Booking-Assistant/releases

1. 同伴信息无法验证是否有效，所以务必填写正确。

2. 预定前请确保电子账户余额充足；对于这两种情况程序无法判断。

3 .如果还未到预定开始时间，错误码为 302，此时程序会一较慢的重复速度重试，接近系统开放时，程序会自动以较快的速度重试，直到成功为止。

4. 如果成功预定也一个场地，那么就不能再预定了，如有需求，退出重新打开即可。


5. 如还有其他问题，github 联系我把！......




2019.11.20
冉成"""
        self.content.set(cont)
        self.frame_1.place(x=50, y=50, width=600, height=400)
        self.text_1.place(x=20, y=20, width=560, height=330)
        self.text_1.insert("insert", self.content.get())
        self.text_1.configure(state=tk.DISABLED, borderwidth=0, fg="Magenta")
