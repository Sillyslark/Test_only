# 2.4.6 Ability 的顺序

<!-- ABILITY_NAV_START -->
[← 上一小节](05_effect_and_ability.md) | [返回 2.4 目录](README.md) | [下一小节 →](07_ability_json_storage.md)
<!-- ABILITY_NAV_END -->
同一张 Card 上的多个 Ability 必须保持定义顺序。

例如：

```text
Card
└─ abilities
   ├─ Ability 1
   ├─ Ability 2
   └─ Ability 3
```

这里的顺序应与 Card 数据中记录的顺序保持一致。

因此：

```text
abilities[]
```

必须使用有序结构保存。

推荐程序表示：

```python
abilities: tuple[AbilityDefinition, ...]
```

而不是：

```python
set[AbilityDefinition]
```

也不应依赖：

```text
Ability Type
Ability Name
Hash
字典遍历顺序
文件系统顺序
```

来重新推导 Ability 的先后关系。

## 顺序属于 Card Definition

Ability 的排列顺序属于 Card Definition 的静态数据。

也就是说：

```text
Card Definition
→ 保存 Ability 1 / 2 / 3 的定义顺序
```

而不是在运行时临时排序。

Loader 在读取 Card JSON 后，应保持输入数组中的 Ability 顺序。

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

对应 Definition 中也必须保持：

```text
1. AutomaticAbility
2. ContinuousAbility
3. ActivatedAbility
```

不得自动重排为：

```text
ACT
AUTO
CONT
```

或任何其他固定类型顺序。

## 定义顺序与结算顺序

必须区分：

```text
Definition Order
→ Card 上多个 Ability 的静态排列顺序

Resolution Order
→ 某次实际规则处理时的结算顺序
```

二者不是同一个概念。

Ability 在 Card Definition 中排在前面，不代表它在所有运行时场景中一定先结算。

例如多个 AUTO 同时满足时，实际进入 Standby Ability Pool、Check Timing，以及后续结算顺序，应由 Engine 与 WS 规则系统决定。

因此：

```text
abilities[] 的顺序
≠ 全局结算优先级
```

本节只要求 Card Definition 不丢失原始 Ability 顺序。

## 为什么必须保留顺序

保留顺序可以支持：

```text
与官方 Card Text 对照
稳定生成显示文本
调试
测试
差异比较
未来需要按印刷顺序处理的规则
```

同时也避免 Loader 或序列化过程对数据做无意义重排。

## 不建立额外顺序编号

当前不要求为每个 Ability 再保存：

```text
ability_index
order
priority
```

之类的重复字段。

数组位置本身已经能够表达定义顺序。

如果未来确实存在独立于数组位置的规则优先级，再单独定义对应字段。

因此当前原则为：

```text
Card JSON abilities 数组顺序
→ Definition 顺序的唯一事实来源
```

本节只定义 Ability 的静态排列顺序。

AUTO 同时触发、待机能力池、Check Timing 与实际 Resolution Order 等运行时规则，不属于本节内容。

<!-- ABILITY_NAV_START -->
[← 上一小节](05_effect_and_ability.md) | [返回 2.4 目录](README.md) | [下一小节 →](07_ability_json_storage.md)
<!-- ABILITY_NAV_END -->
