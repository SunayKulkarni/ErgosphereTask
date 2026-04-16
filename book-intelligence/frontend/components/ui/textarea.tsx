import * as React from "react";

import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => {
  return (
    <textarea
      ref={ref}
      className={cn(
        "min-h-24 w-full rounded-md border border-white/15 bg-panel/60 px-3 py-2 text-sm text-black placeholder:text-black/50 focus:border-gold/70 focus:outline-none",
        className,
      )}
      {...props}
    />
  );
});

Textarea.displayName = "Textarea";
