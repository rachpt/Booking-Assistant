#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from os import path, mkdir, listdir, remove
from threading import Thread
from tkinter import messagebox, Tk, Menu, Frame, PhotoImage

from utils import status, setting, mannual


class MainPage(Tk):

    PROC_PATH = path.abspath(path.realpath(__file__))
    ROOT = path.dirname(PROC_PATH)
    if not path.exists(path.join(ROOT, "config")):
        mkdir(path.join(ROOT, "config"))
    Config_Path = path.join(ROOT, "config/user_info.pickle")
    Cookie_Path = path.join(ROOT, "config/cookie.pickle")

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.author = "rachpt"
        self.version = "v0.2.1"
        self.param_ok = False
        # self.is_checking = True
        self.Ck = Thread(target=self.check, args=())

        # 设置窗口大小
        self.X = self.winfo_screenwidth()
        self.Y = self.winfo_screenheight()
        self.geometry(
            "%dx%d+%d+%d" % (750, 540, (self.X - 750) / 2, (self.Y - 540) / 2)
        )
        self.resizable(False, False)
        self.title("自动预定运动场地 - %s" % self.version)
        self.icon_path = path.join(self.ROOT, "config/favicon.gif")
        if not path.isfile(self.icon_path):
            from utils.pic import favicon_gif, get_pic

            get_pic(favicon_gif, self.icon_path)
        self.call("wm", "iconphoto", self._w, PhotoImage(file=self.icon_path))
        self.frames = {}
        self.create_page()

    def check(self):
        while True:
            if self.param_ok:
                break
            else:
                self.auto_appointmant(True)
                break

    def show_frame(self, page_name):
        """
        Show a frame for the given page name
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def settings(self):
        self.show_frame("SettingPage")

    def auto_appointmant(self, auto=False):
        if auto:
            self.frames["SettingPage"].verification(auto)
        else:
            self.show_frame("RunPage")
        if self.param_ok and auto:
            self.show_frame("RunPage")
        elif not auto:
            pass
        else:
            # messagebox.showinfo('请有效配置', '--'*28+'\n还没有配置登录信息，或者登录信息有误\n请重新配置！\n')
            self.show_frame("SettingPage")

    def how_to_use(self):
        self.show_frame("HowToUsePage")

    def about(self):
        messagebox.showinfo(
            title="About",
            message="--" * 28
            + "\nAuthor：{author}\nVersion：{version}".format(
                author=self.author, version=self.version
            )
            + "\nLICENSE：MIT 许可证"
            + "\n\n更新日期：2019.11.29",
        )

    def call_back(self):
        if messagebox.askokcancel("Quit", "退出后无法自动预定，确定退出程序?\n"):
            self.destroy()
            for file_ in listdir():
                _, ext = path.splitext(file_)
                if ext == ".log":
                    remove(file_)

    def create_page(self):
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (status.RunPage, setting.SettingPage, mannual.HowToUsePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            """
            put all of the utils in the same location;
            the one on the top of the stacking order
            will be the one that is visible.
            """
            frame.grid(row=0, column=0, sticky="nsew")

        # 设置主菜单
        menu = Menu(self)

        # 设置子菜单
        submenu = Menu(menu, tearoff=0)
        submenu.add_command(label="设置", command=self.settings)
        menu.add_cascade(label="设置", menu=submenu)

        # 预约子菜单
        submenu = Menu(menu, tearoff=0)
        submenu.add_command(label="自动预约", command=self.auto_appointmant)
        menu.add_cascade(label="自动预约", menu=submenu)

        # 帮助子菜单
        submenu = Menu(menu, tearoff=0)
        submenu.add_command(label="使用说明", command=self.how_to_use)
        submenu.add_command(label="关于", command=self.about)
        menu.add_cascade(label="帮助", menu=submenu)

        self.config(menu=menu)

        # 起始界面
        self.show_frame("SettingPage")
        self.Ck.daemon = True
        self.Ck.start()


if __name__ == "__main__":
    app = MainPage()
    app.protocol("WM_DELETE_WINDOW", app.call_back)
    app.mainloop()
