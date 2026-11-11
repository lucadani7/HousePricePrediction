"use client";

import { useEffect, useSyncExternalStore } from "react";
import {
  applyTheme,
  readThemePreference,
  setThemePreference,
  subscribeToSystemTheme,
  subscribeToThemePreference,
  ThemePreference,
} from "@/app/lib/theme";

const OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "system", label: "System" },
  { value: "dark", label: "Dark" },
];

export default function ThemeToggle() {
  // null on the server: the saved choice exists only in the browser.
  const preference = useSyncExternalStore(
    subscribeToThemePreference,
    readThemePreference,
    () => null,
  );

  // While "System" is selected, follow live changes of the operating system setting.
  useEffect(() => {
    if (preference !== "system") {
      return;
    }
    return subscribeToSystemTheme(() => applyTheme("system"));
  }, [preference]);

  return (
    <div
      role="radiogroup"
      aria-label="Color theme"
      className="inline-flex rounded-lg border border-zinc-200 bg-white p-1 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
    >
      {OPTIONS.map((option) => {
        const active = preference === option.value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => setThemePreference(option.value)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              active
                ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
