"""Generate synthetic DICOM files with PHI for the lab.

We create a few fake patients so we can demonstrate the core DICOM
insecurity: any node that can talk DIMSE can enumerate patient records
with an empty C-FIND query.
"""
import sys
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, UID, generate_uid

CT_STORAGE = UID("1.2.840.10008.5.1.4.1.1.2")

PATIENTS = [
    ("DOE^JOHN", "P0001", "M", "19750312"),
    ("ROE^JANE", "P0002", "F", "19881104"),
    ("SMITH^ALICE", "P0003", "F", "19650220"),
]


def make_dicom(patient_name, patient_id, sex, birth_date, out_path):
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = CT_STORAGE
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(out_path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientSex = sex
    ds.PatientBirthDate = birth_date
    ds.Modality = "CT"
    ds.StudyDescription = "ROUTINE HEAD CT"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = CT_STORAGE
    ds.Rows = 32
    ds.Columns = 32
    ds.SamplesPerPixel = 1
    ds.BitsAllocated = 16
    ds.PixelData = b"\x00\x11\x22\x33" * 512
    ds.save_as(out_path, enforce_file_format=True)
    print(f"  wrote {out_path} ({patient_name}, {patient_id})")


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("images")
    out_dir.mkdir(parents=True, exist_ok=True)
    print("Generating synthetic DICOM studies:")
    for name, pid, sex, dob in PATIENTS:
        make_dicom(name, pid, sex, dob, out_dir / f"{pid}.dcm")
    print("Done.")


if __name__ == "__main__":
    main()
