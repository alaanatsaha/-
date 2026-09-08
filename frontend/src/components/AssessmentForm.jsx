import { useState } from "react";
import { CreditCard } from "lucide-react";
import { Panel, Field, TextInput, Select, TextArea, ToggleRow } from "./ui.jsx";

const initialForm = {
  customer_name: "",
  age: "",
  account_number: "",
  salary: "",
  other_income: "0",
  existing_facilities: "0",
  salary_transferred: true,
  guarantor_available: false,
  employer_id: "",
  card_id: "",
  notes: "",
};

function validate(form) {
  const errors = {};
  if (!form.customer_name.trim()) errors.customer_name = "الاسم مطلوب";

  const age = Number(form.age);
  if (form.age === "" || !Number.isFinite(age) || age < 18 || age > 100) {
    errors.age = "أدخل عمرًا صحيحًا بين 18 و100";
  }

  if (!form.account_number.trim()) errors.account_number = "رقم الحساب مطلوب";

  const salary = Number(form.salary);
  if (form.salary === "" || !Number.isFinite(salary) || salary <= 0) {
    errors.salary = "أدخل راتبًا شهريًا صحيحًا";
  }

  return errors;
}

export default function AssessmentForm({ cards, employers, onSubmit, submitting, formRef }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  // Default employer/card once reference data loads
  const employerId = form.employer_id || employers[0]?.id || "";
  const cardId = form.card_id || cards[1]?.id || cards[0]?.id || "";

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    onSubmit({
      customer_name: form.customer_name.trim(),
      age: Number(form.age),
      account_number: form.account_number.trim(),
      salary: Number(form.salary),
      other_income: Number(form.other_income || 0),
      existing_facilities: Number(form.existing_facilities || 0),
      salary_transferred: form.salary_transferred,
      guarantor_available: form.guarantor_available,
      employer_id: employerId,
      card_id: cardId,
      notes: form.notes.trim(),
    });
  }

  function handleReset() {
    setForm(initialForm);
    setErrors({});
  }

  const selectedEmployer = employers.find((e) => e.id === employerId);

  return (
    <form ref={formRef} onSubmit={handleSubmit} noValidate>
      <Panel step="١ — بيانات العميل" title="بيانات أساسية">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Field label="اسم العميل *" error={errors.customer_name}>
            <TextInput
              value={form.customer_name}
              onChange={(e) => update("customer_name", e.target.value)}
              placeholder="مثال: أحمد محمد"
              error={errors.customer_name}
            />
          </Field>
          <Field label="العمر *" error={errors.age}>
            <TextInput
              type="number"
              min="18"
              max="100"
              value={form.age}
              onChange={(e) => update("age", e.target.value)}
              placeholder="30"
              error={errors.age}
            />
          </Field>
          <Field label="رقم الحساب *" error={errors.account_number}>
            <TextInput
              value={form.account_number}
              onChange={(e) => update("account_number", e.target.value)}
              placeholder="0000••••"
              error={errors.account_number}
            />
          </Field>
        </div>
      </Panel>

      <Panel
        step="٢ — الوظيفة وتحويل الراتب"
        title="جهة العمل والقطاع"
        hint="اختر جهة العمل وحدد طريقة تحويل الراتب."
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Field label="الجهة">
            <Select value={employerId} onChange={(e) => update("employer_id", e.target.value)}>
              {employers.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="الراتب محوَّل إلى البنك؟">
            <ToggleRow
              value={form.salary_transferred}
              onChange={(v) => update("salary_transferred", v)}
            />
          </Field>
          <Field label="يوجد كفيل محوِّل راتب؟">
            <ToggleRow
              value={form.guarantor_available}
              onChange={(v) => update("guarantor_available", v)}
            />
          </Field>
        </div>
        {selectedEmployer && !selectedEmployer.guarantor_allowed && (
          <p className="text-[14px] text-pib-muted mt-4">
            هذه الجهة لا تقبل كفيلًا بديلاً لتحويل الراتب حسب الإعداد الحالي.
          </p>
        )}
      </Panel>

      <Panel step="٣ — البيانات المالية" title="الدخل والالتزامات الحالية">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Field label="الراتب الشهري (₪) *" error={errors.salary}>
            <TextInput
              type="number"
              min="0"
              step="0.01"
              value={form.salary}
              onChange={(e) => update("salary", e.target.value)}
              placeholder="4500"
              error={errors.salary}
            />
          </Field>
          <Field label="دخل إضافي معتمد (₪)">
            <TextInput
              type="number"
              min="0"
              step="0.01"
              value={form.other_income}
              onChange={(e) => update("other_income", e.target.value)}
            />
          </Field>
          <Field label="التزامات شهرية حالية (₪)">
            <TextInput
              type="number"
              min="0"
              step="0.01"
              value={form.existing_facilities}
              onChange={(e) => update("existing_facilities", e.target.value)}
            />
          </Field>
        </div>
      </Panel>

      <Panel
        step="٤ — اختيار البطاقة"
        title="بطاقة الطلب"
        hint="اختر البطاقة المطلوبة لإكمال الدراسة."
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          {cards.map((card) => {
            const selected = card.id === cardId;
            const image = card.id.includes("world_elite")
              ? "https://www.islamicbank.ps/images/pages/thumbnails/1779082252.png"
              : card.id.includes("world")
                ? "https://www.islamicbank.ps/download?file=8263410921701935464.png"
                : "https://www.islamicbank.ps/download?file=4057869951701935405.png";
            return (
              <button
                type="button"
                key={card.id}
                onClick={() => update("card_id", card.id)}
                className={`text-right border rounded-xl p-4 bg-white transition-shadow hover:shadow-lg ${
                  selected ? "border-2 border-pib-green bg-pib-greenLight" : "border-pib-line"
                }`}
              >
                <div className="flex justify-between items-center font-extrabold text-pib-greenDark text-[15px]">
                  <span>{card.name}</span>
                  <span className="text-pib-green text-[13px]">اقرأ المزيد ←</span>
                </div>
                <div className="h-28 my-3 overflow-hidden rounded-lg bg-[#f5f7f8] flex items-center justify-center">
                  <img src={image} alt={card.name} className="max-h-full max-w-full object-contain" />
                </div>
                <strong className="block text-[24px] mt-2 mb-1 text-pib-ink">
                  {card.currency} {card.credit_limit.toLocaleString()}
                </strong>
                <small className="text-pib-muted text-[13px]">
                  عبء شهري تجريبي: ₪{card.monthly_burden}
                </small>
              </button>
            );
          })}
        </div>
        <div className="mt-4 bg-pib-goldLight border border-[#e6d5a4] text-[#6e5620] rounded-lg px-4 py-3 text-[14px]">
          القيم المعروضة تقديرية لأغراض الدراسة الأولية.
        </div>
      </Panel>

      <Panel step="٥ — ملاحظات" title="ملاحظات الموظف (اختياري)">
        <Field label="">
          <TextArea
            rows={3}
            value={form.notes}
            onChange={(e) => update("notes", e.target.value)}
            placeholder="أي ملاحظات إضافية على الطلب..."
          />
        </Field>
      </Panel>

      <div className="flex gap-3 mt-6">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-xl px-6 py-3.5 font-bold text-[14.5px] bg-pib-green text-white disabled:opacity-60 flex items-center gap-2"
        >
          <CreditCard size={17} />
          {submitting ? "جاري التقييم..." : "إجراء التقييم الأولي"}
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="rounded-xl px-6 py-3.5 font-bold text-[14.5px] bg-white text-pib-muted border border-pib-line"
        >
          إعادة ضبط النموذج
        </button>
      </div>
    </form>
  );
}
