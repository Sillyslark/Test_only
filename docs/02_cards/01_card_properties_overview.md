# 2.1 卡片属性总览

← 上一节 | [返回第 2 章目录](README.md) | [2.2 →](02_base_json_storage/README.md)

本节汇总 WS 卡片中具有规则意义或识别意义的 Card Information，并统一中文名称、官方英文名称与程序表示。

这里的“可用属性”表示该信息在至少一种 Card Type 中具有明确意义。不同 Card Type 实际拥有的 Card Information 并不完全相同。

## 2.1.1 属性名称对照

| 中文名称 | 官方英文名称 | 程序表示 | 说明 |
| --- | --- | --- | --- |
| 卡片编号 | Card Number | [详见 2.3 Base Card Number](03_card_number/README.md) | 官方 Card Information。模拟器中的结构化表示与索引方式留到 Card Number 专门小节定义 |
| 卡名 | Card Name | `name` | 卡片名称 |
| 卡片种类 | Type | `card_type` | 使用 `CardType` 区分 Character / Event / Climax |
| 颜色 | Color | `color` | 使用 `CardColor` |
| 特征 | Trait | `traits` | Character 可拥有多个 Trait，因此程序字段使用复数 |
| 等级 | Level | `level` | Character / Event 使用 |
| 费用 | Cost | `cost` | Character / Event 使用 |
| 图标 | Icon | `card_icons` | 指普通 Card Icon，例如 Counter / Clock；不包括 Trigger Icon 或 Ability Type Icon |
| 力量 | Power | `power` | Character 使用 |
| 灵魂 | Soul | `soul` | Character 使用 |
| 触发图标 | Trigger Icon | `trigger_icons` | 可为空、单个、多个或重复 |
| 卡片文本 | Card Text | [详见 2.4 Card Text / Ability](04_card_text_ability/README.md) | 官方 Card Information。其程序表示与 Ability / Effect 的结构有关，留到 Ability 专门小节定义 |

本节只建立 Card Information 的名称与程序表示对照，不在这里定义 Card Number、Card Text、Ability 或 Effect 的具体内部数据结构。

其中必须严格区分以下三类“图标”概念：

```text
Icon
→ 普通 Card Icon，例如 Counter / Clock

Trigger Icon
→ Trigger Check 使用的 Trigger Icon

Ability Type Icon
→ ACT / AUTO / CONT
```

三者不得使用同一个程序类型或裸 `icon` 名称混用。

## 2.1.2 各 Card Type 拥有的 Card Information

下表中的：

- `O`：该 Card Type 具有这一类 Card Information；
- `X`：该 Card Type 不具有这一类 Card Information。

`O` 只表示该 Card Information 存在，不表示其值必须非空或非零。

| 官方中文名称 | 官方英文名称 | Character（角色） | Event（事件） | Climax（高潮） |
| --- | --- | :---: | :---: | :---: |
| 卡片编号 | Card Number | O | O | O |
| 卡名 | Card Name | O | O | O |
| 卡片种类 | Type | O | O | O |
| 颜色 | Color | O | O | O |
| 特征 | Trait | O | X | X |
| 等级 | Level | O | O | X |
| 费用 | Cost | O | O | X |
| 图标 | Icon | O | O | X |
| 力量 | Power | O | X | X |
| 灵魂 | Soul | O | X | X |
| 触发图标 | Trigger Icon | O | O | O |
| 卡片文本 | Card Text | O | O | O |

必须区分：

```text
该 Card Information 存在，但其内容为空或数值为 0
```

与：

```text
该 Card Type 根本不具有这一 Card Information
```

例如：

```text
Character.power = 0
```

表示 Character 具有 Power，且该卡的基础 Power 为 0。

而：

```text
Climax
```

根本不具有 Power 这一 Card Information，因此不得为了统一结构而人为填入 `0`、`None`、空 tuple 或其他默认值。

同理：

```python
character.card_icons == ()
event.card_icons == ()
```

表示 Character / Event 具有 Icon 这一 Card Information，但该卡当前没有普通 Card Icon。

而 Climax 根本不具有 Icon 这一 Card Information。

`Trigger Icon` 与 `Card Text` 也遵循同样原则：某张卡的对应内容可以为空，但这不等于该 Card Type 不具有这一类 Card Information。

Card Number 与 Card Text 的程序数据结构分别留到后续专门小节定义。完成对应小节后，本节中的“待添加超链接”将替换为直达链接。

← 上一节 | [返回第 2 章目录](README.md) | [2.2 →](02_base_json_storage/README.md)