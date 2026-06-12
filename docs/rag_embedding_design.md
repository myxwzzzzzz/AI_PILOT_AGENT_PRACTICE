# RAG Embedding Retrieval Design

本文件用于设计 `AI Pilot Agent Practice` 项目后续的 embedding-based RAG 检索方案。

当前文档只做方案设计，不在本课实现 embedding、向量索引或向量检索代码。

---

## 1. 背景

当前项目已经具备关键词检索版 RAG：

```text
用户问题
→ rag_retrieval_router.py
→ rag_retriever.py
→ documents/ 本地 Markdown 知识文档
→ rag_qa.py
→ rag_llm_answerer.py 或本地 fallback
```

当前 `rag_retrieval_router.py` 已经提供统一入口：

```python
retrieve_chunks(...)
```

并通过配置项控制默认检索模式：

```python
DEFAULT_RETRIEVAL_MODE = "keyword"
```

这为后续扩展 embedding / hybrid retrieval 提供了接口基础。

---

## 2. 当前 keyword retrieval 的优点

关键词检索当前仍然有价值，不应删除。

优点：

```text
1. 不依赖外部 API
2. 不消耗 token
3. 结果可解释
4. 测试稳定
5. 适合作为 fallback
6. 对明确关键词问题效果较好
```

例如：

```text
最大回撤是什么意思？
MA5-MA10 策略适合震荡行情吗？
sort_by 应该用什么？
```

这些问题包含明显关键词，keyword retrieval 通常可以命中相关文档片段。

---

## 3. 当前 keyword retrieval 的局限

关键词检索的主要问题是语义理解能力有限。

例如用户可能会问：

```text
哪个指标能反映策略最糟糕时亏了多少？
怎么判断一个策略是不是太颠簸？
短均线和长均线交叉为什么会产生信号？
```

这些问题可能没有直接出现：

```text
最大回撤
波动率
均线交叉
```

但语义上仍然对应这些知识点。关键词检索可能因为关键词不匹配而召回不足。

因此，embedding retrieval 的目标是增强语义召回能力。

---

## 4. embedding retrieval 的目标

embedding retrieval 要解决的问题：

```text
1. 用户问题和文档片段用词不同，但语义相近时仍能召回
2. 提升中文自然语言问题的召回稳定性
3. 支持更多知识文档后仍能保持较好检索效果
4. 为后续 hybrid retrieval 做基础
```

embedding retrieval 不负责：

```text
1. 直接生成最终答案
2. 直接执行工具
3. 绕过 llm_router.py 执行代码
4. 替代 keyword retrieval fallback
5. 替代 RAG QA 的本地 fallback
```

---

## 5. 设计原则

后续实现 embedding RAG 时，应继续遵守当前 Agent 工程原则：

```text
LLM 不直接执行代码；
Python 负责索引构建、检索、参数校验和 fallback；
RAG 只提供本地知识上下文；
工具执行仍必须经过 llm_router.py 或规则 router；
keyword retrieval 继续保留为 fallback；
测试必须能在无 API Key 环境下运行。
```

---

## 6. 推荐技术路线

当前推荐采用分阶段实现，而不是一次接入复杂向量数据库。

### 6.1 第一阶段：本地 JSON 向量缓存

建议第 61 / 62 课先实现最小可用版本：

```text
rag_embedding_indexer.py
rag_embedding_retriever.py
data/rag_index/embedding_index.json
```

优点：

```text
1. 项目复杂度低
2. 便于查看索引内容
3. 便于测试
4. 不需要立即引入 Chroma / FAISS
5. 适合教学项目逐步演进
```

### 6.2 第二阶段：hybrid retrieval

在 embedding retriever 稳定后，再实现：

```text
keyword score + embedding similarity score
```

对应模式：

```python
mode="hybrid"
```

### 6.3 第三阶段：可选向量数据库

只有当文档规模明显变大时，再考虑：

```text
Chroma
FAISS
其他本地向量数据库
```

当前阶段不建议立即引入复杂向量数据库。

---

## 7. embedding provider 选择

后续可以支持两类 provider。

### 7.1 API embedding provider

可能方案：

```text
OpenAI-compatible embedding API
DeepSeek 如后续提供 embedding 接口
其他云端 embedding 模型
```

优点：

```text
效果通常较好
实现简单
```

风险：

```text
需要 API Key
可能受网络影响
可能产生调用成本
测试不稳定
```

### 7.2 local / mock embedding provider

教学项目建议必须保留 mock / local fallback。

可选实现：

```text
简单 hashing embedding
TF-IDF 风格稀疏向量
固定 mock vector
```

用途：

```text
1. 无 API Key 时可跑测试
2. CI / 本地回归测试稳定
3. embedding retriever 逻辑可独立验证
```

---

## 8. 推荐新增模块

### 8.1 `rag_embedding_provider.py`

职责：

```text
统一生成 embedding
隐藏具体 provider 细节
支持 real / mock provider
```

建议接口：

```python
def embed_text(text: str) -> list[float]:
    ...


def embed_texts(texts: list[str]) -> list[list[float]]:
    ...
```

### 8.2 `rag_embedding_indexer.py`

职责：

```text
读取 documents/
调用 rag_document_loader.py 切块
为每个 chunk 生成 embedding
保存本地索引文件
```

建议接口：

```python
def build_embedding_index() -> dict:
    ...


def save_embedding_index(index: dict, index_path: Path) -> None:
    ...
```

### 8.3 `rag_embedding_retriever.py`

职责：

```text
读取本地 embedding index
为 query 生成 embedding
计算相似度
返回 top_k chunks
```

建议接口：

```python
def retrieve_relevant_chunks_by_embedding(
    query: str,
    top_k: int = 3,
    min_score: float = 0.0,
) -> list[dict]:
    ...
```

### 8.4 扩展 `rag_retrieval_router.py`

后续支持：

```python
mode="keyword"
mode="embedding"
mode="hybrid"
```

当前上层模块仍只调用：

```python
retrieve_chunks(...)
```

这样 `llm_agent_runner.py`、`llm_tool_selector.py`、`rag_qa.py` 不需要了解底层检索实现。

---

## 9. 推荐索引目录结构

建议新增：

```text
data/rag_index/
```

建议文件：

```text
data/rag_index/embedding_index.json
```

索引文件属于可再生成产物，默认不建议提交 Git。

`.gitignore` 可考虑加入：

```text
data/rag_index/
```

除非后续为了 demo 固定一个小型 mock index，否则不要提交真实 embedding index。

---

## 10. 推荐 embedding index JSON 结构

建议结构：

```json
{
  "version": 1,
  "provider": "mock",
  "embedding_dim": 128,
  "documents_dir": "documents",
  "chunks": [
    {
      "source": "ma_strategy_notes.md",
      "chunk_id": 0,
      "text": "...",
      "embedding": [0.01, 0.02, 0.03]
    }
  ]
}
```

必须保留：

```text
source
chunk_id
text
embedding
```

因为 RAG QA 输出参考片段时仍需要 source 和 text。

---

## 11. 相似度计算

第一版建议使用 cosine similarity。

原因：

```text
1. 实现简单
2. 适合 embedding 向量比较
3. 容易测试
```

建议新增工具函数：

```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    ...
```

需要处理边界情况：

```text
空向量
维度不一致
零向量
非法数值
```

---

## 12. config.py 建议新增配置

后续实现时，可以在 `config.py` 增加：

```python
RAG_INDEX_DIR = DATA_DIR / "rag_index"
RAG_EMBEDDING_INDEX_PATH = RAG_INDEX_DIR / "embedding_index.json"
DEFAULT_EMBEDDING_PROVIDER = "mock"
DEFAULT_RETRIEVAL_MODE = "keyword"
```

暂时不建议把默认检索模式直接改成：

```python
DEFAULT_RETRIEVAL_MODE = "embedding"
```

原因是 embedding 实现稳定前，默认仍应保持 keyword，避免破坏现有功能。

---

## 13. fallback 设计

embedding retrieval 失败时应 fallback 到 keyword retrieval。

推荐路径：

```text
mode="embedding"
→ embedding index 不存在 / 读取失败 / provider 失败
→ fallback keyword retrieval
→ trace 记录 fallback reason
```

hybrid retrieval 失败时：

```text
mode="hybrid"
→ embedding 部分失败
→ 仍使用 keyword 结果
```

不建议因为 embedding 失败导致整个 RAG QA 失败。

---

## 14. trace 设计

后续应在 trace 中展示：

```text
retrieval_mode
embedding_provider
index_path
retrieved_chunk_count
fallback_used
fallback_reason
chunk_score
```

这样用户可以理解：

```text
系统为什么引用这些本地片段
是否使用了 embedding
是否发生 fallback
```

---

## 15. 测试设计

后续至少需要新增以下测试文件：

```text
tests/test_rag_embedding_provider.py
tests/test_rag_embedding_indexer.py
tests/test_rag_embedding_retriever.py
```

测试原则：

```text
1. 默认不依赖真实 API Key
2. 默认使用 mock embedding provider
3. 使用 tmp_path 构建临时索引，避免污染 data/
4. 测试 cosine similarity 边界情况
5. 测试 index 文件不存在时的 fallback
6. 测试 rag_retrieval_router.py 的 mode="embedding"
```

---

## 16. 分课实现建议

### 第 61 课：实现最小 embedding index 构建器

新增：

```text
rag_embedding_provider.py
rag_embedding_indexer.py
tests/test_rag_embedding_provider.py
tests/test_rag_embedding_indexer.py
```

目标：

```text
读取 documents/
生成 mock embedding
保存 data/rag_index/embedding_index.json
测试通过
```

### 第 62 课：实现 embedding retriever

新增：

```text
rag_embedding_retriever.py
tests/test_rag_embedding_retriever.py
```

修改：

```text
rag_retrieval_router.py
config.py
```

目标：

```text
mode="embedding" 可用
embedding 失败 fallback keyword
默认检索模式仍保持 keyword
```

### 第 63 课：实现 hybrid retrieval

新增或修改：

```text
rag_retrieval_router.py
rag_embedding_retriever.py
rag_retriever.py
```

目标：

```text
关键词检索 + embedding 检索融合排序
```

---

## 17. 当前第 60 课结论

当前不立即实现 embedding。

本课只确认设计方向：

```text
1. 保留 keyword retrieval 作为默认和 fallback
2. 第一版 embedding index 使用本地 JSON 缓存
3. 第一版 embedding provider 使用 mock/local，真实 provider 后续可选
4. retrieval router 继续作为统一入口
5. embedding 失败不应中断 RAG QA
6. 后续再分课实现 indexer、retriever、hybrid retrieval
```
