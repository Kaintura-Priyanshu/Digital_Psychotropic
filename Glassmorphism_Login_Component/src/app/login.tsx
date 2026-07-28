import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

const BG =
  "https://images.unsplash.com/photo-1547203928-cadee38b6568?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixlib=rb-4.1.0&q=80&w=1920";

/* ─── tiny helpers ─── */
function FloatingInput({
  id,
  label,
  type = "text",
  value,
  onChange,
  suffix,
}: {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  suffix?: React.ReactNode;
}) {
  return (
    <div className="relative">
      <input
        id={id}
        name={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder=" "
        autoComplete={id}
        required
        className="
          peer w-full bg-transparent
          pt-5 pb-2 pr-8 pl-0
          text-white text-[15px] tracking-wide
          border-b border-white/30
          focus:border-orange-400
          outline-none
          transition-colors duration-300
          placeholder-transparent
        "
      />
      <label
        htmlFor={id}
        className="
          pointer-events-none absolute left-0
          text-white/45 transition-all duration-300
          top-[6px] text-[11px] tracking-wider uppercase
          peer-placeholder-shown:top-[18px] peer-placeholder-shown:text-sm peer-placeholder-shown:normal-case peer-placeholder-shown:tracking-normal peer-placeholder-shown:text-white/38
          peer-focus:top-[6px] peer-focus:text-[11px] peer-focus:tracking-wider peer-focus:uppercase peer-focus:text-orange-400
        "
      >
        {label}
      </label>
      {suffix && (
        <span className="absolute right-0 bottom-[9px]">{suffix}</span>
      )}
    </div>
  );
}

/* ─── main component ─── */
export default function Login() {
  const [tab, setTab] = useState<"signin" | "signup">("signin");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [keep, setKeep] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(tab === "signin" ? "Signed in!" : "Account created!");
  };

  return (
    /* fullscreen backdrop */
    <div
      className="fixed inset-0 flex items-center justify-center bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${BG})` }}
    >
      {/* scrim */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-black/25 to-black/50" />

      {/* glass card */}
      <div
        className="relative z-10 w-full mx-4 rounded-2xl overflow-hidden"
        style={{
          maxWidth: 400,
          background: "rgba(255,255,255,0.07)",
          backdropFilter: "blur(24px) saturate(1.4)",
          WebkitBackdropFilter: "blur(24px) saturate(1.4)",
          border: "1px solid rgba(255,255,255,0.18)",
          boxShadow:
            "0 20px 60px rgba(0,0,0,0.55), 0 1px 0 rgba(255,255,255,0.12) inset",
        }}
      >
        {/* ── tabs ── */}
        <div className="flex">
          {(["signin", "signup"] as const).map((t) => {
            const active = tab === t;
            return (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`
                  relative flex-1 py-[18px] text-[12px] font-bold tracking-[0.18em]
                  transition-colors duration-200
                  ${active ? "text-white" : "text-white/35 hover:text-white/55"}
                `}
              >
                {t === "signin" ? "SIGN IN" : "SIGN UP"}
                {/* active indicator */}
                <span
                  className={`
                    absolute bottom-0 left-1/2 -translate-x-1/2 h-[2.5px] rounded-full
                    bg-orange-500 transition-all duration-300
                    ${active ? "w-10 opacity-100" : "w-0 opacity-0"}
                  `}
                />
              </button>
            );
          })}
        </div>

        {/* separator line */}
        <div className="h-px bg-white/10" />

        {/* ── form body ── */}
        <form onSubmit={handleSubmit} className="px-9 pt-9 pb-8 flex flex-col gap-8">
          {/* inputs */}
          <div className="flex flex-col gap-7">
            <FloatingInput
              id="username"
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <FloatingInput
              id="password"
              label="Password"
              type={showPass ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              suffix={
                <button
                  type="button"
                  onClick={() => setShowPass((v) => !v)}
                  className="text-white/38 hover:text-white/70 transition-colors"
                  aria-label={showPass ? "Hide password" : "Show password"}
                >
                  {showPass
                    ? <EyeOff className="w-[17px] h-[17px]" />
                    : <Eye className="w-[17px] h-[17px]" />}
                </button>
              }
            />
          </div>

          {/* keep me logged in */}
          <label className="flex items-center gap-[10px] cursor-pointer group select-none">
            {/* custom checkbox */}
            <span className="relative w-[17px] h-[17px] flex-shrink-0">
              <input
                type="checkbox"
                checked={keep}
                onChange={(e) => setKeep(e.target.checked)}
                className="peer sr-only"
              />
              <span
                className="
                  block w-full h-full rounded-[4px]
                  border border-white/30
                  bg-white/10
                  peer-checked:bg-orange-500
                  peer-checked:border-orange-500
                  transition-colors duration-200
                "
              />
              {keep && (
                <svg
                  viewBox="0 0 17 17"
                  fill="none"
                  className="absolute inset-0 w-full h-full text-white pointer-events-none"
                >
                  <path
                    d="M3.5 8.5l3.5 3.5 6-6"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </span>
            <span className="text-[13px] text-white/55 group-hover:text-white/80 transition-colors duration-200">
              Keep me logged in
            </span>
          </label>

          {/* CTA button */}
          <button
            type="submit"
            className="
              w-full py-[13px] rounded-full
              bg-orange-500 hover:bg-orange-600
              active:scale-[0.97]
              text-white text-[13px] font-bold tracking-[0.2em] uppercase
              transition-all duration-200
              shadow-[0_6px_28px_rgba(249,115,22,0.38)]
            "
          >
            {tab === "signin" ? "Login" : "Create Account"}
          </button>

          {/* forgot password */}
          <p className="text-center -mt-3">
            <a
              href="#"
              onClick={(e) => e.preventDefault()}
              className="text-[12px] text-white/38 hover:text-orange-400 transition-colors duration-200 tracking-wide"
            >
              Forgot password?
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
