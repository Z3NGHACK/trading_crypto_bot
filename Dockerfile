FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install pandas ccxt python-dotenv

CMD ["python", "main.py"]