FROM python:3.8

COPY . /root/opendrive2lanelet

WORKDIR /root/opendrive2lanelet

RUN python -m pip install --upgrade pip setuptools
RUN python -m pip install numpy==1.21.0 scipy==1.7.3 lxml commonroad-io==2019.1 pyproj lmfit PyQt5 matplotlib
RUN python setup.py install
RUN chmod +x /root/opendrive2lanelet/run.sh
CMD  /root/opendrive2lanelet/run.sh
