FROM fusionapp/base

COPY requirements.txt /application/requirements.txt
RUN /appenv/bin/pip install --no-cache-dir --requirement /application/requirements.txt
COPY . /application
RUN /appenv/bin/pip install --no-cache-dir /application

EXPOSE 8443
WORKDIR "/db"
ENTRYPOINT ["/appenv/bin/axiomatic", "-d", "/db/fusion-index.axiom"]
CMD ["start", "--pidfile", "", "--nodaemon"]
