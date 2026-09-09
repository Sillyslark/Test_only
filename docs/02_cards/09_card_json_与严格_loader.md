> [← 返回第 2 章目录](../02_cards.md)

## 2.9 Card JSON 与严格 Loader

Card JSON 是 `CardDefinition` 的结构化输入格式。当前 Loader 使用严格 Schema：

> 一份 JSON 必须完整且仅包含其 `CardType` 当前定义的 Card Information。

不允许通过忽略未知字段、自动补缺失字段或容忍重复 key 的方式进入规则对象。

### 2.9.1 加载职责边界

当前职责分为：

```text
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

```text
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
逐字段验证 / 规范化
↓
构造 CharacterDefinition / EventDefinition / ClimaxDefinition
```

`card_type` 是特殊公共 Card Information：它存在于三种 Card Type 的 JSON 中，同时承担 Loader 的 Schema discriminator。

### 2.9.2 精确字段集合

公共字段：

```text
card_type
card_number
name
color
trigger_icons
```

Character 专属字段：

```text
level
cost
power
soul
traits
card_icons
```

Event 专属字段：

```text
level
cost
card_icons
```

Climax 不增加专属字段。

采用“有且仅有”原则：

- 应有字段缺失 → 非法；
- 不属于该 Card Type 的字段出现 → 非法；
- 同一 JSON object 中同名 key 重复定义 → 非法；
- 字段存在但值为空，与字段不存在是两种不同状态。

例如：

```json
"trigger_icons": []
```

表示具有 Trigger Icon Information，但当前基础值为空；不得通过省略 `trigger_icons` 表达同一含义。

JSON object 的字段排列顺序没有规则意义。Loader 按字段名读取并以字段集合验证 Schema，因此公共字段与专属字段可以互换或穿插排列。

JSON array / list 内部顺序则保留。例如：

```json
"trigger_icons": ["soul", "shot", "soul"]
```

必须保持顺序与重复项，不自动排序或去重。

### 2.9.3 重复 key

普通 `json.loads()` 最终形成普通 `dict` 时可能丢失重复 key 信息，因此 Loader 使用 `object_pairs_hook`，在最终普通 `dict` 形成前检查重复字段。

重复字段必须明确失败，不允许后值静默覆盖前值。

这一原则同样适用于未来嵌套在 Card JSON 中的 JSON object。

### 2.9.4 值验证与规范化

字段集合正确后，再验证每个字段内部的值。

`card_value_rules.py` 中 validator 的统一约定：

```python
validated_value = validate_xxx(raw_value)
```

即合法时返回规范化后的 Python 值，例如：

```text
"yellow"
→ CardColor.YELLOW

["soul", "shot"]
→ (TriggerIcon.SOUL, TriggerIcon.SHOT)
```

当前已经确认的数据类型与 Enum 合法值立即验证。

对于 `level`、`cost`、`power`、`soul` 等尚未确认完整合法数值范围的字段，当前只验证已经确定的类型要求，并保留进一步规则接口 / TODO；不得擅自设定尚未确认的规则范围。

### 2.9.5 加载错误

当前加载错误边界：

```text
CardLoadError
├─ CardJsonSyntaxError
├─ DuplicateCardFieldError
├─ CardSchemaError
└─ InvalidCardValueError
```

`card_value_rules.py` 内部使用 `CardValueError` 表示单字段验证失败；Loader 捕获后转换为 `InvalidCardValueError`。

错误报告应尽量精确，包括：

- JSON 语法错误的位置；
- 重复了哪些字段；
- 缺失了哪些字段；
- 出现了哪些未定义字段；
- 哪一个具体字段的类型或值不合法；
- 可取得时包含文件路径与 `card_number`。

当 missing 与 unexpected 同时存在时，应在同一次 `CardSchemaError` 中同时报告。

### 2.9.6 Schema 演进原则

当前严格 Schema 表示“当前版本允许什么”，并不表示 Card JSON 永久不能扩展。

以后 Ability / Effect 或其他已经确认的 Card Information 需要进入 Card JSON 时，正确流程是：

```text
先更新规范
↓
明确新的 JSON Schema
↓
更新 Loader / value rules
↓
更新对应测试
```

不得为了未来扩展而把当前 Loader 改成“接受任意未知字段”。未知字段在当前 Schema 下仍应明确失败。

---

---

> [← 返回第 2 章目录](../02_cards.md)
