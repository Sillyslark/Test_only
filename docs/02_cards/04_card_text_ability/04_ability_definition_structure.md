# 2.4.4 Ability Definition 的基本结构

<!-- ABILITY_NAV_START -->
[← 上一小节](03_ability_type.md) | [返回 2.4 目录](README.md) | [下一小节 →](05_effect_and_ability.md)
<!-- ABILITY_NAV_END -->
Ability Definition 用于保存一项 Ability 的静态、结构化规则信息。

不同 Ability Type 的具体字段可以不同，但它们应共享一组基本设计原则。

概念结构可以表示为：

```text
AbilityDefinition
├─ ability_type
├─ condition
├─ timing / trigger
├─ cost
└─ effects[]
```

这里的结构只表示设计方向，不要求所有 Ability Type 都必须实际拥有全部字段。

例如：

```text
ACT
→ 重点关注 activation condition、cost、effects

AUTO
→ 重点关注 trigger / timing、condition、effects

CONT
→ 重点关注 applicable condition、continuous effects
```

因此不应为了统一数据形状而强行给所有 Ability 填入：

```text
trigger = null
cost = null
timing = null
```

如果某一字段对某种 Ability Type 从概念上不存在，应由对应 Definition 类型本身体现。

## Ability Type

每个 Ability Definition 必须能够明确确定其 Ability Type。

例如：

```text
ActivatedAbility
AutomaticAbility
ContinuousAbility
```

具体类型本身已经能够表达 Ability Type 时，程序内部不一定需要重复保存第二份彼此可能冲突的类型信息。

例如：

```python
ActivatedAbility(...)
```

本身已经表示：

```text
ability_type = ACT
```

因此应避免：

```python
ActivatedAbility(
    ability_type="auto"
)
```

这种可能产生自相矛盾的数据结构。

JSON 层是否保留：

```json
{
  "ability_type": "act"
}
```

作为反序列化判别字段，可以由 Loader / Schema 设计决定。

## Condition

Condition 表示 Ability 在当前状态下是否满足某项规则条件。

例如概念上：

```text
你的手牌少于 5 张
这张卡位于 Stage
你的等级为 2 或以上
指定角色存在
```

Condition 应当是结构化规则表达，而不是自然语言字符串。

不推荐：

```json
{
  "condition": "if you have 5 or fewer cards in hand"
}
```

作为 Engine 的直接判定依据。

程序需要能够明确读取 Condition 的类型和参数。

## Timing / Trigger

Timing / Trigger 主要用于 AutomaticAbility。

它描述：

```text
什么规则事件发生时
→ 该 AUTO 应被检测
```

例如概念上：

```text
这张卡从 Hand 放置到 Stage 时
攻击开始时
你的 Encore Step 开始时
伤害被取消时
```

Trigger 描述的是“何时检查”，Condition 描述的是“检查时是否满足”。

两者不应混为同一个概念。

因此：

```text
Trigger
→ 何时检查

Condition
→ 检查时是否成立
```

具体 GameEvent / Timing 数据结构属于后续规则系统设计，本节不提前规定其最终实现。

## Cost

Cost 表示发动或处理 Ability 时需要支付的成本。

它与 Effect 必须在结构上区分。

概念流程：

```text
Ability 可以处理
→ 支付 Cost
→ 执行 Effect
```

Cost 可能包含多个组成部分，因此后续结构应允许：

```text
costs[]
```

而不是假设每个 Ability 只能拥有一个不可拆分的 Cost 字符串。

并非所有 Ability Type 都一定具有 Cost。

没有 Cost 的 Ability 不应通过虚构的：

```text
NO_COST
```

来补齐结构，除非后续规则实现确实需要这种显式对象。

## Effects

Effect 表示 Ability 实际处理时需要执行的规则操作。

一项 Ability 可以包含：

```text
0 个 Effect
1 个 Effect
多个 Effect
```

多个 Effect 必须能够保持定义顺序。

例如：

```text
effects
├─ Effect 1
├─ Effect 2
└─ Effect 3
```

结算时原则上按规则定义的顺序处理。

因此：

```text
effects[]
```

必须使用有序结构，不应使用 `set`。

Effect 的具体设计将在后续小节继续定义。

## 不保存运行时状态

Ability Definition 中不应保存：

```text
是否已经触发
是否正在结算
本次选择了哪个目标
本次支付了什么 Cost
本次生成了哪些临时对象
```

这些都属于运行时 Ability Context / Resolution State。

因此：

```text
Ability Definition
→ 静态定义

Ability Runtime Context
→ 某次实际处理过程的数据
```

必须保持分离。

本节只定义 Ability Definition 的基本结构原则，不在这里锁定最终 Python dataclass 或 JSON Schema。

<!-- ABILITY_NAV_START -->
[← 上一小节](03_ability_type.md) | [返回 2.4 目录](README.md) | [下一小节 →](05_effect_and_ability.md)
<!-- ABILITY_NAV_END -->
