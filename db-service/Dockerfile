FROM python:3.11

WORKDIR /app

COPY db-service /app

ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]