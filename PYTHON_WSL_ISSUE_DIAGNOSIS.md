# Python Execution Issue - WSL Interception Diagnosis

## Problem Summary
All attempts to run Python (including `.venv\Scripts\python.exe`) result in the error:
```
did not find executable at '/usr/bin\python.exe': The system cannot find the path specified.
```

## Root Cause
**Windows Subsystem for Linux (WSL) is intercepting Python execution attempts.**

The error message `/usr/bin\python.exe` is a Unix-style path, which confirms that WSL is trying to handle the Python execution instead of Windows.

## Evidence
1. ✅ WSL is installed with Ubuntu as default distribution
2. ✅ Error message shows Unix path (`/usr/bin\python.exe`) on Windows system
3. ✅ Even `python.exe --version` fails with the same error
4. ✅ Issue persists after reboot
5. ✅ Issue occurs with absolute paths to python.exe

## Solution

### Option 1: Disable Windows App Execution Aliases (RECOMMENDED)
1. Open Windows Settings
2. Go to **Apps** → **Apps & features** → **App execution aliases**
3. Find entries for **python.exe** and **python3.exe**
4. **Turn OFF** both toggles

This will prevent Windows from redirecting `python` commands to the Microsoft Store or WSL.

### Option 2: Use Full Path with File Extension
Instead of:
```powershell
python set_pw.py
```

Use:
```powershell
& "C:\Users\Chris\Desktop\SupplyLine_MRO_Suite\.venv\Scripts\python.exe" set_pw.py
```

**Note**: This didn't work in our case because the interception happens even with full paths.

### Option 3: Temporarily Disable WSL Integration
```powershell
# Check current WSL status
wsl --status

# Shutdown WSL
wsl --shutdown

# Try running Python again
.\.venv\Scripts\python.exe set_pw.py
```

### Option 4: Use a Different Terminal
- Try running from **Command Prompt (cmd.exe)** instead of PowerShell
- Try running from **Windows Terminal** with a fresh profile

## Immediate Workaround for Password Update

Since we can't run Python scripts directly, here are alternative approaches:

### A. Use the Backend Server's Python Process
The backend server (Terminal 18) is already running Python successfully. We could:
1. Create a temporary API endpoint for password reset
2. Make an HTTP request to that endpoint

### B. Direct Database Update
Use SQLite command-line tool to update the database directly:
```sql
-- First, generate the password hash using an online tool or different Python installation
-- Then run:
sqlite3 database/tools.db "UPDATE user SET password_hash = '<GENERATED_HASH>' WHERE employee_number = 'ADMIN001';"
```

### C. Fix WSL Integration First
Follow Option 1 above to disable app execution aliases, then retry the password update script.

## Next Steps
1. **Disable App Execution Aliases** (Option 1 above)
2. **Retry password update script**
3. **Test login with new credentials**

## Related Files
- `set_pw.py` - Password update script
- `update_db_direct.py` - Direct database update script
- `SET_ADMIN_PASSWORD.md` - Password update documentation

## Technical Details
- **Python Version**: 3.13.8
- **Virtual Environment**: `.venv\Scripts\python.exe`
- **WSL Distribution**: Ubuntu (Default)
- **Error Pattern**: All Python execution attempts intercepted by WSL

