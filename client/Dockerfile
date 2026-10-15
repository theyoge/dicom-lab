FROM python:3.12-slim

# DICOM CLI tools (dcmtk) + Python DICOM libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends dcmtk curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pynetdicom pydicom

WORKDIR /scripts
