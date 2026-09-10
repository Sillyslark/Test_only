# 2.2.3 卡片种类 / Type

<!-- SUBSECTION_NAV_START -->
[← 上一小节](02_card_name.md) | [返回 2.2 目录](README.md) | [下一小节 →](04_color.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Type  
**程序字段：** `card_type`

Type 用于区分 Card Definition 所属的三种基本 Card Type：

```text
Character（角色）
Event（事件）
Climax（高潮）
```

Card JSON 中使用字符串枚举值保存。

Card Type 的 JSON 枚举值使用大写，
用于强调其作为 Card Definition 顶层分类与结构判别字段的职责。
其他普通属性枚举仍可使用小写。

JSON 示例：

```json
{
  "card_type": "CHARACTER"
}
```

字段类型：

```text
string enum
```

允许值：

```text
CHARACTER
EVENT
CLIMAX
```

对应程序枚举：

```python
class CardType(Enum):
    CHARACTER = "CHARACTER"
    EVENT = "EVENT"
    CLIMAX = "CLIMAX"
```

规则与约束：

- `card_type` 必须存在；
- 值必须是 `CHARACTER`、`EVENT`、`CLIMAX` 之一；
- 不接受其他自由字符串；
- 不使用 `null` 表示未知 Card Type；
- 不根据其他字段自动推断 Card Type；
- Card Type 决定该 Card JSON 后续允许或要求出现哪些 Card Information。

例如：

```text
CHARACTER
→ 可以具有 Trait、Power、Soul 等 Character 专属信息

EVENT
→ 可以具有 Level、Cost、Icon，但不具有 Power、Soul、Trait

CLIMAX
→ 不具有 Level、Cost、Icon、Power、Soul、Trait
```

具体哪些 Card Information 属于哪一种 Card Type，以 2.1.2 的对照表为准。

对应 Definition 字段：

```python
card_type: CardType
```

`card_type` 属于 Card Definition 的基础静态信息。运行时 Card Instance 不复制独立的 Card Type，而是通过其关联的 Card Definition 取得该信息。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](02_card_name.md) | [返回 2.2 目录](README.md) | [下一小节 →](04_color.md)
<!-- SUBSECTION_NAV_END -->
