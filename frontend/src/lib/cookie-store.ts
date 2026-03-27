const KEY = "eudic_cookie";

export function saveCookie(cookie: string): void {
  sessionStorage.setItem(KEY, cookie);
}

export function loadCookie(): string {
  return sessionStorage.getItem(KEY) ?? "";
}

export function clearCookie(): void {
  sessionStorage.removeItem(KEY);
}

export function hasCookie(): boolean {
  return !!sessionStorage.getItem(KEY);
}
