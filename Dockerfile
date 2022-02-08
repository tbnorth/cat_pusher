FROM python:3.10

WORKDIR /cat_pusher

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ./* ./

CMD ["python", "-u", "cat_push.py"]

