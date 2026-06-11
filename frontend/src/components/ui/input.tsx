import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, icon, ...props }, ref) => {
    return (
      <div className="relative w-full group">
        {icon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-aether-indigo transition-colors duration-200">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            "flex h-11 w-full rounded-xl border border-aether bg-obsidian-depth/80 px-4 py-3 text-sm font-semibold text-foreground ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted/60 focus-visible:outline-none focus-visible:border-aether-indigo/50 focus-visible:ring-4 focus-visible:ring-aether-indigo/10 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-300 focus-visible:shadow-[0_0_20px_rgba(91,108,249,0.08)]",
            icon && "pl-11",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
