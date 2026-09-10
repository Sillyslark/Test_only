# 2.3.7 JSON 存储示例

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](06_product_card_number.md) | [返回 2.3 目录](README.md) | [下一小节 →](08_validation.md)
<!-- CARD_NUMBER_NAV_END -->
Card JSON 中保存的是 Base Card Number 的结构化数据。

当前结构：

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

其中：

```text
title_code
side
product_code
product_card_number
```

共同构成 Base Card Number 的事实来源。

对应生成结果：

```text
TEST/WTE01-T001
```

Card JSON 不额外保存一份独立的完整 Base Card Number 字符串。

因此不推荐同时写成：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": "TE01",
    "product_card_number": "T001",
    "base_card_number": "TEST/WTE01-T001"
  }
}
```

原因是：

```text
结构化字段
+
重复保存的完整字符串
→ 形成两个事实来源
→ 可能产生不一致
```

Base Card Number 应由统一 formatter 根据结构化字段生成。

概念上：

```text
Card JSON
    ↓
structured Card Number
    ↓
formatter
    ↓
Base Card Number
```

Card JSON 中同样不保存 Variant。

也就是说，当前结构中不存在：

```json
{
  "variant": "S"
}
```

也不存在：

```json
{
  "full_card_number": "TEST/WTE01-T001S"
}
```

Variant 确实存在于完整 Card Number 体系中，但它不属于当前基础 Card JSON 的存储内容。

Variant、Full Card Number，以及它们如何参与后续 Index 或资源定位，将在后续相关章节中定义。

一个完整的 Card JSON 片段可以写成：

```json
{
  "card_number": {
    "title_code": "TEST",
    "side": "W",
    "product_code": "TE01",
    "product_card_number": "T001"
  },
  "name": "カード名",
  "card_type": "character",
  "color": "red"
}
```

这里只展示 Card Number 与其他基础 Card Information 的组合方式；具体字段要求仍分别以 2.2 各小节为准。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](06_product_card_number.md) | [返回 2.3 目录](README.md) | [下一小节 →](08_validation.md)
<!-- CARD_NUMBER_NAV_END -->
