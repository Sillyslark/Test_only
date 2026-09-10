# 2.2.5 特征 / Trait

<!-- SUBSECTION_NAV_START -->
[← 上一小节](04_color.md) | [返回 2.2 目录](README.md) | [下一小节 →](06_level.md)
<!-- SUBSECTION_NAV_END -->
**官方英文名称：** Trait  
**程序字段：** `traits`

Trait 在 Card JSON 中使用字符串数组保存。

JSON 示例：

```json
{
  "traits": ["Music", "Magic"]
}
```

字段类型：

```text
array[string]
```

适用 Card Type：

```text
Character（角色）
```

只有 Character 具有 Trait 这一 Card Information。

规则与约束：

- Character JSON 必须具有 `traits` 字段；
- `traits` 的值必须是字符串数组；
- 允许空数组，表示该 Character 当前没有任何 Trait；
- 不使用 `null` 表示没有 Trait；
- Event 与 Climax 根本不具有 Trait，因此它们的 JSON 中不得出现 `traits` 字段；
- 数组顺序应保留输入顺序；
- 不使用 `set` 或其他会自动去重的数据结构；
- 不在基础 JSON 层自动合并、排序或标准化 Trait 名称。

例如：

```json
{
  "traits": []
}
```

表示该 Character 具有 Trait 这一 Card Information，但当前没有任何 Trait。

而 Event / Climax 应直接不存在：

```text
traits
```

这一字段。

对应 Definition 字段：

```python
traits: tuple[str, ...]
```

JSON Loader 在读取后，可将 JSON 数组转换为不可变 tuple 存入 `CharacterDefinition`。

Trait 属于 Card Definition 的基础静态信息。运行时如果 Ability 或 Effect 增加、移除或改变当前 Trait，应由运行时规则查询层计算 Current Traits，不直接修改基础 `traits`。

<!-- SUBSECTION_NAV_START -->
[← 上一小节](04_color.md) | [返回 2.2 目录](README.md) | [下一小节 →](06_level.md)
<!-- SUBSECTION_NAV_END -->
