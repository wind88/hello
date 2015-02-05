#!/usr/bin/env python
# -*- coding:utf-8 -*-

import MySQLdb

class mysql:

    def __init__(self):
        try:
            self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'smsplateform', 3306)
            self.cur = self.conn.cursor()
            self.cur.execute('set names utf8')
        except MySQLdb.Error,e:
            print "Mysql Error %d:%s" % (e.args[0], e.args[1])

    def query(self, sql):
        return self.cur.execute(sql)

    def fetchrow(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def execute(self, sql):
        row = 0
        try:
            row = self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
        return row

    def __del__(self):
        self.cur.close()
        self.conn.close()
