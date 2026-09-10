# 3.1 JSON 文件存储位置的一般原则

Card JSON 统一存储在：

```text
cards/
```

目录下。

Card JSON 的目录层级按照：

```text
Title Code
→ Product Code
```

进行组织。

因此基础目录结构为：

```text
cards/
└─ <title_code>/
   └─ <product_code>/
      └─ Card JSON files
```

例如：

```text
cards/
└─ TEST/
   └─ TE01/
      ├─ TEST_W_TE01_T001.json
      ├─ TEST_W_TE01_T002.json
      └─ TEST_W_TE01_T003.json
```

## 目录层级

第一层目录使用：

```text
title_code
```

第二层目录使用：

```text
product_code
```

因此：

```text
cards/<title_code>/<product_code>/
```

表示某个 Title 下某个 Product 的 Card JSON 存储位置。

例如：

```text
title_code   = TEST
product_code = TE01
```

对应目录：

```text
cards/TEST/TE01/
```

## 文件命名规则

在 `product_code` 目录下，每个基础 Card Definition 对应一个 JSON 文件。

文件名统一按照以下结构生成：

```text
<title_code>_<side>_<product_code>_<product_card_number>.json
```

例如：

```text
TEST_W_TE01_T001.json
```

对应：

```text
title_code          = TEST
side                = W
product_code        = TE01
product_card_number = T001
```

因此文件名能够直接反映该 Card JSON 对应的 Base Card Number 结构。

## 文件名不包含 Variant

Card JSON 始终对应基础 Card Definition。

因此文件名只包含 Base Card Number 的组成字段：

```text
title_code
side
product_code
product_card_number
```

不包含：

```text
variant
```

也不使用 Full Card Number 作为 Card JSON 文件名。

同一基础 Card 的不同 Variant 仍然共享同一个 Card JSON。

## 目录与 JSON 内容的关系

目录和文件名用于：

```text
组织文件
缩小扫描范围
提高人工可读性
辅助 Validation
```

但 Card JSON 内部的结构化 Card Number 仍然是 Card 数据本身的事实来源。

也就是说：

```text
目录 / 文件名
→ 存储组织信息

JSON 中的 card_number
→ Card Number 数据事实
```

扫描与 Validation 时，应检查二者是否一致。

例如文件：

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
```

其 JSON 中的 Card Number 应对应：

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

如果文件路径或文件名表达的信息与 JSON 内容不一致，应由 Validation 报告错误。

## 路径不是上层查询接口

Deck、Engine 或其他业务逻辑不应直接根据 Card Number 自行拼接：

```text
cards/<title_code>/<product_code>/<filename>.json
```

来定位 Card JSON。

文件布局只属于存储层。

后续应由 Card Index 提供：

```text
base_card_number
→ json_path
```

的统一映射。

因此：

```text
Storage Layout
→ 负责“文件如何组织”

Card Index
→ 负责“如何根据 Base Card Number 定位文件”
```

这样未来即使目录结构或文件命名规则改变，上层系统也不需要同步修改路径拼接逻辑。
