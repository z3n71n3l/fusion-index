FROM fusionapp/base

COPY ["fusion-index.pex", "/application/fusion_index.pex"]
RUN ["/application/fusion_index.pex", "--version"]
EXPOSE 80
WORKDIR "/db"
CMD ["/application/fusion_index.pex", "--nodaemon", "--pidfile", "", "fusion-index", "--db", "/db/fusion-index.axiom"]
