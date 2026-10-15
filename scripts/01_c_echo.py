"""C-ECHO: the DICOM equivalent of ping.

Establishes an association with a PACS and sends a verification request.
Usage: python 01_c_echo.py [host] [port]
"""
import os
import sys

from pynetdicom import AE
from pynetdicom.sop_class import Verification

HOST = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PACS_HOST", "127.0.0.1")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PACS_PORT", "4242"))

ae = AE()
ae.add_requested_context(Verification)

print(f"[*] Associating with {HOST}:{PORT} ...")
assoc = ae.associate(HOST, PORT)

if assoc.is_established:
    status = assoc.send_c_echo()
    if status:
        ok = status.Status == 0x0000
        print(f"[+] C-ECHO response: 0x{status.Status:04X} ({'Success' if ok else 'Failed'})")
    assoc.release()
else:
    print("[-] Association rejected.")
