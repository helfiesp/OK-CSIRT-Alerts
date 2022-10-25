from schedule import Scheduler
import threading
import time
from scripts import scanner
from datetime import datetime
from .models import CVEScans


def start_scheduler():
    scheduler = Scheduler()
    print("Starting scheduler")
    #scheduler.every().hour.do(ScheduledTask)
    scheduler.every().day.at("03:00").do(ScheduledTask)
    scheduler.every().day.at("06:00").do(ScheduledTask)
    scheduler.every().day.at("09:00").do(ScheduledTask)
    scheduler.every().day.at("12:00").do(ScheduledTask)
    scheduler.every().day.at("15:00").do(ScheduledTask)
    scheduler.every().day.at("18:00").do(ScheduledTask)
    scheduler.every().day.at("21:00").do(ScheduledTask)
    scheduler.every().day.at("00:00").do(ScheduledTask)
    scheduler.run_continuously()

def ScheduledTask():
    start_time = datetime.now().strftime("%H:%M:%S")
    scanner.NewCveTracker().daily_cve("pub")
    scanner.NewsScanner().main()
    end_time = datetime.now().strftime("%H:%M:%S")
    scan_type = "daily"
    insert_data = CVEScans(scan_type=scan_type, scan_start=start_time, scan_end=end_time)
    insert_data.save()
    print("[{}] CVE Scan completed".format(end_time))

def run_continuously(self, interval=1):

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run

Scheduler.run_continuously = run_continuously