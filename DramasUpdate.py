import urllib.request
import sys
import http.cookiejar
import urllib.parse
import json
import configparser
from bs4 import BeautifulSoup
from email_constructor import Email
import pickle
import feedparser
import os


class Zimuzu(object):
    def __init__(self, user, password):
        self.url = "http://www.zimuzu.tv"
        self.user = user
        self.password = password

        # install opener with cookiejar
        self.cookie = http.cookiejar.CookieJar()
        self.cookie_processor = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.cookie_processor)
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0")]
        urllib.request.install_opener(self.opener)

    def login(self):
        login_url = self.url + "/User/Login/ajaxLogin"

        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'origin': "http://www.zimuzu.tv",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            'content-type': "application/x-www-form-urlencoded",
            'referer': "http://www.zimuzu.tv/user/login",
            'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
        }

        params = {
            'account': self.user,
            'password': self.password
        }
        params = urllib.parse.urlencode(params).encode("utf-8")

        request = urllib.request.Request(login_url, data=params, headers=headers)
        responce = urllib.request.urlopen(request)
        data = responce.read().decode("utf-8")
        data = json.loads(data)

        # Login failed.
        if data["status"] != 1:
            sys.exit(1)

    def get_user_favor(self):
        url = self.url + "/user/fav"

        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'origin': "http://www.zimuzu.tv",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            'content-type': "application/x-www-form-urlencoded",
            'referer': "http://www.zimuzu.tv/user/user",
            'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
        }

        request = urllib.request.Request(url, headers=headers)
        responce = urllib.request.urlopen(request)
        data = responce.read().decode("utf-8")
        
        soup = BeautifulSoup(data, "lxml")

        return (x["itemid"] for x in soup.find_all("span", attrs={"type": "resource"}))

    def get_update(self):
        url = "http://diaodiaode.me/rss/feed/"
        ids = self.get_user_favor()
        msg = ""

        if not os.path.exists("fav_record"):  # 首次运行或记录被清除。
            print("首次运行，更新收藏列表。")
            os.mkdir("fav_record")
            os.chdir("fav_record")
            for id in ids:
                rss_url = url + id
                d = feedparser.parse(rss_url)
                item_set = set(d.entries)
                item_set = filter(lambda x: x.title.find("中英字幕") != -1, item_set)
                link_set = set([i.link for i in item_set])
                link_set.pop()
                with open(id, "wb") as f:
                    pickle.dump(link_set, f)

        else:
            os.chdir("fav_record")
            for id in ids:
                rss_url = url + id
                d = feedparser.parse(rss_url)
                item_set = set(d.entries)
                item_set = set(filter(lambda x: x.title.find("中英字幕") != -1, item_set))
                link_set = set([i.link for i in item_set])
                title = d.feed.title
                with open(id, "rb") as f:
                    old_link_set = pickle.load(f)
                update = link_set - (old_link_set & link_set)
                download_link = ""

                if len(update) == 0:
                    print(title + "no update.")
                    continue
                else:
                    for i in item_set:
                        for u in update:
                            if i.link == u:
                                try:
                                    download_link += i.magnet + '\n'
                                except Exception:
                                    download_link += i.ed2k + '\n'
                                break
                    with open(id, "wb") as f:
                        pickle.dump(link_set, f)
                msg += title + '\n' + download_link + '\n'
        # print(msg)
        return msg

    def logout(self):
        logout_url = self.url + "/user/logout/ajaxLogout"

        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'origin': "http://www.zimuzu.tv",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            'referer': "http://www.zimuzu.tv/",
            'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
        }

        request = urllib.request.Request(logout_url, headers=headers)
        responce = urllib.request.urlopen(request)
        data = responce.read().decode("utf-8")

        data = json.loads(data)
        if data["status"] == 1:
            print("登出成功。")
        else:
            print("登出失败。")


if __name__ == "__main__":
    login_data = configparser.ConfigParser()
    login_data.read("user.ini")
    user = login_data.get("LoginInfo", "user")
    password = login_data.get("LoginInfo", "password")

    zimuzu_api = Zimuzu(user, password)
    zimuzu_api.login()
    data = zimuzu_api.get_update()
    print(data)
    zimuzu_api.logout()

