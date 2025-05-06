FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app/erp

# Copy requirements first for caching Docker layers
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/erp

# Set the Python path so the "erp" module is correctly resolved
ENV PYTHONPATH=/app/erp

# Start the ERP server
CMD ["python", "server.py"]
