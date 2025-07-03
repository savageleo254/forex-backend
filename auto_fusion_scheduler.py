import schedule
import time
from trading_bot import main as trading_main

def job():
    trading_main()

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)