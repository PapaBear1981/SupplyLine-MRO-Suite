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
import adminReducer from './adminSlice';
import announcementsReducer from './announcementSlice';
import cycleCountReducer from './cycleCountSlice';
import kitsReducer from './kitsSlice';
import kitTransfersReducer from './kitTransfersSlice';
import kitMessagesReducer from './kitMessagesSlice';
import departmentsReducer from './departmentsSlice';
import securityReducer from './securitySlice';
import messagingReducer from './messagingSlice';
import ordersReducer from './ordersSlice';
import userRequestsReducer from './userRequestsSlice';

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
    admin: adminReducer,
    announcements: announcementsReducer,
    cycleCount: cycleCountReducer,
    kits: kitsReducer,
    kitTransfers: kitTransfersReducer,
    kitMessages: kitMessagesReducer,
    departments: departmentsReducer,
    security: securityReducer,
    messaging: messagingReducer,
    orders: ordersReducer,
    userRequests: userRequestsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
