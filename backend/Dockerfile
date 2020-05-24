FROM python:3.8

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app


RUN mkdir -p /app/uploads && touch /app/uploads/meta

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]