# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements (create one if needed)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Railway sets PORT dynamically
ENV PORT=3000
EXPOSE ${PORT}

# Run with gunicorn for production
CMD gunicorn --bind 0.0.0.0:${PORT} app:app
