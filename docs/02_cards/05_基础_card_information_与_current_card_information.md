> [← 返回第 2 章目录](../02_cards.md)

## 2.5 基础 Card Information 与 Current Card Information

`CardDefinition` 保存基础 / 印刷 Card Information，并保持不可变。

运行时 Ability、Effect 或其他规则修正不得直接修改 `CardDefinition`。

例如：

```text
CharacterDefinition.power = 5000
```

某 Effect 令该 Card 当前 Power +2000 时：

```text
Definition Power
→ 5000

Current Power
→ 7000
```

不得通过修改：

```python
card.definition.power
```

实现。

### 2.5.1 Card 保持轻量

`Card` 表示本局中的具体实体及其必要运行时状态。

不应把所有 Current Card Information 的规则计算逐步塞入 `Card` 本身，例如：

```python
card.current_power(...)
card.current_level(...)
card.current_color(...)
card.current_traits(...)
card.current_trigger_icons(...)
```

Current Card Information 可能依赖：

- `CardDefinition`
- Card 当前所在 Zone / Position
- 当前 Game State
- 其他 Card
- Continuous Ability
- 临时 Effect
- 当前 Turn / Phase
- 其他规则修正

因此 Current Card Information 属于独立规则查询职责。

### 2.5.2 Query System

项目建立独立的只读 Query 层。

概念关系：

```text
CardDefinition
+
Card Runtime State
+
Game State
+
Current Effects
        ↓
Query System
        ↓
Current Card Information
```

Query System 还可以用于规则合法性查询，例如：

```text
当前 Card 是否可以使用？
当前 Player 有哪些 Legal Actions？
某个 Choice 有哪些合法选项？
```

UI 不自行重新实现规则判断。

例如：

```text
玩家点击 Card
        ↓
Query System
        ↓
返回当前 Card Information
        ↓
UI 显示
```

或者：

```text
玩家点击 Hand 中的 Card
        ↓
Query System
        ↓
查询是否存在合法使用方式
        ↓
合法
→ UI 启用对应按钮

不合法
→ UI 禁用对应按钮
```

### 2.5.3 Query 不执行操作

Query System 必须保持只读。

它只能：

```text
读取当前规则状态
→ 计算
→ 返回结果
```

不得在查询过程中：

- 移动 Card；
- 支付 Cost；
- 改变 Game State；
- 触发 Ability；
- 执行 Effect。

真正的 Action / Command 在执行前仍必须重新进行权威合法性验证。

Query 与 Action Validation 应共享同一套底层规则判断逻辑，避免 UI 查询规则和实际执行规则形成两套实现。

---

---

> [← 返回第 2 章目录](../02_cards.md)
