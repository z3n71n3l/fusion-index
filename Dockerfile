FROM fusionapp/base

COPY requirements.txt /application/requirements.txt
RUN /appenv/bin/pip install --no-cache-dir --requirement /application/requirements.txt
COPY . /application
RUN /appenv/bin/pip install --no-cache-dir /application

EXPOSE 80
WORKDIR "/db"
CMD ["/appenv/bin/twistd", "--nodaemon", "fusion-index", "--db", "/db/fusion-index.axiom"]
