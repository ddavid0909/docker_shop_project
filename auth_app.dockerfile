FROM ubuntu:latest
LABEL authors="fafulja"

ENTRYPOINT ["top", "-b"]