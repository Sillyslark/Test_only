> [← 返回第 2 章目录](../02_cards.md)

# 附录 A：Card Number 与 Card Index

## A.1 目的与范围

Card Number 是 Card Definition 的固有识别编号，同时也是模拟器定位 Card
Definition 与对应卡图的稳定查询键。

本附录规定模拟器如何表示、生成、存储、定位和使用 Card
Number。这里讨论的是 Card 数据、卡图资源与查询基础设施，不负责定义 Deck
本身，也不负责 Game Initialization。

Card 层只要求 Base Card Number 能够唯一地区分并定位 Card
Definition。Full Card Number 可以进一步区分同一基础 Card
的不同表现版本。Card Number
内部字段在其他系统中的规则用途，由对应系统决定。

## A.2 Card Number 的结构化表示

模拟器内部将 Card Number
保存为结构化数据，而不是把完整编号字符串作为唯一事实来源，再依靠不确定的反向切割恢复其结构。

当前结构为：

``` text
CardNumber
├─ title_code
├─ side
├─ product_code
├─ product_card_number
└─ variant_code
```

其中 `variant_code` 为可选字段。

以测试编号为例：

``` text
TEST/WTE01-T001S
```

对应：

``` text
title_code          = TEST
side                = W
product_code        = TE01
product_card_number = T001
variant_code        = S
```

`TEST` 是模拟器保留的测试用 Title Code。它在 Card Number
结构和查询流程中按照普通 Title Code 处理，不建立 TEST 专用解析分支。

Card JSON 保存用于描述基础 Card 的结构化 Card Number
数据，而不是同时保存一份独立的完整编号字符串。完整编号字符串由统一
formatter 根据结构化字段生成。

同一 Base Card Number 的不同 `variant_code` 不创建新的 Card
JSON。多个拥有相同 Base Card Number 的 Full Card Number 应定位到同一个
Card JSON。

这项约束不禁止未来提供具有明确格式规范的
`CardNumber.parse()`，用于处理外部输入、导入或调试命令。禁止的是在内部数据中以完整字符串作为唯一事实来源，再依赖猜测式解析恢复字段边界。

### A.2.1 title_code

`title_code` 对应日文官方所称的作品番号，以及英文资料中的 Title Code。

它位于完整 Card Number 的 `/` 之前。

`title_code` 是 Card Number 的组成部分，同时可以被 Deck
等上层规则系统用于构筑规则判断。Card 层本身不解释 Title Code
之间的构筑兼容关系。

### A.2.2 side

`side` 表示 Card 所属的 Side。

`side` 与 `product_code` 是两个独立字段。即使两者在 Full Card Number
中连续书写，`side` 也不属于 `product_code`。

例如：

``` text
TEST/WTE01-T001
     │└── TE01 = product_code
     └─── W    = side
```

因此：

``` text
WTE01
```

在显示字符串中是 `side + product_code` 的连续结果，而不是一个整体的
`product_code`。

Side 的具体合法值由 Card Number 的合法值接口统一定义。Deck
等规则系统可以根据赛制读取该字段。

### A.2.3 product_code

`product_code` 表示 Card 所属商品或收录批次的内部代码。

该名称是模拟器内部术语，用于明确 Card Number 中商品 /
收录层级的结构边界；当前不将其声明为 Bushiroad 已确认的官方字段名称。

测试数据中：

``` text
TE01
```

表示测试用商品 / 收录批次 01。

`product_code` 不包含 `side`。

### A.2.4 product_card_number

`product_card_number` 表示同一 `product_code` 下用于区分具体基础 Card
的编号。

它不是完整 Card Number，也不是对局中的 `card_id`。

例如：

``` text
TEST/WTE01-T001
TEST/WTE01-T002
```

两者属于同一测试 Title、Side 和 Product，但通过不同的
`product_card_number` 区分不同的基础 Card Definition。

该字段按字符串处理，不假定其必须是纯整数。

### A.2.5 variant_code

`variant_code` 是可选的印刷 / 表现版本代码。

它用于区分同一个基础 Card
的不同印刷、Parallel、异画或其他表现版本，并用于区分对应的实际卡图。

例如：

``` text
TEST/WTE01-T001
TEST/WTE01-T001S
```

二者拥有相同的：

``` text
base_card_number = TEST/WTE01-T001
```

第二个编号额外拥有：

``` text
variant_code = S
```

`variant_code` 不创建新的基础 Card Definition，不改变该 Card
的规则身份，也不参与游戏逻辑。

现实 Card Number 中存在 `S`、`BNP`、`SP`
等不同形式的后缀。当前阶段只把这些值作为版本代码保存，不实现其
Rarity、Parallel 或其他规则语义。

## A.3 Base Card Number 与 Full Card Number

结构化 `CardNumber` 是 Card Number 各组成字段的事实来源。

其中：

``` text
base_card_number
=
title_code
+ side
+ product_code
+ product_card_number
```

而：

``` text
full_card_number
=
base_card_number
+ optional variant_code
```

例如：

``` text
title_code          = TEST
side                = W
product_code        = TE01
product_card_number = T001
variant_code        = S
```

生成：

``` text
base_card_number = TEST/WTE01-T001
full_card_number = TEST/WTE01-T001S
```

`base_card_number` 表示基础 Card 的规则身份。

不同 Card Definition 不得拥有相同的 `base_card_number`。

`variant_code` 不改变基础 Card Definition，因此：

``` text
TEST/WTE01-T001
TEST/WTE01-T001S
TEST/WTE01-T001BNP
```

可以表示同一个基础 Card Definition 的不同表现版本，并应定位到同一个 Card
JSON。

`full_card_number` 用于精确表示具体印刷 /
表现版本，并用于定位对应的实际卡图。

相同结构化数据必须始终生成相同的 `base_card_number` 与
`full_card_number`。Card JSON
不得同时维护一份可能与结构化字段冲突的独立完整编号字符串。

## A.4 Card 与 Card Image 的存储结构

### A.4.1 Card JSON

Card JSON 按 Card Number 中稳定的目录层级组织。

当前目录规则为：

``` text
cards/
└─ <title_code>/
   └─ <product_code>/
      └─ <Base Card Number 对应文件名>.json
```

例如：

``` text
cards/
└─ TEST/
   └─ TE01/
      └─ TEST_WTE01-T001.json
```

因此：

``` text
title_code = TEST
product_code = TE01
```

只能确定 Product 存储目录：

``` text
cards/TEST/TE01/
```

它们不能单独确定具体 Card Definition。

具体基础 Card Definition 由 `base_card_number` 唯一定位。

一个 Base Card Number 对应一个 Card JSON。不同 `variant_code` 不创建新的
Card JSON。

Card JSON 文件名由对应的 Base Card Number 生成。由于 `/`
不能直接作为普通文件名的一部分，生成文件名时统一将 Card Number 中的 `/`
替换为 `_`：

``` text
TEST/WTE01-T001
↓
TEST_WTE01-T001.json
```

该替换仅用于文件名，不改变 Base Card Number 本身。

`side` 不参与目录层级；`variant_code` 不承担 Card Definition
的目录层级或文件命名职责。

业务代码不得自行拼接 Card JSON 路径。

### A.4.2 Card Image

实际卡图统一存放在：

``` text
card_images/
```

`card_images/` 只保存实际卡图，不保存 Card Definition、规则数据或其他 UI
资源。

其目录层级与 `cards/` 保持对应：

``` text
card_images/
└─ <title_code>/
   └─ <product_code>/
      └─ <Full Card Number 对应文件名>.<image extension>
```

例如：

``` text
card_images/
└─ TEST/
   └─ TE01/
      ├─ TEST_WTE01-T001.png
      ├─ TEST_WTE01-T001S.png
      └─ TEST_WTE01-T001SP.png
```

Card Image 文件名由对应的 Full Card Number 生成，并与 Card JSON
使用相同的文件名转换规则：将 Card Number 中的 `/` 替换为 `_`。

例如：

``` text
TEST/WTE01-T001SP
↓
TEST_WTE01-T001SP.png
```

该替换仅用于文件名，不改变 Full Card Number 本身。

因此，同一 Base Card Number 可以只有一个 Card JSON，同时拥有多个不同
Full Card Number 对应的 Card Image。

Card Image 是否存在不影响基础 Card Definition 的规则合法性。缺少卡图属于
UI / Resource 问题，不得因此使 Card Definition、DeckRecipe 或 Deck
构筑在规则层失效。

## A.5 Card Index

Card Index 是根据 `cards/` 与 `card_images/`
中的实际数据批量扫描生成的导航索引。

Card Index 不是 Card 数据的第二份事实来源，也不人工维护 Card
Information。它应能够根据当前实际文件重新生成。

Card Index 的核心查询键为 Full Card Number。每个已登记的 Full Card
Number 可以导航到：

``` text
Full Card Number
├─ 对应 Card JSON location
└─ 对应 Card Image location
```

其中 Card Image location 可以不存在；Card JSON location
对于可用于规则系统的 Card 必须能够定位到合法的基础 Card JSON。

例如：

``` text
TEST/WTE01-T001
├─ cards/TEST/TE01/TEST_WTE01-T001.json
└─ card_images/TEST/TE01/TEST_WTE01-T001.png

TEST/WTE01-T001S
├─ cards/TEST/TE01/TEST_WTE01-T001.json
└─ card_images/TEST/TE01/TEST_WTE01-T001S.png

TEST/WTE01-T001SP
├─ cards/TEST/TE01/TEST_WTE01-T001.json
└─ card_images/TEST/TE01/TEST_WTE01-T001SP.png
```

因此，多个拥有相同 Base Card Number 的 Full Card Number 应导航到同一个
Card JSON，但可以导航到不同的 Card Image。

Card Index 的生成流程概念上为：

``` text
cards/
   ↓
批量扫描 Card JSON
   ↓
Card Loader 严格验证
   ↓
确认合法 Base Card Number 与 Card JSON location
   │
   ├──────────────┐
   │              │
   │         card_images/
   │              ↓
   │       批量扫描实际卡图
   │              ↓
   │       根据文件名确认 Full Card Number
   │              │
   └───────┬──────┘
           ↓
       生成 Card Index
```

Index 生成脚本不得重新实现一套 Card JSON Schema Validation。Card JSON
的合法性继续由既有 Card Loader 与 Card Information 合法值接口负责。

调用方应通过 Card Index 查询位置，而不是自行遍历
`cards/`、`card_images/` 或自行拼接路径。

Card Index 负责隐藏实际文件布局。以后即使 Card 文件或 Card Image
的组织方式改变，Deck、Engine、UI 等调用方也不应因此直接修改其业务逻辑。

Card Index 是派生数据。删除 Card Index
后，应能够通过重新扫描源数据恢复。

## A.6 Card Number 的规则用途

`base_card_number` 首先用于唯一识别基础 Card
Definition，并代表其规则身份。

其结构化字段可以被上层规则系统按需使用：

``` text
title_code
→ 可供 Deck 构筑规则判断使用

side
→ 可供基于 Weiß / Schwarz Side 的构筑规则使用

product_code
→ 当前主要用于数据组织、定位与商品 / 收录归属

product_card_number
→ 区分同一 Product 中的具体基础 Card Definition

variant_code
→ 不改变规则身份；当前仅用于区分印刷 / 表现版本及对应卡图
```

Card 层不负责实现这些上层规则。

Title Code 是否可以共同构筑属于 Deck Legality，而不是 Card Number 本身。

Deck 等游戏逻辑在需要判断"是否为同一基础 Card"时，应以
`base_card_number` 为身份依据，而不是以 `full_card_number`
区分不同表现版本。

## A.7 Variant 扩展接口

Card Number 模型必须允许未来进一步解释
`variant_code`，但当前不得提前建立未经需要验证的 Rarity / Parallel
规则模型。

当前阶段只保证：

``` text
variant_code: optional
```

并规定：

-   `variant_code` 不改变 `base_card_number`；
-   `variant_code` 不创建新的 Card Definition；
-   `variant_code` 可以参与 `full_card_number`；
-   `variant_code` 可以用于区分对应的实际卡图；
-   当前游戏逻辑不得依赖 `variant_code` 判断卡片规则身份。

未来如果确实需要区分具体 Rarity、Parallel
或其他印刷属性，应另行定义对应的数据模型、合法值、语义和测试，而不是直接把
`variant_code` 等同于 Rarity。

## A.8 Validation

Card Number、Card 文件、Card Image 与 Card Index 的 Validation
至少需要区分：

1.  必要组成字段缺失；
2.  字段类型错误；
3.  字段值不属于当前允许的合法值或格式；
4.  两个不同 Card Definition 拥有相同 `base_card_number`；
5.  Card Number 所表达的 `title_code / product_code`
    与实际存储目录不一致；
6.  Card Index 无法根据 Full Card Number 定位对应的合法 Card JSON；
7.  同一 `base_card_number` 对应多个基础 Card Definition；
8.  Card JSON 文件名与其 Base Card Number 按规定生成的文件名不一致；
9.  Card Image 文件名与其 Full Card Number 按规定生成的文件名不一致；
10. Card Image 的 Full Card Number 无法对应到已存在的 Base Card Number；
11. 同一 Full Card Number 对应多个 Card Image；
12. Card Image 缺失。

Validation 应精确报告具体失败原因。

其中，Card Image 缺失属于 UI / Resource 问题，不属于 Card Definition 或
Deck Legality 错误；Validation 可以报告该问题，但不得因此将基础 Card
的规则数据判定为非法。

`variant_code` 不参与基础 Card Definition
的唯一性判断，但参与具体表现版本及 Card Image 映射的唯一性检查。

Card Number Validation 只判断编号及其数据映射是否合法，不承担 Deck
Legality。

## A.9 测试要求

至少覆盖：

-   结构化 Card Number 能稳定生成 `base_card_number`；
-   存在 `variant_code` 时能稳定生成 `full_card_number`；
-   `side` 与 `product_code` 的边界不依赖字符串猜测；
-   Card JSON 使用结构化 Card Number，不维护第二份独立完整编号字符串；
-   `variant_code` 缺省时正常工作；
-   不同 `variant_code` 可以映射到同一个基础 Card Definition；
-   不同 Card Definition 使用相同 `base_card_number` 时被拒绝；
-   一个 Base Card Number 只对应一个 Card JSON；
-   Card JSON 文件名由 Base Card Number 按统一规则生成；
-   Card Image 文件名由 Full Card Number 按统一规则生成；
-   Card JSON 与 Card Image 的文件名转换均只将 Card Number 中的 `/`
    替换为 `_`；
-   Card Index 能根据 Full Card Number 定位正确 Card JSON；
-   多个相同 Base Card Number 的 Full Card Number 能定位到同一个 Card
    JSON；
-   不同 Full Card Number 能定位到各自对应的 Card Image；
-   Card Image 缺失时不影响基础 Card Definition 与 Deck Legality；
-   无法对应到现有 Base Card Number 的 Card Image 被精确报告；
-   `title_code + product_code` 只负责定位 Product 目录，而不是被误用作
    Card Definition 唯一键；
-   不存在的 Card Number 被精确拒绝；
-   Card Number 与实际目录不一致时被拒绝；
-   TEST Card 与正式 Card 使用同一查询路径，不存在 TEST 专用逻辑；
-   Card Index 删除后可以由扫描脚本重新生成；
-   Index 生成过程复用既有 Card Loader，不建立第二套 Card JSON Schema
    Validation；
-   未来如实现 `CardNumber.parse()`，其解析结果必须与结构化 Card Number
    的 formatter 互为一致的规范转换，而不能依赖猜测式切割。

## A.10 尚未决定的问题

当前保留：

-   `variant_code` 的完整合法值集合；
-   Parallel / Rarity 与 `variant_code` 之间的正式映射；
-   Card Image 支持的最终图片格式集合；
-   Card Index 的具体持久化格式；
-   Card Index 是否需要额外的内存缓存；
-   外部完整 Card Number 的正式 Parser 及历史特殊格式兼容策略；
-   Product Code 的进一步官方术语映射；
-   Deck 对 Card Number 各字段的完整使用规则。

------------------------------------------------------------------------

> [← 返回第 2 章目录](../02_cards.md)
