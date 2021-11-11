# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/10 6:11 下午
# Description:
import threading


class MyThread(threading.Thread):
    """
    封装下多线程
    重写下run
    拿到每个线程的返回值
    """
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.res = None

    def run(self):
        self.res = self.func(*self.args)

    def result(self):
        return self.res
