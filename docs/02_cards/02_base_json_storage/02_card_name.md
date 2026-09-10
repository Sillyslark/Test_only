# 2.2.2 卡名 / Card Name

<!-- SUBSECTION_NAV_START -->
[← 上一小节](01_card_number.md) | [返回 2.2 目录](README.md) | [下一小节 →](03_card_type.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Card Name  
**程序字段：** `name`

Card Name 在 Card JSON 中使用字符串保存。

JSON 示例：

```json
{
  "name": "カード名"
}
```

字段类型：

```text
string
```

适用 Card Type：

```text
Character（角色）
Event（事件）
Climax（高潮）
```

三类 Card Type 都必须具有 `name` 字段。

规则与约束：

- `name` 必须存在；
- `name` 的值必须为字符串；
- 不使用 `null` 表示卡名缺失；
- 不从 Card Number、Card Text 或其他字段自动推导卡名；
- `name` 只保存该 Card Definition 的卡名本身，不承担 UI 别名、翻译名或其他显示层职责。

对应 Definition 字段：

```python
name: str
```

Card Name 属于 Card Definition 的基础静态信息。运行时 Card Instance 不复制一份独立卡名，而是通过其关联的 Card Definition 取得该信息。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](01_card_number.md) | [返回 2.2 目录](README.md) | [下一小节 →](03_card_type.md)
<!-- SUBSECTION_NAV_END -->
