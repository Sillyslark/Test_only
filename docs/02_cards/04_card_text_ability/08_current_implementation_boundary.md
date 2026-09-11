# 2.4.8 当前阶段的实现边界

<!-- ABILITY_NAV_START -->
[← 上一小节](07_ability_json_storage.md) | [返回 2.4 目录](README.md) | 下一小节 →
<!-- ABILITY_NAV_END -->
本节定义当前阶段 Card Text / Ability 系统的实现边界。

第二章的目标是确定 Card JSON 与 Ability Definition 的数据原则，而不是一次性完成整个 WS Ability Engine。

因此当前阶段只要求：

```text
Card JSON
→ 能保存有序的 abilities[]

Ability
→ 能明确区分 ACT / AUTO / CONT

Ability Definition
→ 与运行时状态分离

Effect
→ 作为结构化规则操作存在

Engine
→ 不直接依赖自然语言 Card Text
```

## 当前必须确定的内容

当前数据模型至少需要锁定：

```text
abilities 是有序数组
Ability Type 的基本分类
Ability Definition 属于静态数据
Effect 属于 Ability 的结构化执行内容
Card Text 与 Ability Definition 分离
运行时 Ability Context 不进入基础 JSON
```

这些原则应在后续实现中保持稳定。

## 当前不要求完成的内容

当前阶段不要求立即定义完整的：

```text
Trigger 类型全集
Condition 类型全集
Cost 类型全集
Effect 类型全集
Ability Runtime Context 最终结构
Standby Ability Pool 最终实现
Check Timing 最终算法
Continuous Effect 状态叠加系统
所有 WS 官方 Ability 的完整覆盖
```

这些内容属于后续 Engine / Rule System 设计与实现。

第二章不应为了预先覆盖所有官方卡片，而建立过度复杂的数据结构。

## 测试阶段允许无 Ability

为了优先完成 Card 数据、Deck 导入、Zone、移动等基础系统，测试阶段允许 Card JSON 使用：

```json
{
  "abilities": []
}
```

即使现实中的对应 Card 实际具有 Ability。

这表示：

```text
该测试数据当前未实现 Ability
```

而不是修改官方 Card 的规则定义。

因此在测试数据中，可以先验证：

```text
Card JSON
→ Card Definition
→ Deck
→ Game Initialization
→ Zone
→ Card Movement
```

而不要求 Ability Engine 已经完成。

## Ability Library / Template 可以后续建立

大量 WS Ability 具有重复的规则模式。

未来可以建立：

```text
Trigger Template
Condition Template
Cost Template
Effect Template
```

或更高层的 Ability Template Library，以减少重复定义。

例如概念上：

```text
“这张卡放置到 Stage 时”
→ EnterStageTrigger

“抽 1 张牌”
→ DrawEffect(count=1)
```

但模板库只负责复用结构化规则模式。

它不能改变：

```text
Card JSON / Ability Definition
→ Engine 可理解的结构化数据
```

这一基本原则。

模板库的具体形式不在第二章锁定。

## 不提前绑定 Engine 实现

Card JSON 不应直接依赖 Engine 内部函数名。

例如不应把数据写成：

```json
{
  "effect": "engine.draw_card"
}
```

因为这样会使数据格式与某个具体 Engine 实现强耦合。

更合理的关系是：

```text
JSON Rule Data
      ↓
Ability / Effect Definition
      ↓
Rule Handler / Resolver
      ↓
Engine Primitive
```

这样以后即使 Engine 内部重构，Card JSON 仍可以保持稳定。

## 第二章的职责终点

完成本节后，第二章只需要保证能够回答：

```text
Card 有哪些基础属性？
这些属性如何保存到 JSON？
Base Card Number 如何表示？
Card Text 与 Ability 如何转换为程序结构？
Ability 数据应遵守哪些基本原则？
```

至于：

```text
Card JSON 如何被批量扫描
如何建立 Index
Deck Recipe 如何根据编号定位 Card
如何生成 Card Definition
Ability 如何在 Engine 中触发和结算
```

都属于后续章节。

因此第二章在这里停止于：

```text
Authoring Data / Card JSON 的数据规范
```

而不继续进入：

```text
Import Pipeline
Runtime
Engine Execution
```

<!-- ABILITY_NAV_START -->
[← 上一小节](07_ability_json_storage.md) | [返回 2.4 目录](README.md) | 下一小节 →
<!-- ABILITY_NAV_END -->
