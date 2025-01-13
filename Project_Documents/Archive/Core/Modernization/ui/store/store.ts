import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Store {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useStore = create<Store>()(
  persist(
    (set) => ({
      isSidebarOpen: true,
      toggleSidebar: () =>
        set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      setSidebarOpen: (open) => set({ isSidebarOpen: open }),
    }),
    {
      name: 'ariesone-layout',
    }
  )
);
