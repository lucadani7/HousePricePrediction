export type ThemePreference = "light" | "dark" | "system";

export const THEME_STORAGE_KEY = "theme";
const THEME_CHANGE_EVENT = "theme-change";
const DARK_QUERY = "(prefers-color-scheme: dark)";

/**
 * Runs in <head> before the page is painted, so a dark-mode user never sees a white flash.
 * Plain JavaScript in a string: it runs before React and cannot import anything.
 */
export const THEME_INIT_SCRIPT = `(function () {
  try {
    var preference = localStorage.getItem("${THEME_STORAGE_KEY}");
    var dark = preference === "dark" ||
      (preference !== "light" && window.matchMedia("${DARK_QUERY}").matches);
    document.documentElement.classList.toggle("dark", dark);
  } catch (e) {}
})();`;

function isThemePreference(value: string | null): value is ThemePreference {
  return value === "light" || value === "dark" || value === "system";
}

export function readThemePreference(): ThemePreference {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    return isThemePreference(saved) ? saved : "system";
  } catch {
    return "system";
  }
}

export function applyTheme(preference: ThemePreference): void {
  const dark =
    preference === "dark" ||
    (preference === "system" && window.matchMedia(DARK_QUERY).matches);
  document.documentElement.classList.toggle("dark", dark);
}

export function setThemePreference(preference: ThemePreference): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, preference);
  } catch {
    // Storage unavailable (e.g. private mode): the theme still applies for this visit.
  }
  applyTheme(preference);
  window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
}

/** Notifies when the preference changes in this tab or in another tab. */
export function subscribeToThemePreference(onChange: () => void): () => void {
  window.addEventListener(THEME_CHANGE_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(THEME_CHANGE_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

export function subscribeToSystemTheme(onChange: () => void): () => void {
  const media = window.matchMedia(DARK_QUERY);
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}
