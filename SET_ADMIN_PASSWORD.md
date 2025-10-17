# Setting Admin Password to Caden1234!

## Quick Fix

Run this command in your PowerShell terminal (make sure you're in the project root and virtual environment is activated):

```powershell
python set_pw.py
```

This will set the admin password to `Caden1234!`

## Manual Method (if script doesn't work)

1. Open a Python shell in your virtual environment:
   ```powershell
   python
   ```

2. Run these commands:
   ```python
   import sys
   sys.path.insert(0, 'backend')
   from app import app, db
   from models import User
   
   with app.app_context():
       admin = User.query.filter_by(employee_number='ADMIN001').first()
       admin.set_password('Caden1234!')
       db.session.commit()
       print("Password updated!")
   ```

3. Exit Python:
   ```python
   exit()
   ```

## Login Credentials

After running either method above, you can login with:

- **Employee Number**: `ADMIN001`
- **Password**: `Caden1234!`

## Why This Password?

The password `Caden1234!` meets all security requirements:
- ✅ At least 12 characters long
- ✅ Contains uppercase letters (C)
- ✅ Contains lowercase letters (aden)
- ✅ Contains numbers (1234)
- ✅ Contains special characters (!)

## Troubleshooting

If you get "Admin not found" error, the admin user doesn't exist. In that case, restart the backend server - it will create the admin user automatically on startup.

## Security Note

After logging in for the first time, you should change this password to something more secure and personal through the application's profile settings.

