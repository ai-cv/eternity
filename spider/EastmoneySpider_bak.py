#!/usr/bin/env python
# -*-coding:utf-8 -*-

import urllib.request as ur
import re
# 导入对excel文件进行操作的库
import xlwt
# 创建表格，设置编码模式，创建新的sheet
book=xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet=book.add_sheet('dede',cell_overwrite_ok=True)

#j的作用是对url不断进行修改，翻页
for j in range(1, 1192):
    print(j)
    url = 'http://guba.eastmoney.com/list,600030,5,f_'+str(j)+'.html'
    try:
        request = ur .Request(url)
        response = ur .urlopen(request)
        content = response.read().decode('utf-8')
        pattern = re.compile('<span class.*?title=(.*?)>',re.S)
        title = re.findall(pattern, content)
        pattern = re.compile('<span class.*?<a href.*?data-popper.*?>(.*?)</a>', re.S)
        author = re.findall(pattern, content)
        timePattern = re.compile('<span class.*?data-popper.*?</span><span class.*?>(.*?)</span>.*?<span class.*?>(.*?)</span>', re.S)
        time = re.findall(timePattern, content)
        pattern = re.compile('<div class.*?articleh.*?<span.*?>(.*?)</span>.*?<span class.*?>(.*?)</span>', re.S)
        num = re.findall(pattern, content)
        for i in range(0, 80):
            titleans = title[i+1]
            sheet.write((j-1)*80+i,0,titleans)
            authorans = author[i]
            sheet.write((j - 1) * 80 + i, 1, authorans)
            fabiaotime = time[i][0]
            sheet.write((j - 1) * 80 + i, 2, fabiaotime)
            gengxintime=time[i][1]
            sheet.write((j - 1) * 80 + i, 3, gengxintime)
            yuedu = num[i][0]
            #print yuedu
            sheet.write((j - 1) * 80 + i, 4, yuedu)
            pinglun = num[i][1]
            #print pinglun
            sheet.write((j - 1) * 80 + i, 5, pinglun)
            #保存
            book.save('C:\\Users\\Lenovo\\Desktop\\600030.xls')

    except ur.URLError as e:
        if hasattr(e, "code"):
            print(e.code)

        if hasattr(e, "reason"):
            print(e.reason)