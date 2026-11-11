// Shared Tailwind class lists, so every card and field looks the same in light and dark mode.

export const CARD_CLASS =
  "rounded-xl border border-zinc-200 bg-white p-4 shadow-sm sm:p-8 " +
  "dark:border-zinc-800 dark:bg-zinc-900";

export const CARD_TITLE_CLASS =
  "border-b border-zinc-200 pb-3 text-lg font-bold text-zinc-900 sm:text-xl " +
  "dark:border-zinc-800 dark:text-zinc-50";

export const SECTION_TITLE_CLASS =
  "text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400";

export const LABEL_CLASS = "block text-sm font-medium text-zinc-700 dark:text-zinc-300";

// text-base below the "sm" breakpoint: iOS zooms into fields whose font is smaller than 16px.
export const INPUT_CLASS =
  "mt-1 block w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-base " +
  "text-zinc-900 shadow-sm focus:border-zinc-900 focus:outline-none focus:ring-1 " +
  "focus:ring-zinc-900 sm:text-sm dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 " +
  "dark:focus:border-zinc-300 dark:focus:ring-zinc-300";
