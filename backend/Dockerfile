FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn motor

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]