import { useEffect, useRef, useState } from "react";
import Header from "./components/Header.jsx";
import Hero from "./components/Hero.jsx";
import AssessmentForm from "./components/AssessmentForm.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import RulesReference from "./components/RulesReference.jsx";
import Footer from "./components/Footer.jsx";
import { fetchCards, fetchEmployers, createAssessment, ApiError } from "./api.js";

export default function App() {
  const [cards, setCards] = useState([]);
  const [employers, setEmployers] = useState([]);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [submitError, setSubmitError] = useState("");

  const resultRef = useRef(null);

  useEffect(() => {
    Promise.all([fetchCards(), fetchEmployers()])
      .then(([cardsData, employersData]) => {
        setCards(cardsData);
        setEmployers(employersData);
      })
      .catch(() => {
        setLoadError(
          "تعذر الاتصال بخادم FastAPI. تأكد من تشغيل الـ backend على المنفذ 8000 ثم أعد تحميل الصفحة."
        );
      });
  }, []);

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      const data = await createAssessment(payload);
      setResult(data);
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "تعذر إرسال الطلب. حاول مرة أخرى.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <Header />
      <Hero />

      <main className="max-w-6xl mx-auto px-6">
        <section id="assessment" className="py-12">
          <div className="mb-5">
            <h2 className="text-[22px] font-extrabold">نموذج دراسة الطلب</h2>
            <p className="text-pib-muted text-[13.5px] mt-1">
              عبّئ بيانات العميل خطوة بخطوة، ثم اعرض النتيجة الأولية وأسباب القرار.
            </p>
          </div>

          {loadError && (
            <div className="bg-pib-dangerBg text-pib-danger rounded-xl px-4 py-3.5 mb-5 text-sm">
              {loadError}
            </div>
          )}

          {submitError && (
            <div className="bg-pib-dangerBg text-pib-danger rounded-xl px-4 py-3.5 mb-5 text-sm">
              {submitError}
            </div>
          )}

          {cards.length > 0 && employers.length > 0 && (
            <AssessmentForm
              cards={cards}
              employers={employers}
              onSubmit={handleSubmit}
              submitting={submitting}
            />
          )}

          <div className="mt-2">
            <ResultPanel result={result} resultRef={resultRef} />
          </div>
        </section>

        <RulesReference />
      </main>

      <Footer />
    </div>
  );
}
