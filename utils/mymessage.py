#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:rachpt

from tkinter import Toplevel, Frame, Label, StringVar


class CountDownMessageBox(Toplevel):
    TEXT_FONT = ("Helevtica", 12, "bold")
    TEXT = "This process may take up to 4 seconds."
    TIMER_FONT = ("Helevtica", 13, "bold")
    TIMER_COUNT = 4  # Seconds

    def __init__(self, app, msg_text=TEXT):
        self.app = app
        self.msg_text = msg_text
        Toplevel.__init__(self, app)
        self.geometry(
            "%dx%d+%d+%d"
            % (
                400,
                200,
                (self.app.controller.X - 400) / 2,
                (self.app.controller.Y - 200) / 2,
            )
        )
        self.app.message_count_down = True
        self.build()

    def build(self):
        main_frame = Frame(self)
        main_frame.pack(expand=True, padx=20, pady=20)

        message_var = StringVar(self.app, self.msg_text)
        Label(
            main_frame,
            bitmap="hourglass",
            padx=10,
            font=self.TEXT_FONT,
            compound="left",
            textvariable=message_var,
            wraplength=200,
            fg="gray40",
        ).grid(row=0, column=0)

        self.timer_var = StringVar()
        Label(
            main_frame, textvariable=self.timer_var, font=self.TIMER_FONT, fg="blue"
        ).grid(row=1, column=0, padx=20, pady=20)

        self.count_down()

    def count_down(self, time_count=TIMER_COUNT):
        self.timer_var.set("{} 秒后自动关闭提示".format(time_count))
        if time_count == 0:
            self.destroy()
            self.app.message_count_down = False
        time_count -= 1
        self.after(1000, self.count_down, time_count)
