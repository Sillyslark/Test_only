# 2.2.7 费用 / Cost

<!-- SUBSECTION_NAV_START -->
[← 上一小节](06_level.md) | [返回 2.2 目录](README.md) | [下一小节 →](08_icon.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Cost  
**程序字段：** `cost`

Cost 在 Card JSON 中使用整数保存。

JSON 示例：

```json
{
  "cost": 1
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

Character 与 Event 都必须具有 `cost` 字段；Climax 不具有 Cost 这一 Card Information。

规则与约束：

- Character / Event JSON 必须具有 `cost` 字段；
- `cost` 的值必须是整数；
- 允许值为 `0` 或更大的非负整数；
- 不使用 `null` 表示 Cost 不存在；
- 不使用字符串形式的数字，例如 `"1"`；
- Climax JSON 中不得出现 `cost` 字段。

例如：

```json
{
  "cost": 0
}
```

表示该 Character / Event 具有 Cost 这一 Card Information，且基础 Cost 为 0。

而 Climax 根本不具有 Cost，因此不得写成：

```json
{
  "cost": null
}
```

或：

```json
{
  "cost": 0
}
```

对应 Definition 字段：

```python
cost: int
```

Cost 属于 Card Definition 的基础静态信息。运行时如果 Ability 或 Effect 改变当前 Cost，应由运行时规则查询层计算 Current Cost，不直接修改基础 `cost`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](06_level.md) | [返回 2.2 目录](README.md) | [下一小节 →](08_icon.md)
<!-- SUBSECTION_NAV_END -->
