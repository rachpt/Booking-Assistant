#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

import tkinter as tk


class HowToUsePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.content = tk.StringVar()
        self.frame_1 = tk.LabelFrame(self, text='使用说明', height=500, width=500)
        self.text_1 = tk.Text(self.frame_1, height=5)

        self.create_page()

    def create_page(self):
        cont='''
支持 Windows、Linux 系统，需要安装 Chrome 或者 Firefox（用于登录）。
源代码 https://github.com/rachpt/

当前还没有使用说明，有问题联系我把！......











2019.11.03
冉成
        '''
        self.content.set(cont)
        self.frame_1.place(x=50, y=50, width=600, height=400)
        self.text_1.place(x=20, y=20, width=560, height=330)
        self.text_1.insert('insert', self.content.get())
