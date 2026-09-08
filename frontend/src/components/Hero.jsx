export default function Hero() {
  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="bg-gradient-to-br from-pib-greenDark to-pib-green text-white px-6 py-14 sm:py-16">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[1.3fr_1fr] gap-10 items-center">
        <div>
          <span className="inline-block text-[12.5px] text-pib-goldLight bg-white/10 border border-white/20 rounded-full px-3.5 py-1.5 mb-4">
            نظام داخلي — دراسة أولية غير نهائية
          </span>
          <h1 className="text-3xl font-extrabold leading-snug mb-3.5">
            التقييم الأولي لأهلية البطاقات الائتمانية
          </h1>
          <p className="text-[#d7e7f1] text-[18px] leading-8 max-w-lg mb-6">
            دراسة أولية سريعة لطلب البطاقة، وفق بيانات العميل ونسبة عبء الدين وشروط الجهة.
          </p>
          <div className="flex gap-3 flex-wrap">
            <button
              type="button"
              onClick={() => scrollTo("assessment")}
              className="rounded-xl px-6 py-3.5 font-bold text-[14.5px] bg-pib-gold text-pib-greenDark"
            >
              ابدأ التقييم
            </button>
            <button
              type="button"
              onClick={() => scrollTo("rules")}
              className="rounded-xl px-6 py-3.5 font-bold text-[14.5px] border border-white/40"
            >
              شروط ومصادر البطاقات
            </button>
          </div>
        </div>
        <div className="bg-white/[0.07] border border-white/[0.18] rounded-2xl p-5">
          <h3 className="text-[15px] text-pib-goldLight mb-3">كيف تُقرأ النتيجة</h3>
          <ul className="text-[13.5px] text-[#dcefe4] list-disc pr-4.5 space-y-2">
            <li>أدخل بيانات العميل الأساسية.</li>
            <li>اختر جهة العمل والبطاقة.</li>
            <li>راجع النتيجة قبل رفع الطلب.</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
