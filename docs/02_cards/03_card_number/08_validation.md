# 2.3.8 Validation

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](07_json_storage_example.md) | [返回 2.3 目录](README.md) | 下一小节 →
<!-- CARD_NUMBER_NAV_END -->
Base Card Number 在写入或载入 Card Definition 前必须通过 Validation。

Validation 的目标不是解释游戏规则，而是保证 Card JSON 中保存的 Base Card Number 结构完整、类型正确，并且能够稳定生成唯一的基础编号。

至少需要检查以下内容：

```text
结构完整性
→ 必要字段是否全部存在

字段类型
→ 各字段是否为预期的 string

字段格式
→ 是否符合当前允许的格式规范

编号一致性
→ 结构化字段是否能够稳定生成 Base Card Number

唯一性
→ 不同基础 Card Definition 是否发生 Base Card Number 冲突
```

## 必要字段

Card JSON 中的 `card_number` 必须包含：

```text
title_code
side
product_code
product_card_number
```

任一字段缺失，都应视为非法数据。

例如：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": "TE01"
  }
}
```

由于缺少：

```text
product_card_number
```

必须被 Validation 拒绝。

## 字段类型

上述四个字段都必须是字符串。

例如：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": "TE01",
    "product_card_number": 1
  }
}
```

其中：

```text
product_card_number = 1
```

是错误类型。

即使它可以被转换为字符串，也不应由 Loader 静默修正。

## `null` 与空值

Base Card Number 的组成字段不使用 `null` 表示缺省。

例如：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": null,
    "product_card_number": "T001"
  }
}
```

必须被拒绝。

空字符串是否合法，应由对应字段的格式规则统一决定；Loader 不应把空字符串自动解释为“缺省”。

## 格式检查

每个字段的合法格式应由 Card Number Validation 统一管理。

例如可以分别检查：

```text
title_code
side
product_code
product_card_number
```

是否符合当前允许的格式。

具体格式规则不应散落在 Card Loader、Deck 或其他调用方中。

## Base Card Number 生成一致性

通过 Validation 的结构化 Card Number 必须能够由统一 formatter 稳定生成唯一的 Base Card Number。

概念流程：

```text
validated structured Card Number
            ↓
         formatter
            ↓
     Base Card Number
```

相同的结构化字段必须始终生成相同的 Base Card Number。

Card JSON 不保存第二份完整 Base Card Number 字符串，因此不存在“结构化字段与保存字符串不一致”这一双重事实来源问题。

## 唯一性

一个 Base Card Number 只能对应一个基础 Card Definition。

因此，如果两个不同的 Card JSON 最终生成相同的：

```text
base_card_number
```

则必须被拒绝。

例如：

```text
Card A
→ TEST/WTE01-T001

Card B
→ TEST/WTE01-T001
```

如果二者代表不同的基础 Card Definition，则构成编号冲突。

这一类跨文件唯一性检查通常需要在批量扫描或建立 Index 时完成；本节只规定该约束存在。

## Variant

Variant 不属于当前 Card JSON 中保存的 Base Card Number。

因此本节的 Validation 不负责：

```text
Variant 格式
Full Card Number
Variant 唯一性
Variant 与资源映射
```

这些规则留待后续 Index / Variant 相关章节定义。

## 错误报告

Validation 应尽量精确指出失败原因，而不是只返回笼统的：

```text
Invalid Card Number
```

例如：

```text
missing field: product_card_number
invalid type: side must be string
invalid format: title_code
duplicate base_card_number: TEST/WTE01-T001
```

这样可以使 Card 数据错误在导入阶段被直接定位，而不是延迟到 Engine 或 Deck 等上层系统中才暴露。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](07_json_storage_example.md) | [返回 2.3 目录](README.md) | 下一小节 →
<!-- CARD_NUMBER_NAV_END -->
