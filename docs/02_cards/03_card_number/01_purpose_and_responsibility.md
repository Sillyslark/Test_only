# 2.3.1 目的与职责

<!-- CARD_NUMBER_NAV_START -->
← 上一小节 | [返回 2.3 目录](README.md) | [下一小节 →](02_card_number_structure.md)
<!-- CARD_NUMBER_NAV_END -->
Card Number 是 Card Definition 的固有识别信息，同时也是模拟器中稳定定位基础 Card Definition 的核心标识之一。

本节只规定 Card Number 在 Card 数据层中的职责，不在这里定义 Deck 构筑规则、Card Catalog 实现、文件扫描流程或运行时 Card Instance 身份。

Card Number 的职责包括：

```text
识别 Card Definition
→ 区分不同的基础 Card Definition

结构化保存官方编号信息
→ 不把完整编号字符串作为唯一事实来源

生成稳定编号表示
→ 可由统一 formatter 生成 Base Card Number 与 Full Card Number

为其他系统提供稳定查询键
→ 供 Card Catalog、Deck、资源定位等上层系统使用
```

Card Number 不负责：

```text
Deck Legality
→ 不判断不同 Title Code 是否允许共同构筑

Card Instance Identity
→ 不作为对局中具体卡片实例的唯一 ID

Runtime State
→ 不记录卡片所在 Zone、方向、正反面或其他运行时状态

Ability Resolution
→ 不参与 Ability / Effect 的直接结算
```

因此必须区分：

```text
Card Number
→ “这是什么基础卡 / 哪个印刷版本”

Card Instance ID
→ “本局中的这一张具体卡”
```

Card Number 属于 Card Definition 的静态识别数据。

后续小节将继续定义：

- Card Number 的结构化组成；
- Base Card Number 与 Full Card Number 的关系；
- Card JSON 中的存储格式；
- Variant 的处理原则；
- Validation 规则。

<!-- CARD_NUMBER_NAV_START -->
← 上一小节 | [返回 2.3 目录](README.md) | [下一小节 →](02_card_number_structure.md)
<!-- CARD_NUMBER_NAV_END -->
