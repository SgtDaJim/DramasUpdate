import urllib.request
import sys
import http.cookiejar
import urllib.parse
import json
import configparser
from bs4 import BeautifulSoup
from email_constructor import Email

COOKIE = ""
COOKIE_PROCESSOR = ""
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "X-Requested-With" : "XMLHttpRequest",
    "Referer" : "http://www.zmz2017.com/user/login"
}

def build_opener():
    cookie = http.cookiejar.CookieJar()
    cookie_processor = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookie_processor)
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0")]
    urllib.request.install_opener(opener)


def login(user, password):

    login_url = "http://www.zmz2017.com/User/Login/ajaxLogin"

    params = {
        "account" : user,
        "password" : password
    }

    params = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(login_url, params, headers={"Referer":"http://www.zmz2017.com/user/login","X-Requested-With": "XMLHttpRequest"})
    response = urllib.request.urlopen(request)
    data = response.read().decode("utf-8")
    data = json.loads(data)

    return data["status"]


def get_user_info():
    '''
    获取用户信息
    :return:
        用户信息的json数据
    '''

    get_user_info_url = "http://www.zmz2017.com/user/login/getCurUserTopInfo"

    request = urllib.request.Request(get_user_info_url, headers={"Referer":"http://www.zmz2017.com","X-Requested-With": "XMLHttpRequest"})
    response = urllib.request.urlopen(request)
    data = response.read().decode("utf-8")
    data = json.loads(data)

    return data

def get_user_favor():
    '''
    获取收藏列表中的电视剧信息
    :return:
        包含电视剧ID，电视剧名称的list
    '''

    get_user_favor_url = "http://www.zmz2017.com/user/fav"

    request = urllib.request.Request(get_user_favor_url, headers={"Referer":"http://www.zmz2017.com"})
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")

    soup = BeautifulSoup(html, "lxml")
    favor_list = soup.find("ul", class_="user-favlist has-point").find_all("li", class_="clearfix")
    favor = list()
    for li in favor_list:
        item = list()
        item.append(li.find("span", class_="star-fav")["itemid"])
        item.append(li.find("strong").string)
        favor.append(item)

    return favor


def get_programs(pid):
    '''
    获取电视剧的最新中文字幕的HR-HDTV信息
    :param pid:
        电视剧ID
    :return:
        包含电视剧最新中文字幕HR-HDTV视频的时间戳，ed2k链接，名称的list
    '''

    get_programs_url = "http://www.zmz2017.com/resource/list/" + pid

    request = urllib.request.Request(get_programs_url, headers={"referer":"http://www.zmz2017.com/gresource/" + pid})
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")

    soup = BeautifulSoup(html, "lxml")
    #print(soup)

    media_list = soup.find_all("div", class_="media-list")
    for m in media_list:
        if m.h2.string == "HR-HDTV":
            hr_list = m

    episode_list = hr_list.find_all("li")

    # 去除不符合要求的周边资源
    for e in episode_list:
        if int(e["season"]) > 99:
            episode_list.remove(e)

    newest = episode_list[-1]
    timestamp = newest.find("a", class_="f7 lk")["itemid"]
    name = newest.find("a", class_="f7 lk")["title"]
    ed2k = newest.find("a", type="ed2k")["href"]

    set = [timestamp, ed2k, name]

    return set                                                              # ["时间戳", "ed2k连接", "名称"]

def update_config():
    '''
    初始化或更新收藏配置文件
    '''

    favor = get_user_favor()

    config = configparser.ConfigParser()

    if len(config.read("favor.ini")) == 0 :
        config["UserInfo"] = {}
        config["UserInfo"]["IsFirstTimeUsing"] = "True"
        config.add_section("UserFavor")
        with open("favor.ini", "w") as configuration:
            config.write(configuration)

    config.read("favor.ini")

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

        with open("favor.ini", "w") as configuration:
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

        with open("favor.ini", "w") as configuration:
            config.write(configuration)

        print("差异对比完成，配置已保存。")


def get_programs_update_ed2k():
    '''
    打印出和返回最新剧集的ed2k下载链接
    '''

    config = configparser.ConfigParser()
    config.read("favor.ini")

    update_flag = False
    msg = str()

    print("开始查询是否有更新剧集。")

    PID = config.options("UserFavor")
    for p in PID:
        set = get_programs(p)
        print(set)
        if set[0] > config.get("UserFavor", p):
            update_flag = True
            print("更新：" + set[2])
            print("电驴链接：" + set[1])
            config.set("UserFavor", p, set[0])
            msg += "更新：%s\n电驴链接：%s\n\n" % (set[2], set[1])

    if update_flag:
        with open("favor.ini", "w") as configuration:
            config.write(configuration)
        print("配置文件已更新。")
        return msg

    else:
        print("没有更新。")
        return "没有更新。"





if __name__ == "__main__":

    login_config = configparser.ConfigParser()
    login_config.read("user.ini")

    print("1")

    user = login_config.get("LoginInfo", "user")
    password = login_config.get("LoginInfo", "password")

    print("2")

    build_opener()
    status = login(user, password)

    # 用户名或者密码错误，或者其他别的错误导致登录不成功，直接结束程序
    if status != 1:
        sys.exit("登录出错！退出程序！")

    user_data = get_user_info()
    print("登录成功！你好，" + user_data["data"]["userinfo"]["nickname"] + "！")
    print("你当前等级为：" + user_data["data"]["userinfo"]["common_group_name"])
    print("你已登录" + str(user_data["data"]["usercount"]["cont_login"]) + "天，再登录" + str(user_data["data"]["upgrade_day"]) + "天即可升级到下一等级！")

    update_config()
    msg = get_programs_update_ed2k()

    # 发送邮件提示
    email = Email(msg)
    email.send()

    print("运行结束。")





