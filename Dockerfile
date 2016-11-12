## DOCKER-FILE FOR NEXTBUSAPI
FROM python:2.7.12

COPY . /srv

WORKDIR /srv 

RUN pip install -r requirements.txt

ENV PYTHON_PATH /srv/extensions/

EXPOSE 8889

CMD python server.py
#CMD gunicorn server:app -k gevent -w 2
