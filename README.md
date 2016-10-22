DramasUpdate
====================
自动获取人人字幕组中收藏的美剧的最新连载的链接。
##依赖
    BeautifulSoup
    lxml
##安装依赖
    pip install BeautifulSoup4
    pip install lxml
    
windows用户在安装lxml可能会因为缺少C语言库报错<br>
可以选择到[Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/)下载whl文件
例如：<br>
使用python3.5版本<br>
则下载lxml-3.6.4-cp35-cp35m-win_amd64.whl
然后<BR>

    pip install wheel
    pip install f:\lxml-3.6.4-cp35-cp35m-win_amd64.whl (你lxml的whl文件的存放目录)
## 用法
    1. notepad打开login.ini，找到user和password。
    2. 在user和password的等号后面写入帐号密码。保存退出。
    3. 使用python3.x运行DramasUpdate.py。
    4. Enjoy.
