DramasUpdate
====================
自动获取人人字幕组中收藏的美剧的最新连载的链接，并将链接发送到用户邮箱。<br>
若加上添加到系统定时任务，自动运行脚本，岂不是美滋滋。
## 依赖
    BeautifulSoup
    lxml
## 安装依赖
    pip install BeautifulSoup4
    pip install lxml
    
windows用户在安装lxml可能会因为缺少C语言库报错<br>
可以选择到[Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/)下载whl文件
例如：<br>
使用python3.5版本<br>
则下载lxml-3.6.4-cp35-cp35m-win_amd64.whl<br>
然后<br>

    pip install wheel
    pip install f:\lxml-3.6.4-cp35-cp35m-win_amd64.whl (你lxml的whl文件的存放目录)
## 用法
    1. 安装依赖。
    2. notepad打开login.ini。
    3. 在LoginInfo项中，
            user=人人字幕组网站帐号
            password=密码
    4. 在EmailInfo项中，
            from=充当发送者的邮箱
            to=充当收件者的邮箱
            authorization=发送者邮箱的smtp授权码
            smtp_server=发送者邮箱的smtp服务器
            smtp_port=smtp服务器端口
    5. 使用python3.x运行DramasUpdate.py。
    6. Enjoy.
    
## 注意事项
首次运行将更新配置文件，将帐号收藏列表写成favor.ini配置文件，文件中时间戳为最新剧集的时间戳。<br>
从第二次运行开始，程序将检查更新，并返回相关更新信息。
