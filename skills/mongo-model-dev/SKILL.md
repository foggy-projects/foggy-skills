---
name: mongo-model-dev
description: 开发和迭代 foggy-dataset-model-mongo 模块（MongoDB 数据模型支持）。当用户需要修改 MongoDB 查询引擎、表达式处理、TM/QM 模型加载、编写集成测试、或排查 MongoDB 聚合管道问题时使用。
---

# MongoDB 数据模型模块开发

开发和迭代 `addons/foggy-dataset-model-mongo` 模块，该模块将 Foggy 的 TM/QM 数据模型体系桥接到 MongoDB 聚合管道。

## 模块路径

`addons/foggy-dataset-model-mongo/`

## 核心架构

### 源码结构

```
src/main/java/com/foggyframework/dataset/db/model/
├── engine/
│   ├── MongoModelQueryEngine.java         # 核心：将 DbQueryRequest 转为 MongoDB 聚合管道
│   └── expression/                        # 计算字段表达式 → MongoDB $addFields
│       ├── MongoCalculatedFieldProcessor.java  # 入口：处理计算字段定义
│       ├── MongoExpFactory.java                # 表达式工厂（继承 DefaultExpFactory）
│       ├── MongoFragment.java                  # 聚合表达式容器
│       ├── MongoAllowedFunctions.java          # 安全白名单
│       └── mongo/                              # AST 节点实现
│           ├── MongoBinaryExp.java             # 二元运算 → $add/$multiply/...
│           ├── MongoColumnRefExp.java          # 列引用 → "$fieldName"
│           ├── MongoFunctionExp.java           # 函数调用 → $year/$abs/...
│           ├── MongoLiteralExp.java            # 字面量
│           └── MongoUnaryExp.java              # 一元运算 → $not/-
├── impl/mongo/
│   ├── MongoQueryModelImpl.java           # QM 实现：构建并执行聚合管道
│   ├── MongoTableModelImpl.java           # TM 实现
│   ├── MongoQueryModel.java               # 接口
│   └── TmMongoModelLoaderImpl.java        # TM/QM 文件加载器
└── utils/
    └── MongoModelNamedUtils.java          # 命名工具
```

### 聚合管道构建流程

```
DbQueryRequestDef
  → MongoModelQueryEngine.analysisQueryRequest()   # 解析列、切片、权限、排序
  → MongoModelQueryEngine.buildOptions()           # 生成 $match + $project + Sort
  → MongoModelQueryEngine.buildAddFieldsOperation() # 生成 $addFields（计算字段）
  → MongoQueryModelImpl.queryMongo()               # 组装管道并执行
    Pipeline: $match → [$addFields] → $project → [$sort] → $skip → $limit
```

### 关键设计决策

1. **$project 使用原始 Document**：不使用 Spring Data 的 `ProjectionOperation`，因为它会将 `location.coordinates.1` 错误转为 `$location.coordinates[1]`
2. **数组元素用 $arrayElemAt**：TM 中 `column: 'arr.0'` 自动生成 `{ $arrayElemAt: ["$arr", 0] }`
3. **计算字段表达式白名单**：`MongoAllowedFunctions` 控制允许的操作符和函数，防止注入
4. **不支持维度表**：MongoDB 模型不支持 dimension（join），加载时会抛异常

## 测试体系

### 测试配置

- **启动类**: `com.foggyframework.dataset.db.model.test.JdbcModelTestApplication`
- **注解**: `@EnableFoggyFramework(bundleName = "foggy-framework-dataset-jdbc-model-test")`
- **Profile**: `docker`（需要 MongoDB 运行在 `localhost:17017`）
- **Bean**: 定义了 `mongoTemplate`（Primary）和 `mcpMongoTemplate` 两个 MongoTemplate

### 测试基类

`MongoTestSupport` 提供：
- `clearCollection(name)` — 清空集合
- `insertDocument(name, doc)` / `insertDocuments(name, docs)` — 插入数据
- `findAll(name)` / `find(name, query)` — 查询数据
- `getCollectionCount(name)` — 计数

### 测试资源

```
src/test/resources/
├── application-docker.yml                    # MongoDB: localhost:17017
├── foggy/templates/
│   ├── calc_test/
│   │   ├── model/SalesOrderTestModel.tm      # 计算字段测试
│   │   └── query/SalesOrderTestQueryModel.qm
│   └── mcp_audit/
│       ├── model/GeoStationModel.tm          # 数组元素访问测试
│       └── query/GeoStationQueryModel.qm
```

### 测试编写规范

```java
@Slf4j
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("测试描述")
class XxxTest extends MongoTestSupport {

    @Resource
    private JdbcService jdbcService;

    private static final String QUERY_MODEL_NAME = "XxxQueryModel";
    private static final String COLLECTION_NAME = "xxx_test";

    @Test @Order(1) @DisplayName("初始化测试数据")
    void setupTestData() {
        clearCollection(COLLECTION_NAME);
        // 插入测试文档...
    }

    @Test @Order(10) @DisplayName("核心测试")
    void testCore() {
        DbQueryRequestDef queryRequest = new DbQueryRequestDef();
        queryRequest.setQueryModel(QUERY_MODEL_NAME);
        queryRequest.setColumns(Arrays.asList("col1", "col2"));

        PagingRequest<DbQueryRequestDef> form = PagingRequest.buildPagingRequest(queryRequest, 50);
        PagingResultImpl result = jdbcService.queryModelData(form);

        // 断言...
    }

    @Test @Order(99) @DisplayName("清理测试数据")
    void cleanup() {
        clearCollection(COLLECTION_NAME);
    }
}
```

### 切片（过滤）条件

```java
List<SliceRequestDef> slices = new ArrayList<>();
SliceRequestDef slice = new SliceRequestDef();
slice.setField("city");       // QM 中的字段 name
slice.setOp("=");             // 支持: =, <>, in, not in, like, left_like, right_like, [), []
slice.setValue("北京");
slices.add(slice);
queryRequest.setSlice(slices);
```

## TM 模型编写

```javascript
import '@mcpMongoTemplate';   // 引用 Spring Bean 名称

export const model = {
    name: 'XxxModel',
    caption: '模型名称',
    tableName: 'collection_name',   // MongoDB 集合名
    idColumn: '_id',
    type: 'mongo',
    mongoTemplate: mcpMongoTemplate,

    properties: [
        // 基础字段
        { column: '_id', name: 'id', caption: 'ID', type: 'STRING' },
        { column: 'name', caption: '名称', type: 'STRING' },

        // 嵌套文档字段（点号访问）
        { column: 'address.city', name: 'city', caption: '城市', type: 'STRING' },

        // 数组元素字段（自动用 $arrayElemAt）
        { column: 'location.coordinates.0', name: 'lng', caption: '经度', type: 'NUMBER' },
        { column: 'location.coordinates.1', name: 'lat', caption: '纬度', type: 'NUMBER' },

        // 整个数组/子文档
        { column: 'location.coordinates', name: 'coordinates', caption: '坐标' },
    ],

    measures: [
        { column: 'price', name: 'avgPrice', caption: '均价', type: 'NUMBER', aggregation: 'avg' },
        { column: 'quantity', name: 'totalQty', caption: '总量', type: 'INTEGER', aggregation: 'sum' }
    ]
};
```

**类型映射**: `STRING`, `NUMBER`(BigDecimal), `INTEGER`(Integer), `BIGINT`(Long), `DATETIME`(Date), `BOOL`(Boolean)

## QM 模型编写

```javascript
const m = loadTableModel('XxxModel');

export const queryModel = {
    name: 'XxxQueryModel',
    caption: '查询名称',
    model: m,
    loader: 'v2',           // 可选，使用 v2 加载器

    columnGroups: [
        {
            caption: '分组名',
            items: [
                { ref: m.id },
                { ref: m.name }
            ]
        }
    ],

    orders: [
        { ref: m.orderDate, order: 'desc' }
    ],

    accesses: []
};
```

## 构建和测试命令

```bash
# 编译（含依赖模块）
mvn compile test-compile -pl addons/foggy-dataset-model-mongo -am -DskipTests -q

# 运行单个测试类
mvn test -pl addons/foggy-dataset-model-mongo -Dtest="com.foggyframework.dataset.db.model.mongo.XxxTest"

# 运行全部 mongo 模块测试
mvn test -pl addons/foggy-dataset-model-mongo

# 跳过找不到测试类的报错
mvn test -pl addons/foggy-dataset-model-mongo -Dtest="com.foggyframework.dataset.db.model.mongo.XxxTest" -Dsurefire.failIfNoSpecifiedTests=false
```

## 修改决策规则

- 修改 `$project` 投影逻辑 → 编辑 `MongoModelQueryEngine.buildOptions()` 和 `buildFieldExpression()`
- 修改聚合管道组装 → 编辑 `MongoQueryModelImpl.queryMongo()`
- 添加新的计算字段函数 → 在 `MongoAllowedFunctions` 注册映射，在 `MongoFunctionExp` 实现转换
- 修改切片/过滤条件 → 编辑 `MongoModelQueryEngine.buildSlice()`
- 修改 TM 加载逻辑 → 编辑 `TmMongoModelLoaderImpl`
- 添加新测试模型 → 在 `src/test/resources/foggy/templates/` 下创建 `.tm` 和 `.qm` 文件（文件名全局唯一）
- 需要新 MongoTemplate Bean → 在 `JdbcModelTestApplication` 中添加 `@Bean`，TM 中 `import '@beanName'`

## 约束条件

- MongoDB 模型**不支持维度表**（dimension/join），勿在 TM 中定义 dimensions
- TM/QM 文件名在整个 bundle 内必须**全局唯一**（bundle 递归扫描 `foggy/templates/**/`）
- 计算字段中的函数必须在 `MongoAllowedFunctions` 白名单中，否则抛 `SecurityException`
- 测试依赖 Docker 环境中的 MongoDB（端口 17017），profile 为 `docker`
- 不要使用 Spring Data 的 `ProjectionOperation` 构建 `$project`，使用原始 `Document`
- 集合名在测试中应使用 `_test` 后缀，避免与生产数据冲突
