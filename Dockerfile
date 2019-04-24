FROM ubuntu:18.04
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget ca-certificates dpkg-dev doxygen dos2unix graphviz curl pcscd libpcsclite-dev libcppunit-dev libcurl4 libcurl4-openssl-dev

WORKDIR /home/root/
COPY ["rtpdump", "/usr/local/bin/"]
COPY ["requirements.txt", "logger.py", "stream_monitor.py", "/home/root/"]
ENV PATH /opt/conda/bin:$PATH

RUN wget https://github.com/tsduck/tsduck/releases/download/v3.16-1110/tsduck_3.16-1110_amd64.deb \
    && dpkg -i tsduck_3.16-1110_amd64.deb \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-4.6.14-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && pip install --ignore-installed -r requirements.txt







