FROM python:3.11-slim

# Install required packages
RUN pip install psycopg2-binary werkzeug

# Copy the initialization script
COPY db-init-simple.py /app/db-init-simple.py

# Set working directory
WORKDIR /app

# Make script executable
RUN chmod +x db-init-simple.py

# Run the initialization script
CMD ["python", "db-init-simple.py"]
