### 1.5 稳定标识

<!-- SECTION_NAV_START -->
[← 上一节](04_definition_and_instance.md) | [返回本章目录](README.md) | [下一节 →](06_actions_choices_events.md)
<!-- SECTION_NAV_END -->
需要跨规则处理、操作、游戏事件、Replay 或序列化引用的具体对象，应具有稳定标识，原则上使用：

```python
..._id
```

例如：

```python
player_id
card_id
ability_id
```

现有 `instance_id` 是否迁移，留到对应章节单独审计。

<!-- SECTION_NAV_START -->
[← 上一节](04_definition_and_instance.md) | [返回本章目录](README.md) | [下一节 →](06_actions_choices_events.md)
<!-- SECTION_NAV_END -->
