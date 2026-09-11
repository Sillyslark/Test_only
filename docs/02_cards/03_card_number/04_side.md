# 2.3.4 `side`

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](03_title_code.md) | [返回 2.3 目录](README.md) | [下一小节 →](05_product_code.md)
<!-- CARD_NUMBER_NAV_END -->
`side` 表示 Card Number 中的 Side 信息。

它与 `product_code` 是两个独立字段。即使二者在最终显示的 Base Card Number 中连续书写，也不应把它们合并成一个字段。

例如：

```text
TEST/WTE01-T001
```

其中：

```text
side = W
product_code = TE01
```

也就是说：

```text
WTE01
```

在显示字符串中只是：

```text
side + product_code
```

的连续结果，而不是一个整体字段。

在 Card JSON 中，`side` 作为 Base Card Number 的结构化组成字段保存。

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
保存 Card 所属的 Side
→ 作为 Base Card Number 的组成部分

参与生成 Base Card Number
→ 与 title_code、product_code、product_card_number 共同构成稳定编号

向上层规则系统暴露 Side 信息
→ Deck Legality 等系统可以读取该字段
```

`side` 本身不负责解释 Weiß / Schwarz Side 的构筑规则。

因此必须区分：

```text
side
→ Card Number 数据

基于 Side 的构筑限制
→ Deck Legality 规则
```

Card 数据层只负责准确保存 `side`，不在这里实现基于 Side 的游戏规则。

规则与约束：

- `side` 必须存在；
- 值必须是字符串；
- 不使用 `null`；
- `side` 与 `product_code` 必须保持为两个独立字段；
- 不从 `side + product_code` 的连续字符串中临时猜测字段边界；
- 合法值与格式由 Card Number Validation 统一检查。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](03_title_code.md) | [返回 2.3 目录](README.md) | [下一小节 →](05_product_code.md)
<!-- CARD_NUMBER_NAV_END -->
