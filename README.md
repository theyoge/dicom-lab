# DICOM / PACS Security Lab

A self-contained lab for learning the offensive security of medical imaging
(DICOM) and PACS servers. This is **Series 01** of the medical-device security
path — the goal is to go from "what is DICOM" to fuzzing open-source PACS
software and finding real vulnerabilities.

> **Legal/ethical note:** everything here runs against a local container you
> control. Never point these tools at systems you don't own or have written
> authorization to test.

---

## What is DICOM / PACS?

- **DICOM** (Digital Imaging and Communications in Medicine, ISO 12052) is the
  standard format + protocol for medical images (CT, MRI, X-ray, ultrasound…).
- **PACS** (Picture Archiving and Communication System) is the archive/server
  that stores and serves those images.

DICOM is **insecure by design**: no mandatory authentication, no mandatory
encryption, and query/retrieve operations that happily hand over patient data.
Researchers routinely find thousands of PACS servers exposed on the internet.

## The DIMSE services we care about

| Service | Purpose | Offensive use |
|---|---|---|
| C-ECHO | "Are you alive?" | recon / fingerprinting |
| C-FIND | Query records | enumerate patients (PHI exfil) |
| C-STORE | Send an image | inject images / malformed files |
| C-MOVE / C-GET | Retrieve images | bounce attacks, data theft |

## Ports

- **4242** — DIMSE (the classic DICOM protocol)
- **8042** — DICOMweb (HTTP/REST) + the Orthanc web UI
- 104 / 11112 — other common DIMSE ports in the wild

---

## Quickstart

### 1. Start the lab

```bash
docker compose up -d --build
```

This launches:
- `pacs` — an Orthanc PACS on 4242 (DIMSE) and 8042 (web UI: http://localhost:8042)
- `client` — a Python/DCMTK container with all the tools pre-installed

> The lab ships an `orthanc-lab.json` override that **disables authentication**
> (`AuthenticationEnabled: false`) and **allows C-FIND/C-MOVE/C-GET from unknown
> modalities** — on purpose. A stock Orthanc would reject these by default, which
> is exactly the lesson: real-world PACS are often left wide open by
> misconfiguration, and that's what makes them such a high-yield target.

### 2. Generate sample "patients"

```bash
docker compose exec client python 00_generate_samples.py /images
```

This writes three fake CT studies into `./images/` (mounted into the container),
each containing PHI (name, ID, sex, birth date).

### 3. C-ECHO — connect

```bash
docker compose exec client python 01_c_echo.py pacs 4242
```

### 4. C-FIND — dump every patient (no auth!)

```bash
docker compose exec client python 02_c_find_enum.py pacs 4242
```

### 5. C-STORE — inject an image

```bash
docker compose exec client python 03_c_store.py /images/P0001.dcm pacs 4242
```

Open http://localhost:8042 in a browser, switch to the Study/Series view, and
you'll see the images now live in the PACS.

### 6. Watch the cleartext PHI with Wireshark / tshark

```bash
tshark -i any -f "tcp port 4242" -T fields -e frame.number -e _ws.col.Info
```

Run the C-FIND script again and watch patient names/IDs scroll by in plaintext.

---

## What's next (Series roadmap)

1. **DICOM file format** — 128-byte preamble + `DICM` magic, then
   `(group,element) VR length value` elements. Dump with `dcmdump`, parse by
   hand with `pydicom`, then reimplement a parser yourself.
2. **Attack the DICOMweb REST API** (port 8042) — QIDO-RS / WADO-RS / STOW-RS.
3. **Fuzzing** — build DCMTK and Orthanc with AddressSanitizer, feed mutated
   DICOM via AFL++/libFuzzer, hunt for parser bugs.
4. **Real-world research** — read the IOActive "Penetration Testing of the DICOM
   Protocol" paper, reproduce known CVEs (e.g. DCMTK CVE-2026-50003), then look
   for new ones.

## File layout

```
dicom-lab/
├── docker-compose.yml
├── requirements.txt
├── client/Dockerfile          # dcmtk + pynetdicom + pydicom
├── images/                    # generated sample DICOM files
└── scripts/
    ├── 00_generate_samples.py # create fake patients
    ├── 01_c_echo.py           # connectivity check
    ├── 02_c_find_enum.py      # enumerate patients (PHI exfil)
    └── 03_c_store.py          # inject an image
```

## Key references

- DCMTK — https://github.com/DCMTK/dcmtk
- Orthanc — https://github.com/jodogne/Orthanc
- pynetdicom — https://github.com/pydicom/pynetdicom
- IOActive — "Penetration Testing of the DICOM Protocol: Real-World Attacks"
- DICOM fuzzing corpus — https://github.com/pwnlabmx/dicom-fuzzing-corpus
- DICOM fuzzer — https://github.com/r1b/dicom-fuzz
