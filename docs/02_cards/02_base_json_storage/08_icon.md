# 2.2.8 图标 / Icon

<!-- SUBSECTION_NAV_START -->
[← 上一小节](07_cost.md) | [返回 2.2 目录](README.md) | [下一小节 →](09_power.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Icon  
**程序字段：** `card_icons`

Icon 指普通 Card Icon，例如 Counter / Clock。它与 Trigger Icon、Ability Type Icon 是不同概念。

Card JSON 中使用字符串数组保存。

JSON 示例：

```json
{
  "card_icons": ["counter"]
}
```

或：

```json
{
  "card_icons": ["counter", "clock"]
}
```

字段类型：

```text
array[string enum]
```

当前允许的枚举值：

```text
counter
clock
```

对应程序枚举：

```python
class CardIcon(str, Enum):
    COUNTER = "counter"
    CLOCK = "clock"
```

适用 Card Type：

```text
Character（角色）
Event（事件）
```

Character 与 Event 都具有 Icon 这一 Card Information；Climax 不具有 Icon。

规则与约束：

- Character / Event JSON 必须具有 `card_icons` 字段；
- `card_icons` 的值必须是字符串数组；
- 数组元素必须是允许的 CardIcon 枚举值；
- 允许空数组，表示该 Character / Event 当前没有普通 Card Icon；
- 不使用 `null` 表示没有 Icon；
- Climax JSON 中不得出现 `card_icons` 字段；
- 数组顺序保留输入顺序；
- 不使用 `set` 或其他会自动去重的数据结构；
- 不使用 `NONE` 一类虚拟枚举表示“没有 Icon”。

例如：

```json
{
  "card_icons": []
}
```

表示该 Character / Event 具有 Icon 这一 Card Information，但当前没有 Counter / Clock Icon。

而 Climax 根本不具有 Icon，因此不得写成：

```json
{
  "card_icons": []
}
```

或：

```json
{
  "card_icons": null
}
```

对应 Definition 字段：

```python
card_icons: tuple[CardIcon, ...]
```

JSON Loader 在读取后，可将 JSON 数组转换为不可变 tuple 存入对应的 Card Definition。

Icon 属于 Card Definition 的基础静态信息。运行时如果 Ability 或 Effect 改变当前 Icon，应由运行时规则查询层计算 Current Icons，不直接修改基础 `card_icons`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](07_cost.md) | [返回 2.2 目录](README.md) | [下一小节 →](09_power.md)
<!-- SUBSECTION_NAV_END -->
