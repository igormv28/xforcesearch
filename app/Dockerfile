FROM ubuntu:latest
LABEL author="https://github.com/igormv28" 

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip && \
    apt-get clean;

EXPOSE 8080
COPY . /app
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install cryptography
RUN chmod g+w /app

CMD python app.py
