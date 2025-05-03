FROM python:3.11

WORKDIR /app

COPY ml-service /app

ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
