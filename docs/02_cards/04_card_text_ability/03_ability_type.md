# 2.4.3 Ability Type

<!-- ABILITY_NAV_START -->
[← 上一小节](02_ability_basic_definition.md) | [返回 2.4 目录](README.md) | [下一小节 →](04_ability_definition_structure.md)
<!-- ABILITY_NAV_END -->
WS 中的 Ability 按官方 Ability Type 分为：

```text
ACT
AUTO
CONT
```

程序中分别使用完整类型名称表示：

```text
ACT
→ ActivatedAbility

AUTO
→ AutomaticAbility

CONT
→ ContinuousAbility
```

Ability Type 属于 Ability Definition 的基础结构信息。

不同 Ability Type 的处理方式不同，因此不能只把 ACT / AUTO / CONT 当作显示标签。

它们会影响：

```text
Ability 如何进入规则流程
Ability 何时被检查
Ability 是否需要玩家主动发动
Ability 是否产生持续状态修正
Ability 是否在特定 Timing 自动进入后续处理
```

## ACT / ActivatedAbility

ACT 表示玩家主动发动的 Ability。

概念流程：

```text
满足发动条件
→ 玩家选择发动
→ 支付 Cost
→ 执行 Effect
```

ActivatedAbility 不会仅因为条件满足就自动结算。

是否可以发动，应由规则系统根据当前 Game State 判断。

因此：

```text
ACT
→ 需要玩家主动输入
```

## AUTO / AutomaticAbility

AUTO 表示在特定事件或 Timing 发生时被规则系统检测的 Ability。

概念流程：

```text
Game Event / Timing 发生
→ Engine 检查相关 AUTO
→ 条件满足
→ 进入待处理 Ability 流程
→ 结算 Effect
```

AutomaticAbility 的核心特征是：

```text
由规则事件触发检测
```

而不是由玩家直接从无事件状态中主动调用。

AUTO 的具体 Trigger / Timing 表示方式将在后续 Ability 结构章节中定义。

## CONT / ContinuousAbility

CONT 表示持续生效的 Ability。

它通常不是：

```text
触发一次
→ 执行一次
→ 结束
```

而是：

```text
满足适用条件
→ 持续影响当前规则状态
```

ContinuousAbility 的结果应通过持续效果 / 状态查询机制参与当前状态计算。

例如：

```text
Base State
+ Continuous Effect A
+ Continuous Effect B
→ Current State
```

因此不应通过直接永久修改 Card Definition 的基础属性来实现 CONT。

## 程序表示原则

Ability Type 建议使用明确的类型系统表示。

例如：

```python
class AbilityType(str, Enum):
    ACT = "act"
    AUTO = "auto"
    CONT = "cont"
```

并在具体 Definition 中使用对应的完整类型：

```python
ActivatedAbility
AutomaticAbility
ContinuousAbility
```

这里需要区分：

```text
ACT / AUTO / CONT
→ 官方 Ability Type / 序列化枚举值

ActivatedAbility / AutomaticAbility / ContinuousAbility
→ 程序中的具体 Definition 类型
```

二者语义对应，但职责不同。

JSON 中建议继续遵守本章统一的枚举序列化规范：

```json
{
  "ability_type": "auto"
}
```

而不是：

```json
{
  "ability_type": "AUTO"
}
```

也就是说：

```text
Python Enum 成员名
→ UPPER_SNAKE_CASE

JSON 枚举值
→ lowercase
```

本节只定义 ACT / AUTO / CONT 三类 Ability 的基本职责差异。

各类型内部如何表达 Condition、Timing、Trigger、Cost 与 Effect，将在后续小节继续定义。

<!-- ABILITY_NAV_START -->
[← 上一小节](02_ability_basic_definition.md) | [返回 2.4 目录](README.md) | [下一小节 →](04_ability_definition_structure.md)
<!-- ABILITY_NAV_END -->
