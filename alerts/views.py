from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
import os
from datetime import datetime
import scripts.scanner as cve_scanner
import scripts.get_cves as get_cves
import scripts.cve_twitterscraper as twtrscraper
from .forms import NameForm
from .models import CVEScans
import scripts.cve_finder as finder
import scripts.send_alert_email as alert_email


def index(request):
	found_cves = get_cves.daily_cve()
	found_news = get_cves.daily_news()
	scan_info = str(*CVEScans.objects.filter(scan_type="daily").values('scan_end').last().values())
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'Realtime CVE', 'Last_scan':scan_info, 'DailyNews':found_news}
	return render(request,'index.html', context)

def cve_search_daily(request):
	search = finder.daily()
	found_cves = get_cves.daily_cve()
	scan_info = str(*CVEScans.objects.filter(scan_type="daily").values('scan_end').last().values())
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'Realtime CVE', 'Last_scan':scan_info}
	return render(request,'index.html', context)

def daily_cve(request):
	found_cves = get_cves.daily_cve()
	found_news = get_cves.daily_news()
	scan_info = str(*CVEScans.objects.filter(scan_type="daily").values('scan_end').last().values())
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'Realtime CVE', 'Last_scan':scan_info, 'DailyNews':found_news}
	return render(request,'index.html', context)

def yesterdays_cve(request):
	found_cves = get_cves.yesterdays_cve()
	scan_info = str(*CVEScans.objects.filter(scan_type="daily").values('scan_end').last().values())
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'Gårsdagens CVE', 'Last_scan':scan_info}
	return render(request,'index.html', context)

def weekly_cve(request):
	found_cves = get_cves.weekly_cve()
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'CVE Siste 7 dager'}
	return render(request,'index.html', context)
	
def monthly_cve(request):
	found_cves = get_cves.monthly_cve()
	context = {'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'CVE denne måneden'}
	return render(request,'index.html', context)

def send_alert(request):
	if request.method == "POST":
		selected_cves = request.POST.getlist("send_alert")
	context = {'Selected_CVEs':get_cves.single_cve(selected_cves)}
	return render(request,'send_alert.html', context)

def send_alert_email(request):
	if request.method == "POST":
		table = request.POST.get("CVE_Table")
		receiver = request.POST.get("alert_receiver")
		cc = request.POST.get("alert_cc")
		alert_text = request.POST.get("alert_text")
		CVE = request.POST.getlist("CVEs")
		password = request.POST.get("alert_password") 
		if password == "5501":
			context = {'receiver':receiver, 'cc':cc, 'description':alert_text, 'CVES':CVE}
			alert_email.main(context)
			found_cves = get_cves.daily_cve()
			scan_info = str(*CVEScans.objects.filter(scan_type="daily").values('scan_end').last().values())
			context = {'message':'<b>Sucess</b>: E-mail sent to: {}'.format(receiver),'CVE_list':found_cves, 'CVE_Count':len(found_cves), 'Query':'Realtime CVE', 'Last_scan':scan_info}
			return render(request,'index.html', context)
		else:
			cves = eval(request.POST.get("cve_table"))
			context = {'message':'<b>Error:</b> Wrong passcode entered','Selected_CVEs':cves,'receiver':receiver, 'cc':cc, 'description':alert_text, 'CVES':CVE}
			return render(request,'send_alert.html', context)

def new_cve_scraper(request):
	scraper = twtrscraper.main()
	context = {'NewCVES':scraper}
	return render(request,'new_cve_scraper.html', context)

def GoogleNewsScraper(request):
	scraper = twtrscraper.news_scraper()
	context = {'NewsArticles':scraper}
	return render(request,'news_scraper.html', context)
