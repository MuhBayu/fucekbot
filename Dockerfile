FROM python:3.6-alpine

RUN apk update && apk add --no-cache bash \
    && pip install --upgrade pip

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app

RUN pip --no-cache-dir install -r requirements.txt

CMD ["python", "app.py"]