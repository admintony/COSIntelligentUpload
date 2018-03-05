源地址：[腾讯云COS图床智能上传工具编写](http://admintony.com/2018/03/05/%E8%85%BE%E8%AE%AF%E4%BA%91COS%E5%9B%BE%E5%BA%8A%E6%99%BA%E8%83%BD%E4%B8%8A%E4%BC%A0%E5%B7%A5%E5%85%B7%E7%BC%96%E5%86%99/)

# 1.编写意图

在百度上能够找到的都是七牛云的图床上传工具，但是七牛云现在申请图床空间需要拿手持身份证照片来认证，所以果断放弃了七牛云，于是找到了腾讯云的COS，免费额度就够用了。但是，缺点在于，每一个图片都要自己手动上传，没有像七牛云那样的智能上传工具，所以自己用Python编写一款。

# 2.流程图

主要流程：

![](https://blog-1252108140.cos.ap-beijing.myqcloud.com/201803/1520211020.1448267.png)

上传函数流程：


# 3.相关功能实现

## 3.1 将粘贴板的图片保存到本地

**使用win32clipboard**

```python
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
    win32clipboard.CloseClipboard()
```

但是直接将data写入bmp文件中，发现无法打开，百度以后找到解决办法(参考文章1)，代码量很长，这里不附上了，简单说下它的问题：

![](https://blog-1252108140.cos.ap-beijing.myqcloud.com/201803/20180305085907.png)

可以看到，一个全屏截图竟然达到了3.96M ，腾讯云免费空间才50G ， 要是上传这样的图片上去，我可吃不消啊。

**使用PIL对图像处理**

```python
from PIL import ImageGrab
from PIL import Image

# 从粘贴板获取内容
im = ImageGrab.grabclipboard()
# 判断内容是不是图片
if isinstance(im,Image.Image):
    im.save("admintony.png")
```

## 3.2 上传到COS并获取地址

**腾讯COS SDK**

腾讯对开发者提供了SDK，但是这个SDK只支持python2.6和python2.7，由于我的环境只有python3.6，所以没办法用了。[腾讯云COS SDK](https://cloud.tencent.com/document/product/436/12269)

**第三方支持python3的SDK库**

本来想自己写，可是那个数字签名认证没写过，在网上找了找，还是看到了支持py3的第三方库了，直接用第三方库吧，方便。

第三方库地址：

    https://github.com/imu-hupeng/cos-python3-sdk/

这个第三方库不是腾讯开发的，但是也是功能很齐全，例如上传文件实现：

```python
    cos = cos_lib3.Cos(app_id, secret_id,
                    secket_key, region)
    bucket = cos.get_bucket("blog")
    json_data = bucket.upload_file(real_file_path=file_name, file_name=name, dir_name=folder)
    print(json_data)
```

输出结果是返回的json数组，里面包含了上传后的地址

## 3.3 将返回的图片地址复制到粘贴板

**实现剪切板的写入**

还是用的pywin32中的win32clipboard库，代码如下：

```python
    def setText(aString):
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(win32con.CF_UNICODETEXT, aString)
        w.CloseClipboard()
```

这里有一个坑，百度上百度到的代码第三行使用的是win32con.CF_TEXT，但是测试发现CF_TEXT只能写入首字母，比如http://baidu.com 只能写入h。

查阅相关资料以后，发现有一个CF_UNICODETEXT，测试可以写入完整字符串。

**对图片地址处理**

在写入粘贴板之前，对图片地址做一个处理，处理成markdown格式的，\!\[\](PicUrl)然后放入剪切板。

代码实现：

```python
    json_data = sub(bucket.upload_file(real_file_path=file_name, file_name=name, dir_name=folder))
    dict = json.loads(json_data)
    setText(r'![]({})'.format(dict['source_url']))
```

其中sub函数是将单引号替换成双引号的函数，因为该第三方库返回的json数组使用的是单引号，json.loads()不识别单引号。

sub函数代码：

```python
    def sub(string):
        return re.sub('\'','\"',string)
```

## 3.4 腾讯云COS的一处忽略

我发现复制到粘贴板的字符串都是http协议的，然而却防在markdown编辑器中却加载不到图片，看了下手动传的生成的地址，现在COS已经采用https协议了，所以还要对返回的地址做一个处理

```python
    def sub_http(string):
        return re.sub('http:','https:',string)
```

# 4.成品展示

## 4.1 使用展示
![](https://blog-1252108140.cosbj.myqcloud.com/201803/1520257712.6010993.png)

![](https://blog-1252108140.cosbj.myqcloud.com/201803/1520257761.4938865.png)

## 4.2 依赖的第三方库说明

* win32con 和 win32clipboard ：安装了pywin32即可使用

* PIL ：图像处理库

* cos_lib3 : 腾讯云COS支持Python3的库，非官方库(github : https://github.com/imu-hupeng/cos-python3-sdk/)

* httplib2 : cos_lib3中使用了，因此安装

**安装库：**
    
    pip install pywin32
    pip install PIL
    cos_lib3 : 已经放在了同目录下进行引用，无需安装
    pip install httplib2

## 4.3 使用说明

![](https://blog-1252108140.cosbj.myqcloud.com/201803/1520257958.352451.png)

在腾讯云的COS中申请API密钥，然后填写进去即可。

特别说明一下region：

    cos地址与对应园区的关系

    tj -- 华北(天津园区)
    sh -- 华东(上海园区)
    gz -- 华南(广州园区)
    sgp -- 新加坡园区
    bj -- 北京园区

官方只给出了前四个，可能现在更新出了北京园区，官方还没写上去吧。




# 参考文章

[使用Python保存屏幕截图（不使用PIL）](https://www.cnblogs.com/xieqiankun/p/usePythonForScreenShot.html)

[腾讯云对象存储服务(COS) Python3 SDK](http://blog.csdn.net/huplion/article/details/54995090)

# 附录

另外一种操作粘贴板的方法：

```python
from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append('http://www.admintony.com')
r.destroy()
```
