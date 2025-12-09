## Cocos Creator (TypeScript) 最佳实践

### 1) 项目结构与组件化
- **目录建议**：`assets/scripts/{components,services,managers,models,utils}`；按功能/场景分包，Prefab 与脚本同名同目录。
- **组件职责单一**：每个 `Component` 只负责本节点的表现与输入；跨节点逻辑交由 `Manager/Service`。
- **逻辑分离**：  
  - 视图层：`Component`（绑定节点/动画/事件）。  
  - 领域层：`Service/Manager`（数据流、状态机、网络、存档）。  
  - 数据层：`Model`（纯数据与校验）。  
- **生命周期约定**：在 `onLoad` 取引用（`@property`/`getComponent`），`start` 做首帧逻辑，`onEnable/onDisable` 绑定/解绑事件，`onDestroy` 释放资源。
- **事件与解耦**：优先使用 `EventTarget`/`director.on` 做全局事件，不在组件间互相强依赖；UI 层用信号/命令模式隔离业务。
- **依赖注入**：全局单例用懒加载的 `Manager`，避免直接 `new` 组件；通过工厂函数传入配置与回调，方便测试与复用。
- **严格类型**：`strict` 模式，`noImplicitAny`/`exactOptionalPropertyTypes` 开启；节点查找使用自定义类型守卫，避免 `any`。
- **资源与 Prefab**：通过 `resources.load`/`assetManager.loadAny` 的统一封装加载，返回 `Promise<T>`；Prefab 实例化后立即缓存必要引用，避免频繁 `getChildByName`。

### 2) TypeScript 编码规范
- **命名**：类/枚举用 `PascalCase`，实例/函数用 `camelCase`，常量全大写。节点引用加语义后缀：`playerNode`、`hpBarNode`。
- **装饰器使用**：`@property` 仅暴露设计器需要的字段；避免在运行时修改 `@property` 元数据。
- **可空处理**：对 `find`/`getComponent` 结果做空值检查；用 `assertExists` 辅助函数缩短分支。
- **异步与错误**：统一 `async/await`，外围捕获；加载/网络调用包装重试与超时；在 UI 层显示加载与错误提示。
- **不可变/防御式编程**：传入数据做浅/深拷贝（视需求）；对外暴露只读视图。
- **数学与向量**：复用 `Vec2/Vec3/Quat` 变量，避免临时对象；封装常用计算工具函数。
- **状态机**：角色/关卡/流程使用显式状态机（枚举 + 映射），禁止魔法数/字符串状态。
- **更新循环**：在 `update` 中避免分支爆炸；把高频逻辑拆到 `FixedUpdate`（2.x）或自控的计时器；按需 `enabled = false` 关闭不用的组件。

### 3) 性能优化（Cocos 特有）
- **对象池（NodePool）**：  
  - 为高频生成物（子弹、特效、飘字）建立池；`get`/`put` 前后重置组件状态。  
  - 统一 `PoolManager` 管理不同 Prefab 的池，池上限防止无限膨胀。  
  - 避免在 `update` 中创建临时对象或闭包。
- **DrawCall 优化**：  
  - 合图/自动合批：同一材质、同层级、同 BlendMode 的节点放在一起；UI 使用同一 SpriteAtlas，减少材质切换。  
  - 控制 Mask/Spine/Particle 数量，它们会打断合批；必要时分层。  
  - Label：批量静态文本，开启 `Cache Mode`（Bitmap/Char）；动态数字使用预制数字表。  
  - Spine：共享 SkeletonData，复用材质；关闭不必要的事件/slot。  
  - 渲染顺序：减少频繁的节点增删和层级调整；使用 `static` 节点缓存。
- **内存与 GC**：  
  - 复用 `Vec*`、数组与对象；定期清理事件监听；计时器 `unschedule`。  
  - 资源引用计数：加载后持有时 `addRef`，不再使用时 `decRef/release`；场景切换前释放临时资源。  
  - 音频：短音效使用 `playOneShot`；长音频复用 `AudioSource`，避免频繁创建。
- **物理与碰撞**：  
  - 只启用需要的碰撞层；简化碰撞体；在静态物体上禁用多余的刚体属性。  
  - 高频碰撞中避免开销大的字符串比较，使用枚举或位掩码。
- **定时与更新**：  
  - 高频逻辑使用自管的时间累加器而非多个 `schedule`；长间隔事件合并到一个 `TimerManager`。  
  - 在不可见/暂停时关闭组件 `enabled` 或使用全局 `pause` 控制。

### 4) 资源与场景管理
- **场景切换**：淡入淡出/加载界面封装在 `SceneManager`；切换前保存关键状态与存档；切换后预加载下一场景资源。
- **预加载策略**：启动阶段只加载必需资源；按模块/章节懒加载；热点资源常驻，冷资源分帧释放。
- **UI 层级**：统一 `Canvas` 分层（背景/主界面/弹窗/特效/指引）；弹窗使用队列与遮罩管理。
- **存档与配置**：配置表用 JSON/二进制缓存；提供版本号与校验；存档加密/签名，避免破损。

### 5) 测试与调试
- **断言与日志**：提供 `assert`/`assertExists`，在开发版抛错；日志分级（info/warn/error）并可运行时开关。
- **可视化调试**：热键显示性能面板（FPS、DrawCall、内存、节点数）；在编辑器下开启 `Stats`。
- **自动化**：关键逻辑（状态机、数值计算、服务层）用 Jest/ts-node 单测；CI 运行 `eslint` + 单测。

### 6) ESLint/TSConfig 建议
- **TSConfig**：`strict: true`，`moduleResolution: node`，`target: ES2018+`；`paths` 为常用别名（如 `@/` 指向 `assets/scripts`）。
- **ESLint 规则**：  
  - `@typescript-eslint/explicit-function-return-type`（公共 API）；  
  - `no-unused-vars`/`no-floating-promises`；  
  - 禁止 `any`/禁止隐式 `this`；  
  - `max-lines-per-function` 控制复杂度；  
  - `prefer-const`/`eqeqeq`/`no-magic-numbers`（允许少数常量白名单）。
- **格式化**：Prettier 统一风格；提交前 `lint-staged` + `pre-commit`。

### 7) 典型模式速查
- **对象池管理器**：`PoolManager.get(prefabKey): Node` / `put(node)`；取出后重置组件状态。
- **事件总线**：`EventTarget` 单例，约定事件名常量与 payload 类型，避免字符串散落。
- **资源加载封装**：`async load<T>(url, type): Promise<T>`，内部处理超时/重试/引用计数。
- **计时器管理**：统一 `TimerManager`，支持标签/清理，避免孤儿 `scheduleOnce`。
- **状态机**：`state: Enum` + `handlers: Record<State, () => void>`，统一入口 `setState(next)`。

### 8) 发布与平台注意
- **压缩与合图**：使用内置压缩与图集；按平台设置纹理压缩格式（ASTC/ETC2/PVRTC）。  
- **首包体积**：拆分远程包，首包只含核心资源；远程包 CDN 加速。  
- **性能验证**：目标机型真机测试；关注首帧时间、内存、FPS、DrawCall 峰值。

### 9) AI 知识库阅读提示
- 结构化条目短句，便于嵌入检索；关键名词保持一致（对象池、DrawCall、合批、资源引用计数、状态机）。  
- 提供模式名称 + 场景 + 关键 API，减少歧义。  
- 规则与原因并列，方便模型回答“为什么”类问题。