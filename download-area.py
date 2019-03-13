import urllib.request
import urllib.error
import os
import time
import socket
import threadpool
import datetime


def url_open(url):
    print(url)
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36')
        response = urllib.request.urlopen(req, data=None, timeout=10)
        return response.read()
    except urllib.error.URLError as e:
        print(e)
        return False
    except socket.timeout as e:
        print(e)
        return False
        
    


def get_area_txt(url, area):
    html = url_open(url).decode('gb2312', 'ignore').encode('utf-8').decode('utf-8')
    end = 0
    # print(html)
    if html != -1:
        a = html.find(area)
        if a != -1:
            b = a
            while b == -1:
                b = html.find(area, b + 5, a + 1000)
                print(b)
                if b != -1:
                    end = b

            txt = html[a + len(area) + 2:end - 16]
            return txt

def get_provincetr_url(url):
    area_dict = []
    area_txt = get_area_txt(url, "provincetr")
    a = area_txt.find("<td><a href='")
    while a != -1:
        a = area_txt.find("<td><a href='", a)
        b = area_txt.find(".html'>", a, a + 50)
        if b != -1:
            url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + area_txt[a + 13:b + 5]
            print(url)
            a = area_txt.find("<br/></a></td>", b, -1)
            if a != -1:
                name = area_txt[b + 7:a]
                area_dict.append([name, url])
    print(area_dict)
    return area_dict

def while_open_url(url):
    html = ''
    html = url_open(url)
    if not html:
        time.sleep(5)
        html = while_open_url(url)
    
    return html
        
    
def get_area_info(url, parent_code="1", parent_level=None):
    with open('arce.txt', 'a+') as file:
        # time.sleep(1)
        
        html = while_open_url(url).decode('gb2312', 'ignore').encode('utf-8').decode('utf-8')
        level_start = html.find("代码</td><td>名称</td></tr>")
        level_end = html.find("'><td>")
        level = html[level_start+36:level_end]
        if level == "citytr":
            next_u = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/"
        elif level == "countytr" and parent_level == "citytr":
            next_u = url[:-9]
        elif level == "towntr" and parent_level == "citytr":
            next_u = url[:-9]
        elif level == "towntr" and parent_level == "countytr":
            next_u = url[:-11]

        print(level)
        if level != "villagetr":
            a = html.find("<tr class='" + level + "'><td><a href='", level_start, level_end + 15)
            if a == -1:
                end = html.find("</td></tr>", level_end, level_end + 60)
                code = html[level_end + 6:level_end + 18]
                name = html[level_end + 27:end]
                print(level + "," + parent_code + "," + code + "," + name)
                file.write(level + "," + parent_code + "," + code + "," + name + '\n')

            a = html.find("<tr class='" + level + "'><td><a href='")
            while a != -1:
                a = html.find("<tr class='" + level + "'><td><a href='", a)
                b = html.find("</a></td><td><a href='", a, a + 200)
                if b != -1:
                    c = html.find(".html'>", b, b+200)
                    d = html.find("</a></td></tr>", b, b+200)
                    code = html[b-12:b]
                    name = html[c + 7:d]
                    print(level + "," + parent_code + "," + code + "," + name)
                    file.write(level + "," + parent_code + "," + code + "," + name +'\n')
                    #递归
                    next_url = next_u + html[b+22:c+5]
                    get_area_info(next_url, code, level)
                    a = html.find("</tr><tr class='" + level + "'><td><a href='", b)

        elif level == "villagetr":
            a = html.find("<tr class='villagetr'><td>")
            while a != -1:
                a = html.find("<tr class='" + level + "'><td>", a-1)
                b = html.find("</td><td>", a)
                if b != -1:
                    c = html.find("</td><td>", b+5, b + 40)
                    d = html.find("</td></tr>", c+5, c + 200)
                    code = html[b-12:b]
                    name = html[c + 9:d]
                    print(level + "," + parent_code + "," + code + "," + name)
                    file.write(level + "," + parent_code + "," + code + "," + name + '\n')
                    a = html.find("<tr class='" + level + "'><td>", d)
        file.close()

def tpool(d) :
    parent_code = d[1][-7:-5] + "0000000000"
    name = d[0]
    get_area_info(url=d[1], parent_code=parent_code)
    with open('arce.txt', 'a+') as file:
        file.write("provincetr,," + parent_code + "," + name + '\n')
        file.close()

if __name__ == '__main__':
    with open('arce.txt', 'a+') as file:
        file.write("level,parent_code,code,name" + '\n')
        file.close()
   
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html"
    dict_info = get_provincetr_url(url)
    for d in dict_info:

        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        parent_code = d[1][-7:-5] + "0000000000"
        # if int(parent_code) < 410000000000:
        #     continue
        
        name = d[0]
        get_area_info(url=d[1], parent_code=parent_code)
        with open('arce.txt', 'a+') as file:
            file.write("provincetr,,"+ parent_code + "," + name + '\n')
            file.close()
    print("ok")
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    # # 多线程爬取
    # pool = threadpool.ThreadPool(3)
    # requests = threadpool.makeRequests(tpool, dict_info)
    # [pool.putRequest(req) for req in requests]
    # pool.wait()






