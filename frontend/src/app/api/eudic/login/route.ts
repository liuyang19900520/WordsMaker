import { NextRequest, NextResponse } from "next/server";

const LOGIN_PAGE_URL =
  "https://dict.eudic.net/Account/Login?returnUrl=http%3a%2f%2fmy.eudic.net%2f";
const LOGIN_POST_URL = "https://dict.eudic.net/Account/Login";
const MAX_HOPS = 5;

const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

function collectCookies(headers: Headers, jar: Map<string, string>): void {
  const setCookies: string[] =
    typeof (headers as Headers & { getSetCookie?: () => string[] }).getSetCookie === "function"
      ? (headers as Headers & { getSetCookie: () => string[] }).getSetCookie()
      : (headers.get("set-cookie") ?? "").split(/,(?=[^ ])/).filter(Boolean);

  for (const raw of setCookies) {
    const nameValue = raw.split(";")[0].trim();
    const eqIdx = nameValue.indexOf("=");
    if (eqIdx < 0) continue;
    const name = nameValue.slice(0, eqIdx).trim();
    const value = nameValue.slice(eqIdx + 1).trim();
    if (name) jar.set(name, value);
  }
}

function jarToHeader(jar: Map<string, string>): string {
  return [...jar.entries()].map(([k, v]) => `${k}=${v}`).join("; ");
}

export async function POST(req: NextRequest) {
  let email: string;
  let password: string;
  try {
    const body = await req.json();
    email = (body.email ?? "").trim();
    password = body.password ?? "";
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!email || !password) {
    return NextResponse.json(
      { error: "email and password are required" },
      { status: 400 }
    );
  }

  const jar = new Map<string, string>();

  // Phase 1: GET login page for CSRF token and initial cookies
  let loginPageRes: Response;
  try {
    loginPageRes = await fetch(LOGIN_PAGE_URL, {
      method: "GET",
      redirect: "manual",
      headers: { "User-Agent": UA },
    });
  } catch (err) {
    return NextResponse.json(
      { error: `Failed to reach Eudic login page: ${String(err)}` },
      { status: 502 }
    );
  }

  collectCookies(loginPageRes.headers, jar);

  const loginPageHtml = await loginPageRes.text();
  const csrfMatch =
    /__RequestVerificationToken[^>]+value="([^"]+)"/.exec(loginPageHtml) ??
    /name="__RequestVerificationToken"[^>]*value="([^"]+)"/.exec(loginPageHtml);

  // Phase 2: POST login form
  const formBody = new URLSearchParams({
    UserName: email,
    Password: password,
    returnUrl: "http://my.eudic.net/",
    RememberMe: "false",
    ...(csrfMatch ? { __RequestVerificationToken: csrfMatch[1] } : {}),
  });

  let loginRes: Response;
  try {
    loginRes = await fetch(LOGIN_POST_URL, {
      method: "POST",
      redirect: "manual",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": UA,
        Cookie: jarToHeader(jar),
        Referer: LOGIN_PAGE_URL,
        Origin: "https://dict.eudic.net",
      },
      body: formBody.toString(),
    });
  } catch (err) {
    return NextResponse.json(
      { error: `Login POST failed: ${String(err)}` },
      { status: 502 }
    );
  }

  if (loginRes.status < 300 || loginRes.status >= 400) {
    return NextResponse.json(
      { error: "Login failed: invalid credentials" },
      { status: 401 }
    );
  }

  collectCookies(loginRes.headers, jar);

  // Phase 3: Follow redirect chain
  let currentUrl = LOGIN_POST_URL;
  let nextLocation = loginRes.headers.get("location");

  for (let hop = 0; hop < MAX_HOPS && nextLocation; hop++) {
    try {
      currentUrl = new URL(nextLocation, currentUrl).href;
    } catch {
      break;
    }

    let hopRes: Response;
    try {
      hopRes = await fetch(currentUrl, {
        method: "GET",
        redirect: "manual",
        headers: {
          "User-Agent": UA,
          Cookie: jarToHeader(jar),
          Referer: currentUrl,
        },
      });
    } catch {
      break;
    }

    collectCookies(hopRes.headers, jar);

    if (hopRes.status < 300 || hopRes.status >= 400) break;
    nextLocation = hopRes.headers.get("location");
  }

  if (jar.size === 0) {
    return NextResponse.json(
      { error: "Login appeared to succeed but no cookies were collected" },
      { status: 502 }
    );
  }

  return NextResponse.json({ cookie: jarToHeader(jar) });
}
