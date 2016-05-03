FROM apsl/gcloud

RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
      curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fSLk 'https://bootstrap.pypa.io/get-pip.py' | python
RUN pip install sh

COPY GCE-Cluster-Control/gce-cluster-control.py /

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
# CMD ["status"]