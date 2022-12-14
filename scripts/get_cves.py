from alerts.models import CVE
from alerts.models import NewsArticles
from datetime import timedelta
import datetime


def daily_cve():
    cves = []
    data= CVE.objects.values()
    for entry in data:
        if entry["date"] == str(datetime.date.today() - datetime.timedelta(days=1)) or entry["date"] == str(datetime.date.today()):
            cves.append(entry)
        try:
            if entry["cvss_score"] != "N/A" or entry["cvss_score"] != "n/a":
                entry["cvss_score"] = float(entry["cvss_score"])
            else:
                entry["cvss_score"] = 0.0
        except:
            entry["cvss_score"] = 0.0
    sorted_list = sorted(cves, key=lambda d: d['cvss_score'], reverse=True)
    for entry in sorted_list:
        if entry["cvss_score"] == 0.0: entry["cvss_score"] = "N/A"
    return sorted_list

def yesterdays_cve():
    cves = []
    data= CVE.objects.values()
    for entry in data:
        if entry["date"] == str(datetime.date.today() - datetime.timedelta(days=1)):
            cves.append(entry)
        try:
            if entry["cvss_score"] != "N/A" or entry["cvss_score"] != "n/a":
                entry["cvss_score"] = float(entry["cvss_score"])
            else:
                entry["cvss_score"] = 0.0
        except:
            entry["cvss_score"] = 0.0
    sorted_list = sorted(cves, key=lambda d: d['cvss_score'], reverse=True)
    for entry in sorted_list:
        if entry["cvss_score"] == 0.0: entry["cvss_score"] = "N/A"
    return sorted_list

def weekly_cve():
    days_list = []
    for x in range(7):
        day = datetime.date.today() - timedelta(days=x)
        days_list.append(day.strftime("%Y-%m-%d"))
    cves = []
    data= CVE.objects.values()
    for entry in data:
        if entry["date"] in days_list:
            cves.append(entry)
        try:
            if entry["cvss_score"] != "N/A" or entry["cvss_score"] != "n/a":
                entry["cvss_score"] = float(entry["cvss_score"])
            else:
                entry["cvss_score"] = 0.0
        except:
            entry["cvss_score"] = 0.0
    sorted_list = sorted(cves, key=lambda d: d['cvss_score'], reverse=True)
    for entry in sorted_list:
        if entry["cvss_score"] == 0.0: entry["cvss_score"] = "N/A"
    return sorted_list

def monthly_cve():
    current_month = str(datetime.date.today()).split("-")[1]
    cves = []
    data= CVE.objects.values()
    for entry in data:
        if str(entry["date"]).split("-")[1] == current_month:
            cves.append(entry)
        try:
            if entry["cvss_score"] != "N/A" or entry["cvss_score"] != "n/a":
                entry["cvss_score"] = float(entry["cvss_score"])
            else:
                entry["cvss_score"] = 0.0
        except:
            entry["cvss_score"] = 0.0
    sorted_list = sorted(cves, key=lambda d: d['cvss_score'], reverse=True)
    for entry in sorted_list:
        if entry["cvss_score"] == 0.0: entry["cvss_score"] = "N/A"
    return sorted_list


def single_cve(selected_cves):
    data = CVE.objects.values()
    cves = []
    for entry in data:
        if entry["cve_id"] in selected_cves:
            cves.append(entry)
        try:
            if entry["cvss_score"] != "N/A" or entry["cvss_score"] != "n/a":
                entry["cvss_score"] = float(entry["cvss_score"])
            else:
                entry["cvss_score"] = 0.0
        except:
            entry["cvss_score"] = 0.0
    sorted_list = sorted(cves, key=lambda d: d['cvss_score'], reverse=True)
    for entry in sorted_list:
        if entry["cvss_score"] == 0.0: entry["cvss_score"] = "N/A"
    return sorted_list


def daily_news():
    data = NewsArticles.objects.values()
    news = []
    today = datetime.date.today()
    yesterday = today - timedelta(days=1)
    for entry in data:
        if entry["date_added"] == today.strftime("%Y%m-%d") or entry["date_added"] == yesterday.strftime("%Y%m-%d"):
            if entry not in news:
                news.append(entry)
    return news

if __name__ == '__main__':
    main()
