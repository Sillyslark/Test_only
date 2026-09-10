# Scanner Test Case 06 — Empty cards/

本测试只验证一个行为：

```text
当 cards/ 目录存在但其中没有任何 JSON 文件时，
Card Scanner 应正常返回空列表，而不是报错。
```

测试输入：

```text
tests/fixtures/scanner/case_06_empty/
└─ cards/
```

`cards/` 目录存在，但为空。

预期结果：

```json
[]
```

本测试用于区分：

```text
cards/ 存在但为空
→ 合法扫描场景
→ 返回 []

cards/ 不存在
→ 调用 / 配置错误
→ 应由 Scanner 报错
```

运行：

```powershell
pytest tests/scanner/test_case_06_empty.py -v
```

测试实际输出会写入：

```text
tests/artifacts/scanner/case_06_empty.json
```

预期 artifact 内容同样为：

```json
[]
```
