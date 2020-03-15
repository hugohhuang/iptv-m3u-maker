#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools
import db
import time
import re
import json
import os
from plugins import base
# from plugins import lista
from plugins import listb
from plugins import dotpy

class Iptv (object):

    def __init__ (self) :
        self.T = tools.Tools()
        self.DB = db.DataBase()

    def run(self) :
        self.T.logger("开始抓取", True)

        self.DB.chkTable()

        Base = base.Source()
        # Base.getSource()

        Dotpy = dotpy.Source()
        # Dotpy.getSource()

        listB = listb.Source()
        listB.getSource()

        self.outPut()
        self.outJson()

        self.T.logger("抓取完成")

    def outPut (self) :
        self.T.logger("正在生成m3u8文件")

        sql = """SELECT * FROM
            (SELECT * FROM %s WHERE online = 1 ORDER BY delay DESC) AS delay
            GROUP BY LOWER(delay.title)
            HAVING delay.title != '' and delay.title != 'CCTV-' AND delay.delay < 500
            ORDER BY gp ASC, length(title) ASC, title ASC, quality ASC
            """ % (self.DB.table)
        result = self.DB.query(sql)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace('python', 'http'), 'tv.m3u'), 'w') as f:
            f.write("#EXTM3U\n")
            for item in result :
                className = item[1]
                title = item[2]
                quality = item[3]
                if quality!= '':
                    title = title + '【'+quality+'】'

                f.write("#EXTINF:-1, group-title=\"%s\", %s\n" % (className, item[2]))
                f.write("%s\n" % (item[4]))

    def outJson (self) :
        self.T.logger("正在生成Json文件")
        
        sql = """SELECT * FROM
            (SELECT * FROM %s WHERE online = 1 ORDER BY delay DESC) AS delay
            GROUP BY LOWER(delay.title)
            HAVING delay.title != '' and delay.title != 'CCTV-' AND delay.delay < 500
            ORDER BY level ASC, length(title) ASC, title ASC
            """ % (self.DB.table)
        result = self.DB.query(sql)

        fmtList = {
            'cctv': [],
            'local': [],
            'other': [],
            'radio': []
        }

        for item in result :
            tmp = {
                'title': item[2],
                'url': item[4]
            }
            if item[5] == 1 :
                fmtList['cctv'].append(tmp)
            elif item[5] == 2 :
                fmtList['local'].append(tmp)
            elif item[5] == 3 :
                fmtList['local'].append(tmp)
            elif item[5] == 7 :
                fmtList['radio'].append(tmp)
            else :
                fmtList['other'].append(tmp)

        jsonStr = json.dumps(fmtList)

        with open( os.path.join(os.path.dirname(os.path.abspath(__file__)).replace('python', 'http'), 'tv.json'), 'w') as f:
            f.write(jsonStr)

if __name__ == '__main__':
    obj = Iptv()
    obj.run()





