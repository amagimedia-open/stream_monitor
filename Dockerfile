FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /home/root/
COPY ["rtpdump", "/usr/local/bin/"]
COPY ["requirements.txt", "logger.py", "stream_monitor.sh", "stream_monitor.py", "/home/root/"]
ENV PATH /opt/conda/bin:$PATH

RUN buildDeps='wget ca-certificates dpkg-dev doxygen dos2unix graphviz curl pcscd libpcsclite-dev libcppunit-dev tclsh pkg-config cmake build-essential'\
    && apt-get update && apt-get install -y $buildDeps libcurl4 libcurl4-openssl-dev libssl-dev --no-install-recommends \
    && wget https://github.com/tsduck/tsduck/releases/download/v3.16-1110/tsduck_3.16-1110_amd64.deb \
    && dpkg -i tsduck_3.16-1110_amd64.deb \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-4.6.14-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && pip install --ignore-installed -r requirements.txt \
    && wget https://github.com/Haivision/srt/archive/v1.3.2.tar.gz \
    && tar -xvf v1.3.2.tar.gz \
    && cd srt-1.3.2 \
    && ./configure && make && make install \
    && cd - && rm v1.3.2.tar.gz \
    && apt-get purge -y --auto-remove $buildDeps








