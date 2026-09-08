# WS 模拟器术语与命名规范

> 状态：草案 v0.3  
> 用途：统一规则相关的变量名、程序术语与 UI 名称。  
> 原则：正文使用中文；英文仅用于实际代码标识符，以及确有必要说明命名依据的官方英文术语。

## 1. 基本原则

### 1.1 命名优先级

1. 先确认官方规则中的概念及含义。
2. 为该概念确定唯一的规范变量名。
3. Python 代码遵守统一命名形式。
4. UI 名称独立本地化，不反向决定 Engine 变量名。

例如，UI 中显示“控制室”，Engine 使用 `waiting_room`，不使用 `control_room`。

### 1.2 规范变量名与当前变量名

- **规范变量名**：之后新增代码和重构后应统一采用的名称。
- **当前变量名**：仓库当前实际使用的名称。
- 两者不一致时先记录，不立即重命名。
- 涉及 Replay、状态哈希、测试数据时，必须先确认兼容方案。

### 1.3 Python 命名形式

- 类、枚举类型：`PascalCase`
- 变量、函数、序列化值：`snake_case`
- 枚举成员：`UPPER_SNAKE_CASE`
- 布尔查询：`is_*`、`has_*`、`can_*`
- 玩家提交的操作：`XxxAction`
- 合法选择描述：`XxxOptions`
- 内部规则结算：`_resolve_*`
- 基础状态修改：`_move_*`、`_apply_*`

### 1.4 状态标记

- **已确认**：术语和规范变量名均已确定。
- **待检查**：概念明确，但仓库当前实现仍需核对。
- **待定**：名称或具体数据结构尚未确定。
- **待迁移**：规范名已确定，但旧代码仍使用其他名称。
- **项目术语**：模拟器自身的程序抽象，不视为官方规则术语。

---

## 2. 场地区域

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 所属层级 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 卡组 | `deck` | `deck` | 卡组 | 玩家区域 | 已确认 | 对应官方 Deck |
| 手牌 | `hand` | `hand` | 手牌 | 玩家区域 | 已确认 | 对应官方 Hand |
| 控制室 | `waiting_room` | `waiting_room` | 控制室 | 玩家区域 | 已确认 | 官方英文为 Waiting Room |
| 舞台 | `stage` | `stage` | 舞台 | 玩家区域 | 已确认 | 包含 5 个舞台格 |
| 舞台格 | `stage_position` | 当前以舞台位置键表示 | 舞台格 | 舞台 | 待检查 | 官方英文为 Stage Position；是否保留 `stage_slot` 作为程序术语待定 |
| 前列 | `center_stage` | `front_*` | 前列 | 舞台 | 待迁移 | 官方英文为 Center Stage |
| 后列 | `back_stage` | `back_*` | 后列 | 舞台 | 已确认 | 官方英文为 Back Stage |
| 计时区 | `clock` | `clock` | 计时区 | 玩家区域 | 已确认 | — |
| 等级区 | `level` | `level` | 等级区 | 玩家区域 | 已确认 | 注意与卡片的 `level` 属性区分 |
| 库存区 | `stock` | `stock` | 库存区 | 玩家区域 | 已确认 | — |
| 高潮区 | `climax_area` | `climax`（待核对） | 高潮区 | 玩家区域 | 待检查 | 是否保留 `climax` 作为内部简称待定 |
| 思出区 | `memory` | `memory` | 思出区 | 玩家区域 | 已确认 | — |
| 处理区 | `resolution_zone` | `resolution_zone` | 处理区 | 规则处理区域 | 已确认 | — |
| 指示物区域 | `marker_area` | `markers[slot]` | 指示物区 | 舞台格 / 角色 | 待检查 | 当前实现为每个舞台格保存指示物列表 |

### 2.1 舞台格命名迁移候选

| 当前变量名 | 候选规范变量名 | UI 名称 | 状态 |
| --- | --- | --- | --- |
| `front_left` | `center_left` | 前列左 | 待迁移 |
| `front_center` | `center_center` | 前列中 | 待迁移 |
| `front_right` | `center_right` | 前列右 | 待迁移 |
| `back_left` | `back_left` | 后列左 | 已确认 |
| `back_right` | `back_right` | 后列右 | 已确认 |

在确认 Replay 和状态哈希兼容方案之前，不修改已经参与序列化的舞台格名称。

---

## 3. 卡片与卡片属性

### 3.1 卡片种类

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 卡片 | `card` | `card` | 卡片 | 已确认 | 通用概念 |
| 角色卡 | `character` | `"character"` | 角色卡 | 已确认 | — |
| 事件卡 | `event` | 待核对 | 事件卡 | 待检查 | 实际使用逻辑尚未实现 |
| 高潮卡 | `climax` | 待核对 | 高潮卡 | 待检查 | 高潮阶段使用逻辑尚待实现 |

### 3.2 卡片属性

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 卡名 | `name` | 待核对 | 卡名 | 待检查 | — |
| 等级 | `level` | 待核对 | 等级 | 待检查 | 与等级区同名但所属对象不同 |
| 费用 | `cost` | 待核对 | 费用 | 待检查 | 以后可通过规则查询得到当前费用 |
| 力量 | `power` | 待核对 | 力量 | 待检查 | 以后区分印刷值与当前值 |
| 灵魂 | `soul` | 待核对 | 灵魂 | 待检查 | — |
| 颜色 | `color` | 待核对 | 颜色 | 待检查 | — |
| 特征 | `traits` | 待核对 | 特征 | 待检查 | 一张卡可能具有多个特征 |
| 触发图标 | `trigger_icons` | 待核对 | 触发图标 | 待检查 | 一张卡可能具有多个触发图标 |

### 3.3 角色状态

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 竖置 | `stand` | 尚未实现 | 竖置 | 已确认 | 以后可使用 `CardState.STAND` |
| 横置 | `rest` | 尚未实现 | 横置 | 已确认 | 以后可使用 `CardState.REST` |
| 倒置 | `reverse` | 尚未实现 | 倒置 | 已确认 | 以后可使用 `CardState.REVERSE` |

### 3.4 能力种类

能力系统尚未实现，这里只预留命名。

| 中文概念 | 规范变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 永续能力 | `continuous_ability` | 【永】 | 待定 | 对应 CONT |
| 自动能力 | `auto_ability` | 【自】 | 待定 | 对应 AUTO |
| 起动能力 | `activated_ability` | 【起】 | 待定 | 对应 ACT |

### 3.5 卡片数据模型

以下属于项目内部术语。

| 中文概念 | 规范代码名 | UI 名称 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| 卡片定义 | `CardDefinition` | — | 项目术语 | 保存同名卡共享的静态数据 |
| 卡片实例 | `CardInstance` | — | 项目术语 | 表示对局中实际存在的一张牌，以 `instance_id` 区分 |

---

## 4. 游戏流程

### 4.1 回合与阶段

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 所属层级 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 回合 | `turn` | `turn_number` 等 | 回合 | 游戏 | 已确认 | — |
| 重置阶段 | `stand` | `"stand"` | 重置阶段 | 回合 | 已确认 | `Phase.STAND` |
| 抽卡阶段 | `draw` | `"draw"` | 抽卡阶段 | 回合 | 已确认 | `Phase.DRAW` |
| 计时阶段 | `clock` | `"clock"` | 计时阶段 | 回合 | 已确认 | `Phase.CLOCK` |
| 主要阶段 | `main` | `"main"` | 主要阶段 | 回合 | 已确认 | `Phase.MAIN` |
| 高潮阶段 | `climax` | `"climax"` | 高潮阶段 | 回合 | 已确认 | `Phase.CLIMAX` |
| 攻击阶段 | `attack` | 待核对 | 攻击阶段 | 回合 | 待检查 | `Phase.ATTACK` |
| 结束阶段 | `end` | `"end"` | 结束阶段 | 回合 | 已确认 | `Phase.END` |

### 4.2 攻击阶段内部层级

官方英文规则使用 Attack Sub-Phase，因此规范变量名采用 `attack_subphase`，不再采用此前暂定的 `attack_sequence`。

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 所属层级 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 攻击子阶段 | `attack_subphase` | 尚未实现 | 攻击子阶段 | 攻击阶段 | 已确认 | 官方术语为 Attack Sub-Phase |
| 攻击宣言步骤 | `attack_declaration` | 尚未实现 | 攻击宣言步骤 | 攻击阶段 / 攻击子阶段入口 | 已确认 | 具体状态机实现待设计 |
| 触发步骤 | `trigger` | 尚未实现 | 触发步骤 | 攻击子阶段 | 已确认 | — |
| 反击步骤 | `counter` | 尚未实现 | 反击步骤 | 攻击子阶段 | 已确认 | — |
| 伤害步骤 | `damage` | 尚未作为流程状态实现 | 伤害步骤 | 攻击子阶段 | 已确认 | 不等同于伤害结算 |
| 战斗步骤 | `battle` | 尚未实现 | 战斗步骤 | 攻击子阶段 | 已确认 | — |
| 再演步骤 | `encore` | 尚未实现 | 再演步骤 | 攻击阶段 | 已确认 | 不属于单次 `attack_subphase` |

暂定层级：

```text
回合
└── 攻击阶段
    ├── 攻击宣言步骤 / 玩家可操作时点
    ├── 攻击子阶段
    │   ├── 攻击宣言处理
    │   ├── 触发步骤
    │   ├── 反击步骤
    │   ├── 伤害步骤
    │   └── 战斗步骤
    └── 再演步骤
```

这里先确定术语，不提前锁死攻击阶段的具体状态机结构。

### 4.3 生命周期事件

以下属于项目内部事件名。

| 含义 | 规范事件名 | UI 表现 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 阶段开始 | `phase_started` | 通常不直接显示 | 项目术语 | 阶段进入时点 |
| 阶段本体处理 | `phase_processed` | 通常不直接显示 | 项目术语 | 阶段强制规则处理到达或完成 |
| 玩家操作窗口开放 | `action_window_opened` | 显示对应操作 | 项目术语 | 此时 Engine 可以暴露普通合法操作 |
| 阶段结束 | `phase_ended` | 通常不直接显示 | 项目术语 | 阶段离开时点 |
| 回合开始 | `turn_started` | 可显示回合开始 | 项目术语 | 回合生命周期入口 |

`started`、`processed`、`completed`、`ended` 不应混用。若以后引入 `completed`，应专门表示某个离散规则处理或动作完成，而不是阶段结束。

---

## 5. 规则处理

阶段或步骤表示“当前进行到哪里”；规则处理表示“Engine 因规则要求正在执行什么”。

例如：

```text
伤害步骤 → 游戏流程中的位置
damage_resolution → 实际执行伤害的规则处理
```

| 中文概念 | 规范变量名 | 当前变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 抽牌处理 | `draw` / `_draw_*` | 已有相关逻辑 | 抽牌 | 待检查 | 不要与 `Phase.DRAW` 混淆 |
| 伤害结算 | `damage_resolution` | `_deal_damage()` 等 | 伤害处理 | 待检查 | 不要与伤害步骤 `damage` 混淆 |
| 伤害取消 | `damage_cancel` | 已有相关逻辑 | 伤害取消 | 待检查 | 事件名之后统一审计 |
| 卡组更新 | `refresh` | 已有相关逻辑 | 卡组更新 | 已确认 | — |
| 更新点处理 | `refresh_point` | 已有相关逻辑 | 更新点 | 已确认 | 与 `refresh` 分开 |
| 升级 | `level_up` | 已有相关逻辑 | 升级 | 已确认 | — |
| 舞台重叠处理 | `stage_overlap` | 已有相关逻辑 | 舞台重叠 | 待检查 | — |
| 触发判定 | `trigger_check` | 尚未实现 | 触发判定 | 已确认 | 之后用于触发步骤 |
| 规则动作 | `rule_action` | 当前架构部分覆盖 | 规则处理 | 待检查 | 需要与现有 Resolution 体系核对 |
| 检查时点 | `check_timing` | 当前间接表示 | 检查时点 | 待检查 | 以后与自动能力、规则动作关系密切 |
| 出牌时点 | `play_timing` | 当前主要由操作窗口近似表达 | 可操作时点 | 待检查 | `action_window` 不应直接视为完全等同于官方概念 |

### 5.1 结束阶段计划中的规则处理

| 中文概念 | 规范变量名 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 手牌上限 | `hand_limit(player_id)` | 手牌上限 | 待实现 | 默认 7，效果可以修改 |
| 弃牌至手牌上限 | `end_hand_discard` | 请选择弃置至手牌上限 | 待实现 | 需要玩家选择 |
| 高潮区清理 | `end_climax_cleanup` | 高潮卡置入控制室 | 待实现 | 强制规则处理，不是玩家选择 |

---

## 6. 程序基础术语

以下属于模拟器内部抽象，不视为官方规则术语。

| 中文概念 | 规范代码名 | 当前代码名 | UI 名称 | 状态 | 说明 |
| --- | --- | --- | --- | --- | --- |
| 玩家操作 | `Action` / `XxxAction` | 已有多个 Action 类 | 对应具体按钮 | 项目术语 | 玩家提交、Engine 验证并执行的命令 |
| 合法选择描述 | `Options` / `XxxOptions` | 如 `StageSwapOptions` | 对应选择 UI | 项目术语 | 描述合法候选和选择限制，不直接执行 |
| 游戏事件 | `Event` / `EventKind` | 当前主要使用 `"kind"` | 最近记录等 | 待检查 | 以后应集中管理事件类型 |
| 操作窗口 | `action_window` | `action_window_opened` | 操作按钮区域 | 项目术语 | 普通合法操作开放的 Engine 抽象 |
| 结算点 | `resolution_point` | `_resolve_resolution_point()` | — | 项目术语 | 检查规则、事件、触发和待处理内容 |
| 结算上下文 | `ResolutionContext` | `ResolutionContext` | — | 项目术语 | 保存当前结算过程所需状态 |
| 待处理效果 | `pending_effect` | 已有相关骨架 | 待处理效果 | 项目术语 | 未处理完时阻止普通操作 |
| 后续流程 | `Continuation` | 当前为 `pending_continuation` 元组 | — | 待迁移 | 后续建议改为明确类型 |
| 状态哈希 | `state_hash` | `state_hash` | — | 项目术语 | 用于 Replay 确定性检查 |
| Replay | `replay` | 已有 Replay 系统 | Replay | 项目术语 | 保存可确定性重放的操作与配置 |

### 6.1 常用命名模式

```python
# 玩家操作
PlayClimaxAction
ActivateAbilityAction
EndHandDiscardAction

# 合法选择
ClimaxPlayOptions
ActivatedAbilityOptions
EndHandDiscardOptions

# 规则查询
hand_limit(player_id)
get_power(card_id)
get_soul(card_id)
can_play_card(...)
can_attack(...)

# 事件
phase_started
phase_processed
action_window_opened
phase_ended
card_moved
card_played
stage_slots_swapped
damage_completed
```

---

## 7. UI 名称

各术语表已经把**规范变量名、当前变量名和 UI 名称放在相邻列**，这里仅规定总体原则。

1. UI 使用中文玩家熟悉的 WS 术语。
2. Engine 标识符使用统一的英文变量名。
3. UI 文案不进入 Engine 规则逻辑。
4. 某类操作在当前时点存在，但因为选择不足暂时不可执行时，可以显示为不可用。
5. 与当前时点无关的操作通常直接隐藏。

例如以后可以集中维护：

```python
PHASE_NAMES = {
    Phase.STAND: "重置阶段",
    Phase.DRAW: "抽卡阶段",
    Phase.CLOCK: "计时阶段",
    Phase.MAIN: "主要阶段",
    Phase.CLIMAX: "高潮阶段",
    Phase.ATTACK: "攻击阶段",
    Phase.END: "结束阶段",
}
```

这里表示目标结构，不要求现在立即迁移成枚举。

---

## 8. 废弃与迁移名称

| 旧变量名 | 规范变量名 | 范围 | 状态 | 原因 | 兼容性备注 |
| --- | --- | --- | --- | --- | --- |
| `front_left` | `center_left`（候选） | 舞台格 | 待迁移 | 官方使用 Center Stage | 先检查 Replay 与状态哈希 |
| `front_center` | `center_center`（候选） | 舞台格 | 待迁移 | 同上 | 同上 |
| `front_right` | `center_right`（候选） | 舞台格 | 待迁移 | 同上 | 同上 |
| `attack_sequence` | `attack_subphase` | 攻击流程 | 待迁移 | 官方术语为 Attack Sub-Phase | 尚未正式实现，迁移成本较低 |
| `pending_continuation` 元组 | `Continuation` | Engine 流程 | 未来迁移 | 字符串元组随流程增长会变脆弱 | 若以后参与持久化需重新评估 |

---

## 9. 待确认事项

1. `stage_slot` 是否保留为项目 API 术语，还是统一使用 `stage_position`。
2. `front_*` 是否迁移为 `center_*`，以及 Replay、状态哈希如何兼容。
3. 高潮区字段继续使用 `climax`，还是迁移为 `climax_area`。
4. `Phase`、区域、卡片状态和 `EventKind` 的最终枚举结构。
5. 攻击阶段的最终状态机结构。
6. 项目的 `action_window` 与官方 Play Timing、Check Timing 的准确关系。
7. 伤害相关事件的统一命名。
8. 实现【永】前确定规则查询的统一命名。
9. 实现【自】前确定 Choice、Pending、Continuation 的统一命名。

---

## 10. 修改流程

以后新增或修改规则相关概念时：

```text
1. 查官方英文综合规则。
2. 在本文件中找到或新增对应条目。
3. 确认中文概念、规范变量名、UI 名称和所属层级。
4. 若当前代码不一致，先标记为待迁移。
5. 检查 Replay、状态哈希和测试数据兼容性。
6. 同时修改代码与测试。
7. 更新“废弃与迁移名称”。
```

不要在没有同步更新本文件的情况下，零散修改规则相关变量名。

---

## 11. 参考依据

术语优先依据 Bushiroad 官方英文 Weiß Schwarz 综合规则。

其他官方规则页面可以作为场地区域名称、玩家界面用语等内容的辅助依据。

尚未核对清楚的内容应标记为“待检查”或“待定”，不要为了填满表格而猜测。
