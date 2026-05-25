import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "UniNotice - 대학 학사공지 3줄 요약 알리미",
  description: "복잡한 대학교 학사공지사항을 핵심만 빠르게 요약하여 제공합니다. 장학금, 수강신청, 채용 행사 등 중요 소식을 놓치지 마세요.",
  keywords: "대학 공지, 학사공지, 3줄 요약, 대학 축제, 장학금 신청, 알림 서비스",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="ko"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground transition-colors duration-200">
        <main className="flex-1 flex flex-col relative z-10 w-full max-w-4xl mx-auto px-4 py-6 md:py-10">
          {children}
        </main>
      </body>
    </html>
  );
}
