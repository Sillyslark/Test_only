> [← 返回第 2 章目录](../../02_cards.md)

# 附录 B：Deck Recipe 与 Deck Construction

本附录用于定义游戏外的 DeckRecipe、Deck Construction / Legality，以及它们与游戏内 Deck Zone 的职责边界。

## 附录 B 目录

<details>
<summary><b>B.1 目的、术语与职责边界</b></summary>

- [打开 B.1 全文](01_purpose_terminology_boundary.md)

<details>
<summary>B.1 小节</summary>

- B.1.1 `DeckRecipe` 与 `Deck`
- B.1.2 DeckRecipe 的生命周期
- B.1.3 DeckRecipe 不属于 Player
- B.1.4 Deck 是游戏中的 Zone
- B.1.5 Game Initialization 边界
- B.1.6 命名约束
- B.1.7 本节结论

</details>

</details>

<details>
<summary><b>B.2 DeckRecipe 的数据结构</b></summary>

- [打开 B.2 全文](02_deck_recipe_data_structure.md)

<details>
<summary>B.2 小节</summary>

- B.2.1 基本结构
- B.2.2 construction
- B.2.3 Title 的表示
- B.2.4 cards
- B.2.5 Card Number 作为引用
- B.2.6 Variant 的保存方式
- B.2.7 cards 的顺序
- B.2.8 重复 Card Number
- B.2.9 B.2 不规定合法张数
- B.2.10 Editor 与 JSON 持久化
- B.2.11 JSON 与字符编码
- B.2.12 本节结论

</details>

</details>

<details>
<summary><b>B.3 DeckRecipe Loading 与检查管线</b></summary>

- [打开 B.3 全文](03_loading_and_check_pipeline.md)

<details>
<summary>B.3 小节</summary>

- B.3.1 总体流程
- B.3.2 Load 的职责
- B.3.3 Structural Check
- B.3.4 Construction Reference Check
- B.3.5 Card Reference Check
- B.3.6 不自动修复输入
- B.3.7 Deck Construction Legality Check
- B.3.8 PASS / FAIL / SKIPPED
- B.3.9 Check 应尽可能收集全部问题
- B.3.10 DeckCheckResult
- B.3.11 DeckCheckIssue
- B.3.12 第一版的 severity
- B.3.13 Import Gate
- B.3.14 Debug 与 Deck Editor
- B.3.15 本节结论

</details>

</details>

后续 B.4、B.5……将在各自内容定稿后继续加入本目录。

---

> [← 返回第 2 章目录](../../02_cards.md)
