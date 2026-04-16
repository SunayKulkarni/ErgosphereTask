import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline" | "ghost";
};

const variantStyles: Record<NonNullable<ButtonProps["variant"]>, string> = {
  default:
    "bg-gold text-bg hover:bg-gold/90 border border-gold font-semibold shadow-glow disabled:opacity-60",
  outline:
    "border border-gold/60 bg-panel text-gold hover:bg-gold/10 disabled:opacity-60",
  ghost: "text-ink hover:bg-white/5 disabled:opacity-60",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm transition duration-200",
          variantStyles[variant],
          className,
        )}
        {...props}
      />
    );
  },
);

Button.displayName = "Button";
