#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from tkinter import Frame, StringVar, LabelFrame, DISABLED, Text


class HowToUsePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.content = StringVar()
        self.frame_1 = LabelFrame(self, text="使用说明", height=500, width=500)
        self.text_1 = Text(self.frame_1, height=5)

        self.create_page()

    def create_page(self):
        cont = """
支持 Windows、Linux 系统，依赖见 requirement.txt。

源代码更新地址： https://github.com/rachpt/Booking-Assistant

二进制文件更新地址： https://github.com/rachpt/Booking-Assistant/releases


1. 预定前请确保电子账户余额充足；

2 .如果还未到预定开始时间，此时程序会一较慢的速度重试，接近系统开放时，程序会自动以较快的速度重试，直到成功为止；

3. 如果成功预定了一个场地，那么就不能再预定了，如有需求，退出重新打开即可；


4. 如还有其他问题，github 联系我把！......




2019.12.08
冉成"""
        self.content.set(cont)
        self.frame_1.place(x=50, y=50, width=600, height=400)
        self.text_1.place(x=20, y=20, width=560, height=330)
        self.text_1.insert("insert", self.content.get())
        self.text_1.configure(state=DISABLED, borderwidth=0, fg="Magenta")
