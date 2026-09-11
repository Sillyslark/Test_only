# 2.2.10 灵魂 / Soul

<!-- SUBSECTION_NAV_START -->
[← 上一小节](09_power.md) | [返回 2.2 目录](README.md) | [下一小节 →](11_trigger_icon.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Soul  
**程序字段：** `soul`

Soul 在 Card JSON 中使用整数保存。

JSON 示例：

```json
{
  "soul": 1
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

只有 Character 具有 Soul 这一 Card Information。

规则与约束：

- Character JSON 必须具有 `soul` 字段；
- `soul` 的值必须是整数；
- 允许值为 `0` 或更大的非负整数；
- 不使用 `null` 表示 Soul 不存在；
- 不使用字符串形式的数字，例如 `"1"`；
- Event 与 Climax 根本不具有 Soul，因此它们的 JSON 中不得出现 `soul` 字段。

例如：

```json
{
  "soul": 0
}
```

表示该 Character 具有 Soul 这一 Card Information，且基础 Soul 为 0。

而 Event / Climax 根本不具有 Soul，因此不得写成：

```json
{
  "soul": null
}
```

或：

```json
{
  "soul": 0
}
```

对应 Definition 字段：

```python
soul: int
```

Soul 属于 CharacterDefinition 的基础静态信息。运行时如果 Ability 或 Effect 改变当前 Soul，应由运行时规则查询层计算 Current Soul，不直接修改基础 `soul`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](09_power.md) | [返回 2.2 目录](README.md) | [下一小节 →](11_trigger_icon.md)
<!-- SUBSECTION_NAV_END -->
