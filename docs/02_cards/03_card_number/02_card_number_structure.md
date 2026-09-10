# 2.3.2 Card Number 的结构化组成

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](01_purpose_and_responsibility.md) | [返回 2.3 目录](README.md) | [下一小节 →](03_title_code.md)
<!-- CARD_NUMBER_NAV_END -->
模拟器内部将 Card Number 表示为结构化数据，而不是只保存一份完整编号字符串，再依赖字符串切割恢复其组成部分。

基础结构包括：

```text
CardNumber
├─ title_code
├─ side
├─ product_code
└─ product_card_number
```

这些字段共同组成 Base Card Number。

概念关系：

```text
title_code
+ side
+ product_code
+ product_card_number
→ Base Card Number
```

例如：

```text
TEST/WTE01-T001
```

可以表示为：

```text
title_code          = TEST
side                = W
product_code        = TE01
product_card_number = T001
```

其中：

- `title_code`：作品番号 / Title Code；
- `side`：Weiß / Schwarz 等 Side 信息；
- `product_code`：商品或收录批次的内部代码；
- `product_card_number`：同一 Product 中用于区分具体基础 Card Definition 的编号。

此外，Card Number 体系允许存在：

```text
variant
```

用于区分同一基础 Card 的不同印刷或表现版本。

但在当前 Card JSON 规范中：

> Card JSON 始终只保存 Base Card Number 对应的结构化数据，不保存 Variant。

因此 Card JSON 中的 Card Number 事实来源只包括：

```text
title_code
side
product_code
product_card_number
```

Variant 的具体表示、Full Card Number 的生成方式，以及 Variant 如何参与后续索引与资源定位，不在本节展开。

这些内容将在后续 Index / Variant 相关章节中补充定义。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](01_purpose_and_responsibility.md) | [返回 2.3 目录](README.md) | [下一小节 →](03_title_code.md)
<!-- CARD_NUMBER_NAV_END -->
