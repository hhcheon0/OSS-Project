from campus_notice_crawler.utils.db_connection import SessionLocal, Notice

db = SessionLocal()
try:
    notices = db.query(Notice).all()
    print(f"Total notices in DB: {len(notices)}")
    for n in notices[:3]:
        d = n.to_dict()
        print("--- Notice ---")
        print("ID:", d["notice_id"])
        print("Title:", d["title"])
        print("Summary Type:", type(d["summary"]), "Value:", d["summary"])
        print("KeyPoints Type:", type(d["keyPoints"]), "Value:", d["keyPoints"])
finally:
    db.close()
