import os
import sys
import time
import subprocess
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

# .env 로드
load_dotenv()

def run_crawler():
    """Scrapy 크롤러를 별도 프로세스로 안전하게 실행"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Daegu University Notice Crawler...")
    try:
        # Reactor 충돌 및 메모리 누수 방지를 위해 subprocess.run 활용
        result = subprocess.run(
            ["scrapy", "crawl", "daegu_notice"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Crawler finished successfully.")
        # 간략한 수집 결과 파싱하여 출력
        lines = result.stderr.split('\n')
        saved_count = 0
        dropped_count = 0
        for line in lines:
            if "DatabasePipeline: Successfully saved notice" in line:
                saved_count += 1
            elif "DuplicateFilterPipeline: Dropped duplicate" in line:
                dropped_count += 1
        print(f" -> Saved (Upserted) notices: {saved_count}")
        print(f" -> Dropped duplicate notices: {dropped_count}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during crawling process: {e}")
        print(f"Subprocess output (stderr): {e.stderr}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    interval_minutes = int(os.getenv("CRAWL_INTERVAL_MINUTES", "60"))
    print("=" * 60)
    print("      Campus Notice AI Crawler - Background Scheduler")
    print(f"  - System Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - Crawl Interval: Every {interval_minutes} minutes")
    print("=" * 60)

    # 즉시 1회 구동
    run_crawler()

    # APScheduler 등록
    scheduler = BlockingScheduler()
    scheduler.add_job(run_crawler, 'interval', minutes=interval_minutes)

    try:
        print("\nScheduler is now running. Press Ctrl+C to exit.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped by user request.")
