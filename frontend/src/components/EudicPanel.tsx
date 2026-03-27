"use client";

import { useEffect, useState } from "react";
import { saveCookie, loadCookie, clearCookie } from "@/lib/cookie-store";

interface EudicPanelProps {
  onCookieChange: (cookie: string) => void;
}

export default function EudicPanel({ onCookieChange }: EudicPanelProps) {
  const [cookie, setCookie] = useState("");
  const [saved, setSaved] = useState(false);

  const [email, setEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginStatus, setLoginStatus] = useState<"idle" | "loading" | "error">("idle");
  const [loginError, setLoginError] = useState("");

  const [manualOpen, setManualOpen] = useState(false);

  useEffect(() => {
    const stored = loadCookie();
    if (stored) {
      setCookie(stored);
      setSaved(true);
      onCookieChange(stored);
    }
  }, [onCookieChange]);

  async function handleLogin() {
    const trimmedEmail = email.trim();
    if (!trimmedEmail || !loginPassword) return;

    setLoginStatus("loading");
    setLoginError("");

    try {
      const res = await fetch("/api/eudic/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: trimmedEmail, password: loginPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        setLoginError(data.error ?? "Login failed");
        setLoginStatus("error");
        return;
      }

      saveCookie(data.cookie);
      setCookie(data.cookie);
      setSaved(true);
      onCookieChange(data.cookie);
      setLoginStatus("idle");
      setLoginPassword("");
    } catch {
      setLoginError("Network error — please try again");
      setLoginStatus("error");
    }
  }

  function handleSave() {
    const trimmed = cookie.trim();
    if (!trimmed) return;
    saveCookie(trimmed);
    setSaved(true);
    onCookieChange(trimmed);
  }

  function handleClear() {
    clearCookie();
    setCookie("");
    setSaved(false);
    onCookieChange("");
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
        <h2 className="font-semibold text-gray-700">Eudic</h2>
        <div className="flex items-center gap-2">
          {saved ? (
            <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
              Cookie saved
            </span>
          ) : (
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <span className="w-2 h-2 rounded-full bg-gray-300 inline-block" />
              No cookie set
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {/* Login form */}
        <div className="space-y-4">
          <p className="text-sm font-semibold text-gray-700">Sign in to Eudic</p>

          <div className="space-y-2">
            <label className="block text-xs font-medium text-gray-600">Email</label>
            <input
              type="email"
              autoComplete="username"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setLoginStatus("idle"); }}
              placeholder="you@example.com"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-medium text-gray-600">Password</label>
            <input
              type="password"
              autoComplete="current-password"
              value={loginPassword}
              onChange={(e) => { setLoginPassword(e.target.value); setLoginStatus("idle"); }}
              placeholder="••••••••"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-400"
              onKeyDown={(e) => { if (e.key === "Enter") handleLogin(); }}
            />
          </div>

          {loginStatus === "error" && loginError && (
            <p className="text-xs text-red-600">{loginError}</p>
          )}

          <button
            onClick={handleLogin}
            disabled={!email.trim() || !loginPassword || loginStatus === "loading"}
            className="w-full py-2 rounded-lg text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loginStatus === "loading" ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </div>

        {/* Collapsible manual paste fallback */}
        <div className="border border-gray-200 rounded-xl overflow-hidden">
          <button
            onClick={() => setManualOpen((o) => !o)}
            className="w-full flex items-center justify-between px-4 py-3 text-sm text-gray-500 hover:bg-gray-50 transition-colors"
          >
            <span>Paste cookie manually</span>
            <span className="text-xs text-gray-400">{manualOpen ? "▲" : "▼"}</span>
          </button>

          {manualOpen && (
            <div className="px-4 pb-4 space-y-3 border-t border-gray-100">
              <div className="rounded-xl bg-blue-50 border border-blue-100 p-4 space-y-3 mt-3">
                <p className="text-sm font-semibold text-blue-700">How to get your Eudic cookie</p>
                <ol className="text-sm text-blue-700 space-y-2 list-decimal list-inside">
                  <li>
                    Open{" "}
                    <a
                      href="https://my.eudic.net/studylist"
                      target="_blank"
                      rel="noreferrer"
                      className="underline font-medium hover:text-blue-900"
                    >
                      my.eudic.net/studylist
                    </a>{" "}
                    in a new tab and log in.
                  </li>
                  <li>Press <kbd className="px-1.5 py-0.5 rounded bg-blue-100 text-xs font-mono">F12</kbd> to open DevTools.</li>
                  <li>Go to <strong>Network</strong>, reload the page, and click any request.</li>
                  <li>Under <strong>Request Headers</strong>, find the <code className="px-1 bg-blue-100 rounded text-xs">Cookie</code> field.</li>
                  <li>Copy the entire value and paste it below.</li>
                </ol>
                <a
                  href="https://my.eudic.net/studylist"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 transition-colors rounded-lg px-3 py-1.5"
                >
                  Open Eudic in new tab →
                </a>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-medium text-gray-600">Eudic Cookie</label>
                <textarea
                  className="w-full h-28 text-xs font-mono border border-gray-200 rounded-lg p-2 resize-none focus:outline-none focus:ring-1 focus:ring-blue-400 text-gray-700 placeholder-gray-300"
                  placeholder={"Paste your cookie here...\ne.g. SESSION=abc123; user_id=456; ..."}
                  value={cookie}
                  onChange={(e) => {
                    setCookie(e.target.value);
                    setSaved(false);
                  }}
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={!cookie.trim()}
                  className="flex-1 py-2 rounded-lg text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Save Cookie
                </button>
                {saved && (
                  <button
                    onClick={handleClear}
                    className="px-3 py-2 rounded-lg text-sm text-gray-500 hover:text-red-500 hover:bg-red-50 transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
