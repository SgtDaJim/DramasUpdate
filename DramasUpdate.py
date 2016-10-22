import urllib.request
import sys
import http.cookiejar
import urllib.parse
import json
import configparser
import re
import lxml
from bs4 import BeautifulSoup

COOKIE = ""
COOKIE_PROCESSOR = ""
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "X-Requested-With" : "XMLHttpRequest",
    "Referer" : "http://www.zimuzu.tv/user/login"
}

def build_opener():
    cookie = http.cookiejar.CookieJar()
    cookie_processor = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookie_processor)
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0")]
    urllib.request.install_opener(opener)


def login(user, password):

    login_url = "http://www.zimuzu.tv/User/Login/ajaxLogin"

    params = {
        "account" : user,
        "password" : password
    }

    params = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(login_url, params, headers={"Referer":"http://www.zimuzu.tv/user/login","X-Requested-With": "XMLHttpRequest"})
    response = urllib.request.urlopen(request)
    data = response.read().decode("utf-8")
    data = json.loads(data)

    return data["status"]


def get_user_info():

    get_user_info_url = "http://www.zimuzu.tv/user/login/getCurUserTopInfo"

    request = urllib.request.Request(get_user_info_url, headers={"Referer":"http://www.zimuzu.tv","X-Requested-With": "XMLHttpRequest"})
    response = urllib.request.urlopen(request)
    data = response.read().decode("utf-8")
    data = json.loads(data)

    return data

def get_user_favor():

    get_user_favor_url = "http://www.zimuzu.tv/user/fav"

    request = urllib.request.Request(get_user_favor_url, headers={"Referer":"http://www.zimuzu.tv"})
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")

    pattern = r'<strong><a href="/resource/(.+)">(.+)</a></strong><span class="ts">(.+)</span><span class="star-fav" itemid="(.+)" channel="resource">'
    set = re.findall(pattern, html)

    return set

def get_programs(pid):

    get_programs_url = "http://www.zimuzu.tv/resource/list_episode/" + pid

    request = urllib.request.Request(get_programs_url, headers={"referer":"http://www.zimuzu.tv/gresource/" + pid})
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")

    #pattern = r'<div class="media-child-item" dateline="(.+)">\s*?<span class="fr">\s*<a href="(.*?)" type="ed2k"[\s\S]*?<strong>HR-HDTV</strong><a href="/resource/moreway/\d*?" target="_blank" class="lk">(.*?)</a><span class="f4">??'
    #set = re.search(pattern, html)

    soup = BeautifulSoup(html, "lxml")
    programs = soup.find_all("div", class_="media-child-item")

    for p in programs:
        if p.strong.string == "HR-HDTV":
            latest = p
            break

    links = latest.find_all("a")

    set = list()
    set.append(latest["dateline"])
    for l in links:
        if l.string == "电驴":
            set.append(l["href"])
    set.append(latest.find("a", class_="lk").string)

    return set

def update_config():

    favor = get_user_favor()

    config = configparser.ConfigParser()

    if len(config.read("config.ini")) == 0 :
        config["UserInfo"] = {}
        config["UserInfo"]["IsFirstTimeUsing"] = "True"
        config.add_section("UserFavor")
        with open("config.ini", "w") as configuration:
            config.write(configuration)

    config.read("config.ini")

    if config["UserInfo"].getboolean("IsFirstTimeUsing"):
        print("首次使用将更新收藏列表，从下次扫描开始提醒更新内容。")
        print("已收藏内容：")
        for n in favor:
            print(n[1])

        print("载入最新剧集时间戳。")
        for n in favor:
            set = get_programs(n[0])
            config.set("UserFavor", str(n[0]), str(set[0]))
            print(n[1] + "  ID:" + n[0] + "  最新剧集时间戳:" + set[0])

        config.set("UserInfo", "IsFirstTimeUsing", "False")

        with open("config.ini", "w") as configuration:
            config.write(configuration)


        print("配置写入完成。首次运行无法检查更新。下次扫描将返回最新剧集ed2k链接。")
        sys.exit(0)

    else:
        print("开始对比和修复在线收藏列表与配置列表差异。")
        #新添加收藏时
        for n in favor:
            if not config.has_option("UserFavor", str(n[0])):
                set = get_programs(n[0])
                config.set("UserFavor", str(n[0]), str(set[0]))
                print("新增收藏配置：" + n[1] + "  ID:" + n[0] + "  最新剧集时间戳:" + set[0])

        #删除收藏时
        pid = list()
        for n in favor:
            pid.append(n[0])
        for o in config.options("UserFavor"):
            if o not in pid:
                config.remove_option("UserFavor", o)
                print("删除收藏配置：" + o)

        with open("config.ini", "w") as configuration:
            config.write(configuration)

        print("差异对比完成，配置已保存。")


def get_programs_update_ed2k():

    config = configparser.ConfigParser()
    config.read("config.ini")

    update_flag = False

    print("开始查询是否有更新剧集。")

    PID = config.options("UserFavor")
    for p in PID:
        set = get_programs(p)
        if set[0] > config.get("UserFavor", p):
            update_flag = True
            print("更新：" + set[2])
            print("电驴链接：" + set[1])
            config.set("UserFavor", p, set[0])

    if update_flag:
        with open("config.ini", "w") as configuration:
            config.write(configuration)
        print("配置文件已更新。")

    else:
        print("没有更新。")





if __name__ == "__main__":

    login_config = configparser.ConfigParser()
    login_config.read("login.ini")

    user = login_config.get("LoginInfo", "user")
    password = login_config.get("LoginInfo", "password")

    build_opener()
    status = login(user, password)

    #用户名或者密码错误，或者其他别的错误导致登录不成功，直接结束程序
    if status != 1:
        sys.exit("登录出错！退出程序！")

    user_data = get_user_info()
    print("登录成功！你好，" + user_data["data"]["userinfo"]["nickname"] + "！")
    print("你当前等级为：" + user_data["data"]["userinfo"]["common_group_name"])
    print("你已登录" + str(user_data["data"]["usercount"]["cont_login"]) + "天，再登录" + str(user_data["data"]["upgrade_day"]) + "天即可升级到下一等级！")

    update_config()
    get_programs_update_ed2k()

    print("运行结束。")





