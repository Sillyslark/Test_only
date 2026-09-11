# 2.4.7 Card JSON 中的 Ability 存储原则

<!-- ABILITY_NAV_START -->
[← 上一小节](06_ability_order.md) | [返回 2.4 目录](README.md) | [下一小节 →](08_current_implementation_boundary.md)
<!-- ABILITY_NAV_END -->
Card JSON 中保存的是 Ability Definition 的结构化数据。

它不保存某次对局中的触发状态、选择结果、支付结果或结算进度。

因此：

```text
Card JSON
→ Static Ability Definition

Game State / Runtime Context
→ Dynamic Ability State
```

## 基本结构

概念上，Card JSON 可以使用：

```json
{
  "abilities": [
    {
      "ability_type": "auto",
      "trigger": {
        "type": "..."
      },
      "condition": {
        "type": "..."
      },
      "effects": [
        {
          "type": "..."
        }
      ]
    }
  ]
}
```

这里仅表示结构方向，不锁定最终 Schema。

具体字段名称、Trigger 类型、Condition 类型、Cost 类型和 Effect 类型，应由后续 Ability / Rule Schema 设计统一定义。

## `abilities` 必须是有序数组

Card JSON 中：

```text
abilities
```

应使用数组保存。

例如：

```json
{
  "abilities": [
    { "ability_type": "auto" },
    { "ability_type": "cont" },
    { "ability_type": "act" }
  ]
}
```

数组顺序即为 Ability Definition 的顺序。

Loader 必须保持这一顺序，不自动排序。

## 没有 Ability 的 Card

如果 Card 没有任何 Ability，推荐显式保存：

```json
{
  "abilities": []
}
```

而不是：

```json
{
  "abilities": null
}
```

也不推荐让：

```text
字段缺失
```

同时承担“没有 Ability”的语义。

这样可以使：

```text
abilities
→ 始终是 array
```

从而简化 Loader、Validation 和测试。

## Ability Type 的序列化

Ability Type 在 JSON 中建议使用小写枚举值：

```text
act
auto
cont
```

例如：

```json
{
  "ability_type": "auto"
}
```

对应程序中的：

```python
AbilityType.AUTO
AutomaticAbility
```

JSON 不应依赖 Python class 名称作为稳定数据格式。

因此不建议：

```json
{
  "ability_type": "AutomaticAbility"
}
```

因为：

```text
JSON Schema
→ 数据协议

Python Class Name
→ 实现细节
```

二者应保持解耦。

## 不保存可执行代码

Card JSON 中不得直接保存：

```text
Python source code
lambda
eval 表达式
任意脚本
```

来实现 Ability。

例如不应采用：

```json
{
  "effect": "game.player.draw(1)"
}
```

再通过：

```python
eval(...)
```

执行。

Ability JSON 应保存结构化数据，由 Loader 转换为受控的 Ability Definition / Effect Definition。

概念流程：

```text
Card JSON
    ↓
Validation
    ↓
Ability Loader / Compiler
    ↓
AbilityDefinition
    ↓
Engine / Rule System
```

这样可以保证：

```text
数据格式可验证
规则入口受控
行为可测试
错误可以提前发现
```

## 不把自然语言作为执行数据

Card JSON 即使未来保存官方 Card Text，也不能把自然语言字符串作为 Engine 的执行逻辑。

例如：

```json
{
  "card_text": "[AUTO] When this card is placed..."
}
```

可以用于显示或校对。

但不能：

```text
读取 card_text
→ 自然语言解析
→ 直接执行规则
```

正常执行仍应依赖：

```text
abilities[]
```

中的结构化 Ability Definition。

## Definition 与 Runtime 分离

Card JSON 中不得保存：

```text
triggered
activated
resolved
selected_targets
paid_cost
current_step
```

这些内容都属于某次实际 Ability 处理过程。

因此：

```json
{
  "triggered": true
}
```

不属于基础 Card JSON。

运行时数据应由 Game State、Standby Ability、Ability Runtime Context 或对应 Resolution State 保存。

## 当前阶段允许空实现

在测试阶段，如果某张 Card 的 Ability 尚未完成结构化实现，可以暂时使用：

```json
{
  "abilities": []
}
```

使 Card Definition 仍然能够被 Loader 读取并参与基础数据测试。

这表示：

```text
当前模拟器数据尚未实现该 Card 的 Ability
```

而不是声明官方卡片一定没有 Card Text。

因此测试数据与完整 Card 数据之间应能够明确区分其完成程度。

本节只定义 Ability 在 Card JSON 中的基本存储原则。

最终 Ability Schema、Effect Schema、Loader / Compiler 结构和具体规则类型将在对应实现阶段继续定义。

<!-- ABILITY_NAV_START -->
[← 上一小节](06_ability_order.md) | [返回 2.4 目录](README.md) | [下一小节 →](08_current_implementation_boundary.md)
<!-- ABILITY_NAV_END -->
