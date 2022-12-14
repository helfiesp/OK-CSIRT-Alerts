import requests
from bs4 import BeautifulSoup as bs, ResultSet
from alerts.models import CVE
import random
import time

user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
headers = {'User-Agent': user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}

desc_filter = {' · ':'','time siden':'','timer siden':'','Følge: ':'','minutter siden':'', '...':''}
keywords = ['rce', 'remote', 'injection', 'execution','code','cve','cvss','critical','ransomware','hack','exploit','exfiltration','extortion','vulnerability','flaw','security','criticality','cybersecurity','command','high-severity','code-execution','malware','implant','exploited','actively',
'vulnerable','hacking', 'privilege', 'escalation', 'xss', 'cross-site','0day','0-day','zero-day','attack']

def NorskeNyheter():
    search_it_sikkerhet = "https://www.google.com/search?q=IT+sikkerhet&biw=2752&bih=1046&tbs=qdr%3Ad&tbm=nws&sxsrf=ALiCzsbIl7xDUKFSTkKOwBArsXdRGjD6yQ%3A1661421703175&ei=h0gHY-uMCsGrxc8PueqEkAs&ved=0ahUKEwir7MGT3uH5AhXBVfEDHTk1AbIQ4dUDCA0&uact=5&oq=IT+sikkerhet&gs_lcp=Cgxnd3Mtd2l6LW5ld3MQAzIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIGCAAQHhAWMgYIABAeEBYyBggAEB4QFjIGCAAQHhAWOgUIABCRAlAAWLMLYKIMaABwAHgAgAFziAGKBpIBBDExLjGYAQCgAQHAAQE&sclient=gws-wiz-news"
    search_sikkerhet = "https://www.google.com/search?q=sikkerhet&biw=2752&bih=1046&tbs=qdr%3Ad&tbm=nws&sxsrf=ALiCzsYaecjHLnjspDdBK0AqnS4jKLupIA%3A1661421768685&ei=yEgHY5mgKcWExc8P7sWzgAE&ved=0ahUKEwiZpOCy3uH5AhVFQvEDHe7iDBAQ4dUDCA0&uact=5&oq=sikkerhet&gs_lcp=Cgxnd3Mtd2l6LW5ld3MQAzIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQ6BQgAEJECUABYoQZg8gZoAHAAeACAAXCIAYwFkgEDOC4xmAEAoAEBwAEB&sclient=gws-wiz-news"
    search_ok_sikkerhet = "https://www.google.com/search?q=Oslo+kommune+sikkerhet&biw=2752&bih=1046&tbs=qdr%3Ad&tbm=nws&sxsrf=ALiCzsa6UNs_d1woUcSDTI5N-6MrDprV8Q%3A1661421904004&ei=T0kHY-LiPNm7xc8P4Pm4sAM&ved=0ahUKEwiixqPz3uH5AhXZXfEDHeA8DjYQ4dUDCA0&uact=5&oq=Oslo+kommune+sikkerhet&gs_lcp=Cgxnd3Mtd2l6LW5ld3MQAzIFCCEQoAEyBQghEKABMgUIIRCgATIFCCEQoAEyBQghEKABOgYIABAeEBY6BQgAEIYDOgQIABATOggIABAeEBYQEzoFCAAQgAQ6BwghEKABEApQugNYyxhgvhloAHAAeACAAWOIAcQHkgECMTSYAQCgAQHAAQE&sclient=gws-wiz-news"
    search_norge_sikkerhet = "https://www.google.com/search?q=norge+sikkerhet&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsafjZi5kXAQ6gQ3PuV1EJXcJGaKCg:1661422414728&ei=TksHY-2ELIa_xc8Ps_CvMA&start=0&sa=N&ved=2ahUKEwjt4-fm4OH5AhWGX_EDHTP4CwY4ChDy0wN6BAgBEDo&biw=2752&bih=1046&dpr=1.25"




def news_scraper():
    page1 = "https://www.google.com/search?q=%22security%22+%22vulnerability%22&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsYr3txKC81KmkrgsNsjuRgTuu6vkg:1661249248334&ei=4KYEY7nXE7Kqxc8PhKm4-A0&start=0&sa=N&ved=2ahUKEwi5x9Ha29z5AhUyVfEDHYQUDt84MhDy0wN6BAgBEDo&biw=1920&bih=973&dpr=1"
    page2 = "https://www.google.com/search?q=%22security%22+%22vulnerability%22&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsbDg79ymZVwMv-cUS8jigb88CTL3A:1661249255368&ei=56YEY8SGFuO9xc8PrcOQuAM&start=10&sa=N&ved=2ahUKEwiElv_d29z5AhXjXvEDHa0hBDcQ8tMDegQIARA7&biw=1920&bih=973&dpr=1"
    page3 = "https://www.google.com/search?q=%22security%22+%22vulnerability%22&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsYssosLYa20m7a5lwWeKUEdqkrBsQ:1661249262460&ei=7qYEY-LRG9uGxc8P1e-YuAY&start=20&sa=N&ved=2ahUKEwjigLDh29z5AhVbQ_EDHdU3Bmc4ChDy0wN6BAgBED0&biw=1920&bih=973&dpr=1"
    page4 = "https://www.google.com/search?q=%22security%22+%22vulnerability%22&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsbcmf36zLiXk931rneOJ0j8KzSQQA:1661249269713&ei=9aYEY9-HK7-rxc8PhdKGkAo&start=30&sa=N&ved=2ahUKEwif1urk29z5AhW_VfEDHQWpAaI4FBDy0wN6BAgBED8&biw=1920&bih=973&dpr=1"
    page5 = "https://www.google.com/search?q=%22security%22+%22vulnerability%22&tbs=qdr:d&tbm=nws&sxsrf=ALiCzsbfeKIEemoC_6hP43KB6SzEIW2uSg:1661249290381&ei=CqcEY4XpFqzAxc8P5ceXoA0&start=40&sa=N&ved=2ahUKEwiFltju29z5AhUsYPEDHeXjBdQ4HhDy0wN6BAgBEEE&biw=1920&bih=973&dpr=1"
    pages = [page1, page2, page3, page4, page5]
    articles = []
    for page in pages:
        time.sleep(random.randint(1, 4))
        soup = bs(requests.get(page, headers=headers, cookies=cookies).content, "lxml")
        post_info = soup.find_all("div", {'class':'Gx5Zad fP1Qef xpd EtOod pkphOe'})
        for post in post_info:
            article_dict = {}
            try:
                post_time = post.find("span", {'class':'r0bn4c rQMQod'}).text
            except AttributeError:
                post_time = "n/a"
            if "timer siden" in post_time:
                post_time = post_time.replace('for ','')
            else:
                post_time = "n/a"
            header = post.find("h3", {'class':'zBAuLc l97dzf'}).text
            url = post.find("a", href=True)['href'].replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
            description = post.find("div", {'class':'BNeawe s3v9rd AP7Wnd'}).text.replace(post_time, '').strip()
            for key, value in desc_filter.items():
                description = description.replace(key, value)
            words = []
            cves = []
            for x in header.split():
                words.append(x.lower())
            for x in description.split():
                words.append(x.lower())
            keyword_count = 0
            found_keywords = []
            for word in words:
                if word in keywords:
                    if word not in found_keywords:
                        keyword_count += 1
                        found_keywords.append(word)
                if "cve" in word:
                    cve = word.upper().replace('(','').replace(')','').replace(',...','')
                    if cve not in cves:
                        cves.append(cve)
            article_dict["TIME"] = post_time
            article_dict["URL"] = url
            article_dict["WEBSITE"] = url.replace("https://","").replace("www.", "").split("/")[0]
            article_dict["HEADER"] = header
            article_dict["DESCRIPTION"] = description
            article_dict["KEYWORDS"] = ', '.join(found_keywords)
            article_dict["KEYWORD_COUNT"] = keyword_count
            article_dict["CVES"] = ', '.join(cves)

            articles.append(article_dict.copy())
    return articles

def check_nvd(cve):
    time.sleep(0.5)
    url = "https://nvd.nist.gov/vuln/detail/{}".format(cve)
    soup = bs(requests.get(url).content, "lxml")
    not_in_db = soup.find('p', {'data-testid':'service-unavailable-msg'})
    if not_in_db:
        return False
    else:
        return True
    
def main():
    page1 = "https://www.google.com/search?q=%22CVE-2022-%22+-nvd.nist.gov+-cve.mitre.org+-cve.org+-cve.report+-vulners.com+-vulmon.com+-youtube.com+-opencve.io+-github.com+-vuldb.com+-security.snyk.io&biw=1920&bih=973&tbs=qdr%3Ad&sxsrf=ALiCzsb0L5wMmQSk-w0xP0p-arCT4hwUPQ%3A1660038081123&ei=wSvyYp3wBpnAxc8PpN6W0A0&ved=0ahUKEwjd1I3hu7n5AhUZYPEDHSSvBdoQ4dUDCA4&uact=5&oq=%22CVE-2022-%22+-nvd.nist.gov+-cve.mitre.org+-cve.org+-cve.report+-vulners.com+-vulmon.com+-youtube.com+-opencve.io+-github.com+-vuldb.com+-security.snyk.io&gs_lcp=Cgdnd3Mtd2l6EAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsAMyBwgAEEcQsANKBQg8EgExSgQIQRgASgQIRhgAUNEhWN5RYLNhaAFwAXgAgAEAiAEAkgEAmAEAoAEByAEIwAEB&sclient=gws-wiz"
    page2 = "https://www.google.com/search?q=%22CVE-2022-%22+-nvd.nist.gov+-cve.mitre.org+-cve.org+-cve.report+-vulners.com+-vulmon.com+-youtube.com+-opencve.io+-github.com+-vuldb.com+-security.snyk.io&tbs=qdr:d&sxsrf=ALiCzsbu5lb73XzXP9vuzP5oT8CJbV4k9w:1660038094579&ei=zivyYpXzItK6xc8PhvS8kAs&start=10&sa=N&ved=2ahUKEwiVksPnu7n5AhVSXfEDHQY6D7IQ8tMDegQIARA7&biw=1920&bih=973&dpr=1"
    page3 = "https://www.google.com/search?q=%22CVE-2022-%22+-nvd.nist.gov+-cve.mitre.org+-cve.org+-cve.report+-vulners.com+-vulmon.com+-youtube.com+-opencve.io+-github.com+-vuldb.com+-security.snyk.io&tbs=qdr:d&sxsrf=ALiCzsbijDhTi30Ad99V7I4S8_xR8y8npw:1660038112194&ei=4CvyYueyC5SAxc8P0LGd8Ak&start=20&sa=N&ved=2ahUKEwjnovbvu7n5AhUUQPEDHdBYB544ChDy0wN6BAgBED0&biw=1920&bih=973&dpr=1"
    cve_filter = {'(':'',')':'','[':'',']':'',':':'','A':'','No':'',',':'','V3':'','.':'','Sign':'','v3':'','V3':'','n':'','“':'','・':''}
    pages = [page1, page2, page3]
    potential_cves = []
    for page in pages:
        time.sleep(random.randint(1, 4))
        soup = bs(requests.get(page, headers=headers, cookies=cookies).content, "lxml")
        post_info = soup.find_all("div", {'class':'Gx5Zad fP1Qef xpd EtOod pkphOe'})
        for post in post_info:
            cve_dict = {}
            try:
                post_time = post.find("span", {'class':'r0bn4c rQMQod'}).text
            except AttributeError:
                post_time = "n/a"
            if "timer siden" in post_time:
                post_time = post_time.replace('for ','')
            else:
                post_time = "n/a"
            header = post.find("h3", {'class':'zBAuLc l97dzf'}).text
            url = post.find("a", href=True)['href'].replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
            description = post.find("div", {'class':'BNeawe s3v9rd AP7Wnd'}).text.replace(post_time, '')[6:]
            for key, value in desc_filter.items():
                description = description.replace(key, value)
            wordlist = []
            for word in header.split():
                wordlist.append(word.strip())
            for word in description.split():
                wordlist.append(word.strip())
            try:
                url = url.split("&ved=")[0]
            except:
                url = url
            for word in wordlist:
                for key, value in cve_filter.items():
                    word = word.replace(key, value)
                if "CVE-" in word:
                    splitted = word.split("-")
                    if len(splitted) == 3:
                        cve_id = ""
                        for letter in splitted[2]:
                            if letter.isdigit():
                                cve_id += letter
                    cve_full = (splitted[0], splitted[1], cve_id)
                    word = "-".join(cve_full)
                    if len(word) < 15 and len(word)> 12:
                        if not check_nvd(word.strip()):
                            cve_dict["CVE"] = word
                            cve_dict["TIME"] = post_time
                            cve_dict["URL"] = url
                            cve_dict["WEBSITE"] = url.replace("https://","").replace("www.", "").split("/")[0]
                            cve_dict["HEADER"] = header
                            cve_dict["DESCRIPTION"] = description
                            noadd = 0
                            for item in potential_cves:
                                if header == item["HEADER"]:
                                    noadd = 1
                            if noadd == 0:
                                potential_cves.append(cve_dict.copy())
    return potential_cves