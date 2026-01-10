FROM python:3.11-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev curl gcc libffi-dev libssl-dev pkg-config libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY . /app

EXPOSE 8000
CMD ["bash","-lc","python manage.py runserver 0.0.0.0:8000"]
