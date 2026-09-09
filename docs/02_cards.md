# 2. 卡片

本节用于统一卡片本身相关概念的命名。

本节确定卡片相关概念、名称、基础数据模型方向和边界。具体代码迁移按本节规范逐步进行。

**主要类别：**

- `Card`
- `CardDefinition`
- `CharacterDefinition`
- `EventDefinition`
- `ClimaxDefinition`
- `CardType`
- `CardColor`
- Card Information
- `CardIcon`
- `TriggerIcon`
- `CardOrientation`
- `CardFaceState`

信息公开范围不在本节定义。它与区域、卡片正反面以及特殊规则共同有关，将在场地区域章节中单独讨论。

---

## 章节导航

<details>
<summary><b>2.1 卡片定义与卡片实例</b></summary>

- [打开本节全文](02_cards/01_卡片定义与卡片实例.md)

<details>
<summary>本节小节</summary>

- 2.1.1 卡片定义
- 2.1.2 卡片实例

</details>

</details>

<details>
<summary><b>2.2 卡片种类</b></summary>

- [打开本节全文](02_cards/02_卡片种类.md)

</details>

<details>
<summary><b>2.3 卡片信息</b></summary>

- [打开本节全文](02_cards/03_卡片信息.md)

<details>
<summary>本节小节</summary>

- 2.3.1 特征
- 2.3.2 各卡片种类拥有的信息
- 2.3.3 图标与触发图标
- 2.3.4 卡片文本
- 2.3.5 卡片编号

</details>

</details>

<details>
<summary><b>2.4 Card Color</b></summary>

- [打开本节全文](02_cards/04_card_color.md)

</details>

<details>
<summary><b>2.5 基础 Card Information 与 Current Card Information</b></summary>

- [打开本节全文](02_cards/05_基础_card_information_与_current_card_information.md)

<details>
<summary>本节小节</summary>

- 2.5.1 Card 保持轻量
- 2.5.2 Query System
- 2.5.3 Query 不执行操作

</details>

</details>

<details>
<summary><b>2.6 卡片方向</b></summary>

- [打开本节全文](02_cards/06_卡片方向.md)

</details>

<details>
<summary><b>2.7 卡片正反面状态</b></summary>

- [打开本节全文](02_cards/07_卡片正反面状态.md)

<details>
<summary>本节小节</summary>

- 2.7.1 与卡片方向的关系
- 2.7.2 与区域规则的关系

</details>

</details>

<details>
<summary><b>2.8 卡片稳定身份</b></summary>

- [打开本节全文](02_cards/08_卡片稳定身份.md)

</details>

<details>
<summary><b>2.9 Card JSON 与严格 Loader</b></summary>

- [打开本节全文](02_cards/09_card_json_与严格_loader.md)

<details>
<summary>本节小节</summary>

- 2.9.1 加载职责边界
- 2.9.2 精确字段集合
- 2.9.3 重复 key
- 2.9.4 值验证与规范化
- 2.9.5 加载错误
- 2.9.6 Schema 演进原则

</details>

</details>

<details>
<summary><b>2.10 第 2 章测试规范</b></summary>

- [打开本节全文](02_cards/10_第_2_章测试规范.md)

<details>
<summary>本节小节</summary>

- 2.10.1 测试卡数据来源
- 2.10.2 第一批 Card Definition 测试
- 2.10.3 测试与规范的关系

</details>

</details>

<details>
<summary><b>2.11 当前命名审计摘要</b></summary>

- [打开本节全文](02_cards/11_当前命名审计摘要.md)

</details>

<details>
<summary><b>2.12 本节暂不决定的内容</b></summary>

- [打开本节全文](02_cards/12_本节暂不决定的内容.md)

</details>

<details>
<summary><b>2.13 本节命名结论</b></summary>

- [打开本节全文](02_cards/13_本节命名结论.md)

</details>
