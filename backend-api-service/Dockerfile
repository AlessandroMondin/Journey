FROM python:3.9-slim

WORKDIR /app

# Install SQLite and other dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Explicitly install email-validator
RUN pip install --no-cache-dir email-validator

# Copy the rest of the application
COPY . .

# Create SQLite data directory
RUN mkdir -p /var/lib/sqlite

# Expose port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
