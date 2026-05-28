"use client";

import React from "react";
import { Bookmark } from "lucide-react";
import NoticeCard from "./NoticeCard";
import { motion, AnimatePresence } from "framer-motion";

/* 
 * [OSS Upgrade] - BookmarkList 디자인 정돈
 * 개량 내용:
 * 1. 테마 포인트 컬러를 스카이블루에서 청록색(Teal)으로 변경.
 */

export default function BookmarkList({ 
  bookmarkedNotices = [], 
  onToggleBookmark, 
  onOpenDetail,
  subscribedKeywords = []
}) {
  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-5">
        <Bookmark size={18} className="text-teal-600 dark:text-teal-400" />
        <h2 className="text-base font-bold">북마크한 공지사항</h2>
        <span className="text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20 font-bold">
          {bookmarkedNotices.length}개
        </span>
      </div>

      {bookmarkedNotices.length === 0 ? (
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass p-10 text-center flex flex-col items-center justify-center border-dashed border-slate-200 dark:border-slate-800 bg-transparent"
        >
          <div className="w-10 h-10 rounded-full bg-teal-500/10 text-teal-500 flex items-center justify-center mb-3">
            <Bookmark size={20} />
          </div>
          <p className="text-sm font-bold text-foreground mb-1">보관된 공지가 없습니다</p>
          <p className="text-xs text-text-muted leading-relaxed max-w-xs">
            공지 목록에서 북마크 아이콘을 클릭하여 나중에 다시 볼 중요한 소식을 보관함에 담아보세요.
          </p>
        </motion.div>
      ) : (
        <div className="flex flex-col">
          <AnimatePresence mode="popLayout">
            {bookmarkedNotices.map((notice) => (
              <NoticeCard
                key={notice.id}
                notice={notice}
                isBookmarked={true}
                onToggleBookmark={onToggleBookmark}
                onOpenDetail={onOpenDetail}
                subscribedKeywords={subscribedKeywords}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
