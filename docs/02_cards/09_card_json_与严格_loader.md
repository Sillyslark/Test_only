> [← 返回第 2 章目录](../02_cards.md)

## 2.9 Card JSON 与严格 Loader

Card JSON 是 `CardDefinition` 的结构化输入格式。当前 Loader 使用严格
Schema：

> 一份 JSON 必须完整且仅包含其 `CardType` 当前定义的 Card Information。

不允许通过忽略未知字段、自动补缺失字段或容忍重复 key
的方式进入规则对象。

一份 Card JSON 对应一个基础 Card Definition。不同 `variant_code`
不创建新的 Card JSON，也不在 Card JSON 中重复保存同一基础 Card
Definition。

### 2.9.1 Card JSON 中的 Card Number

Card JSON 中的 `card_number`
使用结构化数据，不保存独立的完整编号字符串。

由于一份 Card JSON 对应一个基础 Card Definition，Card JSON 中的
`card_number` 只保存构成 Base Card Number 的字段：

``` text
card_number
├─ title_code
├─ side
├─ product_code
└─ product_card_number
```

例如：

``` json
"card_number": {
  "title_code": "TEST",
  "side": "W",
  "product_code": "TE01",
  "product_card_number": "T001"
}
```

上述结构生成：

``` text
base_card_number = TEST/WTE01-T001
```

`variant_code` 不属于 Card JSON 中基础 Card Definition
的数据，不得为了不同表现版本复制 Card JSON。

因此：

``` text
TEST/WTE01-T001
TEST/WTE01-T001S
TEST/WTE01-T001SP
```

如果三者拥有相同的 Base Card Number，则规则侧均对应同一个 Card JSON：

``` text
cards/TEST/TE01/TEST_WTE01-T001.json
```

不同 Full Card Number 的实际卡图及其导航由 Card Image / Card Index
负责，不改变该 JSON 所表示的 Card Definition。

Card JSON 文件名由 Base Card Number 生成，并将 Card Number 中的 `/`
替换为 `_`。该替换仅用于文件名，不改变 Base Card Number 本身。

### 2.9.2 加载职责边界

当前职责分为：

``` text
card_definition.py
→ 定义 CardDefinition / Enum 等规则数据模型
→ 不知道 JSON

card_value_rules.py
→ 验证单个 Card Information 的值
→ 将合法原始值规范化为 Python 规则值

card_loader.py
→ 解析 JSON
→ 验证结构
→ 调用 value validator
→ 构造具体 CardDefinition
```

Loader 流程：

``` text
原始 JSON
↓
解析并检测重复 key
↓
读取 card_type
↓
验证 card_type 并选择精确 Schema
↓
比较实际字段与应有字段
├─ missing fields
└─ unexpected fields
↓
验证 card_number 的精确嵌套结构
↓
逐字段验证 / 规范化
↓
构造 CharacterDefinition / EventDefinition / ClimaxDefinition
```

`card_type` 是特殊公共 Card Information：它存在于三种 Card Type 的 JSON
中，同时承担 Loader 的 Schema discriminator。

### 2.9.3 精确字段集合

公共字段：

``` text
card_type
card_number
name
color
trigger_icons
```

其中 `card_number` 是一个嵌套 JSON object，并且必须有且仅有：

``` text
title_code
side
product_code
product_card_number
```

Card JSON 中的 `card_number` 不包含 `variant_code`。

Character 专属字段：

``` text
level
cost
power
soul
traits
card_icons
```

Event 专属字段：

``` text
level
cost
card_icons
```

Climax 不增加专属字段。

采用"有且仅有"原则：

-   应有字段缺失 → 非法；
-   不属于该 Card Type 的字段出现 → 非法；
-   `card_number` 内应有字段缺失 → 非法；
-   `card_number` 内出现 `variant_code` 或其他未定义字段 → 非法；
-   同一 JSON object 中同名 key 重复定义 → 非法；
-   字段存在但值为空，与字段不存在是两种不同状态。

例如：

``` json
"trigger_icons": []
```

表示具有 Trigger Icon Information，但当前基础值为空；不得通过省略
`trigger_icons` 表达同一含义。

JSON object 的字段排列顺序没有规则意义。Loader
按字段名读取并以字段集合验证
Schema，因此公共字段与专属字段可以互换或穿插排列。

JSON array / list 内部顺序则保留。例如：

``` json
"trigger_icons": ["soul", "shot", "soul"]
```

必须保持顺序与重复项，不自动排序或去重。

### 2.9.4 重复 key

普通 `json.loads()` 最终形成普通 `dict` 时可能丢失重复 key 信息，因此
Loader 使用 `object_pairs_hook`，在最终普通 `dict` 形成前检查重复字段。

重复字段必须明确失败，不允许后值静默覆盖前值。

这一原则同样适用于嵌套在 Card JSON 中的 `card_number` JSON
object，以及未来其他嵌套 JSON object。

### 2.9.5 值验证与规范化

字段集合正确后，再验证每个字段内部的值。

`card_value_rules.py` 中 validator 的统一约定：

``` python
validated_value = validate_xxx(raw_value)
```

即合法时返回规范化后的 Python 值，例如：

``` text
"yellow"
→ CardColor.YELLOW

["soul", "shot"]
→ (TriggerIcon.SOUL, TriggerIcon.SHOT)
```

`card_number` 的各组成字段分别按照 Card Number
已规定的合法值与格式进行验证，并由统一 formatter 生成
`base_card_number`。Loader 不通过文件名猜测 Card Number 的字段边界。

当前已经确认的数据类型与 Enum 合法值立即验证。

对于 `level`、`cost`、`power`、`soul`
等尚未确认完整合法数值范围的字段，当前只验证已经确定的类型要求，并保留进一步规则接口
/ TODO；不得擅自设定尚未确认的规则范围。

### 2.9.6 文件名与目录一致性

Card JSON 的实际存储位置应与其结构化 `card_number` 一致。

对于：

``` text
title_code = TEST
product_code = TE01
base_card_number = TEST/WTE01-T001
```

对应位置为：

``` text
cards/TEST/TE01/TEST_WTE01-T001.json
```

扫描 Card JSON 时，应检查：

-   `title_code` 与所在 `<title_code>` 目录一致；
-   `product_code` 与所在 `<product_code>` 目录一致；
-   JSON 文件名与 Base Card Number 按既定文件名规则生成的结果一致。

目录或文件名不一致属于数据映射错误，不得通过修改 JSON 内的 Card
Number、猜测路径或静默接受的方式自动修复。

业务代码不得依赖文件名反向切割来构造 Card Definition；结构化
`card_number` 仍是 Card Number 数据的事实来源。

### 2.9.7 加载错误

当前加载错误边界：

``` text
CardLoadError
├─ CardJsonSyntaxError
├─ DuplicateCardFieldError
├─ CardSchemaError
└─ InvalidCardValueError
```

`card_value_rules.py` 内部使用 `CardValueError`
表示单字段验证失败；Loader 捕获后转换为 `InvalidCardValueError`。

错误报告应尽量精确，包括：

-   JSON 语法错误的位置；
-   重复了哪些字段；
-   缺失了哪些字段；
-   出现了哪些未定义字段；
-   `card_number` 内部缺失或出现了哪些不允许的字段；
-   哪一个具体字段的类型或值不合法；
-   可取得时包含文件路径与 `card_number`。

当 missing 与 unexpected 同时存在时，应在同一次 `CardSchemaError`
中同时报告。

Card JSON 的目录与文件名一致性检查可以由批量扫描 / Card Index
生成流程负责；该检查不要求 `card_loader.py` 本身知道 `cards/`
的目录布局。

### 2.9.8 Schema 演进原则

当前严格 Schema 表示"当前版本允许什么"，并不表示 Card JSON
永久不能扩展。

以后 Ability / Effect 或其他已经确认的 Card Information 需要进入 Card
JSON 时，正确流程是：

``` text
先更新规范
↓
明确新的 JSON Schema
↓
更新 Loader / value rules
↓
更新对应测试
```

不得为了未来扩展而把当前 Loader 改成"接受任意未知字段"。未知字段在当前
Schema 下仍应明确失败。

`variant_code` 属于具体表现版本，不因 Card JSON Schema
的扩展而自动进入基础 Card Definition JSON。若未来其 UI / Resource
数据结构发生变化，应在对应资源与索引规范中另行规定。

------------------------------------------------------------------------

> [← 返回第 2 章目录](../02_cards.md)
