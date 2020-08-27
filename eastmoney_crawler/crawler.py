import re
import redis
import queue
from download import load_page
from selenium import webdriver
from selenium.webdriver.chrome import options
from post import Post
from post import detailThread
from post import postThread
from post import commentThread
# from parser import Parser
from db import MongoAPI
from user import User
#from pyvirtualdisplay import Display  


class Crawler:    #一个版块定义一个Crawler
    def __init__(self, link):
        self.link = link
        self.code = re.findall(',(.*).',self.link)[0][:-4]
        self.source = 'eastmoney'
        self.post_list = []  #存放Post对象的列表
        self.user_list = []  #存放User对象的列表
        self.post_list_q = None  #存放版块每一页的链接，如guba.eastmoney.com/list,300743_x.html
        
    def get_page_num(self):        #获取版块总页数
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('lang=zh_CN.UTF-8')
            chrome_options.add_argument('User-Agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            #display = Display(visible=0, size=(800, 800))  #linux服务器需要selenium需要用到
            #display.start()  
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(self.link)
            page_num = driver.find_element_by_xpath('//div[@id="mainbody"]/div[@id="articlelistnew"]/div[@class="pager"]/span/span/span[@class="sumpage"]').text
            driver.quit()
        except:
            page_num = 1
        return int(page_num) 
    
    #获取Post
    def get_post(self, Parser):  #多线程获取文章列表，q为队列，存放页面数
        url = self.post_list_q.get(timeout=20)  #从队列中取一个链接
        html = load_page(url)
        posts = html.xpath('//div[@id="articlelistnew"]/div[@class="articleh"]') #所有文章
        posts_ele = Parser.get_page_ele(posts)  #获取文章的关键元素
        for e in posts_ele:
            if e['post_type'] == 'settop' or e['post_type'] == 'ad':  #如果是 讨论或大赛 类型就跳过
                continue
            p = Post(e['url'], e['user_nickname'], e['title'], e['post_type'], e['post_id'],
                    e['view_count'], e['comment_count'], self.code, self.source)
            self.post_list.append(p)

    def get_post_list_queue(self):   #存放版块页面链接的队列
        q = queue.Queue()
        for i in range(self.page_num):
            q.put(self.link[:-5]+'_'+str(i+1)+'.html')
        self.post_list_q = q
                           
    #获取用户列表
    def get_user_list(self, Parser):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        for post in self.post_list:
            if ((post.user_id) != '') and (r.sismember('user_id', post.user_id)) == False:    #作者id不为空且未保留过
                self.user_list.append(User(post.user_id, post.user_nickname))
                r.sadd('user_id', post.user_id)                #将用户id存入redis
            for comment in post.comments:
                if (r.sismember('user_id', post.user_id)) == False:    #作者id不为空且未保留过
                    self.user_list.append(User(comment['user_id'], comment['user_nickname']))
                    r.sadd('user_id', comment['user_id'])                #将用户id存入redis
    
    def get_page_post(self, url, parser):
        html = load_page(url)
        posts = html.xpath('//div[@id="articlelistnew"]//div[@class="articleh"]') #所有文章    
        posts_ele = parser.get_page_ele(posts)   #获取文章的关键元素
        post_list = []
        for e in posts_ele:
            if e['post_type'] == 'settop' or e['post_type'] == 'ad':  #如果是 讨论或大赛 类型就跳过
                continue
            p = Post(e['url'], e['user_nickname'], e['title'], e['post_type'], e['post_id'],
                    e['view_count'], e['comment_count'], self.code, self.source)
            post_list.append(p)
        return post_list

    #抓取函数   
    def crawl(self):
        self.page_num = self.get_page_num()  #获取版块页数
        #获取存放版块页面链接的队列，如http://guba.eastmoney.com/list,300729_xxxxxx.html
        self.get_post_list_queue()
        print('本版块页数为:' + str(self.page_num))
        parser = Parser()
        # 获取版块页面的帖子列表
        thread_num = 6  #线程数设置为6
        thread_list = []
        for i in range(thread_num):  #获取如http://guba.eastmoney.com/list,300729_1.html页面的帖子的信息
            thread = postThread('Thread'+str(i+1), self.get_post, parser)
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
        #print(len(self.post_list))  #打印该版块帖子数目
        # 获取帖子对象队列及帖子详情
        post_queue = queue.Queue()
        for post in self.post_list:
            post_queue.put(post)
        thread_list = [] 
        db = MongoAPI("localhost", 27017, "community", "post")
        for i in range(thread_num):     #从队列中获取post对象，并获取post的详细信息包括评论
            thread = detailThread('Thread'+str(i+1), parser, post_queue, db) 
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
       
        #  获取用户队列及用户详情
        self.get_user_list(parser)  #获取用户列表
        db = MongoAPI("localhost", 27017, "community", "user")
        user_queue = queue.Queue()
        for user in self.user_list:  #将User对象插入队列中
            user_queue.put(user)
        thread_list = []
        for i in range(thread_num):   #获取用户详情
            thread = detailThread('Thread'+str(i+1), parser, user_queue, db)
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
            
    #爬取新数据
    def crawl_new_data(self):
        parser = Parser()
        """获取新文章数据"""
        isNew = 1
        just_like = 0  #纪录纯点赞导致的帖子更新的数目
        page_num = 1  #设置初始页数
        db = MongoAPI("localhost", 27017, "community", "post")
        while isNew == 1:
            url = 'http://guba.eastmoney.com/list,' + self.code + '_' + str(page_num) +  '.html'  #从第一页开始往后
            try:
                post_list = self.get_page_post(url, parser)  #获取当前页面的所有帖子
            except:
                break
            for post in post_list:  #对每条主帖进行判断
                db_post = db.get_one({'url': post.url})  #从数据库中查询主帖
                if db_post != None:  #有记录说明该主帖已经被保存过 
                    update_time = db_post['last_update_at']  #获取该主帖在数据库中的最后更新时间
                    last_comment_time = post.get_last_comment_time(parser)  #获取主帖页面的最后评论时间
                    if update_time >= last_comment_time:  #若为普通主帖，则判断主帖和评论有无变更，点赞也可能把帖子置顶上去
                        #print('上次最后更新帖子%s，时间为%s' % (post.url, update_time))
                        just_like += 1
                        if just_like == 5:
                            isNew = 0
                            self.post_list = self.post_list[:-5]  #把五条无效旧帖删除
                            break
                    else:
                        just_like = 0
                self.post_list.append(post) 
                #print('这是新帖子，插入：%s' % post.url)   #在运行时，提示新帖子记录
            page_num += 1  #翻页
        """获取新文章的详细数据"""
        # 获取帖子对象队列及帖子详情
        post_queue = queue.Queue()
        for post in self.post_list:
            post_queue.put(post)
        thread_num = 5
        thread_list = []
        for i in range(thread_num):     #从队列中获取post对象，并获取post的详细信息包括评论
            thread = detailThread('Thread'+str(i+1), parser, post_queue, db) 
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
        #  获取用户队列及用户详情
        self.get_user_list(parser)  #获取用户列表
        db = MongoAPI("localhost", 27017, "community", "user")
        for u in self.user_list:
            u.set_detail(parser)
            u.save(db)
        print("爬取代码:%s 页数:%s 文章数:%s 用户数:%s" % (self.code, page_num-1, len(self.post_list), len(self.user_list)))


import re
import datetime
import lxml

"""用于解析页面，参数html为etree元素"""


class Parser(object):
    def get_last_comment_time(self, html):  # 获取文章的最后更新时间
        try:
            last_comment_time = html.xpath(
                '//div[@id="zwlist"]/div[@class="zwli clearfix"][1]/div[@class="zwlitx"]/div/div[@class="zwlitime"]')[
                0].text.split('发表于')[1].strip()
            last_comment_time = datetime.datetime.strptime(last_comment_time, "%Y-%m-%d %H:%M:%S")  # 把字符串转为datetime类型
        except:
            last_comment_time = self.get_post_time(html)  # 若没有评论，就返回发帖时间
        return last_comment_time

    def get_comment_list(self, html):  # 获取文章的评论列表
        comments = html.xpath('//div[@id="mainbody"]/div[@id="zwlist"]//div[@class="zwli clearfix"]')
        return comments

    def get_comment_detail(self, comment):  # 获取文章的评论的细节
        comment_id = comment.attrib['data-huifuid']
        user_id = comment.attrib['data-huifuuid']
        if len(comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlianame"]/span/a')) != 0:
            user_nickname = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlianame"]/span/a')[0].text
        else:  # 如果回帖者是如来自Android客户端的“上海网友”，则评论会没有用户id信息
            user_nickname = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlianame"]/span/span')[0].text
            user_id = 'Null'
            # print(user_nickname, user_id)
        created_at = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlitime"]')[0].text.split('发表于')[1].strip()
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        content = self.get_comment_content(comment)
        reply_to = self.get_comment_reply_to(comment)
        return dict({'comment_id': comment_id,
                     'user_id': user_id,
                     'user_nickname': user_nickname,
                     'created_at': created_at,
                     'content': content,
                     'reply_to': reply_to
                     })

    def get_comment_content(self, comment):  # 获取评论内容
        comment_content = ''
        comment_imgs = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlitext stockcodec"]/img')
        if len(comment_imgs) != 0:
            for img in comment_imgs:
                try:
                    comment_content += '[' + img.attrib['title'] + ']'
                except:
                    continue
        content = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlitext stockcodec"]//text()')
        if len(content) != 0:
            for i in range(len(content)):
                comment_content += content[i].strip()
        return comment_content

    def get_comment_reply_to(self, comment):  # 获取评论 回复的评论 内容
        reply_to = comment.xpath('div[@class="zwlitx"]/div/div[@class="zwlitalkbox clearfix"]')
        if len(reply_to) == 0:
            return ''
        if len(reply_to[0].xpath('div/a')) != 0:
            reply_to_user_nickname = reply_to[0].xpath('div/a')[0].text.strip()
        else:  # 如果回复的对象是如“http://guba.eastmoney.com/news,600000,176775237_2.html#storeply”
            reply_to_user_nickname = reply_to[0].xpath('div/span')[0].text.strip()
        reply_to_comment = ''
        reply_to_comment_imgs = reply_to[0].xpath('div/span/img')
        if len(reply_to_comment_imgs) != 0:
            for img in reply_to_comment_imgs:
                reply_to_comment += '[' + img.attrib['title'] + ']'
        # if (reply_to[0].xpath('div/span'))!= None and len((reply_to[0].xpath('div//span'))) != 0:
        try:
            if len(reply_to[0].xpath('div//span')) == 1:
                reply_to_comment += reply_to[0].xpath('div/span[1]//text()')[0].strip()
            elif len(reply_to[0].xpath('div//span')) == 2:
                reply_to_comment += reply_to[0].xpath('div/span[2]//text()')[0].strip()
        except:
            pass
        reply_to_comment_id = reply_to[0].xpath('div')[0].attrib['data-huifuid']
        reply_to_dict = {
            'reply_to_user_nickname': reply_to_user_nickname,
            'reply_to_comment': reply_to_comment,
            'reply_to_comment_id': reply_to_comment_id
        }
        return reply_to_dict

    def get_post_title(self, html):  # 获取文章标题
        try:
            title = html.xpath('//div[@id="zwcontent"]//div[@id="zwconttbt"]/text()')[0].strip()
        except:
            title = ''
        return title

    def get_post_question(self, html):  # 获取文章问题
        q = \
        html.xpath('//div[@id="zwcontent"]/div[@class="zwcontentmain"]/div[@class="qa"]/div[@class="question"]/div')[
            0].text
        return q

    def get_post_answer(self, html):  # 获取文章答复
        a = html.xpath('//div[@id="zwcontent"]/div[@class="zwcontentmain"]/div[@class="qa"]/div[@class="answer_wrap"]\
        /div/div[@class="content_wrap"]')[0]
        a_from = a.xpath('div[@class="sign"]/span')[0].text[1:-1].split('来自')[1].strip()
        a_time = (a.xpath('div[@class="sign"]/text()'))[1].split('答复时间')[1].strip()
        a_content = (a.xpath('div[@class="content"]/text()'))[1].strip()
        return dict({'from': a_from, 'time': a_time, 'content': a_content})

    def get_news_content(self, html):  # 获取新闻内容
        news_content = ''
        content = html.xpath('//div[@id="zwconbody"]/div[@class="stockcodec"]/div[@id="zw_body"]//p//text()')
        for c in content:
            news_content += (c.strip() + '\n')
        return news_content

    def get_post_content(self, html):  # 获取文章内容
        post_content = ''
        imgs = html.xpath('//div[@id="zwconbody"]/div[@class="stockcodec"]/img')
        if len(imgs) != 0:
            for img in imgs:
                try:
                    post_content += ('[' + img.attrib['title'] + ']')
                except:
                    continue
        content = html.xpath('//div[@id="zwconbody"]/div[@class="stockcodec"]/text()')
        for s in content:
            post_content += (s.strip())
        post_content = post_content.strip()
        return post_content

    def get_post_time(self, html):  # 获取文章发表时间
        try:
            post_time = html.xpath('//div[@id="zwcontent"]/div[@id="zwcontt"]/div[@id="zwconttb"]/div[2]')[0].text
            post_time = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', post_time)[0]
            post_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        except:
            post_time = datetime.datetime.strptime('1970-01-01 12:00:00', "%Y-%m-%d %H:%M:%S")
        return post_time

    def get_author_id(self, html):  # 获取文章作者id
        try:  # 资讯类号不存在userid
            author_id = html.xpath('//div[@id="zwconttphoto"]/a')[0].attrib['data-popper']
        except:
            author_id = ''
        return author_id

    def get_page_ele(self, posts):  # 获取版块某一页的文章的关键元素
        ele_list = []
        for p in posts:
            try:
                url = p.xpath('span[@class="l3"]/a')[0].attrib['href']
                if url[0] == '/':  # 有的链接首个字符带有/，有的没有，要做判断
                    url = url[1:]
            except:
                continue
            post_type = p.xpath('span[@class="l3"]/em/@class')  # 以下为判断文章的类型
            if len(post_type) != 0:  # 如果不是普通帖子，且类型是《大赛》或者《话题讨论》，则跳过
                post_type = post_type[0]
                if post_type == 'ad' or post_type == 'settop':
                    continue
            else:
                post_type = 'normal'
            try:
                title = p.xpath('span[@class="l3"]/a')[0].text
                last_update_time = p.xpath('span[@class="l3"]/em/@class')
                view_count = p.xpath('span[@class="l1"]')[0].text  # 阅读数量
                comment_count = p.xpath('span[@class="l2"]')[0].text  # 评论数量
                if len(p.xpath(
                        'span[@class="l4"]/a')) != 0:  # 用户昵称有可能为如“上海手机网友”的情况。如http://guba.eastmoney.com/news,600000,177049240.html
                    user_nickname = p.xpath('span[@class="l4"]/a')[0].text
                else:
                    user_nickname = p.xpath('span[@class="l4"]/span')[0].text
            except:
                print('出问题了%s:%s' % (url, title))
                continue
            p_ele = dict({
                'url': 'http://guba.eastmoney.com/' + url,
                'user_nickname': user_nickname,
                'title': title,
                'post_type': post_type,
                'last_update_time': last_update_time,
                'post_id': re.findall(r'(\d*).html', url)[0],
                'view_count': view_count,
                'comment_count': comment_count
            })
            ele_list.append(p_ele)
        return ele_list

    """以下函数为获取用户信息"""

    def get_user_reg_date(self, html):
        return html.xpath('//div[@id="influence"]/span/text()')[1][1:-1]  # 注册时间

    def get_user_avator(self, html):
        return html.xpath('//div[@class="tainfo"]/div[@class="photo"]/img/@src')[0]  # 头像链接

    def get_user_fans_count(self, html):
        return html.xpath('//div[@class="tainfo"]/div[@class="photo"]/div[@class="tanums"]//td//text()')[4]  # 粉丝数

    def get_user_following_count(self, html):
        return html.xpath('//div[@class="tainfo"]/div[@class="photo"]/div[@class="tanums"]//td//text()')[2]  # 关注数

    def get_user_influence(self, html):
        return html.xpath('//div[@id="influence"]/span/@data-influence')[0]  # 影响力

    def get_user_introduce(self, html):
        return html.xpath('//div[@class="tainfos"]/div[@class="taintro"]/text()')[0].strip()  # 介绍

    def get_user_visit_count(self, html):
        return html.xpath('//div[@class="tainfos"]/div[@class="sumfw"]/span/text()')[0][:-1]  # 总访问

    def get_user_post_count(self, html):
        return re.findall('（.*）', html.xpath('//div[@id="mainbody"]/div[@class="grtab5"]//a/text()')[0])[0][1:-1]  # 发帖数

    def get_user_comment_count(self, html):
        return re.findall('（.*）', html.xpath('//div[@id="mainbody"]/div[@class="grtab5"]//a/text()')[1])[0][1:-1]  # 评论数

    def get_user_optional_count(self, html):
        return html.xpath('//div[@class="tainfo"]/div[@class="photo"]/div[@class="tanums"]//td//text()')[0]  # 自选股数

    def get_user_capacity_circle(self, html):  ##能力圈
        code_list = []
        capacity_circle = html.xpath('//div[@id="influence"]//a/@href')
        if len(capacity_circle) != 0:
            for i in capacity_circle:  # 能力圈股票代码
                code_list.append(re.findall(',(.*).html', i)[0])
        return code_list