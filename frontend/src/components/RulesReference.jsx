const ROWS = [
  {
    employer: "قطاع حكومي — نموذج",
    transfer: "مطلوب",
    guarantor: "غير متاح",
    collateral: "الراتب",
    maxDpr: "25% — افتراضي",
  },
  {
    employer: "قطاع خاص — نموذج",
    transfer: "مطلوب",
    guarantor: "متاح",
    collateral: "الراتب / كفيل",
    maxDpr: "40% — افتراضي",
  },
];

export default function RulesReference() {
  return (
    <section id="rules" className="py-12">
      <div className="mb-5">
        <h2 className="text-[22px] font-extrabold">شروط الجهات ومصادر البيانات</h2>
        <p className="text-pib-muted text-[15px] mt-1">ملخص سريع للشروط المستخدمة في الدراسة.</p>
      </div>

      <div className="bg-white border border-pib-line rounded-2xl p-6 mb-5 overflow-x-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr>
              {["الجهة / القطاع", "تحويل الراتب", "كفيل بديل", "الضمان", "الحد الأقصى لـ DPR"].map(
                (h) => (
                  <th
                    key={h}
                    className="py-3 px-3.5 border-b border-pib-line bg-pib-greenLight text-pib-greenDark text-xs text-right"
                  >
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {ROWS.map((row) => (
              <tr key={row.employer}>
                <td className="py-3 px-3.5 border-b border-pib-line">{row.employer}</td>
                <td className="py-3 px-3.5 border-b border-pib-line">{row.transfer}</td>
                <td className="py-3 px-3.5 border-b border-pib-line">{row.guarantor}</td>
                <td className="py-3 px-3.5 border-b border-pib-line">{row.collateral}</td>
                <td className="py-3 px-3.5 border-b border-pib-line">
                  <span className="inline-block text-[11px] px-2.5 py-1 rounded-full bg-pib-goldLight text-[#6e5620] font-bold">
                    {row.maxDpr}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-white border border-dashed border-pib-line rounded-xl px-5 py-4 text-[14px] text-pib-muted leading-7">
        <strong className="text-pib-ink">المصدر:</strong>{" "}
        <a
          href="https://www.islamicbank.ps/ar/personal/cards"
          target="_blank"
          rel="noopener noreferrer"
          className="text-pib-green font-bold no-underline"
        >
          موقع البنك الإسلامي الفلسطيني
        </a>{" "}
        للاطلاع على تفاصيل البطاقات والشروط المنشورة. القيم الرقمية في هذه الأداة تقديرية للدراسة الأولية.
      </div>
    </section>
  );
}
