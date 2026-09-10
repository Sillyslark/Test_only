# 2.4.1 Card Text 与程序表示的关系

<!-- ABILITY_NAV_START -->
← 上一小节 | [返回 2.4 目录](README.md) | [下一小节 →](02_ability_basic_definition.md)
<!-- ABILITY_NAV_END -->
Card Text 是 WS 官方 Card Information 的一部分，用于向玩家展示卡片上印刷的规则文本。

模拟器中不能把 Card Text 直接当作规则执行逻辑。

也就是说：

```text
Card Text
→ 人类可读的规则文本

Program Representation
→ 程序可解析、可验证、可执行的结构化规则定义
```

二者表达的是同一张卡的规则含义，但职责不同。

Card Text 主要用于：

```text
显示
文档
调试
与官方卡面信息对应
```

程序规则表示主要用于：

```text
判定触发条件
判定发动条件
生成 Effect
执行 Effect
处理持续效果
进行 Validation
进行测试
```

因此禁止采用：

```text
读取 Card Text 字符串
→ 临时解析自然语言
→ 决定游戏规则
```

作为正常 Engine 执行路径。

Card Text 不应成为 Engine 的规则事实来源。

程序中的规则事实来源应是结构化 Ability Definition。

概念关系：

```text
Official Card Text
        ↓
Authoring / Translation
        ↓
Structured Ability Definition
        ↓
Engine
```

这里的 Authoring / Translation 指将官方 Card Text 转换为模拟器能够理解的结构化规则数据。

这个转换过程可以由人工、辅助工具或未来的自动化流程完成，但转换后的 Ability Definition 必须能够独立被程序读取和执行。

因此：

```text
Card Text
≠ Ability

Card Text
→ 规则的官方可读表达

Ability
→ 规则的程序结构化表达
```

一张 Card 可以具有：

```text
0 个 Ability
1 个 Ability
多个 Ability
```

多个 Ability 的存在顺序必须能够被保存，具体顺序规则将在后续小节定义。

Card JSON 中是否同时保存官方原文 Card Text，可根据未来的显示、校对和数据维护需求决定。

但无论是否保存原文文本，都必须遵守：

> Engine 不直接依赖自然语言 Card Text 执行规则。

本节只定义 Card Text 与程序表示之间的职责边界。

Ability 的具体类型、结构、Effect 关系和 JSON 表示将在后续小节定义。

<!-- ABILITY_NAV_START -->
← 上一小节 | [返回 2.4 目录](README.md) | [下一小节 →](02_ability_basic_definition.md)
<!-- ABILITY_NAV_END -->
