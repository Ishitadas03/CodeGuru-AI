import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string | number, formatStr: string = "MMM dd, yyyy") {
  if (!date) return "";
  try {
    const parsedDate = typeof date === "string" ? parseISO(date) : new Date(date);
    return format(parsedDate, formatStr);
  } catch (error) {
    return String(date);
  }
}

export function truncate(str: string, length: number): string {
  if (!str) return "";
  return str.length > length ? str.substring(0, length) + "..." : str;
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return function(this: any, ...args: Parameters<T>) {
    const context = this;
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}
