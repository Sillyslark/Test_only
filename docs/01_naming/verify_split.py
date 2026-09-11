from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
MARKER = "<!-- NAVIGATION_START -->\n"
preamble = README.split(MARKER, 1)[0].encode("utf-8")

PARTS = ['01_naming_overview.md', '02_official_and_project_concepts.md', '03_category_first.md', '04_definition_and_instance.md', '05_stable_identity.md', '06_actions_choices_events.md', '07_disambiguation.md', '08_official_terms_priority.md', '09_document_usage.md', '10_owner_master_player_control.md']
rebuilt = preamble + b"".join((ROOT / name).read_bytes() for name in PARTS)

EXPECTED_SHA256 = "e3cb2a225b7beb977d459803eb5a3e2f5fdf431a2f7451cd54475346f235ba24"
EXPECTED_GIT_BLOB_SHA1 = "b057b806b1d5edc37d206a923b85cb47bfffc048"

sha256 = hashlib.sha256(rebuilt).hexdigest()
git_blob_sha1 = hashlib.sha1(f"blob {len(rebuilt)}\0".encode() + rebuilt).hexdigest()

print("Rebuilt bytes:", len(rebuilt))
print("SHA-256:", sha256)
print("Git blob SHA-1:", git_blob_sha1)

if sha256 != EXPECTED_SHA256:
    raise SystemExit("FAIL: SHA-256 mismatch")
if git_blob_sha1 != EXPECTED_GIT_BLOB_SHA1:
    raise SystemExit("FAIL: Git blob SHA-1 mismatch")

print("PASS: preamble + 10 subsection files reconstruct the original exactly.")
