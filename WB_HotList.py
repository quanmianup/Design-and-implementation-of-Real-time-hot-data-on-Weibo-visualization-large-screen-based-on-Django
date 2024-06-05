import datetime
import json
import re
import time
from threading import Timer

import mysql.connector
import requests


class Spider:
    # 服务器名,账户,密码,数据库名

    def __init__(self):
        self.url = "https://weibo.com/ajax/statuses/hot_band"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"}
        self.host = '114.55.132.114'
        self.username = 'root'
        self.password = '12580Abc'
        self.database = 'wb_hotlist'

    # 发送请求，获取相应
    def parse_url(self):
        response = requests.get(self.url, headers=self.headers)
        time.sleep(2)
        return response.content.decode()

    def connect_mysql(self):
        db = mysql.connector.connect(host=self.host,
                                     user=self.username,
                                     passwd=self.password,
                                     database=self.database)  # 服务器名,账户,密码,数据库名
        return db

    # 解析数据，入库
    def parse_data(self, data, a):
        star_word = title = category = num = subject_querys = flag = icon_desc = raw_hot = emoticon = icon_desc_color = realpos = onboard_time = topic_flag = ad_info = fun_word = note = rank = url = ''
        json_data = json.loads(data)
        db = self.connect_mysql()
        cursor = db.cursor()

        for i in range(0, json_data['data']['band_list'].__len__()):
            ban_list = json_data['data']['band_list'][i]

            batch = f'第{a}批'

            try:
                star_word = ban_list['star_word']
            except Exception as e:
                print(e, end='')
            try:
                fun_word = ban_list['fun_word']
            except Exception as e:
                print(e, end='')

            try:
                title = ban_list['word']
            except Exception as e:
                print(e, end='')
            try:
                num = ban_list['num']
            except Exception as e:
                print(e, end='')
            try:
                realpos = ban_list['realpos']
            except Exception as e:
                print(e, end='')
            try:
                emoticon = ban_list['emoticon']
            except Exception as e:
                print(e, end='')
            try:
                topic_flag = ban_list['topic_flag']
            except Exception as e:
                print(e, end='')
            try:
                onboard_time = ban_list['onboard_time']
                onboard_time = datetime.datetime.fromtimestamp(onboard_time)
            except Exception as e:
                print(e, end='')
            try:
                ad_info = ban_list['ad_info']
            except Exception as e:
                print(e, end='')
            try:
                category = ban_list['category']
            except Exception as e:
                print(e, end='')
            try:
                note = ban_list['note']
            except Exception as e:
                print(e, end='')
            try:
                flag = ban_list['flag']
            except Exception as e:
                print(e, end='')
            try:
                subject_querys = ban_list['subject_querys']
            except Exception as e:
                print(e, end='')
            try:
                icon_desc: object = ban_list['icon_desc']
            except Exception as e:
                print(e, end='')
            try:
                raw_hot = ban_list['raw_hot']
            except Exception as e:
                print(e, end='')
            try:
                icon_desc_color = ban_list['icon_desc_color']
            except Exception as e:
                print(e, end='')
            try:
                rank = ban_list['rank'] + 1
            except Exception as e:
                print(e, end='')
            try:
                url = json_data['data']['band_list'][i]['mblog']['text']
                url = re.findall('href="(.*?)"', url)[0]
            except Exception as e:
                print(e, end='')
            try:
                # 插入sql语句
                sql = "insert into wb_hotlist(batch,daydate,star_word,title,category,num,subject_querys,flag,icon_desc,raw_hot,emoticon,icon_desc_color,realpos,onboard_time, \
                        topic_flag,ad_info,fun_word,note,`rank`,url) values (%s,CURRENT_TIMESTAMP(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (batch, star_word, title, category, num, subject_querys, flag, icon_desc, raw_hot, emoticon,
                       icon_desc_color, realpos, onboard_time, topic_flag, ad_info, fun_word, note, rank, url)
                # 执行插入操作
                cursor.execute(sql, val)
                db.commit()
                if i == json_data['data']['band_list'].__len__()-1:
                    print(f'\n第{a}批', end='')
                print('成功载入......')

            except Exception as e:
                db.rollback()
                print(str(e))

        # 关闭游标，断开数据库
        cursor.close()
        db.close()

    # 把数据库batch列存入列表并返回（用于判断批次号）

    def batch(self):
        db = self.connect_mysql()
        cursor = db.cursor()
        cursor.execute("select batch from WB_HotList")  # 向数据库发送SQL命令

        rows = cursor.fetchall()
        batchlist = []
        for list_batch in rows:
            batchlist.append(list_batch[0])

        return batchlist

        # 实现主要逻辑

    def run(self, a):

        # 根据数据库批次号给定a的值
        batchlist = self.batch()
        if len(batchlist) != 0:
            batch = batchlist[len(batchlist) - 1]
            a = re.findall('第(.*?)批', batch)
            a = int(a[0]) + 1

        data = self.parse_url()

        self.parse_data(data, a)
        a += 1
        # 定时调用
        t = Timer(28800, self.run, (a,))  # 43200表示43200秒，12小时调用一次；28800表示28800秒，8小时调用一次
        t.start()


if __name__ == "__main__":
    spider = Spider()
    spider.run(1)
