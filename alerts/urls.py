from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.index, name='index'),
    path('cve_search_daily', views.cve_search_daily,name="cve_search_daily"),
    path('daily_cve', views.daily_cve,name="daily_cve"),
    path('yesterdays_cve', views.yesterdays_cve,name="yesterdays_cve"),
    path('weekly_cve', views.weekly_cve,name="weekly_cve"),
    path('monthly_cve', views.monthly_cve,name="monthly_cve"),
    path('send_alert', views.send_alert,name="send_alert"),
    path('send_alert_email', views.send_alert_email,name="send_alert_email"),
    path('new_cve_scraper', views.new_cve_scraper,name="new_cve_scraper"),
    path('top_news_articles', views.GoogleNewsScraper,name="top_news_articles"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico')))
]


