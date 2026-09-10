# 2.2.6 等级 / Level

<!-- SUBSECTION_NAV_START -->
[← 上一小节](05_trait.md) | [返回 2.2 目录](README.md) | [下一小节 →](07_cost.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Level  
**程序字段：** `level`

Level 在 Card JSON 中使用整数保存。

JSON 示例：

```json
{
  "level": 1
}
```

字段类型：

```text
integer
```

适用 Card Type：

```text
Character（角色）
Event（事件）
```

Character 与 Event 都必须具有 `level` 字段；Climax 不具有 Level 这一 Card Information。

规则与约束：

- Character / Event JSON 必须具有 `level` 字段；
- `level` 的值必须是整数；
- 允许值为 `0` 或更大的非负整数；
- 不使用 `null` 表示 Level 不存在；
- 不使用字符串形式的数字，例如 `"1"`；
- Climax JSON 中不得出现 `level` 字段。

例如：

```json
{
  "level": 0
}
```

表示该 Character / Event 具有 Level 这一 Card Information，且基础 Level 为 0。

而 Climax 根本不具有 Level，因此不得写成：

```json
{
  "level": null
}
```

或：

```json
{
  "level": 0
}
```

对应 Definition 字段：

```python
level: int
```

Level 属于 Card Definition 的基础静态信息。运行时如果 Ability 或 Effect 改变当前 Level，应由运行时规则查询层计算 Current Level，不直接修改基础 `level`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](05_trait.md) | [返回 2.2 目录](README.md) | [下一小节 →](07_cost.md)
<!-- SUBSECTION_NAV_END -->
