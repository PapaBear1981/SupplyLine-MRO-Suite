FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/flask_session /app/database
RUN touch /app/database/tools.db
RUN chmod -R 777 /app/database /app/flask_session

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 5000

# Copy the database schema update script
COPY update_tools_schema.py /app/

# Create an entrypoint script to run the schema update before starting the app
RUN echo '#!/bin/sh\n\
echo "Running database schema update..."\n\
python /app/update_tools_schema.py\n\
echo "Starting application..."\n\
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Command to run the application
CMD ["/app/entrypoint.sh"]
