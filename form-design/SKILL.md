---
name: form-design
description: 为Spring Boot项目设计二层结构Form/DTO的开发规范。当用户需要设计接口参数、创建Form/DTO类、或使用 /form-design 时使用。
---

# Form/DTO Design

为Spring Boot项目设计符合二层结构规范的Form/DTO类，用于接口参数传递和数据校验。

## 使用场景

当用户需要以下操作时使用：
- 设计REST API的请求参数类
- 创建新的Form或DTO类
- 重构Entity直接用于接口的代码
- 设计支持部分更新的数据结构

## 设计原则

**为什么使用Form/DTO而非Entity：**
- Entity是数据库表的映射，包含JPA注解和持久化逻辑
- Form/DTO是接口契约，关注业务需求和校验规则
- 分离关注点：数据库结构变化不影响API接口
- 安全性：避免暴露数据库字段和关联关系

## 二层结构设计

### 第一层：通用基本信息（BasicInfo）
存放所有类型共有的字段（名称、描述、状态等）

### 第二层：类型特定信息（xxxInfo）
根据业务类型（type字段）决定使用哪个具体配置
- JdbcDatasourceInfo（JDBC数据源）
- MongoDatasourceInfo（MongoDB数据源）
- RedisDatasourceInfo（Redis数据源）
- 其他类型特定信息

## 执行流程

1. **分析业务需求**
   - 确定Form用途（新建/更新/部分更新）
   - 识别必需字段和可选字段
   - 确定是否需要类型分层

2. **设计类结构**
   - 创建主Form类（XxxForm）
   - 创建BasicInfo类（通用字段）
   - 创建类型特定Info类（可选）

3. **添加校验注解**
   - @NotNull（必需字段）
   - @NotBlank（非空字符串）
   - @Valid（级联校验）
   - 自定义校验注解（如需要）

4. **编写Mapper**
   - Form → Entity 转换方法
   - Entity → Form 转换方法（查询场景）
   - 支持部分更新（只复制非null字段）

## 命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 主Form类 | {业务对象}Form | DatasourceConfigForm |
| 基本信息 | {业务对象}BasicInfo | DatasourceBasicInfo |
| 类型信息 | {类型名}Info | JdbcDatasourceInfo |
| 枚举类型 | {业务对象}Type | DatasourceType |

## 代码模板

### 模板1：二层结构Form（支持多类型）

```java
package com.foggy.navigator.config.form;

import lombok.Data;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;

/**
 * 数据源配置表单（二层结构）
 * 第一层：通用信息
 * 第二层：类型特定信息
 */
@Data
public class DatasourceConfigForm {
    /**
     * 数据源ID（新建时可为空，更新时必填）
     */
    private String id;

    /**
     * 租户ID（多租户场景）
     */
    private String tenantId;

    /**
     * 数据源基本信息
     */
    @Valid
    @NotNull(message = "基本信息不能为空")
    private DatasourceBasicInfo basicInfo;

    /**
     * JDBC类数据源信息（MySQL, PostgreSQL, Oracle等）
     */
    @Valid
    private JdbcDatasourceInfo jdbcInfo;

    /**
     * MongoDB数据源信息（可选）
     */
    @Valid
    private MongoDatasourceInfo mongoInfo;

    // 注：根据 basicInfo.type 决定使用哪个具体配置
}

/**
 * 数据源基本信息
 */
@Data
class DatasourceBasicInfo {
    /**
     * 数据源名称
     */
    @NotBlank(message = "数据源名称不能为空")
    private String name;

    /**
     * 数据源类型：JDBC, MONGO, REDIS等
     */
    @NotNull(message = "数据源类型不能为空")
    private DatasourceType type;

    /**
     * 配置描述
     */
    private String description;

    /**
     * 配置状态（可选，默认为NOT_STARTED）
     */
    private ConfigItemStatus status;
}

/**
 * JDBC数据源信息
 */
@Data
class JdbcDatasourceInfo {
    /**
     * 数据库类型：MySQL, PostgreSQL, Oracle, SQL Server
     */
    @NotBlank(message = "数据库类型不能为空")
    private String dbType;

    /**
     * 主机地址
     */
    @NotBlank(message = "主机地址不能为空")
    private String host;

    /**
     * 端口号
     */
    @NotNull(message = "端口号不能为空")
    private Integer port;

    /**
     * 数据库名称
     */
    @NotBlank(message = "数据库名称不能为空")
    private String databaseName;

    /**
     * 用户名
     */
    @NotBlank(message = "用户名不能为空")
    private String username;

    /**
     * 密码（明文，后端加密存储）
     */
    @NotBlank(message = "密码不能为空")
    private String password;

    /**
     * JDBC URL（可选，如果提供则优先使用）
     */
    private String jdbcUrl;

    /**
     * 额外参数（如 useSSL=false&serverTimezone=UTC）
     */
    private String extraParams;
}

/**
 * 数据源类型枚举
 */
enum DatasourceType {
    JDBC,          // JDBC类数据源
    MONGO,         // MongoDB
    REDIS,         // Redis
    ELASTICSEARCH  // Elasticsearch
}
```

### 模板2：简单Form（无类型分层）

```java
package com.foggy.navigator.user.form;

import lombok.Data;
import javax.validation.constraints.*;

/**
 * 用户创建表单
 */
@Data
public class UserCreateForm {
    /**
     * 用户名
     */
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 32, message = "用户名长度必须在3-32之间")
    private String username;

    /**
     * 邮箱
     */
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    /**
     * 密码
     */
    @NotBlank(message = "密码不能为空")
    @Size(min = 8, message = "密码长度不能少于8位")
    private String password;

    /**
     * 显示名称（可选）
     */
    private String displayName;
}
```

### 模板3：部分更新Form

```java
package com.foggy.navigator.user.form;

import lombok.Data;
import javax.validation.constraints.*;

/**
 * 用户更新表单
 * 仅更新非null字段，支持部分更新
 */
@Data
public class UserUpdateForm {
    /**
     * 邮箱（可选）
     */
    @Email(message = "邮箱格式不正确")
    private String email;

    /**
     * 显示名称（可选）
     */
    private String displayName;

    /**
     * 密码（可选）
     */
    @Size(min = 8, message = "密码长度不能少于8位")
    private String password;

    // 注：所有字段都是可选的，只更新非null字段
}
```

### 模板4：自应用Form（推荐）

Form 自身实现 `apply` 方法，将非 null 字段应用到目标对象。这种设计将更新逻辑封装到 Form 内部，调用者只需传递需要更新的字段。

```java
package com.foggy.navigator.config.form;

import com.foggy.core.util.BeanUtils;
import lombok.Data;
import javax.validation.Valid;

/**
 * 数据源配置表单（自应用模式）
 *
 * 使用方式：
 * - 新建：form.apply(new DatasourceConfig())
 * - 更新：form.apply(existingConfig)
 * - 部分更新：只传需要修改的字段，其余为null
 */
@Data
public class DatasourceConfigForm {

    private String id;

    @Valid
    private DatasourceBasicInfo basicInfo;

    @Valid
    private JdbcDatasourceInfo jdbcInfo;

    @Valid
    private MongoDatasourceInfo mongoInfo;

    /**
     * 将表单数据应用到目标对象（部分更新）
     * 只有非null的Info对象才会被应用
     *
     * @param target 目标配置对象
     * @return 返回target，支持链式调用
     */
    public DatasourceConfig apply(DatasourceConfig target) {
        if (basicInfo != null) {
            BeanUtils.copyNonNullProperties(basicInfo, target);
        }
        if (jdbcInfo != null) {
            BeanUtils.copyNonNullProperties(jdbcInfo, target);
        }
        if (mongoInfo != null) {
            BeanUtils.copyNonNullProperties(mongoInfo, target);
        }
        return target;
    }
}

/**
 * 基本信息（字段与DatasourceConfig中的字段名对应）
 */
@Data
class DatasourceBasicInfo {
    private String name;
    private DatasourceType type;
    private String description;
    private ConfigItemStatus status;
}

/**
 * JDBC信息（字段与DatasourceConfig中的字段名对应）
 */
@Data
class JdbcDatasourceInfo {
    private String dbType;
    private String host;
    private Integer port;
    private String databaseName;
    private String username;
    private String password;
    private String jdbcUrl;
    private String extraParams;
}
```

**使用示例：**

```java
@Service
@RequiredArgsConstructor
public class DatasourceConfigService {

    private final DatasourceConfigRepository repository;

    /**
     * 创建配置
     */
    public DatasourceConfig create(DatasourceConfigForm form) {
        DatasourceConfig config = new DatasourceConfig();
        form.apply(config);  // 应用所有非null字段
        return repository.save(config);
    }

    /**
     * 部分更新配置
     */
    public DatasourceConfig update(String id, DatasourceConfigForm form) {
        DatasourceConfig config = repository.findById(id)
            .orElseThrow(() -> new NotFoundException("配置不存在"));
        form.apply(config);  // 只更新非null字段
        return repository.save(config);
    }
}
```

**前端调用示例：**

```javascript
// 只更新描述
await api.patch('/datasource/123', {
  basicInfo: { description: '新描述' }
});

// 只更新JDBC连接信息
await api.patch('/datasource/123', {
  jdbcInfo: { host: '192.168.1.100', port: 3307 }
});

// 同时更新多个部分
await api.patch('/datasource/123', {
  basicInfo: { status: 'ACTIVE' },
  jdbcInfo: { password: 'newPassword' }
});
```

### 模板5：BeanUtils工具类

```java
package com.foggy.core.util;

import org.springframework.beans.BeanWrapper;
import org.springframework.beans.BeanWrapperImpl;
import java.beans.PropertyDescriptor;
import java.util.HashSet;
import java.util.Set;

/**
 * Bean拷贝工具类
 */
public class BeanUtils {

    /**
     * 拷贝非null属性到目标对象
     *
     * @param source 源对象
     * @param target 目标对象
     */
    public static void copyNonNullProperties(Object source, Object target) {
        org.springframework.beans.BeanUtils.copyProperties(
            source, target, getNullPropertyNames(source)
        );
    }

    /**
     * 获取对象中值为null的属性名
     */
    private static String[] getNullPropertyNames(Object source) {
        BeanWrapper wrapper = new BeanWrapperImpl(source);
        PropertyDescriptor[] pds = wrapper.getPropertyDescriptors();

        Set<String> nullNames = new HashSet<>();
        for (PropertyDescriptor pd : pds) {
            if (wrapper.getPropertyValue(pd.getName()) == null) {
                nullNames.add(pd.getName());
            }
        }
        return nullNames.toArray(new String[0]);
    }
}
```

### 模板6：Form到Entity的Mapper（传统方式）

如果不使用自应用模式，可以使用传统的Mapper方式：

```java
package com.foggy.navigator.config.mapper;

import com.foggy.navigator.config.entity.DatasourceConfigEntity;
import com.foggy.navigator.config.form.DatasourceConfigForm;
import org.springframework.stereotype.Component;

/**
 * 数据源配置Mapper
 */
@Component
public class DatasourceConfigMapper {

    /**
     * Form转Entity（新建场景）
     */
    public DatasourceConfigEntity toEntity(DatasourceConfigForm form) {
        DatasourceConfigEntity entity = new DatasourceConfigEntity();

        // 基本信息
        entity.setName(form.getBasicInfo().getName());
        entity.setType(form.getBasicInfo().getType());
        entity.setDescription(form.getBasicInfo().getDescription());
        entity.setStatus(form.getBasicInfo().getStatus());

        // JDBC信息
        if (form.getJdbcInfo() != null) {
            entity.setDbType(form.getJdbcInfo().getDbType());
            entity.setHost(form.getJdbcInfo().getHost());
            entity.setPort(form.getJdbcInfo().getPort());
            entity.setDatabaseName(form.getJdbcInfo().getDatabaseName());
            entity.setUsername(form.getJdbcInfo().getUsername());
            // 注意：密码需要加密
            entity.setPassword(encrypt(form.getJdbcInfo().getPassword()));
        }

        return entity;
    }

    /**
     * 部分更新Entity（只更新非null字段）
     */
    public void updateEntity(DatasourceConfigEntity entity, DatasourceConfigForm form) {
        // 基本信息
        if (form.getBasicInfo() != null) {
            if (form.getBasicInfo().getName() != null) {
                entity.setName(form.getBasicInfo().getName());
            }
            if (form.getBasicInfo().getDescription() != null) {
                entity.setDescription(form.getBasicInfo().getDescription());
            }
            if (form.getBasicInfo().getStatus() != null) {
                entity.setStatus(form.getBasicInfo().getStatus());
            }
        }

        // JDBC信息（只在提供时更新）
        if (form.getJdbcInfo() != null) {
            if (form.getJdbcInfo().getHost() != null) {
                entity.setHost(form.getJdbcInfo().getHost());
            }
            if (form.getJdbcInfo().getPort() != null) {
                entity.setPort(form.getJdbcInfo().getPort());
            }
            if (form.getJdbcInfo().getPassword() != null) {
                entity.setPassword(encrypt(form.getJdbcInfo().getPassword()));
            }
        }
    }

    /**
     * Entity转Form（查询场景）
     */
    public DatasourceConfigForm toForm(DatasourceConfigEntity entity) {
        // 实现省略
        return null;
    }

    private String encrypt(String password) {
        // 密码加密逻辑
        return password;
    }
}
```

## 最佳实践

### 1. 优先使用自应用Form模式
- Form实现`apply(Entity target)`方法，封装更新逻辑
- 使用`BeanUtils.copyNonNullProperties()`自动跳过null字段
- 调用者只需传递需要更新的字段，其余为null
- 新建和更新共用一个Form类，无需单独的CreateForm/UpdateForm
- 减少Mapper样板代码，逻辑更内聚

### 2. 支持部分更新（传统方式）
- UpdateForm中所有字段都是可选的
- Mapper中只复制非null字段
- 避免意外覆盖未修改的字段

### 3. 校验规则
- 使用JSR-303/380标准注解
- 在Form层做校验，不在Entity层
- 提供清晰的错误信息（message属性）

### 4. 类型安全
- 使用枚举而非字符串常量
- 使用Integer/Long而非int/long（支持null）
- 避免使用Map存储结构化数据

### 5. 安全性
- 密码等敏感字段在Mapper中加密
- 避免暴露内部ID生成规则
- UpdateForm不允许修改id、createdAt等字段

### 6. 文档化
- 每个字段添加Javadoc注释
- 说明可选/必需、默认值
- 对于复杂逻辑添加示例

## 约束条件

- 所有Form类使用Lombok的@Data注解
- 包路径统一为 {模块}.form
- 嵌套类（BasicInfo、xxxInfo）定义在同一文件中
- 校验注解使用javax.validation包
- 不在Form中使用JPA注解（@Entity、@Table等）

## 决策规则

- 如果业务对象有多种类型 → 使用二层结构（BasicInfo + xxxInfo）
- 如果只是简单数据结构 → 使用单层Form
- 如果需要支持部分更新 → 使用自应用Form（模板4），实现apply方法
- 如果Form需要复杂转换逻辑（加密、格式转换等） → 使用传统Mapper（模板6）
- 如果字段有校验规则 → 使用@NotNull、@NotBlank等注解
- 如果字段是枚举值 → 创建enum类型，不使用String
- 如果Form有嵌套对象 → 在嵌套对象上添加@Valid注解
- 如果希望减少样板代码 → 优先使用自应用Form + BeanUtils

## 与Entity的区别

| 特性 | Entity | Form/DTO |
|------|--------|----------|
| 用途 | 数据库映射 | 接口参数 |
| 注解 | JPA注解 | 校验注解 |
| 字段 | 数据库所有列 | 业务需要的字段 |
| 关联 | @ManyToOne等 | 外键ID字符串 |
| 可变性 | 可变 | 不可变（仅传输） |
| 包路径 | entity | form/dto |

## Controller使用示例

```java
@RestController
@RequestMapping("/api/datasource")
@RequiredArgsConstructor
public class DatasourceController {

    private final ConfigurationManager configManager;

    /**
     * 创建数据源配置
     */
    @PostMapping
    public ResponseEntity<String> createDatasource(
            @Valid @RequestBody DatasourceConfigForm form) {
        String id = configManager.saveDatasourceConfig(form);
        return ResponseEntity.ok(id);
    }

    /**
     * 更新数据源配置（部分更新）
     */
    @PatchMapping("/{id}")
    public ResponseEntity<Void> updateDatasource(
            @PathVariable String id,
            @Valid @RequestBody DatasourceConfigForm form) {
        configManager.updateDatasourceConfig(id, form);
        return ResponseEntity.ok().build();
    }
}
```
