# 3.2 扫描范围与文件发现规则

Card JSON Scanner 负责从 `cards/` 目录树中发现候选 Card JSON 文件。

Scanner 的职责仅限于：

```text
发现文件
```

它不负责判断文件内容是否合法，也不负责生成 Card Index。

## 扫描起点与扫描边界

Card Scanner 的扫描范围严格限制在：

```text
cards/
```

目录树内部。

Scanner 不应扫描仓库中的其他 JSON 数据域。

例如：

```text
decks/
└─ example_deck.json
```

不属于 Card Scanner 的扫描范围，也不应进入 Card Validation。

后续如果 Deck 数据也采用 JSON，应由独立的 Deck Scanner / Deck Loader 负责处理。

因此应保持：

```text
cards/
→ Card Scanner

decks/
→ Deck Scanner / Deck Loader
```

不同数据域之间互不混用 Scanner。

## 规范目录结构

Card JSON 的规范目录结构按照第 3.1 节规定：

```text
cards/
└─ <title_code>/
   └─ <product_code>/
      └─ *.json
```

例如：

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
cards/TEST/TE01/TEST_W_TE01_T002.json
cards/TEST/TE02/TEST_W_TE02_T001.json
```

## 候选文件

Scanner 在 `cards/` 目录树内部识别：

```text
*.json
```

作为候选 Card JSON。

扫描结果应是一组候选文件路径。

概念上：

```text
scan_cards()
→ [
    path_1,
    path_2,
    path_3,
    ...
  ]
```

此时这些路径只表示：

```text
发现了可能的 Card JSON
```

不表示它们已经通过 Validation。

## `cards/` 内非规范位置的 JSON

对于 `cards/` 目录树内部发现的 JSON，即使其位置不符合：

```text
cards/<title_code>/<product_code>/
```

的规范结构，Scanner 仍可以将其作为候选 Card JSON 返回。

例如：

```text
cards/TEST_W_TE01_T001.json
```

或：

```text
cards/TEST/TEST_W_TE01_T001.json
```

都位于 `cards/` 扫描边界内，因此可以被发现。

后续由 Validation 判断其：

```text
目录层级
文件名
JSON 内容
```

是否符合 Card 数据规范。

这样可以避免因为目录结构错误而使非法 Card JSON 被 Scanner 直接跳过，从而失去错误报告机会。

但这一规则只适用于：

```text
cards/
```

内部。

`cards/` 之外的 JSON 文件不属于 Card Scanner 的候选范围。

## Scanner 不解释 Card Number

Scanner 不应仅根据文件名直接生成 Base Card Number。

例如发现：

```text
TEST_W_TE01_T001.json
```

Scanner 只负责记录这个文件路径。

它不应直接推断：

```text
base_card_number = TEST/WTE01-T001
```

Base Card Number 必须在读取并验证 JSON 中的结构化 `card_number` 后，由统一 formatter 生成。

文件名只用于后续 Validation 时检查：

```text
文件名
↔ JSON 中的 Card Number
```

是否一致。

## Scanner 不判断合法性

Scanner 不负责判断：

```text
JSON 是否可以解析
必要字段是否存在
字段类型是否正确
Card Number 格式是否合法
文件名是否符合命名规范
目录层级是否正确
路径与 JSON 内容是否一致
是否存在重复 Base Card Number
```

这些都属于后续 Validator / Index Builder 的职责。

因此：

```text
Scanner
→ Candidate Discovery

Validator
→ Data Legality

Index Builder
→ Mapping Construction
```

三者应保持分离。

## 非 JSON 文件

`cards/` 目录中如果存在其他类型文件，例如：

```text
README.md
notes.txt
image.png
```

Scanner 应忽略这些文件。

只有：

```text
*.json
```

进入候选 Card JSON 集合。

## 扫描顺序

文件系统返回的遍历顺序不能作为 Card 数据顺序或 Index 顺序的事实来源。

因此 Scanner 不应依赖：

```text
文件系统顺序
创建时间
修改时间
操作系统返回顺序
```

来建立稳定语义。

如果后续 Index 输出需要稳定顺序，应在 Index 构建阶段按照明确规则排序。

## 扫描结果

Scanner 的输出只应包含足够进行后续处理的信息。

最小结果可以是：

```text
CandidateCardFile
└─ json_path
```

或者直接返回路径集合。

不建议 Scanner 提前读取并保存大量 Card 内容。

推荐处理链：

```text
cards/
  ↓
Scanner
  ↓
Candidate JSON Paths
  ↓
Validator
  ↓
Validated Card Data
  ↓
Base Card Number Formatter
  ↓
Index Builder
```

本节只定义候选 Card JSON 的发现规则。

JSON 内容合法性、路径一致性、Base Card Number 生成和 Index 构建将在后续小节定义。
