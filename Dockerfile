FROM odoo:13.0
LABEL Aashim Bajracharya. <ashimbazracharya@gmail.com>

USER root
RUN mkdir -p /mnt/custom_addons

RUN apt-get update \
    && apt-get install

RUN chown -R odoo /mnt
RUN chown -R odoo /mnt/*
