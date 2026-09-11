# 2.3.6 `product_card_number`

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](05_product_code.md) | [返回 2.3 目录](README.md) | [下一小节 →](07_json_storage_example.md)
<!-- CARD_NUMBER_NAV_END -->
`product_card_number` 表示同一 `product_code` 下用于区分具体基础 Card Definition 的编号部分。

例如：

```text
TEST/WTE01-T001
```

其中：

```text
product_card_number = T001
```

在 Card JSON 中，`product_card_number` 作为 Base Card Number 的结构化组成字段保存。

JSON 示例：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": "TE01",
    "product_card_number": "T001"
  }
}
```

字段类型：

```text
string
```

职责：

```text
区分同一 Product 中的具体基础 Card Definition
→ 作为 Base Card Number 的组成部分

参与生成 Base Card Number
→ 与 title_code、side、product_code 共同构成稳定编号
```

例如：

```text
TEST/WTE01-T001
TEST/WTE01-T002
```

两者具有相同的：

```text
title_code
side
product_code
```

但通过不同的：

```text
product_card_number
```

区分为不同的基础 Card Definition。

`product_card_number` 不是完整 Card Number，也不是运行时 Card Instance 的 ID。

因此必须区分：

```text
product_card_number
→ Product 内部的编号组成部分

Base Card Number
→ 完整的基础 Card Definition 编号

Card Instance ID
→ 对局中某一张具体卡片实例的唯一身份
```

`product_card_number` 按字符串保存，而不是按整数保存。

原因是该字段可能包含字母、前缀、补零或其他非纯数字格式，例如：

```text
T001
```

因此不得通过：

```text
int
```

类型强制把它简化为纯数字。

规则与约束：

- `product_card_number` 必须存在；
- 值必须是字符串；
- 不使用 `null`；
- 不假定其必须是纯整数；
- 不移除前导零；
- 不自动拆分其中的字母与数字部分；
- 不与 `product_code` 合并保存；
- 合法值与格式由 Card Number Validation 统一检查。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](05_product_code.md) | [返回 2.3 目录](README.md) | [下一小节 →](07_json_storage_example.md)
<!-- CARD_NUMBER_NAV_END -->
