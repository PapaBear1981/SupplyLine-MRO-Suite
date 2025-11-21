# PR 498 Quick Testing Guide

## 🚀 Quick Start

The application is now running at: **http://localhost:5173**

## 🎯 Essential Tests (5 minutes)

### 1. View the Hotkey Help (30 seconds)
**Action:** Press `Ctrl+/` (or `Cmd+/` on Mac)  
**Expected:** A modal should appear showing all available keyboard shortcuts organized by category

**What to check:**
- ✅ Modal opens smoothly
- ✅ Categories are clearly labeled (Navigation, Actions, List Views, etc.)
- ✅ Keys are displayed correctly (Ctrl vs ⌘ based on your OS)
- ✅ Modal has a clean, modern design
- ✅ Close button works
- ✅ Pressing `Escape` closes the modal

---

### 2. Test Navigation Hotkeys (2 minutes)

Try these shortcuts from any page:

| Hotkey | Expected Result |
|--------|----------------|
| `Ctrl+D` | Navigate to Dashboard |
| `Ctrl+T` | Navigate to Tools page |
| `Ctrl+K` | Navigate to Kits page |
| `Ctrl+C` | Navigate to Chemicals page |
| `Ctrl+O` | Navigate to Orders page |
| `Ctrl+H` | Navigate to History page |

**What to check:**
- ✅ Each hotkey navigates to the correct page
- ✅ Navigation is instant (no delay)
- ✅ Works from any page in the application
- ✅ If you don't have permission for a page, the hotkey should not navigate

---

### 3. Test Action Hotkeys (1 minute)

| Hotkey | Expected Result |
|--------|----------------|
| `Ctrl+P` | Open Profile modal (NOT browser print dialog) |
| `Ctrl+Shift+T` | Toggle between light and dark theme |
| `Ctrl+/` | Show/hide hotkey help modal |

**What to check:**
- ✅ `Ctrl+P` opens your profile (browser print should NOT appear)
- ✅ Theme toggle works smoothly with animation
- ✅ Help modal toggles on/off

---

### 4. Test Input Field Detection (1 minute)

**Action:** 
1. Go to any page with a search box (like Tools or Kits)
2. Click in the search box
3. Try typing the letter `n` or `/`

**Expected:** 
- ✅ The letters should appear in the search box (NOT trigger hotkeys)
- ✅ `Ctrl+/` should STILL work (open help modal) even while typing
- ✅ `Escape` should STILL work to close modals

---

### 5. Test Preferences Toggle (30 seconds)

**Action:**
1. Press `Ctrl+P` to open Profile modal
2. Look for "Keyboard Shortcuts: Enabled" toggle
3. Turn it OFF
4. Close the modal
5. Try pressing `Ctrl+D`

**Expected:**
- ✅ Toggle switch is visible in Profile modal
- ✅ When OFF, hotkeys should NOT work
- ✅ When turned back ON, hotkeys should work again
- ✅ Setting persists after page reload

---

## 🎨 Visual Tests

### Dark Mode Test (30 seconds)
1. Press `Ctrl+Shift+T` to switch to dark mode
2. Press `Ctrl+/` to open help modal

**What to check:**
- ✅ Modal background is dark
- ✅ Text is readable (good contrast)
- ✅ Keyboard badges look good
- ✅ Hover effects work smoothly

---

## 🔐 Permission Tests (if applicable)

### Admin Shortcuts
If you're logged in as an admin:
- Press `Ctrl+Shift+A` - should navigate to Admin Dashboard
- Open help modal (`Ctrl+/`) - should see "Admin" category

If you're NOT an admin:
- `Ctrl+Shift+A` should do nothing
- Help modal should NOT show "Admin" category

---

## 🐛 Common Issues to Watch For

### Issue: Hotkeys don't work at all
**Check:**
- Are hotkeys enabled in Profile modal?
- Are you in an input field? (Try clicking outside first)
- Check browser console for errors (F12)

### Issue: Browser print dialog appears with Ctrl+P
**This is a bug** - the hotkey should prevent the default browser behavior

### Issue: Single letters trigger hotkeys while typing
**This is a bug** - single-key hotkeys should be disabled in input fields

### Issue: Help modal doesn't show all shortcuts
**Check:** Are you logged in? Some shortcuts require permissions

---

## ✅ Success Criteria

The PR is working correctly if:

1. ✅ Help modal opens with `Ctrl+/` and shows all shortcuts
2. ✅ Navigation hotkeys work from any page
3. ✅ `Ctrl+P` opens profile (NOT browser print)
4. ✅ Theme toggle works with `Ctrl+Shift+T`
5. ✅ Single-key hotkeys don't interfere with typing
6. ✅ Preferences toggle works and persists
7. ✅ Dark mode styling looks good
8. ✅ No console errors

---

## 📝 Reporting Issues

If you find any issues, please note:
- What hotkey you pressed
- What page you were on
- What happened vs. what should have happened
- Any console errors (F12 → Console tab)
- Your browser and OS

---

## 🎉 Quick Win Features

Try these cool features:
- **Rapid Navigation**: Press `Ctrl+D`, `Ctrl+T`, `Ctrl+K` in quick succession to jump between pages
- **Theme Toggle**: Press `Ctrl+Shift+T` multiple times to see the smooth theme transition
- **Help Anywhere**: Press `Ctrl+/` from any page to see available shortcuts
- **Smart Input**: Start typing in a search box - notice how hotkeys don't interfere!

---

**Estimated Testing Time:** 5-10 minutes for complete verification

