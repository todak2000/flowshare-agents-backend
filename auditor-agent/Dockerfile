FROM python:3.11-slim

WORKDIR /app

# Copy shared dependencies
COPY shared/ ./shared/

# Copy agent code
COPY auditor-agent/requirements.txt .
COPY auditor-agent/*.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8081

# Set environment
ENV PORT=8081
ENV PYTHONUNBUFFERED=1

# Run application
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
