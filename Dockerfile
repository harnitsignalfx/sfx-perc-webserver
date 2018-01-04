FROM python:alpine3.6

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY web-server.py ./

CMD python36 web-server.py
