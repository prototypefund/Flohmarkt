FROM docker.io/library/python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

ADD flohmarkt ./flohmarkt
ADD static ./static
ADD templates ./templates

COPY ./docker/config_generator.py /
COPY ./docker/entrypoint.sh /
COPY ./initialize_couchdb.py .

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["default"]
