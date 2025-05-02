import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import toolsReducer from './toolsSlice';
import checkoutsReducer from './checkoutsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tools: toolsReducer,
    checkouts: checkoutsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
