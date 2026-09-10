# 2.2.4 颜色 / Color

<!-- SUBSECTION_NAV_START -->
[← 上一小节](03_card_type.md) | [返回 2.2 目录](README.md) | [下一小节 →](05_trait.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Color  
**程序字段：** `color`

Color 在 Card JSON 中使用字符串枚举值保存。

JSON 示例：

```json
{
  "color": "red"
}
```

字段类型：

```text
string enum
```

当前允许值：

```text
yellow
green
red
blue
```

对应程序枚举：

```python
class CardColor(str, Enum):
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    BLUE = "blue"
```

适用 Card Type：

```text
Character（角色）
Event（事件）
Climax（高潮）
```

三类 Card Type 都必须具有 `color` 字段。

规则与约束：

- `color` 必须存在；
- 值必须是 `yellow`、`green`、`red`、`blue` 之一；
- 不接受其他自由字符串；
- 不使用 `null` 表示未知颜色；
- JSON 中保存的是规范化枚举值，不保存中文显示名；
- UI 层如需显示“黄 / 绿 / 红 / 蓝”，应由显示层根据 `CardColor` 转换，不改变基础 JSON 数据。

对应 Definition 字段：

```python
color: CardColor
```

Color 属于 Card Definition 的基础静态信息。运行时 Card Instance 不复制独立的 Color，而是通过其关联的 Card Definition 取得基础颜色。

如果游戏中的 Ability 或 Effect 改变当前颜色，应由运行时规则查询层计算 Current Color，不直接修改 Card Definition 中的基础 `color`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](03_card_type.md) | [返回 2.2 目录](README.md) | [下一小节 →](05_trait.md)
<!-- SUBSECTION_NAV_END -->
