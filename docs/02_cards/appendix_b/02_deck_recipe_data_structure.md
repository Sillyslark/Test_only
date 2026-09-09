> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)

# B.2 DeckRecipe 的数据结构

本节只定义 `DeckRecipe` 保存什么数据，以及这些数据本身的语义。

Card Number 是否存在、DeckRecipe 是否满足张数限制、同卡数量限制、Climax 数量限制、Title / Side 构筑限制等，均属于后续 Validation / Deck Construction Legality，不在本节判断。

## B.2.1 基本结构

`DeckRecipe` 是游戏外的卡组构成清单。

当前基本结构为：

```text
DeckRecipe
├─ construction
│  ├─ type
│  └─ type-specific declaration
│
└─ cards
   └─ sequence[Canonical Full Card Number]

一个 `cards` 元素表示一张 Card；同一卡使用多张时，以相同编号重复出现表示，不使用 `count` 字段。
```

其中：

- `construction` 声明该 DeckRecipe 采用的官方 Deck Construction 形式及其必要参数；
- `cards` 逐张记录该 DeckRecipe 实际选择的 Card；
- `DeckRecipe` 不复制 Card Information；
- `DeckRecipe` 不保存 Player / Game 信息；
- `DeckRecipe` 不表示游戏中的 Deck Zone。

## B.2.2 construction

英文官方资料使用 `Deck Construction Rules`，并使用 `Standard Constructed`、`Side Constructed`、`Neo-Standard Constructed` 等名称；日文官方资料对应使用「デッキ構築ルール」「スタンダード構築」「サイド限定構築」「ネオスタンダード構築」。

因此，本项目使用 `construction` 表示 DeckRecipe 的构筑声明，并尽量沿用官方构筑名称。

概念上：

```text
construction
├─ type = neo_standard
│  └─ title
│
├─ type = side
│  └─ side
│
└─ type = standard
```

不同 `type` 使用各自严格的 Schema。

当前已定义的合法构筑类型包括：

```text
neo_standard
side
standard
```

这不是对未来构筑类型的永久封闭枚举。若后续需要支持新的官方构筑形式，必须显式扩展 DeckRecipe Schema 与对应的 Deck Construction Rule；未知字符串不得因为未被识别而自动视为合法构筑类型。

也就是说，某种 `type` 所要求的字段必须存在，而不属于该 `type` 的字段不得混入。

### B.2.2.1 Neo-Standard Constructed

Neo-Standard 构筑声明：

```json
{
  "construction": {
    "type": "neo_standard",
    "title": "テスト"
  }
}
```

其中 `title` 表示该 DeckRecipe 声明采用的 Title。

`title` 不直接等同于单个 `title_code`。

一个官方 Title 可以对应一个或多个 Title Code；具体的：

```text
Title
↓
allowed title_codes
```

映射属于独立的 Deck Construction Rule Data，而不是由每份 DeckRecipe 自行重复保存。

因此 DeckRecipe 保存：

```text
title = canonical Title string
```

而不保存：

```text
title_codes = [...]
```

作为该 Title 的规则定义。

DeckRecipe 不自行创建或定义 Title。合法的 canonical Title string 以 Deck Construction Rule Data 中登记的 Title 为准；`DeckRecipe.construction.title` 只引用该已登记值。

### B.2.2.2 Side Constructed

Side Constructed 使用：

```text
construction.type = side
```

并保存对应的 Side 声明。

其具体合法值和构筑规则由后续 Deck Construction Rule Data 定义。

### B.2.2.3 Standard Constructed

Standard Constructed 使用：

```json
{
  "construction": {
    "type": "standard"
  }
}
```

当前不要求额外的 Title 或 Side 声明。

如果未来官方规则要求额外参数，应通过对应 construction schema 明确扩展，而不是加入与当前语义无关的可选字段。

## B.2.3 Title 的表示

`title` 可以直接保存官方使用的日文 Title 字符串，包括平假名、片假名、汉字及其他 Unicode 字符。

例如：

```json
{
  "construction": {
    "type": "neo_standard",
    "title": "魔法少女リリカルなのは"
  }
}
```

本项目不为了程序索引而额外发明与官方 Title 平行的自定义英文 slug 或 Title ID，除非未来出现明确需求。

用于规则索引的 Title 字符串应：

1. 从 UTF-8 数据读取；
2. 在输入边界统一进行 Unicode NFC normalization；
3. normalization 后与规则数据中的 canonical Title string 精确匹配。

不得自动进行：

```text
平假名 ↔ 片假名转换
日文名 ↔ 英文名翻译
近似字符串匹配
错别字修正
```

Unicode normalization 只用于统一等价的字符编码表示，不改变 Title 的语言或规则身份。

机器存储路径仍应优先使用稳定的 ASCII `title_code` 等标识，不要求以日文 Title 作为目录名。

## B.2.4 cards

`cards` 是一个 Card Number 序列。

DeckRecipe 中：

```text
一个数组元素
=
实际选择的一张 Card
```

因此，如果同一张 Card 使用多张，就在 `cards` 中重复写入多次。

例如：

```json
{
  "construction": {
    "type": "neo_standard",
    "title": "テスト"
  },
  "cards": [
    "TEST/WTE01-001",
    "TEST/WTE01-001",
    "TEST/WTE01-001S",
    "TEST/WTE01-002"
  ]
}
```

这里表示 DeckRecipe 中实际记录了 4 张 Card。

不使用：

```json
{
  "card_number": "TEST/WTE01-001",
  "count": 2
}
```

这样的数量压缩结构作为 DeckRecipe 的规范持久化表示。

UI 或编辑器可以为了显示方便临时聚合成：

```text
TEST/WTE01-001   × 2
TEST/WTE01-001S  × 1
TEST/WTE01-002   × 1
```

但保存为规范 DeckRecipe JSON 时仍逐张展开。

## B.2.5 Card Number 作为引用

`cards` 中保存的是附录 A 所定义的 Canonical Full Card Number。

例如：

```text
TEST/WTE01-001S
```

DeckRecipe 不复制：

```text
title_code
side
product_code
product_card_number
Card Type
Level
Cost
Power
...
```

等 Card Information。

DeckRecipe 中的 Full Card Number 是对 Card Catalog 的精确引用键。

概念链条为：

```text
DeckRecipe
    ↓ Canonical Full Card Number
Card Catalog
    ↓
CardDefinition / Variant
```

DeckRecipe 本身不负责通过字符串截断推断：

```text
001S
=
001 + S
```

也不负责恢复 Card Number 的内部字段。

Card JSON 中的结构化 Card Number 是事实来源；Card Catalog 根据该结构化数据生成并登记唯一确定的 Canonical Full Card Number。

DeckRecipe 中的字符串只有与 Catalog 已登记的 Full Card Number 完全一致时，才能成为有效 Card 引用。

Full Card Number 已登记，只表示该 Card / Variant 引用在 Card Catalog 中有效；它不保证对应的 Artwork Resource 已经存在。

因此必须区分：

```text
Full Card Number 已登记
→ Card 引用有效

Artwork Resource 已存在
→ UI 可以取得对应 Variant 的表现资源
```

缺少 Artwork Resource 属于 UI / Resource 层问题，不得因此把一个已经有效登记的 Card 引用判定为 Deck Construction 非法。

因此：

```text
DeckRecipe
→ 引用 Card

Card JSON
→ 定义 Card
```

两者职责不得混淆。

## B.2.6 Variant 的保存方式

DeckRecipe 不单独保存 `variant_code` 字段。

具体 Variant 已包含在 Canonical Full Card Number 中。

例如：

```text
TEST/WTE01-001
TEST/WTE01-001S
TEST/WTE01-001BNP
```

可以表示同一个基础 Card 的不同表现版本。

DeckRecipe 可以逐张保留用户实际选择的 Variant，因此以后 Card / Deck Editor 或 UI 可以恢复相应的卡图选择。

规则意义上的同卡判断不以 Full Card Number 直接区分，而应在后续 Deck Construction Legality 中根据 Card Catalog 提供的 `base_card_number` 聚合。

因此：

```text
Full Card Number
→ 保留具体表现版本

Base Card Number
→ 规则身份
```

## B.2.7 cards 的顺序

`cards` 的数组顺序不具有游戏规则意义。

例如：

```text
A
B
A
C
```

与：

```text
C
A
B
A
```

在卡片构成相同的情况下表示相同的 DeckRecipe 构筑内容。

`cards[0]` 不表示游戏开始后的 Deck 顶，也不得利用 DeckRecipe JSON 的排列顺序决定初始 Deck Zone 顺序。

Deck Zone 的创建、Card Instance 的生成和 Shuffle 均属于 Game Initialization。

为了版本控制、Diff 或人工阅读，Serializer / Editor 未来可以采用稳定排序，但这只是持久化表现策略，不改变 DeckRecipe 的规则语义。

## B.2.8 重复 Card Number

`cards` 中重复出现相同 Full Card Number 是正常且有意义的数据。

例如：

```json
"cards": [
  "TEST/WTE01-001",
  "TEST/WTE01-001",
  "TEST/WTE01-001S"
]
```

表示实际选择了三张 Card。

因此：

```text
重复 Card Number
≠
JSON duplicate field
≠
Schema error
```

同一基础 Card 是否超过允许数量，需要在 Deck Construction Legality 阶段按 `base_card_number` 聚合后判断。

## B.2.9 B.2 不规定合法张数

本节不要求 `cards` 必须恰好包含 50 个元素。

B.2 只规定：

```text
len(cards)
=
DeckRecipe 当前记录的实际 Card 张数
```

例如 49 张或 51 张的 DeckRecipe 仍然可以作为结构化数据被读取，然后由后续 Deck Construction Legality 精确报告张数错误。

因此：

```text
JSON / Schema 可读取
≠
Deck Construction 合法
```

这两个层级必须保持分离。

## B.2.10 Editor 与 JSON 持久化

未来的 Card Editor 与 Deck Editor 继续使用本项目定义的规范 JSON 作为持久化格式。

编辑器不建立第二套专用数据格式。

概念上：

```text
Card Editor
    ↓
Card JSON
    ↓
现有 Card Loader / Validator

Deck Editor
    ↓
DeckRecipe JSON
    ↓
DeckRecipe Loader / Validator
```

Deck Editor 可以在 UI 中将重复 Card 聚合为数量显示，也可以提供 Variant 卡图选择。编辑器内部可以使用适合 UI 操作的聚合模型、View Model 或其他临时数据结构；这些都不是第二套持久化格式。

保存时，Deck Editor 必须通过 Serializer 生成符合本附录定义的规范 DeckRecipe JSON，并将 Card 逐张展开。

因此，“Editor 不建立第二套专用数据格式”特指：

> 不建立第二套与规范 JSON 并行存在的持久化格式。

它不限制 Editor 为界面操作建立内部临时模型。

编辑器生成的数据不得绕过正常 Loader、Schema Validation 或 Deck Construction Legality。

因此：

```text
手写 JSON
编辑器生成 JSON
```

必须经过同一套数据入口和验证规则。

## B.2.11 JSON 与字符编码

所有：

```text
Card JSON
DeckRecipe JSON
Title Rule Data
其他相关规则数据
```

统一使用 UTF-8。

读取和写入时应显式指定 UTF-8，不依赖操作系统默认编码。

例如 Python：

```python
path.read_text(encoding="utf-8")
path.write_text(text, encoding="utf-8")
```

JSON 输出允许直接保留 Unicode 字符，例如使用：

```python
json.dumps(data, ensure_ascii=False)
```

因此日文 Title、假名及其他 Unicode 文本可以直接保存在 JSON 中。

## B.2.12 本节结论

当前 `DeckRecipe` 的规范数据模型为：

```text
DeckRecipe
├─ construction
│  ├─ type
│  │  ├─ neo_standard
│  │  ├─ side
│  │  └─ standard
│  │
│  └─ type-specific declaration
│     ├─ title
│     └─ side
│
└─ cards
   └─ sequence[Canonical Full Card Number]

一个 `cards` 元素表示一张 Card；同一卡使用多张时，以相同编号重复出现表示，不使用 `count` 字段。
```

核心原则为：

```text
DeckRecipe
→ 保存卡组构成
→ 逐张保存 Canonical Full Card Number
→ 不保存 count 压缩结构
→ 不复制 Card Information
→ 不直接保存 CardDefinition
→ 不解析 Full Card Number 内部结构
→ 不保存 Player / Game 信息
→ 不决定 Deck Zone 顺序
→ 不在数据结构层判断 Deck Construction 合法性
```

并且：

```text
DeckRecipe Full Card Number
        ↓ exact match
Card Catalog
        ↓
CardDefinition / Variant
```

Title 使用 canonical official Title string；相关 JSON 与规则数据统一使用 UTF-8，并在规则索引边界进行 Unicode NFC normalization 后精确匹配。

---

> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)
