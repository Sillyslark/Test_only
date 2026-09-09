> [← 返回第 2 章目录](../02_cards.md)

## 2.4 Card Color

颜色属于规则值，不使用任意字符串作为最终规则状态。

规范类型：

```python
class CardColor(Enum):
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    BLUE = "blue"
```

当前先支持：

```text
YELLOW
GREEN
RED
BLUE
```

以后确认存在需要支持的新颜色时，再扩展 `CardColor`。

当前不预留：

```text
OTHER
UNKNOWN
CUSTOM
```

等兜底值。

未知或尚未支持的颜色应在数据加载 / 验证阶段明确失败，而不是静默进入规则对象。

`CardDefinition.color` 表示基础 / 印刷 Color。若未来 Ability / Effect 改变某张 Card 的当前 Color，同样由规则查询层计算 Current Color，不修改 Definition。

---

---

> [← 返回第 2 章目录](../02_cards.md)
