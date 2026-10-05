# نظام التقييم الأولي لأهلية البطاقات الائتمانية — PIB

مشروع تدريبي/داخلي لمساندة موظف الفرع في دراسة أولية لأهلية العميل لبطاقات
**Platinum / World / World Elite**، عبر حساب نسبة عبء الدين (DPR) ومطابقة
شروط تحويل الراتب والضمانات، ثم توليد تقرير دراسة بصيغة Word أو PDF.

> **تنبيه:** النتيجة أولية وليست قرارًا ائتمانيًا نهائيًا. بعض القيم (نسب DPR
> الحدية، عبء البطاقة الشهري) هي **افتراضات Demo** إلى حين توفر السياسة
> الداخلية الرسمية — راجع `backend/app/seed_data.py` لمعرفة أيها مأخوذ من
> صفحات البنك المنشورة فعليًا وأيها افتراضي.

---

## البنية التقنية

| الطبقة | التقنية |
|---|---|
| Backend | Python 3.11+ / FastAPI |
| Database | SQLite (افتراضي، بدون إعداد) → قابل للتحويل لـ PostgreSQL بسطر واحد |
| Business Logic | محرك قواعد Python بسيط (`rules_engine.py`) |
| Reports | Word عبر `python-docx`، PDF عبر `reportlab` (بتشكيل عربي صحيح) |
| Frontend | React + Vite + Tailwind CSS |

```
pib-credit-assessment/
├── backend/
│   ├── app/
│   │   ├── main.py            # نقطة دخول FastAPI
│   │   ├── config.py          # الإعدادات (متغيرات البيئة)
│   │   ├── database.py        # اتصال SQLAlchemy (SQLite/PostgreSQL)
│   │   ├── models.py          # جداول قاعدة البيانات
│   │   ├── schemas.py         # عقود الـ API (Pydantic)
│   │   ├── rules_engine.py    # محرك القواعد — قلب المنطق
│   │   ├── seed_data.py       # بيانات البطاقات/الجهات الأولية
│   │   ├── routers/           # مسارات الـ API
│   │   └── reports/           # مولّد تقارير Word و PDF
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js              # كل نداءات الـ backend في مكان واحد
    │   └── components/
    └── package.json
```

---

## التشغيل

### 1) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # على Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env             # اختياري — القيم الافتراضية تعمل مباشرة

uvicorn app.main:app --reload
```

- الـ API: http://127.0.0.1:8000
- توثيق Swagger التفاعلي: http://127.0.0.1:8000/docs
- عند أول تشغيل، يُنشئ التطبيق قاعدة بيانات SQLite محليًا (`pib_assessment.db`)
  ويزرع فيها بطاقات وجهات العمل الافتراضية تلقائيًا.

### 2) Frontend (React + Vite + Tailwind)

```bash
cd frontend
npm install
cp .env.example .env             # اختياري — يشير افتراضيًا لـ localhost:8000

npm run dev
```

- الواجهة: http://localhost:5173

شغّل الـ backend أولًا ثم الـ frontend؛ الواجهة تعرض رسالة واضحة إن تعذّر
الاتصال بالـ API.

---

## التنقل بين SQLite و PostgreSQL

المشروع يستخدم SQLite افتراضيًا (ملف واحد، بدون أي إعداد). للانتقال لاحقًا
إلى PostgreSQL:

```bash
pip install psycopg2-binary
```

ثم في `backend/.env`:

```
DATABASE_URL=postgresql+psycopg2://pib_user:pib_password@localhost:5432/pib_assessment
```

لا حاجة لأي تعديل آخر في الكود — `app/database.py` يقرأ هذا المتغير مباشرة.

---

## محرك القواعد (Business Rules Engine)

كل قاعدة عمل مستقلة في صنف (class) خاص بها داخل `backend/app/rules_engine.py`:

- `SalaryTransferRule` — تحويل الراتب، أو كفيل بديل إن كانت الجهة تقبل ذلك.
- `DebtBurdenRatioRule` — نسبة عبء الدين (DPR) مقابل الحد الأقصى للجهة.
- `MinimumAgeRule` — الحد الأدنى للعمر.

`RulesEngine` يشغّل كل القواعد المسجّلة ويجمع نتيجتها. لإضافة قاعدة جديدة:
أنشئ صنفًا يرث من `Rule` وأضفه إلى `RulesEngine.default_rules()` — لا حاجة
لتعديل أي ملف آخر (الـ API، الواجهة، والتقارير تقرأ نتيجة المحرك تلقائيًا).

القيم القابلة للتعديل (حدود DPR، عبء البطاقة الشهري، شروط الجهة) هي بيانات
في قاعدة البيانات (`Card` و`Employer`)، وليست ثوابت مبرمجة — يمكن تحديثها
لاحقًا من لوحة إدارة أو مباشرة في القاعدة دون أي نشر (deploy) جديد للكود.

---

## التقارير (Word / PDF)

- **Word**: `backend/app/reports/word_report.py` باستخدام `python-docx`.
- **PDF**: `backend/app/reports/pdf_report.py` باستخدام `reportlab`، مع تشكيل
  عربي صحيح عبر `arabic-reshaper` + `python-bidi`، وخط `FreeSerif` المرفق في
  `backend/app/reports/fonts/` (خط GNU FreeFont، مرخّص بموجب GPL مع استثناء
  تضمين الخطوط — التفاصيل في `fonts/LICENSE.txt`).

للحصول على أي من التقريرين لدراسة سابقة:

```
GET /api/assessments/{id}/report.docx
GET /api/assessments/{id}/report.pdf
```

---

## المصدر الرسمي مقابل الافتراضات (Demo)

- **منشور رسميًا** على [موقع البنك](https://www.islamicbank.ps/ar/personal/cards):
  وجود بطاقات Platinum وWorld وWorld Elite، واشتراط تحويل الراتب أو كفيل
  محوِّل راتب، وألا تتجاوز الالتزامات الشهرية النسبة المعتمدة ضمن سياسة
  المنح الائتمانية.
- **افتراضات Demo** لأغراض هذا النموذج فقط: نسب DPR الحدية (25% حكومي / 40%
  خاص)، وقيم عبء البطاقة الشهري، والحدود الائتمانية بالدولار. يجب استبدالها
  بالسياسة الداخلية الرسمية قبل أي استخدام فعلي.

---

## ملاحظات إضافية

- كل استجابة تقييم تتضمن `assumptions` توضّح بالضبط ما هو افتراضي، وتظهر
  أيضًا في تذييل كل تقرير Word/PDF.
- الواجهة والـ API لا يخزّنان أي بيانات عميل خارج قاعدة بيانات هذا النظام،
  ولا يرسلان أي شيء لأي جهة خارجية.

## تجهيز الإنتاج والأمان

- لا تنشر `uvicorn` أو Vite مباشرة على الإنترنت؛ استخدم IIS/Nginx خلف HTTPS.
- اضبط `ENVIRONMENT=production` لإخفاء Swagger وOpenAPI، وحدد `CORS_ORIGINS`
  و`ALLOWED_HOSTS` على نطاق النظام الحقيقي فقط.
- استخدم PostgreSQL في الإنتاج بدل SQLite، وضع بيانات الاتصال في `.env` خارج Git.
- شغّل النسخ الاحتياطي الدوري من مجلد `backend`:
  `python scripts/backup_data.py`
- تُسجل عمليات إنشاء التقييم وتنزيل Word/PDF/Excel في جدول `audit_logs`.
- قبل الربط الرسمي، يجب إضافة موفر هوية البنك (Active Directory/Entra ID) وربط
  اسم المستخدم الحقيقي بحقل `actor` بدل القيمة الافتراضية `anonymous`.

## النشر المجاني التجريبي

ينشئ ملف `render.yaml` واجهة ثابتة وواجهة API وقاعدة PostgreSQL، ويربطها تلقائيًا
بعناوين `onrender.com` المحددة في الملف. للنشر:

1. ادفع التغييرات إلى مستودع GitHub المتصل.
2. افتح [نشر المشروع على Render](https://render.com/deploy?repo=https://github.com/alaanatsaha/-)،
   ثم سجّل الدخول وامنح Render صلاحية المستودع.
3. راجع الموارد التي سيُنشئها Render، ثم اختر **Apply** لبدء النشر.

بعد اكتمال النشر، رابط الواجهة هو
`https://pib-credit-assessment-web.onrender.com` ورابط الـ API هو
`https://pib-credit-assessment-api.onrender.com`. الخطة المجانية مناسبة للتجربة؛
قد تدخل الخدمات في السكون، وقاعدة البيانات المجانية محدودة بعمر تخزين قصير.
لا تستخدم النشر التجريبي لتخزين بيانات عملاء حقيقية. قاعدة البيانات هي المصدر
الرسمي، وExcel للتصدير والمراجعة فقط.
