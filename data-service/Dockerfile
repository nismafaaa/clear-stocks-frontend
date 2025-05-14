FROM python:3.11

WORKDIR /app

COPY data-service /app

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8001

# Run service FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]