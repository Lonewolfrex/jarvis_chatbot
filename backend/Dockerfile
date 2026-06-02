FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl
COPY . .

CMD ["python","manage.py","runserver","0.0.0.0:8000"]