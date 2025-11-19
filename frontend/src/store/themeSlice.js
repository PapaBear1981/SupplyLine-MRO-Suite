import { createSlice } from '@reduxjs/toolkit';

// Get theme from localStorage or default to 'dark'
const getInitialTheme = () => {
  const savedTheme = localStorage.getItem('theme');
  return savedTheme || 'dark';
};

const initialState = {
  theme: getInitialTheme(),
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
      // Save to localStorage
      localStorage.setItem('theme', state.theme);
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
      // Save to localStorage
      localStorage.setItem('theme', state.theme);
    },
  },
});

export const { toggleTheme, setTheme } = themeSlice.actions;
export default themeSlice.reducer;
