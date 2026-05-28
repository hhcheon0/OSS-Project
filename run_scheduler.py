import os
import sys
import time
import subprocess
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from campus_notice_crawler.utils.env_loader import load_project_env

# 프로젝트 루트 `.env`만 명시적으로 로드
load_project_env()
PROJECT_ROOT = Path(__file__).resolve().parent

def run_crawler():
    """Scrapy 크롤러를 별도 프로세스로 안전하게 실행"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Daegu University Notice Crawler...")
    try:
        # stdout/stderr를 그대로 출력해 진행 상황을 즉시 확인하고 버퍼 블로킹을 피합니다.
        subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", "daegu_notice"],
            cwd=str(PROJECT_ROOT),
            check=True
        )
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Crawler finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during crawling process: {e}")
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
