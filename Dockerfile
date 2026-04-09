FROM python:3.9

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
