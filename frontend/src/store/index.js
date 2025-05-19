import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import toolsReducer from './toolsSlice';
import checkoutsReducer from './checkoutsSlice';
import usersReducer from './usersSlice';
import auditReducer from './auditSlice';
import themeReducer from './themeSlice';
import reportReducer from './reportSlice';
import chemicalsReducer from './chemicalsSlice';
import calibrationReducer from './calibrationSlice';
import rbacReducer from './rbacSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tools: toolsReducer,
    checkouts: checkoutsReducer,
    users: usersReducer,
    audit: auditReducer,
    theme: themeReducer,
    reports: reportReducer,
    chemicals: chemicalsReducer,
    calibration: calibrationReducer,
    rbac: rbacReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
