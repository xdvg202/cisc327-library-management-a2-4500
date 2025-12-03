# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY app.py .
COPY database.py .
COPY routes/ ./routes/
COPY services/ ./services/
COPY templates/ ./templates/

# Expose port 5000
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]

