FROM lambci/lambda:build-python3.7
WORKDIR /deploy
RUN mkdir -p /deploy/.chalice
ADD app.py /deploy
ADD requirements.txt /deploy
ADD .chalice/config.json /deploy/.chalice/
RUN echo "Europe/Helsinki" > /etc/timezone
RUN pip install -r requirements.txt
