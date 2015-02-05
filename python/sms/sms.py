#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from mysql import mysql
import ConfigParser
import httplib
import urllib
from xml.etree import ElementTree

def get_conf(db, conf, id, type):
    send_conf = {}
    if type == 1:
        name = "provider"
    else:
        name = "plateform"
    conf.read("cfg/" + name + ".cfg")
    sections = conf.sections()
    id = str(id)
    if id in sections:
        if type == 1:
            send_conf['class_name'] = conf.get(id, 'class_name')
            send_conf['account'] = conf.get(id, 'account')
            send_conf['passwd'] = conf.get(id, 'passwd')
            send_conf['send_number'] = conf.get(id, 'send_number')
        else:
            send_conf['use_tablename'] = conf.get(id, 'use_tablename')
        return send_conf
    pro_sql = 'select * from sms_' + name
    row = db.query(pro_sql)
    if row > 0:
        pro_results = db.fetchall()
        for pro in pro_results:
            pro_id = str(pro[0])
            if pro_id not in sections:
                conf.add_section(pro_id)
            if type == 1:
                conf.set(pro_id, 'class_name', pro[7])
                conf.set(pro_id, 'account', pro[2])
                conf.set(pro_id, 'passwd', pro[3])
                conf.set(pro_id, 'send_number', pro[8])
            else:
                conf.set(pro_id, 'use_tablename', pro[3])
            if pro[0] == int(id):
                send_conf['class_name'] = pro[7]
                send_conf['account'] = pro[2]
                send_conf['passwd'] = pro[3]
                send_conf['send_number'] = pro[8]
            else:
                send_conf['use_tablename'] = pro[3]
        conf.write(open("cfg/" + name + '.cfg', 'w'))
        return send_conf
    else:
        return send_conf

def send(sms):
    print 'Send Mobile:%s' % (sms['sdst'])
    param = urllib.urlencode(sms)
    req = httplib.HTTPConnection("cf.lmobile.cn")
    request_url = '/submitdata/service.asmx/g_Submit?'+param;
    req.request('GET', request_url)
    result = req.getresponse()
    print 'GET http://cf.lmobile.cn'+request_url
    if result.status == 200:
        data = result.read()
        xml = ElementTree.fromstring(data)
        childrens = xml.getchildren()
        res = {}
        for node in childrens:
            res[node.tag.replace("{http://tempuri.org/}", "")] = node.text
        if res['State'] == '0':
            print 'Send Success'
            return True
        else:
            print 'Send Error %s:%s' % (res['State'],res['MsgState'].encode('utf-8'))
            return False
    else:
        print 'Http Error %d' % result.status
        return False

if __name__ == '__main__':
    uninx_time = time.time()
    print 'start send sms at %s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(uninx_time))
    db = mysql()
    conf = ConfigParser.ConfigParser()

    while 1:
        sql = 'select * from sms_queue where status=-1 and expect_sendtime<%d limit 20' % uninx_time
        row = db.query(sql)
        if row > 0:
            results = db.fetchall()
            for r in results:
                provider = get_conf(db, conf, r[7], 1)
                plate = get_conf(db, conf, r[2], 2)
                print 'check table %s,where logid=%d,queueid=%d' % (plate['use_tablename'],r[1],r[0])
                sms_sql = 'select receive_phone,message from %s where logid=%d' % (plate['use_tablename'],r[1])
                sms_row = db.query(sms_sql)
                if sms_row > 0:
                    sms = db.fetchrow()
                    send_flag = send({'sdst':sms[0],'smsg':sms[1],'sprdid':r[12],'sname':provider['account'],'spwd':provider['passwd'],'scorpid':''})
                    if send_flag:
                        status = 99
                    else:
                        status = 0
                    queue_sql = 'update sms_queue set status=%d where queueid=%d' % (status,r[0])
                    log_sql = 'update %s set status=%d where logid=%d' % (plate['use_tablename'],status,r[1])
                    db.execute(queue_sql)
                    db.execute(log_sql)
                else:
                    print 'no sms data'
                print
