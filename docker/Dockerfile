FROM alpine

RUN apk add --update --no-cache bash python3
RUN ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip --upgrade

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ../requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

ADD ../src .

CMD ["python3", "./main.py"]