from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('Caden1234!')
print(f"UPDATE user SET password_hash = '{password_hash}' WHERE employee_number = 'ADMIN001';")

