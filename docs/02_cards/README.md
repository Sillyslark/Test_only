# 第 2 章 Card 数据与 JSON 规范

本章定义 Card 数据在模拟器中的基础表示方式，重点规定：

```text
Card 有哪些基础属性
这些属性如何保存到 JSON
Base Card Number 如何表示
Card Text 如何映射为结构化 Ability / Effect
```

本章只负责 Card 数据层与 Authoring Data / Card JSON 的规范。

以下内容不属于本章：

```text
Card JSON 的批量扫描
Index / Catalog 的生成
Deck Recipe 的解析
Card Definition 的完整导入流程
Card Instance 的运行时状态
Engine 中 Ability 的实际触发与结算
```

这些内容将在后续章节中分别定义。

## 目录

### [2.1 卡片属性总览](01_card_properties_overview.md)

定义 WS Card Information 在本项目中的属性名称、程序表示，以及 Character / Event / Climax 分别拥有哪些 Card Information。

主要内容：

```text
官方中文名称
官方英文名称
程序字段
各 Card Type 的属性差异
```

---

### [2.2 基础 JSON 存储](02_base_json_storage/README.md)

按照 2.1 的属性顺序，逐项定义基础 Card Information 在 Card JSON 中的存储方式。

包括：

```text
Card Number
Card Name
Type
Color
Trait
Level
Cost
Icon
Power
Soul
Trigger Icon
Card Text
```

其中 Card Number 与 Card Text 只在本节保留基础位置，其详细结构分别由 2.3 与 2.4 定义。

---

### [2.3 Base Card Number](03_card_number/README.md)

定义 Card JSON 中保存的 Base Card Number 结构。

当前 Base Card Number 由以下字段组成：

```text
title_code
side
product_code
product_card_number
```

Card JSON 始终只保存 Base Card Number 对应的结构化数据。

Variant 虽然存在于完整 Card Number 体系中，但不属于本章当前基础 Card JSON 的存储内容；其具体处理留待后续 Index / Variant 相关章节定义。

---

### [2.4 Card Text / Ability](04_card_text_ability/README.md)

定义 Card Text 与程序中结构化 Ability / Effect 表示之间的关系。

核心原则：

```text
Card Text
→ 官方、人类可读的规则文本

Ability Definition
→ 程序中的静态结构化规则定义

Effect
→ Ability 处理过程中执行的具体规则操作
```

并规定：

```text
ACT  → ActivatedAbility
AUTO → AutomaticAbility
CONT → ContinuousAbility
```

以及 Ability 的基本结构、顺序、JSON 存储原则和当前阶段的实现边界。

## 本章数据边界

本章结束后，Card 数据层应能够回答：

```text
这张 Card 的基础属性是什么？
这些属性如何写入 JSON？
它的 Base Card Number 如何结构化保存？
它具有哪些结构化 Ability Definition？
```

但本章不负责回答：

```text
这些 JSON 文件如何被扫描和建立 Index？
Deck Recipe 如何找到对应 Card？
Card Definition 如何进入 Game？
Card Instance 如何生成？
AUTO 如何进入 Standby Ability Pool？
CONT 如何叠加到 Current State？
Effect 最终如何调用 Engine Primitive？
```

这些问题属于后续的数据流、导入、运行时与 Engine 章节。
