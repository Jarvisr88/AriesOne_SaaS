import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
  sidebarOpen: boolean;
  activeModal: string | null;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
  }>;
  loading: {
    [key: string]: boolean;
  };
}

const initialState: UiState = {
  sidebarOpen: true,
  activeModal: null,
  notifications: [],
  loading: {},
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setActiveModal: (state, action: PayloadAction<string | null>) => {
      state.activeModal = action.payload;
    },
    addNotification: (
      state,
      action: PayloadAction<{
        type: 'success' | 'error' | 'info' | 'warning';
        message: string;
      }>
    ) => {
      const id = Math.random().toString(36).substr(2, 9);
      state.notifications.push({
        id,
        ...action.payload,
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    setLoading: (
      state,
      action: PayloadAction<{ key: string; value: boolean }>
    ) => {
      state.loading[action.payload.key] = action.payload.value;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  setActiveModal,
  addNotification,
  removeNotification,
  setLoading,
} = uiSlice.actions;

export default uiSlice.reducer;
