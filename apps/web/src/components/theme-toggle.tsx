"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Moon, Sun, Monitor } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return <span className="inline-block h-11 w-[132px]" aria-hidden />;
  const opts = [
    { v: "light", icon: Sun, label: "Light theme" },
    { v: "dark", icon: Moon, label: "Dark theme" },
    { v: "system", icon: Monitor, label: "Follow system theme" },
  ] as const;
  return (
    <div role="group" aria-label="Theme" className="inline-flex rounded-xl border border-border bg-bg-elev p-0.5">
      {opts.map(({ v, icon: Icon, label }) => (
        <button key={v} type="button" aria-label={label} aria-pressed={theme === v} onClick={() => setTheme(v)}
          className={`inline-flex h-10 w-10 min-h-0 items-center justify-center rounded-lg ${theme === v ? "bg-accent text-accent-fg" : "text-fg-muted hover:text-fg"}`}>
          <Icon className="h-4 w-4" aria-hidden />
        </button>
      ))}
    </div>
  );
}
