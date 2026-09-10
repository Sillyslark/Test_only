# 2.2.11 触发图标 / Trigger Icon

<!-- SUBSECTION_NAV_START -->
[← 上一小节](10_soul.md) | [返回 2.2 目录](README.md) | [下一小节 →](12_card_text.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Trigger Icon  
**程序字段：** `trigger_icons`

Trigger Icon 在 Card JSON 中使用字符串数组保存。

JSON 示例：

```json
{
  "trigger_icons": ["soul", "shot"]
}
```

允许空数组：

```json
{
  "trigger_icons": []
}
```

字段类型：

```text
array[string enum]
```

当前允许的枚举值：

```text
soul
return
pool
shot
treasure
comeback
draw
standby
choice
```

对应程序枚举：

```python
class TriggerIcon(str, Enum):
    SOUL = "soul"
    RETURN = "return"
    POOL = "pool"
    SHOT = "shot"
    TREASURE = "treasure"
    COMEBACK = "comeback"
    DRAW = "draw"
    STANDBY = "standby"
    CHOICE = "choice"
```

适用 Card Type：

```text
Character（角色）
Event（事件）
Climax（高潮）
```

三类 Card Type 都具有 Trigger Icon 这一 Card Information。

规则与约束：

- 三类 Card JSON 都必须具有 `trigger_icons` 字段；
- `trigger_icons` 的值必须是字符串数组；
- 数组元素必须是允许的 `TriggerIcon` 枚举值；
- 允许空数组，表示该卡当前没有基础 Trigger Icon；
- 允许一个或多个 Trigger Icon；
- 允许重复的 Trigger Icon；
- 数组顺序必须保留输入顺序；
- 不使用 `set` 或其他会自动去重的数据结构；
- 不使用 `null` 表示没有 Trigger Icon；
- 不使用 `NONE` 一类虚拟枚举值表示“没有 Trigger Icon”。

例如：

```json
{
  "trigger_icons": ["soul", "soul"]
}
```

是合法的数据表示，表示该卡具有两个 Soul Trigger Icon。

对应 Definition 字段：

```python
trigger_icons: tuple[TriggerIcon, ...]
```

JSON Loader 在读取后，可将 JSON 数组转换为不可变 tuple 存入 Card Definition。

`trigger_icons` 表示 Card Definition 中的基础 / 印刷 Trigger Icon。

运行时如果 Ability 或 Effect 增加、移除或改变当前 Trigger Icon，应由运行时规则查询层计算 Current Trigger Icons，不直接修改基础 `trigger_icons`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](10_soul.md) | [返回 2.2 目录](README.md) | [下一小节 →](12_card_text.md)
<!-- SUBSECTION_NAV_END -->
