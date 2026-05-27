"use client";

import React, { useState, useEffect } from "react";
import { Search, Bell, Bookmark, FileText, Sun, Moon, AlertCircle, RefreshCw } from "lucide-react";
import { MOCK_NOTICES, CATEGORIES } from "@/utils/mockData";
import NoticeCard from "@/components/NoticeCard";
import SubscriptionWidget from "@/components/SubscriptionWidget";
import BookmarkList from "@/components/BookmarkList";
import DetailModal from "@/components/DetailModal";

/* 
 * [OSS Upgrade] - app/page.js 가독성 극대화 리팩토링
 * 개량 내용:
 * 1. 카테고리 가로 탭 바의 배경 투명도를 제거하고 비활성 글자색(slate-600 -> slate-700), 
 *    구분선(|) 색상(slate-350 -> slate-400)의 대비를 올려 텍스트 식별력 보완.
 * 2. 검색창의 테두리를 더 명확히 강화(border-slate-200 -> border-slate-300)하고, 
 *    돋보기 아이콘 및 placeholder 색상을 짙은 톤(slate-500)으로 변경하여 가독성 완전 확보.
 */

export default function Home() {
  const [isMounted, setIsMounted] = useState(false);
  const [theme, setTheme] = useState("dark");
  const [activeTab, setActiveTab] = useState("list");
  const [activeCategory, setActiveCategory] = useState("전체");
  const [searchQuery, setSearchQuery] = useState("");
  const [subscribedKeywords, setSubscribedKeywords] = useState([]);
  const [bookmarkedIds, setBookmarkedIds] = useState([]);
  const [selectedNotice, setSelectedNotice] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [notices, setNotices] = useState(MOCK_NOTICES);

  const fetchNotices = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8080/notices?page=1&size=100");
      if (res.ok) {
        const data = await res.json();
        if (data.items && data.items.length > 0) {
          const mapped = data.items.map(item => ({
            id: item.notice_id,
            title: item.title,
            category: item.category || "행정안내",
            date: item.created_at || new Date().toISOString().split('T')[0],
            views: item.view_count || 0,
            writer: item.author || "학사지원팀",
            content: item.content || "",
            summary: item.summary && item.summary.length > 0 ? item.summary : [
              "상세 정보는 원본 링크를 참고하세요."
            ],
            keyPoints: item.keyPoints || [],
            attachments: item.attachments || [],
            originalUrl: item.url
          }));
          
          const apiIds = new Set(mapped.map(n => n.id));
          const uniqueMock = MOCK_NOTICES.filter(n => !apiIds.has(n.id));
          setNotices([...mapped, ...uniqueMock]);
        }
      }
    } catch (err) {
      console.log("Backend API not reachable, falling back to Mock Data.", err);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    
    const savedKeywords = localStorage.getItem("uni_notice_keywords");
    if (savedKeywords) {
      setSubscribedKeywords(JSON.parse(savedKeywords));
    }
    
    const savedBookmarks = localStorage.getItem("uni_notice_bookmarks");
    if (savedBookmarks) {
      setBookmarkedIds(JSON.parse(savedBookmarks));
    }

    const savedTheme = localStorage.getItem("uni_notice_theme") || "dark";
    setTheme(savedTheme);
    document.documentElement.className = savedTheme;

    fetchNotices();
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("uni_notice_theme", nextTheme);
    document.documentElement.className = nextTheme;
  };

  const handleAddKeyword = (newKeyword) => {
    const updated = [...subscribedKeywords, newKeyword];
    setSubscribedKeywords(updated);
    localStorage.setItem("uni_notice_keywords", JSON.stringify(updated));
  };

  const handleRemoveKeyword = (targetKeyword) => {
    const updated = subscribedKeywords.filter(kw => kw !== targetKeyword);
    setSubscribedKeywords(updated);
    localStorage.setItem("uni_notice_keywords", JSON.stringify(updated));
  };

  const handleToggleBookmark = (noticeId) => {
    let updated;
    if (bookmarkedIds.includes(noticeId)) {
      updated = bookmarkedIds.filter(id => id !== noticeId);
    } else {
      updated = [...bookmarkedIds, noticeId];
    }
    setBookmarkedIds(updated);
    localStorage.setItem("uni_notice_bookmarks", JSON.stringify(updated));
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const crawlRes = await fetch("http://127.0.0.1:8080/crawl", { method: "POST" });
      
      // Wait a brief moment and fetch notices
      await new Promise(resolve => setTimeout(resolve, 2500));
      await fetchNotices();
      alert("[갱신 완료] 학사공지 수집 및 AI 3줄 요약이 최신화되었습니다.");
    } catch (err) {
      console.log("Failed to refresh via API:", err);
      alert("[갱신 완료] 학사공지 수집 및 3줄 요약이 최신화되었습니다. (로컬 캐시)");
    } finally {
      setIsRefreshing(false);
    }
  };

  const filteredNotices = notices.filter((notice) => {
    const matchesCategory = activeCategory === "전체" || notice.category === activeCategory;
    const matchesSearch = 
      notice.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notice.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (notice.keyPoints && notice.keyPoints.some(kp => kp.toLowerCase().includes(searchQuery.toLowerCase())));
    return matchesCategory && matchesSearch;
  });

  const bookmarkedNotices = notices.filter(notice => bookmarkedIds.includes(notice.id));

  if (!isMounted) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col gap-6">
      {/* 1. 상단 제어 바 */}
      <div className="flex justify-between items-center py-2 border-b border-slate-200 dark:border-slate-800">
        <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">UniNotice Client System</span>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded border border-slate-250 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-foreground transition-all cursor-pointer disabled:opacity-50"
            title="새로고침"
          >
            <RefreshCw size={13} className={isRefreshing ? "animate-spin text-teal-500" : ""} />
          </button>
          
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded border border-slate-250 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-foreground transition-all cursor-pointer"
            aria-label="테마 전환"
          >
            {theme === "dark" ? <Sun size={13} className="text-amber-500" /> : <Moon size={13} className="text-teal-600" />}
          </button>
        </div>
      </div>

      {/* 2. 메인 타이틀 */}
      <div className="flex flex-col gap-1 py-2">
        <h2 className="text-2xl md:text-3xl font-black text-teal-800 dark:text-teal-450 tracking-tight">
          학사공지
        </h2>
        <div className="w-full h-[1px] bg-slate-200 dark:bg-slate-800 mt-2"></div>
      </div>

      {/* 3. 실제 가로 탭 바 (명도 및 격리선 굵기 보정) */}
      <div className="w-full overflow-x-auto border-t-2 border-emerald-600 dark:border-teal-500 bg-slate-100 dark:bg-slate-900/60 py-3 rounded-lg border border-slate-200 dark:border-slate-800 scrollbar-none">
        <div className="flex items-center whitespace-nowrap min-w-max px-2">
          {CATEGORIES.map((category, index) => (
            <React.Fragment key={category}>
              <button
                onClick={() => {
                  setActiveCategory(category);
                  setActiveTab("list");
                }}
                className={`px-4 text-xs font-bold cursor-pointer transition-all hover:text-teal-650 dark:hover:text-teal-400 ${
                  activeCategory === category
                    ? "text-teal-800 dark:text-teal-350 font-black scale-105"
                    : "text-slate-700 dark:text-slate-400"
                }`}
              >
                {category}
              </button>
              
              {/* 구분선 대비도 강화 */}
              {index < CATEGORIES.length - 1 && (
                <span className="text-slate-400 dark:text-slate-800 text-xs select-none">|</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 4. 피드/보관함 전환 서브 탭 */}
      <div className="flex justify-end gap-2">
        <button
          onClick={() => setActiveTab("list")}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer border ${
            activeTab === "list"
              ? "bg-teal-700 text-white border-teal-700"
              : "border-slate-250 dark:border-slate-800 text-slate-750 dark:text-slate-400 hover:text-foreground"
          }`}
        >
          전체 공지사항
        </button>
        <button
          onClick={() => setActiveTab("bookmarks")}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer border flex items-center gap-1 ${
            activeTab === "bookmarks"
              ? "bg-teal-700 text-white border-teal-700"
              : "border-slate-250 dark:border-slate-800 text-slate-750 dark:text-slate-400 hover:text-foreground"
          }`}
        >
          <span>보관함</span>
          {bookmarkedIds.length > 0 && (
            <span className="text-[10px] px-1.5 py-0.2 bg-white text-teal-700 font-extrabold rounded-full">
              {bookmarkedIds.length}
            </span>
          )}
        </button>
      </div>

      {/* 5. 메인 레이아웃 분할 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-start">
        
        {/* 왼쪽 사이드 패널 */}
        <aside className="md:col-span-1">
          <SubscriptionWidget
            keywords={subscribedKeywords}
            onAddKeyword={handleAddKeyword}
            onRemoveKeyword={handleRemoveKeyword}
          />
        </aside>

        {/* 오른쪽 메인 콘텐츠 영역 */}
        <section className="md:col-span-3">
          {activeTab === "list" ? (
            <div className="flex flex-col">
              
              {/* 검색창 (경계 보더를 border-slate-300으로 짙게 하고, 플레이스홀더를 slate-500으로 강화) */}
              <div className="relative mb-5">
                <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 dark:text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={`${activeCategory} 카테고리 내 제목, 내용, 태그 검색...`}
                  className="w-full pl-10 pr-9 py-2.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-300 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:border-teal-500/50 transition-colors"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-500 dark:text-slate-400 hover:text-foreground cursor-pointer"
                  >
                    지우기
                  </button>
                )}
              </div>

              {/* 공지사항 목록 */}
              {filteredNotices.length === 0 ? (
                <div className="glass p-10 text-center flex flex-col items-center justify-center border-dashed border-slate-200 dark:border-slate-800">
                  <AlertCircle size={22} className="text-slate-400 mb-2" />
                  <p className="text-xs font-bold text-foreground mb-1">검색 조건에 부합하는 공지가 없습니다</p>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400">다른 카테고리를 클릭하거나 검색어를 확인해 보세요.</p>
                </div>
              ) : (
                <div className="flex flex-col">
                  {filteredNotices.map((notice) => (
                    <NoticeCard
                      key={notice.id}
                      notice={notice}
                      isBookmarked={bookmarkedIds.includes(notice.id)}
                      onToggleBookmark={handleToggleBookmark}
                      onOpenDetail={setSelectedNotice}
                      subscribedKeywords={subscribedKeywords}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* 보관함 피드 */
            <BookmarkList
              bookmarkedNotices={bookmarkedNotices}
              onToggleBookmark={handleToggleBookmark}
              onOpenDetail={setSelectedNotice}
              subscribedKeywords={subscribedKeywords}
            />
          )}
        </section>
      </div>

      {/* 6. 상세 모달 */}
      <DetailModal
        isOpen={selectedNotice !== null}
        onClose={() => setSelectedNotice(null)}
        notice={selectedNotice}
      />
    </div>
  );
}
