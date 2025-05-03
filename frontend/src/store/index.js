import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import toolsReducer from './toolsSlice';
import checkoutsReducer from './checkoutsSlice';
import usersReducer from './usersSlice';
import auditReducer from './auditSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tools: toolsReducer,
    checkouts: checkoutsReducer,
    users: usersReducer,
    audit: auditReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
