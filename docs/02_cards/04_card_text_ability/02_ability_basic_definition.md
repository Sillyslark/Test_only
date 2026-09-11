# 2.4.2 Ability 的基本定义

<!-- ABILITY_NAV_START -->
[← 上一小节](01_card_text_and_program_representation.md) | [返回 2.4 目录](README.md) | [下一小节 →](03_ability_type.md)
<!-- ABILITY_NAV_END -->
Ability 是 Card 上一项可独立识别、可独立判定并由规则系统处理的结构化规则定义。

它是程序中的规则单位之一。

概念上：

```text
Card
└─ Ability[]
   ├─ Ability 1
   ├─ Ability 2
   └─ ...
```

一张 Card 可以具有：

```text
0 个 Ability
1 个 Ability
多个 Ability
```

Ability 的职责是描述：

```text
何时可以或应当处理
→ Timing / Trigger / Activation Condition

是否允许发动或结算
→ Condition / Cost / Permissibility

处理时需要执行什么
→ Effect
```

Ability 本身不是运行时效果结果。

因此应区分：

```text
Ability Definition
→ 静态规则定义

Ability Runtime Context
→ 某次实际触发、发动或结算时的上下文

Effect
→ Ability 处理过程中执行的具体规则操作
```

Ability Definition 属于 Card Definition 的静态数据。

也就是说，Card JSON 中保存的是 Ability 的定义，而不是某次对局中已经触发或正在结算的状态。

例如：

```text
Card Definition
└─ abilities
   └─ AutomaticAbility(...)
```

而不是：

```text
Card Definition
└─ triggered = true
```

后者属于运行时状态，不应写入基础 Card JSON。

## Ability 的独立性

每个 Ability 应当作为独立结构保存。

如果一张卡印有多个独立能力，不应把它们合并成一个无法区分内部边界的大型规则块。

例如概念上：

```text
Card Text

[AUTO] ...
[CONT] ...
```

应表示为：

```text
abilities
├─ AutomaticAbility
└─ ContinuousAbility
```

而不是：

```text
abilities
└─ OneCombinedAbility
```

这样可以使不同 Ability：

```text
独立识别
独立判定
独立触发
独立发动
独立结算
独立测试
```

## Ability 与 Card 的关系

Ability 从属于 Card Definition。

它描述该基础 Card 印刷规则的一部分，但不承担 Card 本身的其他 Card Information。

因此 Ability 不负责保存：

```text
Card Name
Color
Level
Power
Soul
Trigger Icon
Card Number
```

这些内容仍属于 Card Definition 的基础属性。

Ability 只描述规则行为。

## Ability 的不可变性

作为 Card Definition 的组成部分，Ability Definition 应视为不可变数据。

运行时效果不得直接修改 Ability Definition 本身。

例如：

```text
某个 CONT Ability 当前失效
```

不应实现为：

```text
删除或修改 Card Definition 中的 Ability
```

而应由运行时状态与规则查询决定该 Ability 当前是否有效。

因此：

```text
Ability Definition
→ 静态规则事实

Current Ability State
→ 由运行时状态与规则系统判断
```

## Ability 的基本组成方向

不同 Ability Type 的具体结构并不完全相同，但后续设计至少需要能够表达：

```text
Ability Type
Condition
Timing / Trigger
Cost
Effect
```

其中哪些字段适用于 ACT / AUTO / CONT，将在后续小节分别定义。

本节只规定 Ability 作为独立、结构化、静态规则定义的基本职责。

<!-- ABILITY_NAV_START -->
[← 上一小节](01_card_text_and_program_representation.md) | [返回 2.4 目录](README.md) | [下一小节 →](03_ability_type.md)
<!-- ABILITY_NAV_END -->
