# TM 字典引用（dictRef）指南

## 核心链路

```
Java Entity @DictRef(Xxx.class)
    → dicts.fsscript 注册字典
        → TM 中 dictRef: dicts.Xxx
            → frontend-meta 输出 dictId + dictMode
                → 前端生成字典下拉筛选器
```

## 1. 字典注册（dicts.fsscript）

### 方式 A：从 Java 类自动注册（推荐）

适用于 Java 接口/类中用 `@ApiModelProperty` 标注了静态常量的字典。

```javascript
import { registerFromClass } from '@dictFromClass';

export const dicts = {
    OrgNature: registerFromClass(
        'com.foggysource.open.saas.basic.identity.domain.OrgNature',
        'OrgNature',
        '机构性质'
    ),
};
```

`registerFromClass` 通过反射读取 Java 类的 static fields + `@ApiModelProperty`，自动生成 items。

### 方式 B：手动注册

适用于无对应 Java 类的字典，或需要自定义 value-label 映射。

```javascript
import { registerDict } from '@jdbcModelDictService';

export const dicts = {
    orderStatus: registerDict({
        id: 'orderStatus',
        caption: '订单状态',
        items: [
            { value: 'PENDING', label: '待处理' },
            { value: 'CONFIRMED', label: '已确认' },
            { value: 'COMPLETED', label: '已完成' }
        ]
    }),
};
```

## 2. TM 中引用字典

```javascript
import { dicts } from './dicts.fsscript';

export const model = {
    properties: [
        {
            column: 'org_nature',
            caption: '机构性质',
            type: 'INTEGER',
            dictRef: dicts.OrgNature       // ← 引用注册后的 dictId
        }
    ]
};
```

## 3. 错误写法对照

| 写法 | 结果 | 原因 |
|------|------|------|
| `dictRef: dicts.OrgNature` | ✅ 正确 | registerDict 返回 dictId 字符串 |
| `dictRef: 'OrgNature'` | ⚠️ 有 dictId 但无 items | 字符串未经 registerDict 注册，运行时无字典数据 |
| 无 dictRef | ❌ 当作普通数字列 | 前端生成"最小/最大"数字筛选器 |

## 4. 从 Entity 到 TM 的检测流程

1. 找到对应 Entity 类（如 `OrgEntity.java`）
2. 搜索所有 `@DictRef(Xxx.class)` 注解
3. 对每个 `Xxx.class`：
   - 确认其 package 全限定名
   - 在 `dicts.fsscript` 中注册（优先用 `registerFromClass`）
4. 在 TM 对应字段加 `dictRef: dicts.Xxx`

## 5. registerFromClass 依赖说明

- 需要宿主服务注册 `@Component("dictFromClass")` Bean
- Java 字典类必须在 classpath 中（通过 Maven 依赖引入）
- 字典类的 static fields 必须有 `@ApiModelProperty` 注解才会被提取
- 无 `@ApiModelProperty` 的常量会被跳过
