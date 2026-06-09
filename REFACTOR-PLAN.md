> ## ✅ 完成记录（2026-06-09）—— 方案 A 已落地（`astro-migration` 分支）
>
> 全量迁移到 **Astro 6 + Vue islands** 完成并通过 `astro check`（0 error）+ 本地 `build`/`preview` 验证。`main` 分支保持原样、线上不受影响；**未部署**（等批准）。
>
> **做到的：** `.astro` 组件取代 build.py 的 f-string；`data/*.json` 接入 content collection + **Zod schema**（取代手写结构校验）；**构建期 KaTeX**（`src/lib/md.ts` 的 `katex.renderToString`，**删掉运行时 KaTeX JS**，字体自托管）；593 行 app.js 拆成 `src/lib/client/*` 多个作用域清晰的 ES 模块 + 4 个 Vue 岛屿；`dist/`/`node_modules/`/`.astro/` 移出仓库，改 GitHub Actions 部署；旧产物（index/chapters/*.html、search-index.js、build.py、deploy.ps1、assets/）已删除。
>
> **与原计划的务实偏离（有意为之）：**
> 1. **搜索没用 Pagefind**，而是构建期生成结构化 `/search-index.json`（端点）由岛屿 fetch。原因：Pagefind 只做全文，而 tags/exams/review 页面依赖每题的结构化字段（type/sources/tags），全文索引无法驱动这些分组页。比旧的 inline `window.SEARCH_INDEX` 更干净。
> 2. **岛屿划分**：search/tags/exams/review 这类「动态长列表」页用 **Vue 岛屿**（收益最大）；逐题的 quiz/study 控件与进度仪表盘用**框架无关的 ES 模块脚本**（章节页有上百题，若每题一个 Vue 实例反而是负优化）。这才是诚实的 islands 架构。
> 3. **KaTeX 用 `renderToString` 而非 remark/rehype-katex**：内容是 JSON 字符串不是 .md，没有 markdown 管线可挂；直接在 md 渲染器里渲染数学更直接。
> 4. **qid 算法逐字节复刻**（`src/lib/qid.ts` 的 sha1），锚点与 localStorage/Firestore 进度键全部沿用 → **老用户进度无缝继承**（已验证 ch01 锚点与旧站一致）。
> 5. Node 用便携版 24 LTS（winget 机器级 MSI 卡在提权）。`tools/`（挖题+校验脚本）保持原样，重排留作后续。
>
> **部署步骤（待你同意）：** 合并分支到 main → GitHub **Settings→Pages→Source 改为 "GitHub Actions"**（原为 main/root）→ Actions 自动 build+deploy。详见 README「Deploy」。
>
> ---

# i2dl-exam-qa 重构方案

> 目标:简化代码、提升可维护性/可读性、模块化。
> 背景:静态考试 Q&A 站,512 题 / 7 章,内容基本固定;唯一可变数据是用户学习进度(已用 localStorage + Firebase 解决)。考试还早(>1 个月),有时间做全量迁移。

---

## 1. 现状诊断

当前栈:Python stdlib 生成器(`build.py`)→ 静态 HTML + inline 搜索索引;前端 vanilla JS;Firebase 做进度云同步;GitHub Pages(main/root)托管。**优点是零构建依赖**,缺点集中在四处:

| 痛点 | 位置 | 问题 |
|---|---|---|
| HTML 用 Python f-string 拼接 | `build.py`(584 行) | 模板与逻辑耦合,改 UI 要在字符串里翻;无组件复用 |
| 前端单体 | `assets/app.js`(593 行 IIFE) | 搜索 / quiz / SRS / 进度 / Firebase 全在一个文件,无模块边界 |
| 构建产物进仓库 | `chapters/*.html`(~1MB)、`search-index.js`(393KB) | 每次 build 产生巨大 diff 噪声 |
| 一次性脚本堆积 | `tools/add_*.py`(~2600 行) | 挖题脚本(归档性质)与验证器混放 |

**结论先行:**
- **数据库 ❌** —— 内容静态,加后端 DB 等于凭空引入服务器/托管/运维;唯一可变的进度数据 Firestore 已覆盖。是负优化。
- **整站 Vue SPA 🟡** —— 牺牲静态托管的 SEO/首屏,对内容站是退步。Vue 只在「有状态的交互小岛」(进度环、学习控件)有价值。
- **Astro ✅** —— 为「内容为主 + 少量交互」的静态站设计,贴合本项目。Vue 以 island 形式嵌入,各取所长。

---

## 2. 方案 A:全量迁移到 Astro(推荐)

### 2.1 目标结构

```
src/
  content/
    config.ts          # Zod schema:章 / 知识点 / 题(类型校验,取代部分手写验证器)
    chapters/          # 你现有的 chNN_*.json 几乎原样搬入(content collection)
  components/
    QuestionCard.astro # 取代 build.py 的 render_question
    KnowledgePoint.astro
    SiteFooter.astro
    Topbar.astro
  islands/             # 仅交互处加载 JS
    Quiz.vue           # MC 选-检查-揭晓
    StudyControls.vue  # Reviewed / 错题本 / 笔记(localStorage)
    Progress.vue       # 进度环 + per-chapter mini-rings
    Search.vue / 或直接用 Pagefind UI
  pages/
    index.astro  tags.astro  exams.astro  review.astro
    chapters/[id].astro      # getStaticPaths 由 content collection 生成
  lib/
    store.ts           # 进度 store(localStorage,SRS 间隔)
    cloud.ts           # Firebase 同步(从 app.js 抽出)
astro.config.mjs       # remark-math + rehype-katex + pagefind
.github/workflows/deploy.yml
package.json
```

### 2.2 关键收益点

1. **`.astro` 组件取代 f-string** —— 可读性最大一笔。`render_question` / `render_kp` / `site_footer` 变成可复用组件。
2. **Content Collections + Zod** —— chapter JSON 加 schema,build 时类型校验 sources/freq/options/type;`check_*.py` 的结构校验融入其中。
3. **Islands 架构** —— 593 行 app.js 拆成 4 个作用域清晰的 island,JS 按需加载。需要响应式的进度/学习状态用 **Vue island**(这就是 Vue 的正确落点)。
4. **构建期渲染数学** —— `remark-math` + `rehype-katex` 在 build 时把 `$...$` 渲成 HTML,**删掉运行时 KaTeX JS**(性能 + 简化双赢)。
5. **搜索换 Pagefind** —— Astro 生态零配置静态全文搜索,取代手写 393KB inline 索引 + app.js 搜索逻辑。
6. **构建产物移出仓库** —— `dist/` 进 `.gitignore`,GitHub Actions 负责 build + deploy,仓库只剩源码,diff 干净。

### 2.3 代价(要清醒)

- **失去「零依赖」** —— 换来 Node/npm 工具链(`package.json` / lockfile / `node_modules` / CI)。本质是:**用工具链复杂度换模块化与可读性**。
- 学习/迁移成本:内容 JSON 基本机械搬运;前端逻辑(quiz/SRS/Firebase)需重写为组件;CSS 拆分 + scoped。
- 数学渲染从「运行时」改「构建期」,需验证现有公式全部通过 rehype-katex(可能有个别语法要修)。

### 2.4 迁移步骤(建议在 `astro-migration` 分支,主分支保持可用)

1. `npm create astro@latest`,接 Vue + Pagefind 集成;配 `astro.config.mjs`(base 路径 = `/i2dl-exam-qa`,remark-math/rehype-katex)。
2. 把 `data/chNN_*.json` 接入 content collection,写 `config.ts` 的 Zod schema;跑通类型校验。
3. 静态部分先行:`QuestionCard.astro` / `KnowledgePoint.astro` / footer / topbar / chapter 页 / index。先确保**无 JS 也能正确渲染内容 + 数学**。
4. 交互逐个补 island:Quiz → StudyControls → Progress → Search(Pagefind)。
5. 抽 `lib/cloud.ts`(Firebase),`config.js` 的公开配置迁为环境/常量。
6. 配 `.github/workflows/deploy.yml`(actions/deploy-pages);`dist/` 与旧 `chapters/*.html`、`search-index.js` 加进 `.gitignore`。
7. 视觉/功能逐页对照旧站验收 → 切换 Pages 源 → 上线。

### 2.5 工作量

约 **2–3 天**(分支并行,不影响现网)。风险中等,但有旧站兜底。

---

## 3. 方案 B:原地模块化(保零依赖,作为备选)

不换框架,只拆分。拿到约 80% 的可读性收益,零新依赖、零风险。

```
build/
  __init__.py
  templates.py   # 组件化的 HTML 片段(question / kp / footer / shell)
  render.py      # md_inline / md_block / plain
  search.py      # 搜索索引构建
build.py         # 只剩编排:读 manifest → 调 build 包 → 写文件
assets/js/
  store.js  search.js  quiz.js  study.js  cloud.js  main.js   # ES modules
assets/css/
  base.css hero.css question.css study.css ...                # 按区块拆 + @import
```

外加:`chapters/*.html`、`search-index.js` 移出仓库(本地 build / CI 生成);`tools/` 分成 `tools/mine/`(归档挖题脚本)和 `tools/check/`(验证器)。

工作量约 **半天**,适合「想立刻干净但不想引入 Node」的情况。

---

## 4. 推荐路径

考试还早 → **走方案 A(Astro)**,在 `astro-migration` 分支推进,主分支随时可用、可回退。
若中途想降风险,可先做方案 B 的「产物移出仓库 + tools 分类」这两步(与 A 不冲突,先清理仓库噪声)。

**不做:** 后端数据库;整站 Vue SPA。

---

## 5. 决策记录

- 数据库:否(内容静态,进度已由 Firestore 覆盖)。
- 框架:Astro(静态优先) + Vue island(仅有状态交互)。
- 数学:构建期渲染(rehype-katex),去运行时 KaTeX。
- 搜索:Pagefind 取代手写 inline 索引。
- 同步:沿用 Firebase,localStorage-first。
- 托管:GitHub Pages,改由 Actions 部署,`dist/` 不入库。
