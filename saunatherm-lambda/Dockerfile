FROM lambci/lambda:build-python3.7
RUN mkdir -p /deploy/.chalice
ADD app.py /deploy
ADD .chalice/config.json /deploy/.chalice/
WORKDIR /deploy
RUN echo "Europe/Helsinki" > /etc/timezone
RUN pip install chalice
