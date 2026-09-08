export function Panel({ step, title, hint, children }) {
  return (
    <div className="bg-white border border-pib-line rounded-xl p-7 mb-6 shadow-[0_3px_14px_rgba(0,55,100,0.04)]">
      {step && (
        <span className="text-[13px] font-extrabold text-pib-green bg-pib-greenLight rounded-full px-3.5 py-1.5">
          {step}
        </span>
      )}
      {title && <h3 className="mt-4 mb-1.5 text-[19px] font-bold">{title}</h3>}
      {hint && <p className="text-pib-muted text-[15px] mb-6 leading-7">{hint}</p>}
      {children}
    </div>
  );
}

export function Field({ label, error, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[15px] font-bold text-pib-ink">{label}</label>
      {children}
      {error && <small className="text-pib-danger text-[11.5px]">{error}</small>}
    </div>
  );
}

const inputBase =
  "border rounded-lg px-3.5 py-3 text-[15px] outline-none bg-[#fcfdfc] text-pib-ink " +
  "focus:border-pib-green focus:ring-2 focus:ring-pib-green/10";

export function TextInput({ error, className = "", ...props }) {
  return (
    <input
      className={`${inputBase} ${error ? "border-pib-danger" : "border-pib-line"} ${className}`}
      {...props}
    />
  );
}

export function Select({ error, className = "", children, ...props }) {
  return (
    <select
      className={`${inputBase} ${error ? "border-pib-danger" : "border-pib-line"} ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}

export function TextArea({ error, className = "", ...props }) {
  return (
    <textarea
      className={`${inputBase} ${error ? "border-pib-danger" : "border-pib-line"} w-full resize-y ${className}`}
      {...props}
    />
  );
}

export function ToggleRow({ value, onChange, yesLabel = "نعم", noLabel = "لا" }) {
  return (
    <div className="flex gap-2.5">
      <button
        type="button"
        onClick={() => onChange(true)}
        className={`flex-1 border rounded-lg py-3 text-[15px] font-bold ${
          value
            ? "bg-pib-greenLight border-pib-green text-pib-greenDark"
            : "bg-[#fcfdfc] border-pib-line text-pib-muted"
        }`}
      >
        {yesLabel}
      </button>
      <button
        type="button"
        onClick={() => onChange(false)}
        className={`flex-1 border rounded-lg py-2.5 text-[13.5px] font-bold ${
          !value
            ? "bg-pib-greenLight border-pib-green text-pib-greenDark"
            : "bg-[#fcfdfc] border-pib-line text-pib-muted"
        }`}
      >
        {noLabel}
      </button>
    </div>
  );
}
