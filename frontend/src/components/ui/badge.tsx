import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-[20px] border px-3 py-1 text-[11px] font-medium tracking-[0.2px] transition-colors duration-200 select-none",
  {
    variants: {
      variant: {
        primary:
          "bg-aether-indigo/10 border-aether-indigo/25 text-[#A4AFFF] shadow-[0_0_8px_rgba(91,108,249,0.15)]",
        secondary:
          "bg-aether-violet/10 border-aether-violet/25 text-[#C9A9F9] shadow-[0_0_8px_rgba(155,89,245,0.15)]",
        success:
          "bg-aether-emerald/10 border-aether-emerald/20 text-[#6EE7B7] shadow-[0_0_8px_rgba(52,211,153,0.15)]",
        danger:
          "bg-aether-rose/10 border-aether-rose/20 text-[#F9A8D4] shadow-[0_0_8px_rgba(244,114,182,0.15)]",
        warning:
          "bg-aether-amber/10 border-aether-amber/20 text-[#FCD34D] shadow-[0_0_8px_rgba(251,191,36,0.15)]",
        teal:
          "bg-aether-teal/10 border-aether-teal/25 text-[#7EE8F5] shadow-[0_0_8px_rgba(34,211,238,0.15)]",
        purple:
          "bg-aether-purple/10 border-aether-purple/20 text-[#D8B4FE] shadow-[0_0_8px_rgba(168,85,247,0.15)]",
        aurora:
          "bg-aether-aurora/10 border-aether-aurora/20 text-[#7DD3FC] shadow-[0_0_8px_rgba(56,189,248,0.15)]",
        outline: "text-foreground border-border",
      },
    },
    defaultVariants: {
      variant: "primary",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
