import ast
import re
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup as bs, ResultSet
from datetime import datetime, timedelta
from datetime import date
import os
from collections import defaultdict
import sys
import argparse
from cvsslib import cvss2, cvss3, calculate_vector
import base64
from email.utils import formataddr
import smtplib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from alerts.models import CVE
from alerts.models import NewsArticles



class NewCveTracker:
    """
    It is possible to use the NIST API to get CVE information, which makes it easier than web scraping
    Notes about the program:
        The CVE_Config value downloads the affected software associated with the vulnerability.
        In some cases this field will be very large, so this field should be filtered by keyword in order to place an alert for a keyword found.
        For exmaple, keyword "Windows", the software config is checked if windows is in it.
    """

    def __init__(self):
        self.result_check = 0
        self.api_data = 0
        self.skip_data = 0

    def main(self):
        self.last_week_cve("pub")

    def full_cve_scan(self, weekcheck=None):
        print("[!] Running scan for new and modified CVEs")
        self.full_html_files = []
        if self.user_input["daily"]:
            self.daily_cve("pub")
            if not weekcheck:
                self.daily_cve("mod")
        if self.user_input["weekly"]:
            self.last_week_cve("pub")
            if not weekcheck:
                self.last_week_cve("mod")

    def last_week_cve(self, parameter):
        """
        This function fetches all of the CVEs from the previous week.
        """
        self.current_parameter = parameter
        self.current_scan_type = "Weekly"
        days_list = []
        for x in range(7):
            day = date.today() - timedelta(days=x + 1)
            days_list.append(day.strftime("%Y-%m-%d"))
        print("[!] Gathering the CVEs between: {} and {}".format(days_list[-1], days_list[0]))
        self.date_range_search(parameter, days_list[-1], days_list[0])

    def daily_cve(self, parameter):
        """
        This function fetches all of the CVEs that was added to NVD for the previous calendar day.
        """
        print("[*] Running daily CVE scan with parameter: {}".format(parameter))
        self.current_scan_type = "Daily"
        self.current_parameter = parameter
        yesterday = datetime.strftime(datetime.today() - timedelta(1), "%Y-%m-%d")
        today = datetime.strftime(datetime.today(), "%Y-%m-%d")
        self.date_range_search(parameter, yesterday, today, userinput=yesterday)


    def cve_search_single(self, cve):
        """
        Finds all of the data connected to a single CVE.
        Usage: self.cve_search_single("CVE-2021-44228")
        """
        self.current_scan_type = "Single"
        cve = "CVE-{}".format(cve)
        url = "https://services.nvd.nist.gov/rest/json/cve/1.0/"
        cve_data = requests.get('{}{}'.format(url, cve)).json()["result"]["CVE_Items"]
        self.cve_data_handler(cve_data, userinput=cve)

    def date_range_search(self, type=None, date1=None, date2=None, base_url=None, userinput=None):
        """
        Retrieves all of the CVEs within a specific date window.
        Parameter1 is specified to be either mod or pub, referencing modified or published.
        The NVD API only fetches 20 results at a time, so a while statement was made to ensure all data was obtained.
        """
        if not base_url:
            base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0/?{}StartDate={}T00:00:00.000-05:00&{}EndDate={}T23:59:59.999-05:00".format(type, date1, type, date2)
        result = requests.get(base_url).json()
        result_amount = result["totalResults"]
        results_per_page = result["resultsPerPage"]
        cve_data = result["vulnerabilities"]
        check = self.cve_page_processor(result_amount, results_per_page, base_url, cve_data)
        user_input = [userinput, type]
        if check:
            self.cve_data_handler(result, user_input)
        else:
            self.cve_data_handler(cve_data, user_input)

    def cve_page_processor(self, result_amount, results_per_page, base_url, cve_data):
        time.sleep(2)
        while result_amount != results_per_page:
            print("[!] Adding all CVEs to list: {} of {}...".format(results_per_page, result_amount), end='\r')
            url = "{}&startIndex={}".format(base_url, results_per_page)
            results_per_page += requests.get(url).json()["resultsPerPage"]
            result = []
            cve_data.extend(requests.get(url).json()["result"]["CVE_Items"])
            for entry in cve_data:
                if entry not in result:
                    result.append(entry)
            time.sleep(40)

    def cve_data_handler(self, cve_data, userinput=None):
        """
        This function is the main data handler for the CVE data.
        The method is used by all CVE request functions, and calls the HTML creator functions.
        """
        cve_data_dict = {}
        all_data = []
        found_changes = ""
        print("[!] CVE checker started...")
        print("[!] Checking {} CVEs...\n".format(len(cve_data)))
        for cve in cve_data:
            cve = cve["cve"]
            if not CVE.objects.filter(cve_id=cve["id"]).exists():
                if cve["vulnStatus"] != "Rejected":
                    try:
                        cve_config = cve["configurations"]
                    except:
                        cve_config = "n/a"
                    cve_mod_date = cve["lastModified"].split("T")[0]
                    cve_pub_date = cve["published"].split("T")[0]
                    cve_url = cve["id"]
                    print("[*] Checking CVE: {}...".format(cve_url), end="\r")
                    cve_source = cve["sourceIdentifier"]
                    cve_description = cve["descriptions"][0]["value"]
                    try:
                        cvss_scores = cve["metrics"]["cvssMetricV31"]
                        cvss_score = ""
                        for score in cvss_scores:
                            if score["source"] == "nvd@nist.gov":
                                cvss_score = score["cvssData"]["baseScore"]
                            else:
                                cvss_score_alt = score["cvssData"]["baseScore"]
                        if len(str(cvss_score)) == 0:
                            cvss_score = cvss_score_alt
                    except:
                        cvss_score = "N/A"
                    cve_data_dict["CVE"] = cve_url
                    cve_data_dict["Date added"] = cve_pub_date
                    check_impact = self.check_impact(cve_description)
                    tweet_count = self.TwitterScraper(cve["id"])
                    if "mod" in userinput:
                        if found_changes == "No changes found." or len(found_changes) <= 1:
                            continue
                        cve_data_dict["Date modified"] = cve_mod_date
                        cve_data_dict["Source"] = cve_source
                        cve_data_dict["CVSS score"] = cvss_score
                        cve_data_dict["Potentially impacted"] = check_impact
                        cve_data_dict["Changes"] = found_changes
                        cve_data_dict["CVE Description"] = cve_description
                    else:
                        cve_data_dict["Source"] = cve_source
                        cve_data_dict["CVSS score"] = cvss_score
                        cve_data_dict["Potentially impacted"] = check_impact
                        cve_data_dict["CVE Description"] = cve_description
                        insert_data = CVE(cve_id=cve["id"], cve_url=cve_url, date=cve_pub_date, source=cve_source, cvss_score=cvss_score, potentially_impacted=check_impact, recent_tweets=tweet_count, description=cve_description)
                        insert_data.save()
            else:
                cve_info = CVE.objects.filter(cve_id=cve["id"]).values()[0]
                cve_id = cve_info["cve_id"]
                tweetCount = self.TwitterScraper(cve_id)
                if cve_info["recent_tweets"] == "0":
                    CVE.objects.filter(cve_id=cve["id"]).update(recent_tweets=tweetCount)
                elif tweetCount != cve_info["recent_tweets"]:
                    CVE.objects.filter(cve_id=cve["id"]).update(recent_tweets=tweetCount)



    def TwitterScraper(self, cve):
        base_query = "https://api.twitter.com/2/tweets/counts/recent?query={}".format(cve)
        header = {"Authorization": os.environ["TWITTER_API_SECRET"]}
        tweetData = requests.get(base_query, headers=header).json()
        time.sleep(0.5)
        try:
            tweetCount = tweetData["meta"]["total_tweet_count"]
        except:
            tweetCount = 0
        return tweetCount

    def check_impact(self, description, configurations=None):
        """
        This function is used to check the CVE up against specific keywords.
        The result will be a True or False statement if potentially impacted
        NLTK data is in /var/www/ntlk_data
        """
        blacklist = ['ome']
        if not self.api_data and not self.skip_data:
            self.KartoteketAPI()
            if not self.api_data:
                self.skip_data = 1
        known_keywords = requests.get(
            'https://raw.githubusercontent.com/helfiesp/helfie-rep/master/CSIRT/cve_scanner/cve_tracker_keywords.txt',
            auth=('helfiesp', os.environ["CVE_KEYWORD_GHUB_SECRET"])).text.split(",")
        found_keywords = []

        def append_keyword(keyword):
            if not self.skip_data:
                for system in self.api_data:
                    name = system[0].split("(")[0].strip()
                    if name.lower() == keyword.lower() and name.lower() not in blacklist:
                        found_keywords.append("<b>{}:</b> {}".format(name, system[3]))
                        return
            else:
                found_keywords.append(keyword)

        def check_keyword(input):
            text_tokens = word_tokenize(input)
            filtered = " ".join([word for word in text_tokens if not word in stopwords.words()])
            input = " ".join(nltk.RegexpTokenizer(r"\w+").tokenize(filtered))
            for keyword in known_keywords:
                keyword = keyword.strip()
                if keyword.lower() in input.lower():
                    if ' ' in keyword:
                        append_keyword(keyword)
                        continue
                    elif keyword.lower() in input.lower().split():
                        append_keyword(keyword)
                        continue
                    else:
                        if keyword.lower() in input.lower().replace("(", "").replace(")", "").split():
                            append_keyword("{}".format(keyword))
                            continue

        check_keyword(description)
        if configurations:
            for entry in configurations:
                check_keyword(entry)
        found_keywords = ", ".join(self.clear_duplicates(found_keywords))
        return found_keywords

    def defined_search(self, parameter, value):
        """
        Retrieves a collection CVEs with own parameter and values
        Example: self.defined_search("keyword", "log4j")
        """
        self.current_scan_type = "Keyword"
        url = "https://services.nvd.nist.gov/rest/json/cves/1.0?{}={}".format(parameter, value)
        result = requests.get(url).json()
        cve_data = result["result"]["CVE_Items"]
        userinput = "{}_{}".format(parameter, value)
        check = self.cve_page_processor(result["totalResults"], result["resultsPerPage"], url, cve_data)
        if check:
            self.cve_data_handler(result, userinput)
        else:
            self.cve_data_handler(cve_data, userinput)

    def html_sorter(self, data, base_html):
        """
        This function takes the raw CVE data and sorts it by CVSS score.
        In the future this might also include other areas of sorting, for example sorted by if a keyword is present.
        """
        print("[!] Sorting HTML code...")
        sorted_list = sorted(data, key=lambda d: float(d['SCORE']), reverse=True)
        for entry in sorted_list:
            if entry["SCORE"] == 0: entry["SCORE"] = "n/a".upper()
        for entry in sorted_list: base_html += entry["HTML"]
        return base_html

    def cve_statistics(self, data):
        print("[!] Writing CVE statistics...")
        statistics = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "unassigned": 0}
        for cve in data:
            score = cve["CVSS score"]
            statistics["total"] += 1
            if score == "n/a".upper():
                statistics["unassigned"] += 1
            elif float(score) >= 9:
                statistics["critical"] += 1
            elif float(score) >= float(7.5) <= 8.9:
                statistics["high"] += 1
            elif float(score) >= 5 <= 7.4:
                statistics["medium"] += 1
            elif float(score) <= float(4.9):
                statistics["low"] += 1
        return statistics

    def check_dates(self, cve_data):
        result = True
        valuelist = [cve_dict["Date added"] for cve_dict in cve_data]
        first_element = valuelist[0]
        for entry in valuelist:
            if entry != first_element:
                result = False
                break
            else:
                result = True
        if result:
            for entry in cve_data:
                del entry["Date added"]
        return cve_data

    def check_cvss_score(self, url, changes=None):
        """
        The NVD API does not return a CVSS score if it has not been assigned by NVD itself.
        New vulnerabilities will not have a CVSS score assigned by NVD, but often by a third party.
        This function uses web scraping to fetch that CVSS score, and the source it comes from.
        """
        time.sleep(0.2)
        soup = bs(requests.get("https://nvd.nist.gov/vuln/detail/{}".format(url)).content, "lxml")
        sources = soup.find_all("span", {'class': 'wrapData'})
        cvss_scores = soup.find_all("span", {'class': 'severityDetail'})
        source = sources[0].text
        cvss_score = cvss_scores[0].text.split()[0]
        if cvss_score == "N/A" and len(sources) > 1:
            if cvss_scores[1].text.split()[1] != "N/A":
                source = sources[1].text
                cvss_score = cvss_scores[1].text.split()[0]
        if changes:
            return cvss_score, source, self.fetch_cve_changes(url)
        else:
            return cvss_score, source

    def calculate_cvss_score(self, string):
        if len(string) > 30:
            result = calculate_vector(string, cvss3)[0]
        else:
            result = calculate_vector(string, cvss2)[0]
        return result

    def write_to_file(self, file, text, type):
        """
        The function takes a file parameter(file.txt) and a text value to write to a file.
        The function can also choose to overwrite or append(w, a)
        """
        f = open("{}".format(file), "{}".format(type))
        f.write(text)
        print("[!] Contents have been written to file: {}".format(file))
        f.close()

    def combine_lists_of_dict(self, list_of_dicts):
        """
        This function combines a list of dictonaries where the key is similar.
        """
        dd = defaultdict(list)
        for d in list_of_dicts:
            for key, value in d.items():
                dd[key].append(value)
        return dd

    def get_affected_systems(self, cve_config):
        systems = []
        total_systems = []
        for entry in cve_config:
            for item in entry["cpe_match"]:
                if item["vulnerable"]:
                    values = list(filter(None, ast.literal_eval(
                        str(item["cpe23Uri"].split(":")).replace("-", "").replace("*", ""))))
                    try:
                        affected_systems = {values[3]: [values[4], values[5]]}
                    except:
                        affected_systems = {values[3]: [values[4]]}
                    total_systems.append(values[4])
                    systems.append(affected_systems)
        affected_systems = self.combine_lists_of_dict(systems)
        cve_affected_systems = ""
        suppliers = []
        for key, value in affected_systems.items():
            if any(isinstance(el, list) for el in value):
                value = [item for sublist in value for item in sublist]
            values = ", ".join(str(v) for v in value)
            cve_affected_systems += "<b>{}:</b> {} ".format(key.capitalize(), values)
            suppliers.append(key.capitalize())
        return cve_affected_systems, suppliers, self.clear_duplicates(total_systems)

    def fetch_cve_changes(self, url):
        print("[!] Checking changes...".format(url), end="\r")
        response = requests.get("https://nvd.nist.gov/vuln/detail/{}#VulnChangeHistorySection".format(url))
        html = response.content
        soup = bs(html, "lxml")
        time.sleep(0.5)
        data = []
        base_class = soup.find('div', attrs={'class': 'vuln-change-history-container'})
        try:
            table = base_class.find('table',
                                    attrs={'class': 'table table-striped table-condensed table-bordered detail-table'})
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                data.append([ele for ele in [ele.text.strip() for ele in row.find_all('td')] if ele])
            return self.filter_cve_changes_data(data)
        except:
            return "No changes found."

    def filter_cve_changes_data(self, data):
        """
        This function is responsible for sorting the changes made to CVE.
        The function is long and is poorly created, but it was a hassle to sort the data properly.
        Blakclisteds configrations are not added, they can be added by adding an else statement and:
        filtered_data.append([changes[0], changes[1]]) in the for loop.
        """
        filtered_data = []
        accepted_types = ['Added', 'Changed']
        accepted_configurations = ['CVSS V3.1', 'CVSS V2', 'CPE Configuration']
        for changes in data:
            if changes[0] in accepted_types and changes[1] in accepted_configurations:
                for entry in changes:
                    working_list = []
                    if "*cpe" in entry:
                        if self.user_input["mod_data"]:
                            sections = entry.replace("*", "").replace("-", "").split("\n")
                            for section in sections:
                                section = section.split(":")
                                if len(section) > 1:
                                    section = [i for i in section[3:] if i]
                                    working_list.append(section)
                        else:
                            working_list.append("Affected systems")
                    if "NIST" in entry:
                        cvss_score = entry.split()[1].replace("(", "").replace(")", "")
                        working_list.append(self.calculate_cvss_score(cvss_score))
                    else:
                        if "*" not in entry:
                            working_list.append(entry)
                    filtered_data.append(working_list)
        new_list = []
        for entry in filtered_data:
            for x in entry:
                if isinstance(x, list):
                    for y in x:
                        if y not in new_list:
                            new_list.append(y)
                else:
                    if x not in new_list:
                        new_list.append(x)
        for entry in new_list:
            if entry in accepted_types:
                if entry == accepted_types[0]:
                    new_list[new_list.index(entry)] = '<b style="color: Green"> {} </b><br>'.format(entry)
                else:
                    new_list[new_list.index(entry)] = '<b style="color: Orange"> {} </b><br>'.format(entry)
            if entry in accepted_configurations:
                new_list[new_list.index(entry)] = '<b>{}: </b>'.format(entry)
        final_str = ' '.join([str(elem) for elem in new_list])
        return final_str

    def clear_duplicates(self, input_list):
        """
        The function is used to remove duplicates from a list.
        """
        seen = set()
        unique = []
        for x in input_list:
            if x not in seen:
                unique.append(x)
                seen.add(x)
        return unique

    def KartoteketAPI(self):
        try:
            print("[!] Gathering Kartoteket API information...")
            key = {"key": "001D4233A0265736B41D95E850103C5B1D9E159A19526883DDF3FFB799BCB9F6"}
            result = requests.get('https://kartoteket.oslo.kommune.no/cmdb/csirt_api/', headers=key).json()
            api_data = []
            for system in result:
                api_data.append([system["systemnavn"], system["id"], system["systemeier"], system["systemforvalter"]])
            self.api_data = api_data
        except:
            print("[ERROR] Could not fetch Kartoteket API information...")

class NewsScanner:

    def main(self):
        global total
        total = []
        print("[!] News scanner init...")
        sites = [self.CISA().main(), self.NorCERT().main()]
        print(total)
        return total

    def CurrentDates(self):
        self.current_day = int(datetime.now().strftime('%d')) - 1
        self.current_month = datetime.now().strftime('%B')
        self.current_year = int(datetime.now().strftime('%Y'))
        return self.current_day, self.current_month, self.current_year

    def DictionaryBuilder(self, source, date, title, url, description):
        todays_date = datetime.strftime(datetime.today(), "%Y%m-%d")
        working_dict = {}
        working_dict["Source"] = source
        working_dict["Date"] = " ".join(date)
        working_dict["Title"] = '<a href="{}">{}</a>'.format(url, title)
        working_dict["Description"] = description
        if not NewsArticles.objects.filter(article_title=working_dict["Title"]).exists():
            insert_data = NewsArticles(article_title=working_dict["Title"], article_date=working_dict["Date"], article_description=working_dict["Description"], article_source=working_dict["Source"], date_added=todays_date)
            insert_data.save()
        total.append(working_dict.copy())

    class CISA:
        def main(self):
            self.cisa_alerts_url = "https://www.cisa.gov/uscert/ncas/alerts"
            self.cisa_curract_url = "https://www.cisa.gov/uscert/ncas/current-activity"
            self.cisa_vuln_summary = "https://www.cisa.gov/uscert/ncas/bulletins"
            alerts = self.alert_data_finder()
            current_activity = self.ca_locator()

        def alert_post_locator(self):
            url = self.cisa_alerts_url
            post_dictionary = {"id": [], "url": [], "title": []}
            soup = bs(requests.get(url).content, "lxml")
            raw_posts = str(soup.find_all('span', {'class': 'field-content'})).split('<span class="field-content">')
            for post in raw_posts:
                if "href" in post:
                    post_id = post.split(" ")[0]
                    post_dictionary["id"].append(post_id)
                    post_dictionary["url"].append(str("{}/{}".format(url, post_id)))
                    post_dictionary["title"].append(post.split('">')[1].split("</a>")[0])
            return post_dictionary

        def alert_data_finder(self):
            data = self.alert_post_locator()
            print("[*] Searching for CISA Alerts...")
            for url in data["url"]:
                time.sleep(1.5)
                soup = bs(requests.get(url).content, "lxml")
                raw_date_info = soup.find('div', {'class': 'submitted meta-text'}).text.strip().split(" | ")
                date_info = raw_date_info[0].split(":")[1].strip().split(",")
                day = int(date_info[0].split()[1])
                month = date_info[0].split()[0]
                current_date_info = NewsScanner().CurrentDates()
                if month != current_date_info[1]:
                    break
                if month == current_date_info[1] and int(date_info[1].strip()) == int(current_date_info[2]):
                    if day == int(current_date_info[0]):
                        source = "<b>CISA</b>: Alerts"
                        NewsScanner().DictionaryBuilder(source, date_info, soup.find('h2', {'id': 'page-sub-title'}).text.strip(), url, "N/A")

        def ca_locator(self):
            print("[*] Searching for CISA Current Activity...")
            url = "https://www.cisa.gov/uscert/ncas/current-activity"
            soup = bs(requests.get(url).content, "lxml")
            raw_posts = soup.find_all('div', {'class': 'views-row'})
            for x in raw_posts:
                time.sleep(1.5)
                description = x.find('div', {'class': 'field-content'}).text.strip()
                date_info = x.find('div', {'class': 'entry-date'}).text.strip().split(":")[1].split(",")
                day = int(date_info[1].split()[1])
                month = date_info[1].split()[0]
                current_dates = NewsScanner().CurrentDates()
                if month != current_dates[1]:
                    break
                year = int(date_info[2].strip())
                title = x.find('a', href=True)
                post_title = title.text
                post_url = "https://www.cisa.gov/uscert/{}".format(title['href'])
                if month == current_dates[1] and year == int(current_dates[2]):
                    if day == int(current_dates[0]):
                        source = "<b>CISA</b>: Current Activity"
                        NewsScanner().DictionaryBuilder(source, date_info, post_title, post_url, description)

    class NorCERT:
        def main(self):
            self.nor_month = ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September',
                              'Oktober', 'November', 'Desember']
            self.dates = [int(datetime.now().strftime('%d')) - 1, int(datetime.now().strftime('%m')),
                          int(datetime.now().strftime('%Y'))]
            self.norcert_alerts_url = "https://nsm.no/fagomrader/digital-sikkerhet/nasjonalt-cybersikkerhetssenter/varsler-fra-ncsc/"
            self.norcert_news_url = "https://nsm.no/fagomrader/digital-sikkerhet/nasjonalt-cybersikkerhetssenter/nyheter-fra-ncsc/"

        def NorCERTAlerts(self):
            print("[*] Searching for NorCERT Alerts")
            time.sleep(1.5)
            soup = bs(requests.get(self.norcert_alerts_url).content, "lxml")
            raw_date_info = soup.find('ul', {'class': 'd-flex articles list-unstyled row'})
            title = raw_date_info.find_all('a', href=True)
            for entry in title:
                date = entry.find('div', {'class', 'articlelist__meta'}).text.strip().split()
                try:
                    description = entry.find('div', {'class', 'digest'}).text
                except:
                    description = "N/A"
                if date[1].capitalize() == self.nor_month[self.dates[1] - 1] and int(date[2]) == self.dates[2]:
                    if int(date[0]) == self.dates[0]:
                        source = "<b>NORCERT</b>: Varsler"
                        title = entry.find('h3', {'property': 'headline'}).text
                        NewsScanner().DictionaryBuilder(source, date, title, entry['href'], description)