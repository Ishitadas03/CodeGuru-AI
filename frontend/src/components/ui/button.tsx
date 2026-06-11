import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { magneticHover } from "@/lib/animations";
import { useUIStore } from "@/store/uiStore";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-aether-indigo disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden select-none active:translate-y-0.5",
  {
    variants: {
      variant: {
        primary:
          "bg-gradient-to-br from-aether-indigo to-aether-violet border-none text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.1),0_4px_20px_rgba(91,108,249,0.35)] transition-all duration-250 ease-[cubic-bezier(0.23,1,0.32,1)] hover:from-[#6B7CFF] hover:to-[#A869F7] hover:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.15),0_6px_28px_rgba(91,108,249,0.5),0_0_60px_rgba(155,89,245,0.2)] hover:-translate-y-0.5",
        secondary:
          "bg-aether-teal/10 border border-aether-teal/30 text-aether-teal hover:bg-aether-teal/20 hover:border-aether-teal/50 shadow-[0_0_15px_rgba(34,211,238,0.15)]",
        outline:
          "bg-aether-indigo/5 border border-aether-indigo/20 text-[#A4AFFF] hover:border-aether-teal/40 hover:text-aether-teal hover:bg-aether-indigo/10",
        ghost:
          "text-[#8892B0] hover:bg-aether-indigo/5 hover:text-aether-teal",
        danger:
          "bg-aether-rose/10 border border-aether-rose/30 text-aether-rose hover:bg-aether-rose/20 hover:border-aether-rose/50 shadow-[0_0_15px_rgba(244,114,182,0.15)]",
      },
      size: {
        default: "h-11 px-5 py-2.5",
        sm: "h-9 rounded-lg px-3.5 text-[10px]",
        lg: "h-14 rounded-2xl px-8 text-sm",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  magnetic?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, magnetic = true, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    const localRef = React.useRef<HTMLButtonElement>(null);
    const setCursorType = useUIStore((state) => state.setCursorType);

    // Merge refs
    const combinedRef = (node: HTMLButtonElement) => {
      // @ts-ignore
      localRef.current = node;
      if (typeof ref === "function") ref(node);
      else if (ref) ref.current = node;
    };

    React.useEffect(() => {
      if (!magnetic || !localRef.current) return;
      const cleanup = magneticHover(localRef.current);
      return cleanup;
    }, [magnetic]);

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={combinedRef as any}
        onMouseEnter={() => setCursorType("hover")}
        onMouseLeave={() => setCursorType("default")}
        onMouseDown={() => setCursorType("active")}
        onMouseUp={() => setCursorType("hover")}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
