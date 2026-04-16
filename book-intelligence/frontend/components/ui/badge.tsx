import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "gold" | "green" | "red" | "gray";
};

const toneStyles: Record<NonNullable<BadgeProps["tone"]>, string> = {
  gold: "bg-gold/15 text-gold border border-gold/30",
  green: "bg-emerald-500/15 text-emerald-300 border border-emerald-400/40",
  red: "bg-rose-500/15 text-rose-300 border border-rose-400/40",
  gray: "bg-slate-500/15 text-slate-300 border border-slate-400/40",
};

export function Badge({ className, tone = "gold", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  );
}
