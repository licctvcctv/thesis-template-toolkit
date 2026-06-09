# -*- coding: utf-8 -*-
"""Chapter 2 expansion paragraphs to insert before 2.7 本章小结."""


def blocks_before_27():
    """Return list of (heading_or_none, paragraph_text). None heading = body only."""
    return [
        ('Heading 3', '2.4.1 自博弈数据收集与轨迹表示'),
        (None, '自博弈（self-play）在本文中指：在同一历史情景 τ 下，让保守型、均衡型、激进型与记忆审计型四类智能体读取相同的价格向量 p_t、新闻集合 N_t 与记忆集合 M_t，分别输出结构化决策 d_t,i，再由评分模块根据真实下一期价格 p_t+1 计算收益反馈 r_t,i。该过程不依赖人工标注动作标签，轨迹由系统运行自然产生，并写入 runs 目录下各轮次 JSON，便于论文复现。'),
        (None, '将单智能体在一轮情景中的记录记为轨迹片段 τ_t,i = (s_t, d_t,i, r_t,i, m_t,i)，其中 s_t 为市场状态，d_t,i 包含 commodity、action、confidence、reason、evidence，m_t,i 为记忆教训与策略补丁。累计 36 轮形成轨迹序列，构成自进化算法的训练材料。'),
        (None, '（2.4）'),
        (None, '式（2.4）中，i 表示智能体编号，t 表示轮次，|A|=4 为智能体数量。系统在第 6 轮结束训练段后冻结 Prompt 版本进入测试段，因此轨迹自然划分为训练轨迹与测试轨迹，用于分别计算 trainingScore 与 testScore，避免“只在训练样本上调参”的假象。'),
        ('Heading 3', '2.4.2 Prompt 分层设计与 LLM 提示词模板'),
        (None, '本文 Prompt 分为系统层（system）与用户层（user JSON）。系统层固化角色定位、风控框架、决策原则、品种偏好、训练/测试段规则及审计官义务；用户层注入 tradingDay（date、regime、prices、news、retrievedMemory）、agent 画像、activeStrategyRules、baselineDecision，审计官额外注入 peerDecisions。该分层保证四类智能体输入可比，差异主要来自画像与记忆。'),
        (None, '训练段（轮次 1–6）允许输出 strategyPatchNotes，由引擎累积至 pendingLlmPatchNotes，并在第 4、7 轮（prompt 迭代轮）合并入 patchNotes，触发 prompt→promptv1→promptv2 版本跃迁；测试段（轮次 7–36）冻结 Prompt，禁止新增补丁，用于检验泛化。'),
        (None, '程序2-1 交易决策 LLM 系统提示（节选，与 server/llmClient.js buildMessages 一致）'),
        (None, '你是一个期货长线交易智能体，只能按交易日做决策。动作只能是 BUY、SELL、HOLD。每轮必须且只能选择一个交易品种（黄金期货/原油期货/大豆期货）。【角色定位】{mandate}【风控框架】{riskFramework}【决策原则】{decisionPrinciples}。训练段：输出 strategyPatchNotes；测试段：不要提出新的 strategyPatchNotes。'),
        (None, '程序2-2 记忆审计官附加约束（节选）'),
        (None, '你是记忆审计官：必须先审阅 peerDecisions 中其他智能体的观点，识别拥挤交易、一致预期与历史失败模式的相似性，再给出独立第三方动作。若三者高度同向，应优先质疑并倾向 HOLD 或反向减仓。'),
        (None, '程序2-3 用户层 JSON 必填字段（requiredJsonSchema）'),
        (None, 'commodity、action、confidence、reason、evidence、strategyPatchNotes（训练段）、memoryLesson。输出必须为单一 JSON 对象，便于 extractJsonObject 解析并写入 llmDecisionLedger。'),
        ('Heading 3', '2.4.3 长短期目标与 CoT 推理抽象'),
        (None, '短期目标写入当前轮 Prompt：控制单轮风险暴露、避免重复上一轮失败动作、在训练段给出可执行的 strategyPatchNotes。长期目标写入 patchNotes 与 memoryLesson：提高测试段相对得分、降低最大回撤、减少同类失败样本在相似 regime 下重复出现。'),
        (None, '本文不将大模型完整思维链原文写入论文（不可复现且冗长），而将 CoT 抽象为可记录的五个步骤：观察（读取价格/新闻/记忆）→ 判断（趋势与风险）→ 协商（审计官审阅 peerDecisions；辩论场统计共识/异议）→ 行动（输出 JSON 决策）→ 反思（评分后生成补丁）。DeepSeek 审计官可启用 thinking 模式提高审阅深度，但对外仍只暴露结构化 JSON。'),
        ('Heading 3', '2.4.4 评价指标与计分公式'),
        (None, '评价指标包括：单轮得分 Δscore、原始累计收益 Raw、相对 alpha 总分（四者减均值）、训练段/测试段得分、胜率 HitRate、最大回撤 MDD、动作分布与失败样本。单轮得分由相邻历史价格变化与动作方向、敞口系数 ω_i 决定，与 adapter/simulationEngine.js 中 calculateTradeScore 一致。'),
        (None, '（2.5）'),
        (None, '式（2.5）中，p_t 为合约在 t 期价格，d ∈ {+1,0,-1} 对应 BUY/HOLD/SELL 方向，ω_i 为智能体风险暴露系数（保守 0.65、均衡 0.9、激进 1.25、审计 0.75）。HOLD 在小幅波动时给稳定分，剧烈波动记机会损失。'),
        (None, '（2.6）'),
        (None, '式（2.6）中，Raw_i 为原始累计，Raw_mean 为四智能体均值，Score_i 为相对 alpha，用于排名（第一至第四）。训练段得分与测试段得分分别在 t≤6 与 t>6 的区间上求和。胜率 HitRate 为 Δscore>0 的轮次占比；MDD 为累计收益曲线峰值到谷值的最大回落。'),
        ('Heading 3', '2.4.5 大模型如何模拟期货交易与“协商”'),
        (None, '期货交易模拟通过“历史情景 + 真实月度价格 + 结构化决策”完成：LLM 不生成价格，只在大模型可见的 regime/news/memory 约束下选择品种与方向。谈判协商在实现上分为两层：一是审计官对三份 peerDecisions 的语义审阅（软协商）；二是 buildDebateRound 对四份决策做共识/异议/立场标注（硬聚合），形成可展示的辩论场文本，而非单一 LLM 直接输出 final_action。该设计兼顾可解释性与可复现性。'),
        (None, '36 轮完整 LLM 运行（runs/预设运行版本，DeepSeek-V4-Flash）中，四智能体共形成 144 条决策记录（36 轮×4），评分基于模型决策 ledger 与下一期本地真实价格。排名第 1–4 分别为激进型、均衡型、保守型、记忆审计型，与第六章实验结果一致。'),
    ]
