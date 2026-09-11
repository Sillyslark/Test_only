# 2.2.9 力量 / Power

<!-- SUBSECTION_NAV_START -->
[← 上一小节](08_icon.md) | [返回 2.2 目录](README.md) | [下一小节 →](10_soul.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Power  
**程序字段：** `power`

Power 在 Card JSON 中使用整数保存。

JSON 示例：

```json
{
  "power": 5000
}
```

字段类型：

```text
integer
```

适用 Card Type：

```text
Character（角色）
```

只有 Character 具有 Power 这一 Card Information。

规则与约束：

- Character JSON 必须具有 `power` 字段；
- `power` 的值必须是整数；
- 允许值为 `0` 或更大的非负整数；
- 不使用 `null` 表示 Power 不存在；
- 不使用字符串形式的数字，例如 `"5000"`；
- Event 与 Climax 根本不具有 Power，因此它们的 JSON 中不得出现 `power` 字段。

例如：

```json
{
  "power": 0
}
```

表示该 Character 具有 Power 这一 Card Information，且基础 Power 为 0。

而 Event / Climax 根本不具有 Power，因此不得写成：

```json
{
  "power": null
}
```

或：

```json
{
  "power": 0
}
```

对应 Definition 字段：

```python
power: int
```

Power 属于 CharacterDefinition 的基础静态信息。运行时如果 Ability 或 Effect 改变当前 Power，应由运行时规则查询层计算 Current Power，不直接修改基础 `power`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](08_icon.md) | [返回 2.2 目录](README.md) | [下一小节 →](10_soul.md)
<!-- SUBSECTION_NAV_END -->
