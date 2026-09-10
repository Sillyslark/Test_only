# Scanner Test Case 05 — Multiple Titles and Products

本测试只验证一个行为：

```text
当 cards/ 下同时存在多个 Title Code 与多个 Product Code 时，
Card Scanner 应完整发现所有 JSON 文件。
```

测试输入：

```text
cards/
├─ TEST/
│  ├─ TE01/
│  │  └─ TEST_W_TE01_T001.json
│  └─ TE02/
│     └─ TEST_W_TE02_T001.json
└─ DEMO/
   └─ DE01/
      └─ DEMO_S_DE01_D001.json
```

预期结果：

```text
cards/DEMO/DE01/DEMO_S_DE01_D001.json
cards/TEST/TE01/TEST_W_TE01_T001.json
cards/TEST/TE02/TEST_W_TE02_T001.json
```

本测试不检查：

```text
JSON 内容是否合法
目录结构是否合法
Card Number 是否正确
```

这些属于后续 Validator。

运行：

```powershell
pytest tests/scanner/test_case_05_multiple_titles_products.py -v
```

测试实际输出会写入：

```text
tests/artifacts/scanner/case_05_multiple_titles_products.json
```

该 artifact 当前允许被后续测试覆盖。
