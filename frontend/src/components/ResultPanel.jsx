import { FileDown, Printer } from "lucide-react";
import { wordReportUrl, pdfReportUrl } from "../api.js";

export default function ResultPanel({ result, resultRef }) {
  if (!result) return null;

  const eligible = result.status === "eligible";

  return (
    <div
      ref={resultRef}
      className={`rounded-2xl border-2 bg-white p-7 ${
        eligible ? "border-[#bfe0d1]" : "border-[#e7c3bf]"
      }`}
    >
      <div className="flex justify-between items-center gap-6 flex-wrap">
        <div>
          <div className="text-[11.5px] tracking-wide text-pib-green font-extrabold">
            PRELIMINARY ASSESSMENT — تقييم أولي غير نهائي
          </div>
          <h2 className="my-1.5 text-2xl font-extrabold">
            {eligible ? "مؤهل مبدئيًا" : "غير مؤهل مبدئيًا"}
          </h2>
          <p className="text-pib-muted text-[13.5px]">{result.decision_summary}</p>
        </div>
        <div
          className={`w-[104px] h-[104px] rounded-full flex-none flex flex-col items-center justify-center font-extrabold text-2xl ${
            eligible ? "bg-pib-greenLight text-pib-greenDark" : "bg-pib-dangerBg text-pib-danger"
          }`}
        >
          <span>{result.dpr.toFixed(1)}%</span>
          <span className="text-[10px] font-bold mt-0.5">DPR</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-6">
        <Metric label="الدخل المعتمد" value={`${result.approved_income.toLocaleString()} ₪`} />
        <Metric label="عبء البطاقة الشهري" value={`${result.card_monthly_burden.toLocaleString()} ₪`} />
        <Metric label="الالتزامات الحالية" value={`${result.existing_facilities.toLocaleString()} ₪`} />
        <Metric label="الحد الأقصى المسموح لـ DPR" value={`${result.max_dpr_applied}%`} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {result.checks.map((check) => (
          <div
            key={check.key}
            className={`flex gap-2.5 p-3.5 rounded-xl ${
              check.passed ? "bg-[#f6f8f7]" : "bg-pib-dangerBg"
            }`}
          >
            <span
              className={`w-6.5 h-6.5 rounded-full flex-none grid place-items-center font-extrabold text-[13px] ${
                check.passed ? "bg-[#d7efe2] text-pib-greenDark" : "bg-[#f2d6d2] text-pib-danger"
              }`}
            >
              {check.passed ? "✓" : "×"}
            </span>
            <div>
              <strong className="block text-[12.5px]">{check.label}</strong>
              <small className="block text-pib-muted text-[11px] mt-0.5">{check.detail}</small>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 flex-wrap mt-5 no-print">
        <a
          href={wordReportUrl(result.id)}
          className="rounded-xl px-5 py-3 font-bold text-[13.5px] bg-pib-green text-white flex items-center gap-2"
        >
          <FileDown size={16} /> تحميل تقرير Word
        </a>
        <a
          href={pdfReportUrl(result.id)}
          className="rounded-xl px-5 py-3 font-bold text-[13.5px] bg-pib-greenDark text-white flex items-center gap-2"
        >
          <FileDown size={16} /> تحميل تقرير PDF
        </a>
        <button
          type="button"
          onClick={() => window.print()}
          className="rounded-xl px-5 py-3 font-bold text-[13.5px] bg-white text-pib-muted border border-pib-line flex items-center gap-2"
        >
          <Printer size={16} /> طباعة الصفحة
        </button>
      </div>

      {result.assumptions?.length > 0 && (
        <div className="mt-5 bg-[#fdf7ea] border border-[#eddcae] rounded-lg px-4 py-3.5 text-[11.5px] text-[#6e5620]">
          <strong>ملاحظات هامة: </strong>
          <ul className="list-disc pr-4 mt-1 space-y-1">
            {result.assumptions.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="bg-[#f6f8f7] rounded-xl p-3.5">
      <span className="block text-[11px] text-pib-muted">{label}</span>
      <strong className="block text-[16px] mt-1">{value}</strong>
    </div>
  );
}
