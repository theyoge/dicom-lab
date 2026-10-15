"""C-STORE: push a DICOM file into the PACS.

Demonstrates that a remote node can inject arbitrary images (and, with a
bit more work, malformed files to trigger parser bugs).
Usage: python 03_c_store.py <file.dcm> [host] [port]
"""
import os
import sys

from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage

if len(sys.argv) < 2:
    print("Usage: python 03_c_store.py <file.dcm> [host] [port]")
    sys.exit(1)

path = sys.argv[1]
HOST = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("PACS_HOST", "127.0.0.1")
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else int(os.environ.get("PACS_PORT", "4242"))

ds = dcmread(path)

ae = AE()
ae.add_requested_context(CTImageStorage)

print(f"[*] Sending {path} to {HOST}:{PORT} ...")
assoc = ae.associate(HOST, PORT)

if not assoc.is_established:
    print("[-] Association rejected.")
    sys.exit(1)

status = assoc.send_c_store(ds)
if status:
    print(f"[+] C-STORE response: 0x{status.Status:04X}")
    if status.Status == 0x0000:
        print(f"    Image stored as patient {ds.PatientName} ({ds.PatientID})")
assoc.release()
