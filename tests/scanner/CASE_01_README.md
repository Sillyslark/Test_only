# Scanner Test Case 01 — Basic Discovery

This case verifies one behavior only:

```text
Given three JSON files in a valid cards/<title_code>/<product_code>/ directory,
the Card Scanner discovers exactly those three files.
```

Expected result:

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
cards/TEST/TE01/TEST_W_TE01_T002.json
cards/TEST/TE01/TEST_W_TE01_T003.json
```

The test also writes the actual result to:

```text
tests/artifacts/scanner/case_01_basic.json
```

The artifact may be overwritten by later runs.
