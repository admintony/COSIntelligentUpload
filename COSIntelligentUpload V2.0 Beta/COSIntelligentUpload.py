Author = "AdminTony"
Blog = "http://www.admintony.com"
bbs = "http://t00ls.net"
date = "2018.03.06"
version = "V2.0 Beta"

"""
    更新说明：
        1. API接口信息从外部吸取
        2. 修复目录下无image目录报错
"""

"""
    所依赖的第三方库说明：
        win32con 和 win32clipboard ：安装了pywin32即可使用
        PIL ：图像处理库
        cos_lib3 : 腾讯云COS支持Python3的库，非官方库(github : https://github.com/imu-hupeng/cos-python3-sdk/)
        httplib2 : cos_lib3中使用了，因此安装
    安装：
        pip install pywin32
        pip install PIL
        cos_lib3 : 已经放在了同目录下进行引用，无需安装
        pip install httplib2
"""
import win32con
import json
import win32clipboard as w
from PIL import ImageGrab
from PIL import Image
import os,time,sys,re,random

sys.path.append(os.path.dirname(__file__))

import cos_lib3

class COS_Intelligent_Upload(object):
    def __init__(self,app_id,secret_id,secket_key,region):
        self.app_id = app_id
        self.secret_id = secret_id
        self.secket_key = secket_key
        self.region = region

    # 将字符串写入粘贴板
    def setText(self,aString):
        w.OpenClipboard()
        w.EmptyClipboard()
        #print(aString)
        w.SetClipboardData(win32con.CF_UNICODETEXT, aString)
        w.CloseClipboard()


    # 从粘贴板获取图片，并保存到本地 ， 文件名为时间戳
    def imageSave(self):
        im = ImageGrab.grabclipboard()
        if isinstance(im,Image.Image):
            name = str(time.time())+".png"
            if not os.path.exists("image"):
                os.mkdir("image")
            path = "image/"+ name
            im.save(path)
            print("[+] 图片准备上传!")
            self.upload(path,name)

    def sub(self,string):
        return re.sub('\'','\"',string)

    def sub_http(self,string):
        return re.sub('http:','https:',string)

    def upload(self,file_name,name):
        cos = cos_lib3.Cos(self.app_id, self.secret_id,
                           self.secket_key, self.region)
        bucket = cos.get_bucket("blog")
        # 判断目录是否存在
        now = time.localtime(time.time())
        if now.tm_mon < 10:
            folder = str(now.tm_year) +"0"+ str(now.tm_mon)
        else:
            folder = str(now.tm_year) + str(now.tm_mon)
        data = bucket.query_folder(folder)
        # 不存在这个目录则创建
        if "SUCCESS" not in data:
            bucket.create_folder(folder)
        # 存储图片
        json_data = self.sub(bucket.upload_file(real_file_path=file_name, file_name=name, dir_name=folder))
        #print(json_data)
        dict = json.loads(json_data)
        print(r'![]({})'.format(self.sub_http(dict['source_url'])))
        #self.setText(dict['source_url'])
        self.setText(r'![]({})'.format(self.sub_http(dict['source_url'])))
        print("[+] 上传成功，已将地址复制到粘贴板")
        print("[+] 正在监听...")
def main():
    #imageSave()
    """
    
    #======================设置区========================
    app_id = 1252108140
    secret_id = "AK"
    secket_key = "M5JYU"
    region = ""
    #====================设置区结束======================
    
    """
    # 从外部吸取config.conf内容
    try:
        infoDict = {}
        with open("config.conf","r") as file:
            ApiInfo = file.readlines()
            for info in ApiInfo:
                try:
                    if info != "\n" and info != "":
                        tmp = info.split("=")
                        infoDict[tmp[0].strip()] = tmp[1].strip()
                        #print(tmp)
                except Exception as e:
                    #print(e)
                    print("[-] 请按照要求配置config.conf")
                    sys.exit()
    except Exception as e:
        #print(e)
        print("[-] 请在config.conf中配置您的腾讯云COS API信息")
        sys.exit()

    # 配置API信息
    app_id = infoDict["app_id"]
    secret_id = infoDict["secret_id"]
    secket_key = infoDict["secret_key"]
    region = infoDict["region"]
    cos = COS_Intelligent_Upload(app_id, secret_id, secket_key, region)
    print("""
*******************************************
*            Author : AdminTony           *
*        Blog : http://admintony.com      *
*           Copyright : by T00LS          *
*           Version : V2.0 Beta           *
*******************************************
    """)
    print("[+] 正在监听...")
    while True:
        cos.imageSave()
        time.sleep(random.random())
    #upload(app_id,secret_id,secket_key,region)
    #pass

if __name__ == '__main__':
    main()

