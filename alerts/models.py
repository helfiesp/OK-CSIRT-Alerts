from django.db import models

# Create your models here.
class CVE(models.Model):
	cve_id = models.CharField(max_length=100)
	cve_url = models.CharField(max_length=200)
	date = models.CharField(max_length=100)
	source = models.CharField(max_length=100)
	cvss_score = models.CharField(max_length=100)
	affected_systems = models.TextField()
	potentially_impacted = models.TextField()
	recent_tweets = models.CharField(max_length=100)
	description = models.TextField()

class CVEScans(models.Model):
	scan_type = models.CharField(max_length=100)
	scan_start = models.CharField(max_length=100)
	scan_end = models.CharField(max_length=100)

class PageDescriptions(models.Model):
	page_name = models.CharField(max_length=100)
	page_description = models.TextField()

class NewsArticles(models.Model):
	article_title = models.TextField()
	article_date = models.CharField(max_length=100)
	article_description = models.TextField()
	article_source = models.CharField(max_length=100)
	date_added = models.CharField(max_length=100)
