### 1.5 稳定标识

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

