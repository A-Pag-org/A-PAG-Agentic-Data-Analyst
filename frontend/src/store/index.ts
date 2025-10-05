import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AppState {
  // Single user session
  isAuthenticated: boolean;
  sessionToken: string | null;
  
  // UI state
  sidebarOpen: boolean;
  
  // Actions
  setAuthenticated: (value: boolean, token?: string) => void;
  toggleSidebar: () => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        isAuthenticated: false,
        sessionToken: null,
        sidebarOpen: true,
        
        setAuthenticated: (value, token) =>
          set({ isAuthenticated: value, sessionToken: token }),
        
        toggleSidebar: () =>
          set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        
        logout: () =>
          set({ isAuthenticated: false, sessionToken: null }),
      }),
      {
        name: 'app-storage',
      }
    )
  )
);