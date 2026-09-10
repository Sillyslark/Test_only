# Scanner Test Case 04 — Ignore JSON Outside cards/

This case verifies one behavior only:

```text
The Card Scanner scans only the supplied cards/ root.
JSON files in other data domains must not be discovered.
```

Fixture:

```text
cards/TEST/TE01/TEST_W_TE01_T001.json  → should be discovered
decks/sample_deck.json                  → should be ignored
```

Expected result:

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
```

The test writes the actual result to:

```text
tests/artifacts/scanner/case_04_ignore_outside_cards.json
```
