# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables to prevent buffering of stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
