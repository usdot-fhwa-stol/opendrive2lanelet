FROM python:3.6

COPY . /root/opendrive2lanelet

Workdir /root/opendrive2lanelet

RUN python setup.py install
RUN chmod +x /root/opendrive2lanelet/run.sh
CMD  /root/opendrive2lanelet/run.sh