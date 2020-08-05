FROM python:3.7.5-alpine AS base
ARG USER=fmc
RUN addgroup -S ${USER} && adduser -S ${USER} -G ${USER}
RUN mkdir -p cisco-fmc-automation
WORKDIR cisco-fmc-automation
COPY . .
RUN pip install .
RUN chown -R ${USER}:${USER} /var/log
USER ${USER}
