# 2.4.5 Effect 与 Ability 的关系

<!-- ABILITY_NAV_START -->
[← 上一小节](04_ability_definition_structure.md) | [返回 2.4 目录](README.md) | [下一小节 →](06_ability_order.md)
<!-- ABILITY_NAV_END -->
Effect 表示 Ability 在实际处理过程中执行的具体规则操作。

如果说 Ability Definition 描述：

```text
“这项能力在什么情况下、以什么方式被处理”
```

那么 Effect 描述：

```text
“处理这项能力时，具体做什么”
```

因此二者职责不同。

概念关系：

```text
Ability
├─ Trigger / Timing
├─ Condition
├─ Cost
└─ Effects[]
   ├─ Effect 1
   ├─ Effect 2
   └─ ...
```

Ability 是规则行为的上层定义单位，Effect 是其内部的执行单位。

## Effect 不等于 Ability

一个 Ability 可以包含多个 Effect。

例如概念上：

```text
选择一个角色
→ 将其返回手牌
→ 抽 1 张牌
```

可以表示为：

```text
Ability
└─ effects
   ├─ SelectCharacterEffect
   ├─ MoveCardEffect
   └─ DrawCardEffect
```

这些 Effect 共同组成同一个 Ability 的处理内容。

因此不应把每个 Effect 都提升成独立 Ability。

反过来，也不应把整项 Ability 压缩成一个无法拆分的大型字符串或大型单一执行块。

## Effect 的职责

Effect 应描述可被规则系统执行的具体规则操作。

例如概念上：

```text
移动 Card
抽牌
造成伤害
改变当前 Power
选择对象
查看区域中的 Card
将 Card 置于特定状态
```

Effect 本身不负责决定：

```text
Ability 是否被触发
玩家是否可以发动 Ability
Ability 的 Trigger 是什么
Ability 属于 ACT / AUTO / CONT 中哪一种
```

这些仍属于 Ability 层。

因此：

```text
Ability
→ 决定何时、为何进入处理

Effect
→ 决定进入处理后具体执行什么
```

## Effect 与 Primitive

Effect 也不应直接等同于最底层规则 Primitive。

建议保持：

```text
Ability
→ Effect
→ Rule Process / Primitive
```

例如：

```text
MoveCardEffect
→ 根据 Effect 参数确定目标和目的 Zone
→ 调用统一的 move_card() Primitive
```

这样可以保证所有 Card 移动最终仍经过统一底层规则入口，而不是由每个 Ability 自行修改 Game State。

同理：

```text
DrawEffect
DamageEffect
RestEffect
PowerModificationEffect
```

都可以在更高层表达规则语义，再由规则系统调用对应 Primitive 或 Rule Process 完成实际状态变更。

因此禁止：

```text
Effect
→ 直接随意修改 GameState 内部容器
```

应当遵守统一规则入口。

## Effect 的顺序

同一个 Ability 中的多个 Effect 必须保持定义顺序。

例如：

```text
effects
├─ Effect A
├─ Effect B
└─ Effect C
```

原则上按：

```text
A
→ B
→ C
```

的顺序进入处理。

因此 `effects` 必须使用有序结构。

程序表示可采用：

```python
effects: tuple[EffectDefinition, ...]
```

而不是：

```python
set[EffectDefinition]
```

## Effect Definition 与运行时 Effect Context

和 Ability 一样，Effect 也需要区分静态定义与运行时处理数据。

```text
EffectDefinition
→ “应该执行什么”

Effect Runtime Context
→ “这一次执行时选了谁、得到什么结果、当前执行到哪里”
```

例如一个“选择 1 个角色”的 Effect Definition 可以规定：

```text
选择范围
数量
合法目标条件
```

而某次实际结算时选择了哪一张 Card，则属于运行时 Context。

因此不应把实际选择结果写回 Effect Definition。

## Effect 的可组合性

Effect 应尽量设计为可组合的结构单位。

这样不同 Ability 可以复用相同的 Effect Definition 类型。

例如：

```text
DrawCardEffect
MoveCardEffect
DealDamageEffect
ModifyPowerEffect
```

可以被多种不同 Ability 组合使用。

这并不意味着所有官方文本都必须被强行拆成极细粒度 Effect。

Effect 的粒度应以：

```text
规则语义清晰
可验证
可测试
可复用
能够稳定映射到规则执行流程
```

为主要判断标准。

本节只定义 Effect 与 Ability 的职责边界以及基本结构原则。

具体 Effect 类型、参数 Schema、Primitive 映射和运行时执行接口将在后续规则实现阶段继续定义。

<!-- ABILITY_NAV_START -->
[← 上一小节](04_ability_definition_structure.md) | [返回 2.4 目录](README.md) | [下一小节 →](06_ability_order.md)
<!-- ABILITY_NAV_END -->
