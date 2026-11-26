FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Install dependencies first, so rebuilds stay fast
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
