# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install system dependencies required for mysqlclient
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
