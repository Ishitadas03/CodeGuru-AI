import { create } from "zustand";

interface UIState {
  cursorType: "default" | "hover" | "active";
  sidebarOpen: boolean;
  pageTransitionState: "idle" | "exiting" | "entering";
  setCursorType: (type: "default" | "hover" | "active") => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setPageTransitionState: (state: "idle" | "exiting" | "entering") => void;
}

export const useUIStore = create<UIState>((set) => ({
  cursorType: "default",
  sidebarOpen: true,
  pageTransitionState: "idle",
  setCursorType: (cursorType) => set({ cursorType }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setPageTransitionState: (pageTransitionState) => set({ pageTransitionState }),
}));
