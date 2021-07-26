FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY cert_inspect.py .

CMD [ "python", "./cert_inspect.py" ]