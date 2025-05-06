FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the gRPC port
EXPOSE 50051

# Start the ERP2 server
CMD ["python", "-m", "app.main"]