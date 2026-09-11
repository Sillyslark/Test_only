# 2.3.3 `title_code`

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](02_card_number_structure.md) | [返回 2.3 目录](README.md) | [下一小节 →](04_side.md)
<!-- CARD_NUMBER_NAV_END -->
`title_code` 表示 Card Number 中的作品番号 / Title Code。

它位于 Base Card Number 的最前部，并位于 `/` 之前。

例如：

```text
TEST/WTE01-T001
```

其中：

```text
title_code = TEST
```

在 Card JSON 中，`title_code` 作为 Base Card Number 的结构化组成字段保存。

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
标识 Card 所属的作品 / Title
→ 作为 Base Card Number 的组成部分

参与生成 Base Card Number
→ 与 side、product_code、product_card_number 共同构成稳定编号

为上层系统提供 Title 信息
→ Deck Legality 等系统可以读取该字段
```

`title_code` 本身不负责解释不同 Title 之间是否允许共同构筑。

因此必须区分：

```text
title_code
→ Card Number 数据

Title 之间的构筑兼容关系
→ Deck Legality 规则
```

Card 数据层只负责准确保存 `title_code`，不在这里编码 Title 之间的游戏规则关系。

规则与约束：

- `title_code` 必须存在；
- 值必须是字符串；
- 不使用 `null`；
- 不从完整 Card Number 字符串中临时猜测式切割；
- 不由文件夹名称隐式替代 JSON 中的事实来源；
- 合法值与格式由 Card Number Validation 统一检查。

测试数据可以使用保留的测试用 Title Code，例如：

```text
TEST
```

测试用 Title Code 仍按普通 `title_code` 处理，不建立 TEST 专用的数据结构或解析分支。

<!-- CARD_NUMBER_NAV_START -->
[← 上一小节](02_card_number_structure.md) | [返回 2.3 目录](README.md) | [下一小节 →](04_side.md)
<!-- CARD_NUMBER_NAV_END -->
