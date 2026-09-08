const NAV_ITEMS = ["الرئيسية", "الأفراد", "البطاقات", "برامج التمويل", "الخدمات المصرفية الإلكترونية"];

export default function Header() {
  return (
    <header className="bg-white text-pib-greenDark border-b-4 border-pib-gold shadow-sm">
      <div className="max-w-6xl mx-auto flex flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <img
            src="https://www.islamicbank.ps/img/logo.png"
            alt="البنك الإسلامي الفلسطيني"
            className="w-[205px] h-auto"
          />
          <div>
            <strong className="block text-sm text-pib-greenDark">نظام تقييم ائتماني</strong>
            <span className="block text-[11.5px] text-pib-muted mt-0.5">للاستخدام الداخلي للفروع</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-pib-muted">
          <div className="hidden md:flex items-center border border-[#cfd5da] h-10 w-44 px-3 text-right">
            <span className="text-[#999]">البحث ...</span>
            <span className="mr-auto text-lg text-[#aab2b8]">⌕</span>
          </div>
          <span className="hidden lg:block px-2">English</span>
          <span className="hidden lg:block px-2">تواصل معنا</span>
        </div>
      </div>
      <div className="border-t border-[#e8edf1] bg-white">
        <nav className="no-print max-w-6xl mx-auto px-6 flex items-center gap-6 text-[13px] text-pib-ink overflow-x-auto">
          {NAV_ITEMS.map((item, i) => (
            <span
              key={item}
              className={`py-3 whitespace-nowrap ${
                i === 2
                  ? "text-pib-green font-bold border-b-2 border-pib-gold"
                  : "text-pib-ink"
              }`}
            >
              {item}
            </span>
          ))}
          <div className="mr-auto hidden sm:flex items-center gap-1.5" aria-label="روابط التواصل الاجتماعي">
            <span className="grid h-9 w-9 place-items-center bg-[#0b5a8f] text-white">in</span>
            <span className="grid h-9 w-9 place-items-center bg-[#c9202b] text-white">▶</span>
            <span className="grid h-9 w-9 place-items-center bg-[#1c4a84] text-white">f</span>
            <span className="grid h-9 w-9 place-items-center bg-[#08a95b] text-white">◔</span>
            <span className="grid h-9 w-9 place-items-center bg-pib-greenDark text-white text-lg">☰</span>
          </div>
        </nav>
      </div>
    </header>
  );
}
