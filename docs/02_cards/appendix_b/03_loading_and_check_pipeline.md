> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)

# B.3 DeckRecipe Loading 与 Data Validation

本节定义 DeckRecipe JSON 从文件读取到成为 `Valid DeckRecipe` 的处理流程。本节只检查 DeckRecipe 自身的数据结构，以及 DeckRecipe 所声明或引用的数据是否能够解析到有效的既有数据。

Deck Construction Legality 不属于本节。卡组张数、同一卡数量限制、Climax 数量限制、Title / Side 构筑兼容性、禁限卡及特殊构筑规则，应由 Game Start / Initialization 阶段的独立 Legality 管理负责。

## B.3.1 总体流程

```text
DeckRecipe JSON
      ↓
UTF-8 Decode
      ↓
JSON Decode
      ↓
RawDeckRecipeData
      ↓
DeckRecipe Schema Validation
      ↓
DeckRecipe
      ↓
Reference Validation
├─ Construction Data
├─ Title Reference（需要时）
├─ Side Value（需要时）
└─ Card References
      ↓
Valid DeckRecipe
```

因此：

```text
JSON Decode 成功
≠ DeckRecipe Schema 有效
≠ DeckRecipe Reference 有效
≠ Deck Construction 合法
```

附录 B 到 `Valid DeckRecipe` 为止。之后由游戏开始相关流程接手：

```text
Valid DeckRecipe
      ↓
Deck Legality
      ↓
Legal / Illegal
      ↓ Legal
Game Initialization
```

## B.3.2 Load 的职责

Load 只负责读取 UTF-8 文件并完成 JSON Decode，结果为 `RawDeckRecipeData`。

```text
JSON Decode 成功
≠ DeckRecipe 构造成功
```

JSON Decode 成功但字段缺失、类型错误或 construction 结构错误时，应保留原始数据及诊断信息供 Debug / Deck Editor 使用。只有 Schema Validation 通过后，才构造正式 `DeckRecipe`。

JSON 本身无法 Decode 时属于 Decode Error，此时不存在可继续进行字段验证的有效 JSON 数据结构。

## B.3.3 DeckRecipe Schema Validation

Schema Validation 检查 B.2 定义的数据结构，至少包括：

```text
根节点类型正确
construction 存在且类型正确
construction.type 存在且类型正确
cards 存在且为 sequence
cards 中每个元素均为 string
```

并执行 type-specific schema：

```text
neo_standard → 必须有 title，不得混入 side 专属字段
side         → 必须有 side，不得混入 title
standard     → 不要求 title / side，不得混入无关声明字段
```

`construction.type` 的合法类型集合属于 Schema 定义。未知 `construction.type` 属于 Schema Error。

它只回答“这份数据是否符合 DeckRecipe 的规范结构”，不检查引用是否存在，也不判断构筑是否合法。

Schema 通过后：

```text
RawDeckRecipeData
      ↓
DeckRecipe
```

正式 `DeckRecipe` 不应为了容纳错误输入而把规范字段设计成大量 `Any` 或无意义的可空类型。

## B.3.4 Reference Validation

正式 `DeckRecipe` 构造后，执行 Reference Validation。它只回答：

> DeckRecipe 中需要引用既有数据的值，是否能够解析到系统已经认可的有效数据？

当前至少包括：

```text
Title Reference 是否存在（需要时）
Side Value 的外部规则引用是否存在（仅当其值由外部 Rule Data 定义时）
每个 Canonical Full Card Number 是否能解析到有效 Card
```

`construction.type` 属于 DeckRecipe Schema，而不是外部 Reference。未知的 `construction.type` 应在 Schema Validation 阶段报告，而不得延后解释为 Reference Error。

Reference Valid 只表示引用能够成立，不表示 Deck Construction Legal。

## B.3.5 Card Reference Validation

每个 `cards[n]` 均按 Canonical Full Card Number 对 Card Catalog 做 exact lookup：

```text
DeckRecipe.cards[n]
        ↓
Canonical Full Card Number
        ↓ exact lookup
Card Catalog
        ↓
Valid CardDefinition / Variant
```

Catalog 中不存在完全一致的 Full Card Number 时，产生 Card Reference Error。

DeckRecipe Validator 不重新检查 `Card.level`、`Card.type`、Card Number 内部字段、Card JSON Schema 或其他 CardDefinition 内部规则。Card 层负责：

```text
Card JSON
    ↓
Card Validation
    ↓
Valid CardDefinition
    ↓
Card Catalog
```

DeckRecipe 层只验证其引用是否能解析到 Card Catalog 已认可的有效结果。不得形成第二套 Card Validation。

## B.3.6 Construction / Title / Side Reference Validation

construction 中需要引用规则数据的字段，也只检查引用本身。

Neo-Standard 的 Title：

```text
construction.title
        ↓
Unicode NFC normalization
        ↓
Deck Construction Rule Data
        ↓
canonical Title exact match
```

Title 不存在时报告 Unknown Title Reference；本节不检查 DeckRecipe 中的 Card 是否属于该 Title。

`side` 的字段存在性、字段类型及其与 `construction.type` 的结构关系属于 Schema Validation。

至于 `side` 的具体合法值如何定义，本附录不提前锁定实现方式：

```text
若 side 是固定 Schema enum
→ 合法值由 Schema Validation 检查

若 side 的合法值未来来自外部 Rule Data
→ 值是否存在由 Reference Validation 检查
```

无论采用哪种实现：

```text
side 值本身是否有效
→ Data Validation

所有 Card 是否符合该 Side
→ Deck Legality
```

## B.3.7 不自动修复输入

Data Validation 负责验证和诊断，不静默修复输入。除 B.2 已规定的 Unicode NFC normalization 外，不自动执行：

```text
"Neo Standard"      → "neo_standard"
"test/wte01-001"    → "TEST/WTE01-001"
" TEST/WTE01-001 "  → "TEST/WTE01-001"
```

Unicode NFC normalization 只统一等价 Unicode 编码表示，不属于拼写纠错、翻译或模糊匹配。

## B.3.8 尽可能收集全部可可靠判断的问题

Data Validation 原则上不采用全局 fail-fast。发现局部问题后，只要其他项目仍能可靠判断，就继续收集诊断信息。

各验证项目仍必须遵守自身的数据依赖。例如 `cards` 整体不是 sequence 时无法执行 Card Reference Validation；但 construction 结构有效时，其相关验证仍可继续。

原则为：

> 能可靠判断的项目继续验证；缺少必要前置条件的项目不强行执行。

## B.3.9 DeckRecipeValidationResult

完整 Data Validation 不只返回单一 `bool`：

```text
DeckRecipeValidationResult
├─ valid
└─ issues[]
```

`valid` 表示是否已经成为 `Valid DeckRecipe`；`issues` 保存发现的数据验证问题。

这里的 `valid` 不表示 Deck Construction Legal。

## B.3.10 DeckRecipeValidationIssue

每个问题至少具有：

```text
DeckRecipeValidationIssue
├─ code
├─ stage
├─ path
├─ value       (optional)
└─ message
```

例如：

```text
code:    UNKNOWN_CARD_REFERENCE
stage:   reference
path:    cards[23]
value:   TEST/WTE01-999S
message: Card Catalog 中不存在该 Canonical Full Card Number
```

`code` 用于稳定的机器判断；`stage` 区分 decode / schema / reference；`path` 定位具体数据；`value` 在有助于诊断时保存输入值；`message` 仅用于人类阅读。

自动测试与 Deck Editor 应优先依赖稳定的 `code` 和 `path`。第一版不为尚不存在的 Warning / Info 需求预设 `severity` 字段。

## B.3.11 Valid DeckRecipe

只有：

```text
JSON Decode
        ↓ PASS
DeckRecipe Schema Validation
        ↓ PASS
Required Reference Validation
        ↓ PASS
Valid DeckRecipe
```

`Valid DeckRecipe` 严格表示：

> DeckRecipe 自身结构正确，且其必须引用的既有数据均能够被系统有效解析。

因此：

```text
Valid DeckRecipe
≠ Legal Deck
```

本附录中的 `RawDeckRecipeData`、`DeckRecipe` 与 `Valid DeckRecipe` 表示数据处理阶段和语义状态，不强制要求实现为三个独立的 class、运行时类型或持久化格式。

例如，实现可以采用：

```text
raw dict
   ↓
DeckRecipe
+
DeckRecipeValidationResult(valid=True)
```

只要能够保持本节规定的阶段边界与语义保证即可。

## B.3.12 Debug 与 Deck Editor

验证失败时，应尽可能保留 `RawDeckRecipeData` 或已构造的 `DeckRecipe`，以及对应的 `DeckRecipeValidationResult`，供 CLI Debug、自动测试、Deck Editor 和人工修正使用。

例如：

```text
cards[17]:
UNKNOWN_CARD_REFERENCE

construction.title:
UNKNOWN_TITLE_REFERENCE
```

Deck Editor 可以依赖 `path` 和 `code` 定位并高亮错误条目，修正后重新执行同一套 Data Validation。Editor 不拥有另一套更宽松的 DeckRecipe Data Validation。

## B.3.13 与 Deck Legality 的边界

```text
DeckRecipe Data Validation
──────────────────────────
DeckRecipe Schema                 ✓
Card Reference resolves to a Card Catalog 已登记的 Valid CardDefinition / Variant   ✓
Title Reference Exists            ✓
Side value / external reference valid（按其最终定义方式） ✓

Deck Legality
──────────────────────────
规定卡组张数                      ✗
同一卡数量限制                    ✗
Climax 数量限制                   ✗
Title compatibility               ✗
Side compatibility                ✗
禁限卡                            ✗
特殊构筑规则                      ✗
```

Deck Legality 在 Game Start / Initialization 相关章节中独立定义，其输入应为 `Valid DeckRecipe`，而不是未经 Data Validation 的原始 JSON。

## B.3.14 本节结论

```text
File
 ↓
UTF-8 Decode
 ↓
JSON Decode
 ↓
RawDeckRecipeData
 ↓
DeckRecipe Schema Validation
 ↓
DeckRecipe
 ↓
Reference Validation
 ↓
Valid DeckRecipe
```

附录 B 到此结束其职责。

```text
RawDeckRecipeData
→ JSON 已读取，但 DeckRecipe 结构尚未得到保证

DeckRecipe
→ Schema 已通过

Valid DeckRecipe
→ Schema 与 Required References 均有效

Legal Deck
→ 在指定 Deck Construction Rules 下合法
  （不属于附录 B）
```

---

> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)
