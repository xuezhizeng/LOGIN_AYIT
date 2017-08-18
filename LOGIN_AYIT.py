# _*_encoding:utf-8 _*_
"""
@Software: PyCharm
@Python: 3.X   X==5
@抓包：fiddler
@Time: 2017.8.15
@Contact:520@skyne.cn
@Author: SKYNE
@友情提醒：各教务网大同小异，最重要的是模拟登录思想，
只要我们能完全模仿出正常浏览器对教务网服务器的请求方式，
所携带的请求头，cookies，那么服务器就会返回给我们想要的信息。
"""
"""
###下面是测试过的各基本的URL地址以及请求方法###

home_page = http://jwgl.ayit.edu.cn/        method=GET    # 教务网主页
login_url = http://jwgl.ayit.edu.cn/_data/login.aspx，   method=POST    # 教务网post登陆地址
Vcode_url = http://jwgl.ayit.edu.cn/sys/ValidateCode.aspx，   method=GET   # 获取验证码验证码地址
Basic_info_url = http://jwgl.ayit.edu.cn/xsxj/Stu_MyInfo_RPT.aspx,  method=GET  # 基本信息获取地址
name_code_url = http://jwgl.ayit.edu.cn/xscj/private/list_xhxm.aspx, method=GET  # 姓名，学号获取地址
your_image = http://jwgl.ayit.edu.cn/_photo/student/20150000331008nBNWLMbf.JPG,  method=GET  # 顾名思义
score_url = http://jwgl.ayit.edu.cn/xscj/Stu_cjfb_rpt.aspx,      method=POST  # 成绩信息获取地址，需要post提交数据
###http://jwgl.ayit.edu.cn/xscj/Stu_MyScore_rpt.aspx###该地址也是成绩地址，但返回的是图片，不是文本。难以提取其中信息。
"""
"""下述是本脚本所需要的库"""
import requests
import hashlib
import re
import time
from lxml import html
from urllib.parse import urljoin
"""下面的类主要是构建Header请求头和POST数据以及加密密码(PWD)与验证码(Vcode)，叫什么名字呢，就叫HPPV吧"""
class hppv:
    def __init__(self,Basic_info):
        self.school_code = Basic_info["school_code"]
        self.user_id = Basic_info["user_id"]
        self.pwd = Basic_info["pwd"]
        self.home_url = Basic_info["home_url"]
        self.login_url = urljoin(self.home_url,'_data/login.aspx')
        self.vcode_url = urljoin(self.home_url,'/sys/ValidateCode.aspx')
        self.ses = requests.session()
    def Header(self):
        Basic_Header = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        }
        Basic_Header["Host"] = self.home_url
        Basic_Header["Origin"] = self.home_url
        Basic_Header["Referer"] = self.login_url
        return Basic_Header
    def Post_data(self):
        post_data = {
            "Sel_Type": "STU",
            "typeName": u"学生".encode('gb2312'),
            "txt_asmcdefsddsd": "",            # 学号，暂时置空
            "dsdsdsdsdxcxdfgfg": "",           # 密码，暂时置空
            "fgfggfdgtyuuyyuuckjg": "",         # 验证码 暂时置空
            "txt_pewerwedsdfsdff": "",          # 未发现实际意义
            "txt_sdertfgsadscxcadsads": "",     # 未发现实际意义
            "pcInfo": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36undefined5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 SN:NULL",
        }
        self.ses.get(url=self.home_url,headers=self.Header())                 ###直接访问login_url会发生错误，故先访问home_page
        response = self.ses.get(url=self.login_url,headers=self.Header())      ###此处注意，url位于login_url
        if response.status_code == 200:
            selector = html.fromstring(response.text)
            post_data["__VIEWSTATE"] = selector.xpath("//*[@id='Logon']/input[1]/@value")[0]
            post_data["__VIEWSTATEGENERATOR"] = selector.xpath("//*[@id='Logon']/input[2]/@value")[0]
            post_data["txt_asmcdefsddsd"] = self.user_id
            post_data["dsdsdsdsdxcxdfgfg"] = self.Pwd_encrypt()
            post_data["fgfggfdgtyuuyyuuckjg"] = self.Vcode_encrypt()
            return post_data
        else:
            print("Sorry A {} Error Occurred!" .format(response.status_code))
    def Md5_sum(self,obj):
        """这个是根据加密机制，反过来推出的，首先计算密码的16进制的哈希值，取前30位，并大写。然后再与学号，学校代码相加，
        再重复上一步骤，最终获得加密后的密码。验证码则不需要加学号。"""
        md5= hashlib.md5 (obj.encode ('gb2312')).hexdigest()[0:30].upper()
        return md5
    def Pwd_encrypt(self):
        pwd = self.Md5_sum(self.user_id + self.Md5_sum(self.pwd) + self.school_code)
        return pwd
    def Get_vcode(self):
        self.ses.get(url=self.home_url,headers=self.Header())
        self.ses.get(url=self.login_url,headers=self.Header())
        response = self.ses.get(url=self.vcode_url,headers=self.Header())
        with open('vcode.jpg','wb') as f:
            f.write(response.content)
    def Vcode_encrypt(self):
        vcode = input("Please input the vcode:")
        vcode_encrypt = self.Md5_sum(self.Md5_sum(vcode.upper()) + self.school_code)
        return vcode_encrypt
    def Get_All(self):
        res_name = self.ses.get(url=urljoin(self.home_url,'xscj/private/list_xhxm.aspx'),headers=self.Header())
        res_score = self.ses.post(url=urljoin(self.home_url,'xscj/Stu_cjfb_rpt.aspx'),data= self.Postdata_score(),headers=self.Header())
        self.Get_Basic_info()
        with open('Your_Score.docx','ab') as f:
            f.write(res_name.content)
            f.write(res_score.content)
            print ( "All infomation is saved,Please check!" )
    def Get_Basic_info(self):
        info_num = input("Do you have access to your Personal information?\n1->YES OR 任意键->NO:")
        if info_num == '1':
            Basic_info = self.ses.get(url=urljoin(self.home_url,'xsxj/Stu_MyInfo_RPT.aspx'),headers=self.Header())
            if Basic_info.status_code == 200:
                with open('Basic_info.docx','wb') as f:
                    f.write(Basic_info.content)
            selector = html.fromstring(Basic_info.text)
            photo_url = selector.xpath("//img/@src")
            Your_photo = self.ses.get(url=urljoin(self.home_url,photo_url[0]),headers=self.Header())
            if Your_photo.status_code == 200:
                with open('Your_photo.jpg','wb') as f:
                    f.write(Your_photo.content)
    def Postdata_score(self):
        postdata_score = {
            "sel_xq": "",               ### 学期，0代表第一学期，1代表第二学期
            "SelXNXQ": "",              ### 学期，学年。0==入学以来，1==学年，2==学期
            "sel_xn": "",            ### 年份
            "submit": "检索".encode ('gb2312'),

        }
        XNXQ = input(u"Please choose the way you want to query\nand 0->入学以来，1->学年，2->学期:")
        if XNXQ == '0':
            Year = int(input("Please enter the year you need query:"))
            sys_year = int(time.strftime("%Y"))
            if sys_year <= Year <=sys_year - 4:
                postdata_score["SelXNXQ"] = '0'
                postdata_score.pop("sel_xq")
                postdata_score.pop("SelXNXQ")
                return postdata_score
        elif XNXQ == '1':
            Year = int(input ("Please enter the year you need query:"))
            sys_year = int(time.strftime ("%Y"))
            if sys_year <= Year <= sys_year - 4:
                postdata_score["sel_xn"] = str(Year)
                postdata_score["SelXNXQ"] = '1'
                postdata_score.pop("sel_xq")
                return postdata_score
        elif XNXQ == '2':
            Year = int(input ("Please enter the year you need query:"))
            sys_year = int(time.strftime("%Y"))
            if sys_year <= Year <= sys_year - 4:
                Term = input ("Please enter the term you need query:")
                if Term in ['1','2']:
                    Term = str(int(Term) - 1)
                    postdata_score["sel_xn"] = str(Year)
                    postdata_score["sel_xq"] = Term
                    postdata_score["SelXNXQ"] = '2'
                    return postdata_score
        else:
            print("Sorry enter error,Please enter again!")
            self.Postdata_score()
    def Try_login(self):
        self.Get_vcode()
        response = self.ses.post(url=self.login_url,data=self.Post_data(),headers=self.Header())
        if re.search(u"正在加载权限",response.text):
            print ( u"Login Successful,Please wait a monent")
            self.Get_All()
        elif re.search(u"帐号或密码不正确",response.text):
            print(u"Sorry The Account Number Or Password Is Incorrect!，Please Try Again")
        elif re.search(u"验证码错误",response.text):
            print(u"Sorry Vcode(验证码) Error，Please Try Again")
        else:
            print(u"Sorry Login Error")

if __name__ == '__main__':
    Basic_info = {      ###以下是个人信息，学校代码可登录教务网主页，翻看网页源代码得到###
        "school_code": "11330",                       ###学校代码 ###
        "user_id": "*********",                     ###学号###
        "pwd": "******",                              ###密码####
        "home_url": "http://jwgl.ayit.edu.cn/"        ###教务网主页 ###
    }
    login = hppv(Basic_info)
    login.Try_login()