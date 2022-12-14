from alerts.models import CVE
from email import encoders
from email.message import EmailMessage
from email.utils import formataddr
import smtplib
import base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ast import literal_eval
import requests
import os

def main(values):
    sender = "okcsirtalerts@gmail.com"
    auth = os.environ["EMAIL_AUTH_SECRET"]
    css = "body {font-family: Arial;} th { font-weight: bold; color: black; padding:10px; background-color: #3399ff;border-radius: 5px;} td { padding:10px;border-radius: 5px; } tr {background-color: #ebebeb;}"
    base_msg = """<h2>Varsling om sårbarhet</h2>
    <p>Hei<br><br>Du mottar denne meldingen fordi at det har blitt publisert nye sårbarheter i et eller flere systemer du forvalter.<br>
    Vedlagt i e-posten medfølger en tabell med informasjon om sårbarheten(e).<br><br>
    Om du ønsker assistanse, eller informasjon rundt sårbarheten(e) kontakt gjerne oss i CSIRT på: csirt@oslo.kommune.no</p> """
    html_section = '''<html><head><style>{}</style></head><body>{}<hr><br>

    {}<br><br>{}</body></html>'''.format(css, base_msg, str(values['description']), cve_table(values['CVES']))
    email_message = MIMEMultipart('alternative')
    email_message.attach(MIMEText(html_section, 'html'))
    email_message['From'] = formataddr(('OK CSIRT Alerts', sender))
    email_message['To'] = str(values['receiver'])
    email_message['Cc'] = str(values['cc'])
    email_message['Subject'] = "OK CSIRT: Varsling om sårbarhet"
    email_message.content_subtype = "html"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, base64.b64decode(auth).decode('utf-8'))
        smtp.send_message(email_message)
    print("[!] Email sent: {}".format(email_message['Subject']))


def cve_table(table):
    html = '<table>'
    html += "<thead><th>CVE</th><th>Dato publisert</th><th>Kritikalitet</th><th>Beskrivelse</th>"
    cvss_style = 'style="font-weight: bold; text-align: center;"'
    for cve in table:
        cve = literal_eval(cve)
        html += '<tr><td><a href="https://nvd.nist.gov/vuln/detail/{}">{}</td></a>'.format(cve["cve_url"],cve["cve_url"])
        html += "<td>{}</td>".format(cve["date"])
        html += '<td {}>{}</td>'.format(cvss_style, cve["cvss_score"])
        html += "<td>{}</td></tr>".format(cve["description"])
    html += "</table>"
    return html