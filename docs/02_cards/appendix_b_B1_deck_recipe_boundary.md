> [← 返回第 2 章目录](../02_cards.md)

# 附录 B：Deck Recipe 与 Deck Construction

## B.1 目的、术语与职责边界

本附录讨论游戏开始前存在的卡组构成数据，以及该数据的读取、保存与 Deck Construction / Legality 检查。

本附录不讨论 Game Initialization，也不讨论游戏开始后作为 Zone 存在的 Deck 的运行时行为。

### B.1.1 `DeckRecipe` 与 `Deck`

官方英文资料中，游戏开始前准备的卡组与游戏中的 Deck 区域都使用 `deck` 一词；英文官网同时使用 `Deck Recipe` 表示一套卡组构成清单。

为避免程序模型中的术语歧义，本项目统一使用：

```text
DeckRecipe
→ 游戏外的卡组构成数据

Deck
→ 游戏中的官方 Deck Zone
```

这里的 `DeckRecipe` 是模拟器用于消除程序命名歧义的名称。它借用英文官网已经使用的 `Deck Recipe` 术语，但不将其解释为官方综合规则对赛前卡组对象的唯一正式类型名称。

### B.1.2 DeckRecipe 的生命周期

`DeckRecipe` 在 Game 之外存在。

它可以被创建、保存、读取、编辑和验证，而不要求任何 Game 已经开始。

概念上：

```text
DeckRecipe JSON
      ↓
DeckRecipe Loading
      ↓
DeckRecipe
      ↓
Deck Construction / Legality Check
      ↓
合法的 DeckRecipe
```

到此为止仍然没有创建任何对局中的 Card Instance。

因此 `DeckRecipe` 本身：

```text
不属于 Game
不属于 Player
不具有 owner_id
不具有 card_id
不具有 Zone
不具有牌堆顶 / 牌堆底
不具有运行时顺序
不执行 draw / shuffle / move
```

`DeckRecipe` 只描述：

> 这套卡组选择了哪些 Card，以及各自的数量和必要的版本信息。

### B.1.3 DeckRecipe 不属于 Player

`DeckRecipe` 是独立的游戏外数据。

某个用户可以选择一个 `DeckRecipe` 用于参加一局 Game，但：

```text
用户选择 DeckRecipe
≠
DeckRecipe 属于某个 Player
```

在本附录范围内，不建立：

```text
DeckRecipe.owner_id
DeckRecipe.player_id
```

等对局归属字段。

DeckRecipe 与本局 Player 的关系只会在后续 Game Initialization 中建立。

### B.1.4 Deck 是游戏中的 Zone

`Deck` 保留为官方规则中的 Zone 名称。

游戏开始后，`Deck` 表示 Game State 中实际存在的 Deck Zone，并保存对局中的 Card Instance。

它与 `DeckRecipe` 的性质不同：

```text
DeckRecipe
→ 游戏外
→ 构筑数据
→ Card Number / 数量
→ 不具有运行时顺序

Deck
→ 游戏内
→ Zone
→ Card Instance
→ 具有顺序
→ 存在 top / bottom
→ 可以被 shuffle / draw / move
```

因此，游戏中的 Card 从 Deck 移动到 Hand、Waiting Room、Clock 或其他 Zone 时，不会反向修改原始 `DeckRecipe`。

`DeckRecipe` 描述的是进入游戏前选择的构筑结果；`Deck` 描述的是当前 Game State 中一个会持续变化的 Zone。

### B.1.5 Game Initialization 边界

本附录的职责终点是：

```text
合法的 DeckRecipe
```

其后发生的：

```text
创建 Card Instance
生成 card_id
确定 owner_id
建立初始 Game State
放入 Deck Zone
Shuffle
抽取初始 Hand
决定先后手
```

均属于 Game Initialization，不属于 DeckRecipe 或 Deck Construction 的职责。

边界如下：

```text
DeckRecipe JSON
      ↓
DeckRecipe Loading
      ↓
DeckRecipe
      ↓
Deck Construction / Legality Check
      ↓
合法的 DeckRecipe
      ↓
════════════════════════════
 Game Initialization 边界
════════════════════════════
      ↓
      （本附录不定义）
      ↓
Game 中的 Deck Zone
```

因此不得为了方便而让 `DeckRecipeLoader` 或 Deck Construction Validator 直接创建：

```text
Card
PlayerState
GameState
Deck Zone
```

### B.1.6 命名约束

在代码与文档中，`DeckRecipe` 与 `Deck` 不得混用。

建议：

```python
recipe = load_deck_recipe(...)
```

而不是：

```python
deck = load_deck_recipe(...)
```

`deck` 应保留给游戏中的 Deck Zone 或与该 Zone 直接相关的运行时对象。

同理，后续 DeckRecipe 相关模块、类型和变量应优先使用明确名称，例如：

```text
DeckRecipe
DeckRecipeEntry
DeckRecipeLoader
```

具体 Validator 是否拆分为 Schema Validation 与 Deck Construction / Legality Validation，留到后续小节分析后再决定，不在 B.1 提前锁死。

### B.1.7 本节结论

本节正式确定：

```text
DeckRecipe
→ 游戏外的卡组构成数据
→ 独立于 Game
→ 独立于 Player
→ 描述 Card 选择与数量
→ 接受 Deck Construction / Legality Check

Deck
→ 游戏中的官方 Zone
→ 属于 Game State
→ 保存 Card Instance
→ 具有运行时顺序
→ 随游戏过程变化
```

并明确：

```text
DeckRecipe → Deck
```

不是 DeckRecipe 自身的转换职责，而属于后续 Game Initialization。

---

> [← 返回第 2 章目录](../02_cards.md)
