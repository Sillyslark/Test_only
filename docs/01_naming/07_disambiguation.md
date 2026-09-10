### 1.7 同名概念消歧原则

<!-- SECTION_NAV_START -->
[← 上一节](06_actions_choices_events.md) | [返回本章目录](README.md) | [下一节 →](08_official_terms_priority.md)
<!-- SECTION_NAV_END -->
| 名称 | 含义一 | 含义二或其他含义 | 规范示例 |
| --- | --- | --- | --- |
| Event | 事件卡 | 游戏事件 | `CardType.EVENT` / `GameEvent` |
| Climax | 高潮卡 | 高潮区、高潮阶段 | `CardType.CLIMAX` / `Zone.CLIMAX_AREA` / `Phase.CLIMAX` |
| Clock | 计时区 | 计时阶段 | `Zone.CLOCK` / `Phase.CLOCK` |
| Level | 卡片等级 | 等级区 | `definition.level` / `Zone.LEVEL` |
| Stand | 竖置状态 | 重置阶段 | `CardState.STAND` / `Phase.STAND` |
| Trigger | 触发图标 | 触发步骤、能力触发等 | `TriggerIcon` / `AttackStep.TRIGGER` / `AbilityTrigger` |
| Damage | 伤害步骤 | 伤害处理 | `AttackStep.DAMAGE` / `damage_resolution` |
| State | 卡片状态 | 游戏状态、玩家状态 | `CardState` / `GameState` / `PlayerState` |
| Type | 卡片种类 | 能力种类等 | `CardType` / `AbilityType` |
| Action | 玩家操作 | 规则动作 | `Action` / `RuleAction` |
| Encore | 再演步骤 | 再演相关能力或处理 | 使用所属流程或能力类别明确区分 |

应尽量避免定义过于宽泛的裸类型名称，例如 `Type`、`State`、`Event`、`Trigger`、`Step`。

优先使用 `CardType`、`AbilityType`、`CardState`、`GameState`、`GameEvent`、`TriggerIcon`、`AbilityTrigger`、`AttackStep` 等能直接表达所属领域的名称。

<!-- SECTION_NAV_START -->
[← 上一节](06_actions_choices_events.md) | [返回本章目录](README.md) | [下一节 →](08_official_terms_priority.md)
<!-- SECTION_NAV_END -->
