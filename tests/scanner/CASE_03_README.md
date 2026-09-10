# Scanner Test Case 03 — Wrong Paths Inside cards/

This case verifies one behavior only:

```text
A JSON file located anywhere inside cards/ is still discovered by the Card Scanner,
even when its directory structure is invalid.
```

Fixture:

```text
cards/TEST_W_TE01_T001.json
cards/TEST/TEST_W_TE01_T002.json
cards/TEST/TE01/extra/TEST_W_TE01_T003.json
```

All three paths are intentionally invalid according to the Card storage layout,
but all three are still within the Card Scanner boundary.

Expected behavior:

```text
Scanner
→ discovers all three JSON files

Validator
→ later decides that their paths are invalid
```

The test writes the actual result to:

```text
tests/artifacts/scanner/case_03_wrong_paths.json
```
