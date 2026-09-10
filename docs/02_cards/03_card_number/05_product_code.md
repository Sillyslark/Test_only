# 2.3.5 `product_code`

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](04_side.md) | [返回 2.3 目录](README.md) | [下一小节 →](06_product_card_number.md)
<!-- CARD_NUMBER_NAV_END -->
`product_code` 表示 Card Number 中用于区分商品、补充包、预组或其他收录批次的代码。

它是模拟器内部用于表达 Card Number 结构边界的字段名称。当前阶段不将 `product_code` 声明为 Bushiroad 已确认的官方字段术语。

例如：

```text
TEST/WTE01-T001
```

其中：

```text
product_code = TE01
```

在 Card JSON 中，`product_code` 作为 Base Card Number 的结构化组成字段保存。

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
标识 Card 所属的商品 / 收录批次
→ 作为 Base Card Number 的组成部分

参与生成 Base Card Number
→ 与 title_code、side、product_card_number 共同构成稳定编号

为后续数据组织提供稳定字段
→ Index、文件组织或资源系统可以读取该字段
```

`product_code` 不包含 `side`。

因此：

```text
WTE01
```

不能直接视为 `product_code`。

其结构仍然是：

```text
W
→ side

TE01
→ product_code
```

Card 数据层只负责保存 `product_code` 本身，不在这里定义它如何参与 Index、目录布局或其他查询基础设施。

规则与约束：

- `product_code` 必须存在；
- 值必须是字符串；
- 不使用 `null`；
- 不包含 `side`；
- 不与 `product_card_number` 合并；
- 不通过完整 Card Number 字符串的猜测式切割临时恢复；
- 合法值与格式由 Card Number Validation 统一检查。

例如：

```text
TE01
```

可以作为测试数据中的 `product_code`。

其具体含义由测试数据约定决定，但不建立测试专用的数据结构。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](04_side.md) | [返回 2.3 目录](README.md) | [下一小节 →](06_product_card_number.md)
<!-- CARD_NUMBER_NAV_END -->
