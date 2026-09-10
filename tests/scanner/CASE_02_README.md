# Scanner Test Case 02 — Ignore Non-JSON Files

This case verifies one behavior only:

```text
Given a valid Card JSON together with non-JSON files inside cards/,
the Card Scanner discovers only the JSON file.
```

Fixture contains:

```text
TEST_W_TE01_T001.json  → should be discovered
notes.txt               → should be ignored
README.md               → should be ignored
preview.png             → should be ignored
```

Expected result:

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
```

The test writes the actual result to:

```text
tests/artifacts/scanner/case_02_ignore_non_json.json
```
