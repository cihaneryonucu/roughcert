FROM python:3

LABEL version="1.0"
LABEL mantainer="marcosp@kth.se"
LABEL description="Contact server for secureChat application"


EXPOSE 10050/tcp

ENV ZMQ_VERSION 4.1.4

# Install needed packages
RUN apt-get update && apt-get install -y --fix-missing \
    apt-utils \
    curl \
    libtool \
    pkg-config \
    build-essential \
    autoconf \
    automake \
    && mkdir -p /tmp/zeromq \
    && curl -SL http://download.zeromq.org/zeromq-$ZMQ_VERSION.tar.gz | tar zxC /tmp/zeromq \
    && cd /tmp/zeromq/zeromq-$ZMQ_VERSION/ \
    && ./configure --without-libsodium \
    && make \
    && make install \
    && ldconfig \
    && rm -rf /tmp/zeromq \
    && apt-get purge -y \
    curl \
    libtool \
    pkg-config \
    build-essential \
    autoconf \
    automake \
    && apt-get clean && apt-get autoclean && apt-get -y autoremove

COPY server.py ./
COPY python-requirements.txt ./

RUN  pip install --no-cache-dir -r python-requirements.txt

CMD [ "python", "./server.py" ]