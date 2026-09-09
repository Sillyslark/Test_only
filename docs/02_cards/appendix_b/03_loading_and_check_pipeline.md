> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)

# B.3 DeckRecipe Loading 与检查管线

本节定义 DeckRecipe JSON 从读取到取得游戏导入资格之前的处理边界，以及检查过程的分层、执行顺序和错误报告原则。

本节不定义具体的 Weiss Schwarz Deck Construction 数值规则；例如标准卡组张数、同卡数量上限、Climax 数量上限、Title / Side 兼容规则及禁限卡规则等，留给后续 Deck Construction Legality 小节定义。

## B.3.1 总体流程

DeckRecipe 的处理流程为：

```text
DeckRecipe JSON
      ↓
Load / JSON Decode
      ↓
RawDeckRecipeData
      ↓
Structural Check
      ↓
DeckRecipe
      ↓
Reference / Legality Checks
├─ Construction Reference Check
├─ Card Reference Check
└─ Deck Construction Legality Check
      ↓
DeckCheckResult
      ↓
PASS
      ↓
允许作为 Game Initialization 的输入
```

如果 Check 失败：

```text
FAIL
 ↓
保留已读取的数据
 ↓
返回结构化检查结果
 ↓
Debug / Deck Editor 修正
```

因此必须区分：

```text
能够读取 DeckRecipe
≠
DeckRecipe 可以导入游戏
```

只有完成所有 Import-required checks 且不存在阻断错误的 DeckRecipe，才允许进入 Game Initialization。

## B.3.2 Load 的职责

Load 负责：

```text
读取文件
↓
UTF-8 Decode
↓
JSON Decode
↓
取得可供后续检查的数据
```

Load 不负责证明 DeckRecipe 的 Card Reference 或 Deck Construction 合法。

因此，一份 JSON 可以被成功读取，同时仍然包含：

```text
未知 Card Number
未知 Title
不合法的 construction 声明
错误的卡组张数
违反同卡数量限制
其他 Deck Construction 问题
```

这些问题由后续 Check 报告。若 Structural Check 失败，应保留 `RawDeckRecipeData` 及其诊断结果供 Debug / Editor 使用，但不得把结构不合法的数据伪装成正式 `DeckRecipe`。

如果 JSON 本身无法 Decode，则属于 Decode Error；此时不存在可继续进行 DeckRecipe 字段检查的有效 JSON 数据结构。

## B.3.3 Structural Check

Structural Check 检查 DeckRecipe 数据是否符合 B.2 定义的结构要求。

至少包括：

```text
根节点类型正确
construction 存在且类型正确
construction.type 存在且类型正确
cards 存在且为 sequence
cards 中每个元素均为 string
```

并检查 construction 的 type-specific schema。

例如：

```text
type = neo_standard
→ 必须存在 title
→ 不得出现仅属于 side 的字段

type = side
→ 必须存在 side
→ 不得出现仅属于 neo_standard 的 title

type = standard
→ 不要求 title / side
→ 不得混入与该 type 无关的声明字段
```

Structural Check 只回答：

> DeckRecipe 的数据结构是否满足后续检查所要求的形状？

它不检查：

```text
Card Number 是否存在
Title 是否存在
卡组是否正好满足规定张数
同卡是否超过允许数量
Climax 是否超过允许数量
Card 是否符合 Title / Side 构筑限制
```

因此：

```text
Structurally Valid
≠
Reference Valid
≠
Deck Construction Legal
```

检查管线的章节顺序表示职责分层，不表示“上一阶段必须整体 PASS，下一阶段才能开始”。

各检查项应根据自身依赖条件决定是否执行。例如：

```text
cards 整体不是 sequence
→ Card Reference Check: SKIPPED
→ Total Card Count: SKIPPED

construction 结构有效
但 cards[3] 不是 string
→ Construction Reference Check 可以继续
→ 其他结构有效的 Card 条目可以继续进行可可靠执行的诊断
→ cards[3] 报告 Structural FAIL
```

因此，Check 的执行原则是：

> 能够在当前数据上可靠判断的检查继续执行；缺少必要前置条件的检查标记为 `SKIPPED`。

不得把整个 Check 实现成单纯的全阶段串行短路。

## B.3.4 Construction Reference Check

当 construction 的结构足以进行引用检查后，检查其声明是否能被对应的 Deck Construction Rule Data 识别。

Neo-Standard 示例：

```text
construction.type = neo_standard
construction.title = "<Title>"
        ↓
UTF-8 string
        ↓
Unicode NFC normalization
        ↓
Deck Construction Rule Data
        ↓
exact match
```

如果 canonical Title 不存在，应产生明确的 Reference Error，而不是将其报告为 JSON Decode Error 或 Deck Construction Legality Error。

Side 等其他需要外部规则引用的数据同理。

Construction Reference Check 只回答：

> DeckRecipe 所引用的构筑规则对象是否存在？

它不在这一阶段判断 cards 是否满足该构筑规则。

## B.3.5 Card Reference Check

当 `cards` 的结构足以检查时，对其中每一个 Canonical Full Card Number 进行 Card Catalog 精确查询。

例如：

```text
cards[23]
    ↓
"TEST/WTE01-999S"
    ↓ exact lookup
Card Catalog
```

如果 Catalog 中不存在完全一致的 Full Card Number，则该条目产生 Card Reference Error。

DeckRecipe Check 不通过：

```text
字符串截断
大小写猜测
自动补全
近似匹配
自动 strip 后接受
```

等方式修复 Card Number。

Canonical Full Card Number 必须与 Card Catalog 已登记值精确匹配。

Card Reference Check 应尽可能检查全部可检查条目，而不是发现第一项错误后立即停止。

例如：

```text
cards[7]   → invalid
cards[19]  → invalid
cards[42]  → invalid
```

一次 Check 应尽可能同时报告这三项问题，以便 Debug 和 Deck Editor 一次定位。

## B.3.6 不自动修复输入

Check 的职责是诊断，而不是静默修改用户数据。

除 B.2 已明确规定的 Unicode NFC normalization 外，不应自动把非 canonical 输入转换为 canonical 数据。

例如不得：

```text
"Neo Standard"
→ "neo_standard"

"test/wte01-001"
→ "TEST/WTE01-001"

" TEST/WTE01-001 "
→ "TEST/WTE01-001"
```

后再将其视为原始输入合法。

Unicode NFC normalization 只统一等价的 Unicode 编码表示，不属于拼写纠错、翻译或模糊匹配。

## B.3.7 Deck Construction Legality Check

当已有足够信息时，进入 Deck Construction Legality Check。

该阶段未来可以包括：

```text
总 Card 数量
同 base_card_number 数量
Climax 数量
Neo-Standard Title compatibility
Side compatibility
特殊构筑限制
禁限卡规则
其他官方 Deck Construction Rules
```

具体规则由后续小节定义。

B.3 只规定 Legality Check 与前置检查之间的依赖关系。

某些规则即使存在前置 Reference Error 仍然可以可靠检查。

例如：

```text
cards 中共有 50 个 string
```

即使其中一张 Card Reference 未解析，也仍然可以判断当前记录的总条目数。

但依赖 CardDefinition 的规则，例如：

```text
Climax 数量
Title compatibility
```

如果存在无法解析的 Card Reference，可能无法得到可靠结论。

此时不得把“无法判断”报告成规则失败。

## B.3.8 PASS / FAIL / SKIPPED

单项检查至少支持：

```text
PASS
FAIL
SKIPPED
```

其语义为：

```text
PASS
→ 已执行检查，结果满足要求

FAIL
→ 已执行检查，能够确定不满足要求

SKIPPED
→ 因前置数据或引用不足，当前无法可靠执行该检查
```

例如：

```text
Total Card Count       PASS
Card References        FAIL
Climax Limit           SKIPPED
Title Compatibility    SKIPPED
```

`SKIPPED` 应保存可理解的原因，例如：

```text
requires all Card References to resolve
```

不得把由于前置条件不足而无法判断的规则标记为 `FAIL`。

## B.3.9 Check 应尽可能收集全部问题

DeckRecipe Check 原则上不采用全局 fail-fast。

发现一个问题后，只要其他检查仍然能够可靠执行，就应继续检查并收集结果。

目标是：

```text
一次 Check
↓
尽可能完整的诊断信息
↓
一次性用于 Debug / Editor 修正
```

但这不意味着忽略依赖关系。

如果某项检查的必要前置条件已经失败，则该项应：

```text
SKIPPED
```

而不是在不完整数据上强行执行并产生不可靠结果。

## B.3.10 DeckCheckResult

完整检查不应只返回单一 `bool`。

概念模型至少包括：

```text
DeckCheckResult
├─ passed
├─ checks[]
└─ issues[]
```

其中：

```text
passed
→ 整体聚合结果：是否取得进入 Game Initialization 的资格

checks
→ 各独立检查项及其 PASS / FAIL / SKIPPED 状态

issues
→ 已发现的结构化问题
```

必须区分：

```text
DeckCheckResult.passed
→ aggregate import eligibility

individual check status
→ 单个检查项的执行结果
```

两者不是同一个层级的 PASS 概念。

具体代码类型可以在实现阶段确定，但不得丢失这些语义。

## B.3.11 DeckCheckIssue

每个可报告问题应具有稳定的机器可读信息。

概念上：

```text
DeckCheckIssue
├─ code
├─ stage
├─ path
├─ value       (optional)
└─ message
```

例如：

```text
code:
UNKNOWN_CARD_REFERENCE

stage:
reference

path:
cards[23]

value:
TEST/WTE01-999S

message:
Card Catalog 中不存在该 Canonical Full Card Number

```

其中：

- `code` 是稳定的机器可读错误类型；
- `stage` 表示问题来自 structural / reference / legality 等阶段；
- `path` 定位到 DeckRecipe 中的具体数据；
- `value` 在有助于诊断时保存相关输入值；
- `message` 用于人类阅读，不作为程序判断错误类型的唯一依据。

测试与 Editor 不应依赖具体自然语言 `message` 判断错误类别，而应优先使用稳定的 `code`。

## B.3.12 第一版不预设 severity 字段

第一版的 `DeckCheckIssue` 不预先加入 `severity` 字段。

当前需要报告的 Issue 均属于会阻止相应 Import-required check 通过的实际问题。

未来只有在出现明确的：

```text
数据仍允许导入
但值得提醒用户
```

需求时，再扩展：

```text
WARNING
INFO
```

等等级及对应字段。

不得为了尚不存在的需求提前制造持久化或公共接口字段。

## B.3.13 Import Gate

DeckRecipe 是否允许进入 Game Initialization，应由完整 CheckResult 决定，而不是由 Loader 决定。

原则上：

```text
存在阻断 ERROR
→ 不允许 Import

存在 Import-required check 的 FAIL
→ 不允许 Import

存在 Import-required check 的 SKIPPED
→ 不允许 Import

所有 Import-required checks 均已可靠完成
且不存在阻断 ERROR
→ 允许 Import
```

只有被明确标记为 `Import-required` 的检查才参与 Import Gate。

未来纯诊断性、UI 或 Resource 层检查即使出现 `SKIPPED`，也不得仅因此阻止 Import。例如 Variant Artwork 是否可用不属于 Deck Construction Legality，也不应成为默认的 Import-required check。

因此：

```text
Load Success
```

只表示数据已经能够被读取，不表示：

```text
Import Allowed
```

Game Initialization 不得绕过这一检查门。

## B.3.14 Debug 与 Deck Editor

检查失败时，DeckRecipe 数据应尽可能保留，以供：

```text
CLI Debug
自动测试
Deck Editor
人工修正
```

使用。

例如：

```text
cards[17]:
UNKNOWN_CARD_REFERENCE

construction.title:
UNKNOWN_TITLE
```

应能够定位到具体输入位置。

Deck Editor 可以根据 `path` 和 `code`：

```text
定位对应字段
高亮错误条目
显示 message
等待用户修正
```

修正后重新执行同一套 Check。

Editor 不拥有另一套更宽松的合法性规则。

## B.3.15 本节结论

DeckRecipe 的读取与检查采用以下类型与职责边界：

```text
File
 ↓
UTF-8 Decode
 ↓
JSON Decode
 ↓
RawDeckRecipeData
 ↓
Structural Check
 ↓
DeckRecipe
 ↓
Reference / Legality Checks
 ↓
DeckCheckResult
 ↓
Import Gate
 ↓
Game Initialization
```

其中 Check 按检查项依赖关系执行，而不是简单的全阶段串行短路。

其中：

```text
Load
→ JSON Decode 后取得 RawDeckRecipeData

Structural Check
→ 通过后才构造正式 DeckRecipe

Check
→ 按依赖关系执行 Construction Reference
→ Card Reference
→ Deck Construction Legality

Import Gate
→ 只有完整检查通过后才允许进入 Game Initialization
```

并正式确定：

```text
能够读取
≠
引用有效
≠
构筑合法
≠
允许导入游戏
```

Check 应尽可能一次收集所有能够可靠判断的问题；因前置条件不足而无法执行的检查使用 `SKIPPED`，不得伪装成 `FAIL`。

检查结果必须提供稳定的机器可读错误 `code` 和可定位的 `path`，以同时服务于 Debug、自动测试和未来 Deck Editor。

---

> [← 返回附录 B 目录](00_overview.md) · [返回第 2 章目录](../../02_cards.md)
