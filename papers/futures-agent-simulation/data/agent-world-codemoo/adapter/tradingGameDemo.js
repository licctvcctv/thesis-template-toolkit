const { ensureWorldState, ensureAvatar } = require('./worldModel');
const LocalDataLoader = require('./localDataLoader');

const DEFAULT_LLM_MODEL = 'deepseek-ai/DeepSeek-V4-Flash';
let localDataLoader = null;

function getLocalDataLoader() {
  if (!localDataLoader) {
    localDataLoader = new LocalDataLoader();
  }
  return localDataLoader;
}

const AGENT_IDS = Object.freeze([
  'conservative-hedger',
  'balanced-strategist',
  'aggressive-breakout',
  'memory-auditor'
]);

const AGENT_PROFILES = Object.freeze({
  'conservative-hedger': {
    role: '保守型',
    style: '先保本金。至少等待两个信号互相确认后，才逐步增加仓位。',
    commodityBias: 'gold',
    model: DEFAULT_LLM_MODEL,
    modelChain: [
      'deepseek-ai/DeepSeek-V4-Flash',
      'deepseek-ai/DeepSeek-V3.2',
      'deepseek-ai/DeepSeek-V3.1-Terminus',
      'Qwen/Qwen3.6-27B'
    ],
    color: '#38bdf8'
  },
  'balanced-strategist': {
    role: '均衡型',
    style: '综合宏观资讯、价格趋势和回撤压力，偏好分批进出。',
    commodityBias: 'crude_oil',
    model: DEFAULT_LLM_MODEL,
    modelChain: [
      'deepseek-ai/DeepSeek-V4-Flash',
      'deepseek-ai/DeepSeek-V3.2',
      'Qwen/Qwen3.6-35B-A3B',
      'deepseek-ai/DeepSeek-V3.1-Terminus'
    ],
    color: '#4ade80'
  },
  'aggressive-breakout': {
    role: '激进型',
    style: '当动量和资讯共振时提前行动，接受更大的阶段性回撤。',
    commodityBias: 'soybean',
    model: DEFAULT_LLM_MODEL,
    modelChain: [
      'deepseek-ai/DeepSeek-V4-Flash',
      'Qwen/Qwen3.6-35B-A3B',
      'deepseek-ai/DeepSeek-V3.2',
      'deepseek-ai/DeepSeek-V3.1-Terminus'
    ],
    color: '#f97316'
  },
  'memory-auditor': {
    role: '记忆审计',
    style: '质疑拥挤交易，检索相似失败案例，并在每一季后修正提示词。',
    commodityBias: 'gold',
    model: DEFAULT_LLM_MODEL,
    modelChain: [
      'deepseek-ai/DeepSeek-V4-Flash',
      'deepseek-ai/DeepSeek-V3.2',
      'moonshotai/Kimi-K2-Instruct-0905',
      'Qwen/Qwen3.6-35B-A3B'
    ],
    color: '#eab308'
  }
});

const COMMODITIES = Object.freeze([
  { id: 'gold', name: '黄金', symbol: 'GC', unit: '美元/盎司' },
  { id: 'soybean', name: '大豆', symbol: 'ZS', unit: '美分/蒲式耳' },
  { id: 'crude_oil', name: '原油', symbol: 'CL', unit: '美元/桶' }
]);

const STATIONS = Object.freeze([
  { id: 'news', label: '资讯采集台', x: 4, y: 11, locationId: 'store', activity: '抓取市场新闻' },
  { id: 'memory', label: '记忆档案馆', x: 25, y: 21, locationId: 'library', activity: '检索相似历史案例' },
  { id: 'price', label: '价格趋势墙', x: 24, y: 3, locationId: 'home_ne', activity: '读取价格趋势' },
  { id: 'risk', label: '风险控制室', x: 4, y: 21, locationId: 'home_sw', activity: '检查回撤边界' },
  { id: 'debate', label: '智能体辩论场', x: 14, y: 14, locationId: null, activity: '辩论信号质量' },
  { id: 'trade', label: '交易执行门', x: 11, y: 3, locationId: 'office', activity: '生成交易指令' }
]);

const ROUNDS = Object.freeze([
  {
    date: '2016-02-11',
    regime: '避险冲击',
    prices: { gold: 1247, soybean: 878, crude_oil: 26.2 },
    news: [
      '全球股市抛售推动资金流向黄金避险。',
      '美国大豆出口检验量低于上一季节奏。',
      '原油库存上升，需求预测被下调。'
    ],
    memory: [
      '2011 欧债压力：波动率上升后，黄金避险行情延续。',
      '2014 原油供给冲击：库存可信度下降时，过早做多受到惩罚。',
      '2015 谷物过剩：出口节奏偏弱会压制反弹高度。'
    ],
    scoreboard: { conservative: 0.8, balanced: 0.3, aggressive: -0.4, auditor: 0.5 }
  },
  {
    date: '2016-09-28',
    regime: 'OPEC减产协议',
    prices: { gold: 1322, soybean: 1035, crude_oil: 47.8 },
    news: [
      'OPEC达成限产协议，原油价格从低点反弹。',
      '黄金因美联储加息预期升温而承压。',
      '大豆受良好天气和丰收预期压制。'
    ],
    memory: [
      '2008 OPEC减产：价格支撑短暂，需求才是决定性因素。',
      '2013 黄金加息冲击：实际收益率上行压制无息资产。',
      '2012 大豆天气行情：供给端意外才能打破平衡。'
    ],
    scoreboard: { conservative: 1.0, balanced: 0.8, aggressive: 1.2, auditor: 0.7 }
  },
  {
    date: '2017-06-15',
    regime: '温和复苏',
    prices: { gold: 1215, soybean: 968, crude_oil: 45.6 },
    news: [
      '全球经济温和复苏，风险偏好上升。',
      '美联储缓慢加息路径压制黄金。',
      '大豆出口需求稳定，但南美产量恢复。'
    ],
    memory: [
      '2016 黄金底部震荡：低波动环境下缺乏方向性驱动。',
      '2014 大豆供给扩张：南美产量增加持续压制价格。',
      '2015 原油底部震荡：OPEC市场份额战略拖累价格。'
    ],
    scoreboard: { conservative: 1.4, balanced: 1.2, aggressive: 1.5, auditor: 1.1 }
  },
  {
    date: '2018-05-09',
    regime: '贸易摩擦',
    prices: { gold: 1313, soybean: 1018, crude_oil: 71.1 },
    news: [
      '关税消息增加农产品流向的不确定性。',
      '地缘供给风险升温后，油价继续走高。',
      '尽管消息波动加大，黄金仍维持区间震荡。'
    ],
    memory: [
      '2012 干旱行情：供给担忧叠加资金流入时，大豆上涨加速。',
      '2016 原油反弹：备用产能偏紧时，趋势得以延续。',
      '2017 黄金震荡：单靠消息风险不足以突破阻力。'
    ],
    scoreboard: { conservative: 1.2, balanced: 1.4, aggressive: 2.1, auditor: 1.0 }
  },
  {
    date: '2018-12-20',
    regime: '贸易战升级',
    prices: { gold: 1262, soybean: 916, crude_oil: 44.2 },
    news: [
      '中美贸易摩擦升级，大豆出口几乎停滞。',
      '原油价格暴跌，OPEC紧急会议讨论减产。',
      '股市大幅波动，黄金未能有效避险。'
    ],
    memory: [
      '2018 大豆贸易战：中国关税直接切断美国出口渠道。',
      '2014-2016 原油崩盘：供给过剩时需求故事失效。',
      '2013 黄金失灵：美元流动性危机中所有资产被抛售。'
    ],
    scoreboard: { conservative: 1.8, balanced: 1.1, aggressive: -0.5, auditor: 2.0 }
  },
  {
    date: '2019-08-05',
    regime: '降息周期开启',
    prices: { gold: 1487, soybean: 862, crude_oil: 55.8 },
    news: [
      '美联储宣布降息，黄金突破关键阻力。',
      '贸易摩擦持续压制大豆出口前景。',
      '原油受制于全球经济增长放缓。'
    ],
    memory: [
      '2016 黄金反弹：降息预期提振避险需求。',
      '2012 大豆反弹：天气炒作叠加出口恢复。',
      '2019 原油疲软：需求担忧压倒供给端支撑。'
    ],
    scoreboard: { conservative: 2.4, balanced: 2.2, aggressive: 1.8, auditor: 2.6 }
  },
  {
    date: '2020-01-15',
    regime: '第一阶段协议',
    prices: { gold: 1548, soybean: 935, crude_oil: 58.4 },
    news: [
      '中美签署第一阶段贸易协议，大豆出口恢复预期。',
      '黄金在贸易缓和后仍保持强势。',
      '原油需求预期改善，但供给充足。'
    ],
    memory: [
      '2018 大豆贸易协议：消息落地后价格反弹有限。',
      '2019 黄金持续走强：地缘不确定性提供支撑。',
      '2016 原油反弹：协议利好需要库存数据确认。'
    ],
    scoreboard: { conservative: 2.8, balanced: 2.9, aggressive: 2.5, auditor: 3.0 }
  },
  {
    date: '2020-04-20',
    regime: '疫情错位',
    prices: { gold: 1693, soybean: 832, crude_oil: -37.6 },
    news: [
      '近月原油合约因库容压力崩塌。',
      '各国央行扩大紧急流动性计划。',
      '食品供应链出现物流摩擦，但需求能见度仍然很低。'
    ],
    memory: [
      '2008 流动性冲击：被动抛售会扭曲正常宏观信号。',
      '2015 原油升水结构：合约机制比现货叙事更重要。',
      '2019 大豆反复震荡：物流消息需要价差确认。'
    ],
    scoreboard: { conservative: 2.2, balanced: 0.7, aggressive: -1.8, auditor: 2.4 }
  },
  {
    date: '2020-08-07',
    regime: '黄金历史新高',
    prices: { gold: 2063, soybean: 928, crude_oil: 41.5 },
    news: [
      '黄金首次突破2000美元，创历史新高。',
      '美联储无限量QE推动大宗商品反弹。',
      '大豆出口需求强劲，中国大量采购。'
    ],
    memory: [
      '2011 黄金历史高点：情绪极值往往是反转信号。',
      '2008 QE效应：流动性注入推升所有资产价格。',
      '2012 大豆出口潮：中国需求可以改变供需平衡。'
    ],
    scoreboard: { conservative: 3.5, balanced: 3.2, aggressive: 2.8, auditor: 3.6 }
  },
  {
    date: '2021-05-12',
    regime: '通胀交易',
    prices: { gold: 1832, soybean: 1498, crude_oil: 65.3 },
    news: [
      '大宗商品全面上涨，通胀交易盛行。',
      '大豆受天气和出口双重推动。',
      '黄金从高位回落，实际收益率压力增大。'
    ],
    memory: [
      '2011 大宗牛市：通胀预期可以自我强化。',
      '2008 通胀见顶：政策收紧往往终结趋势。',
      '2014 黄金回调：实际收益率回升是核心压力。'
    ],
    scoreboard: { conservative: 3.8, balanced: 4.2, aggressive: 4.5, auditor: 3.9 }
  },
  {
    date: '2021-11-08',
    regime: '紧缩预期',
    prices: { gold: 1822, soybean: 1298, crude_oil: 81.2 },
    news: [
      '美联储开始缩减QE，收紧预期升温。',
      '原油需求恢复推动价格走高。',
      '大豆从高位回落，但仍处历史高位区间。'
    ],
    memory: [
      '2013 缩减恐慌：政策转向往往引发剧烈波动。',
      '2018 原油高位：需求见顶担忧随后出现。',
      '2011 黄金回撤：流动性收紧预期打压价格。'
    ],
    scoreboard: { conservative: 4.0, balanced: 4.3, aggressive: 3.9, auditor: 4.2 }
  },
  {
    date: '2022-03-08',
    regime: '供给冲击',
    prices: { gold: 2043, soybean: 1689, crude_oil: 123.7 },
    news: [
      '能源供给担忧触发大宗商品全面挤压。',
      '粮食安全担忧抬升谷物和油籽风险溢价。',
      '通胀与地缘风险共振，黄金快速拉升。'
    ],
    memory: [
      '2011 黄金急涨：抛物线式避险行情会惩罚追高入场。',
      '2008 原油尖峰：趋势跟随有效，直到波动率翻倍。',
      '2012 大豆稀缺：强基差确认期货强势。'
    ],
    scoreboard: { conservative: 2.6, balanced: 3.0, aggressive: 3.7, auditor: 3.2 }
  },
  {
    date: '2022-06-15',
    regime: '激进加息',
    prices: { gold: 1836, soybean: 1485, crude_oil: 118.5 },
    news: [
      '美联储加息75个基点，美元走强压制黄金。',
      '原油因地缘冲突维持高位震荡。',
      '大豆受天气支撑，但加息压力开始显现。'
    ],
    memory: [
      '2018 加息周期：美元走强是商品最大逆风。',
      '2022 黄金回调：实际收益率快速上升打压价格。',
      '2012 天气行情：供给端炒作往往快于需求破坏。'
    ],
    scoreboard: { conservative: 3.2, balanced: 3.5, aggressive: 2.8, auditor: 3.6 }
  },
  {
    date: '2022-11-10',
    regime: '通胀见顶',
    prices: { gold: 1768, soybean: 1432, crude_oil: 88.2 },
    news: [
      '美国CPI低于预期，市场押注加息放缓。',
      '黄金反弹，但上行空间仍然受限。',
      '原油因需求衰退担忧回落。'
    ],
    memory: [
      '2019 降息预期：政策转向初期波动率上升。',
      '2008 需求破坏：通胀见顶后商品往往大幅回落。',
      '2016 黄金底部：实际收益率是关键驱动。'
    ],
    scoreboard: { conservative: 3.6, balanced: 3.8, aggressive: 3.2, auditor: 4.0 }
  },
  {
    date: '2023-05-03',
    regime: '银行业危机',
    prices: { gold: 2052, soybean: 1468, crude_oil: 73.5 },
    news: [
      '美国地区银行危机推动避险需求。',
      '黄金再次测试2000美元上方阻力。',
      '原油受制于经济衰退担忧。'
    ],
    memory: [
      '2008 银行危机：流动性紧张引发全面抛售。',
      '2020 黄金避险：系统性风险中黄金表现优异。',
      '2016 原油低迷：需求故事在危机中失效。'
    ],
    scoreboard: { conservative: 4.2, balanced: 3.9, aggressive: 3.5, auditor: 4.5 }
  },
  {
    date: '2023-10-05',
    regime: '高利率更久',
    prices: { gold: 1831, soybean: 1278, crude_oil: 82.3 },
    news: [
      '实际收益率上行压制无息资产。',
      '需求担忧抵消减产支撑，原油回落。',
      '大豆收获压力遇上出口需求不均衡。'
    ],
    memory: [
      '2018 利率重定价：实际收益率上升时，黄金向下破位。',
      '2022 原油反转：需求预期转弱后，减产支撑失效。',
      '2020 收获压力：大豆反弹需要出口确认。'
    ],
    scoreboard: { conservative: 3.3, balanced: 3.4, aggressive: 2.9, auditor: 3.8 }
  },
  {
    date: '2024-04-12',
    regime: '地缘风险溢价',
    prices: { gold: 2385, soybean: 1185, crude_oil: 87.6 },
    news: [
      '中东局势紧张，原油风险溢价上升。',
      '央行购金推动黄金持续走强。',
      '大豆受南美天气和出口竞争影响。'
    ],
    memory: [
      '2022 地缘冲击：事件驱动行情来得快去得也快。',
      '2020 央行购金：官方需求是长期支撑因素。',
      '2018 南美天气：天气炒作窗口期短暂。'
    ],
    scoreboard: { conservative: 4.0, balanced: 4.3, aggressive: 4.6, auditor: 4.1 }
  },
  {
    date: '2024-09-18',
    regime: '降息周期重启',
    prices: { gold: 2582, soybean: 1025, crude_oil: 71.2 },
    news: [
      '美联储启动降息，黄金创历史新高。',
      '大豆因供给充足和需求疲软走弱。',
      '原油因OPEC增产和经济放缓承压。'
    ],
    memory: [
      '2019 降息效应：实际收益率下降提振黄金。',
      '2016 大豆弱势：供给过剩需要天气冲击扭转。',
      '2020 原油需求：经济放缓预期压制价格。'
    ],
    scoreboard: { conservative: 4.5, balanced: 4.6, aggressive: 4.2, auditor: 4.8 }
  },
  {
    date: '2025-01-17',
    regime: '软着陆争论',
    prices: { gold: 2716, soybean: 1042, crude_oil: 78.5 },
    news: [
      '黄金在多月机构买盘后进入整理。',
      '供应预估仍较宽松，大豆走势偏弱。',
      '宏观需求与航运风险相互拉扯，原油维持区间。'
    ],
    memory: [
      '2020 黄金整理：回撤守住前高后，趋势仍然延续。',
      '2016 大豆筑底：偏弱供给故事需要天气冲击才能反转。',
      '2023 原油区间：实物平衡转松后，地缘风险溢价消退。'
    ],
    scoreboard: { conservative: 4.1, balanced: 4.2, aggressive: 3.5, auditor: 4.4 }
  },
  {
    date: '2025-04-22',
    regime: '关税冲击',
    prices: { gold: 3125, soybean: 965, crude_oil: 62.8 },
    news: [
      '全球关税政策不确定性引发市场动荡。',
      '黄金因避险需求飙升至3000美元上方。',
      '大豆出口受关税影响，需求前景恶化。'
    ],
    memory: [
      '2018 关税冲击：贸易壁垒改变全球供应链。',
      '2020 避险飙升：系统性风险中资金涌入黄金。',
      '2019 大豆困境：出口渠道受阻压制价格。'
    ],
    scoreboard: { conservative: 4.8, balanced: 4.5, aggressive: 3.8, auditor: 5.0 }
  },
  {
    date: '2025-07-15',
    regime: ' supply 重构',
    prices: { gold: 3285, soybean: 1125, crude_oil: 75.3 },
    news: [
      '全球供应链重构加速，大宗商品需求格局变化。',
      '黄金央行购金持续，新兴市场去美元化趋势。',
      '大豆出口恢复，南美产量不及预期。'
    ],
    memory: [
      '2021 供应链瓶颈：需求转移推升区域溢价。',
      '2024 央行购金：官方需求成为价格底线。',
      '2012 南美天气：产量意外支撑全球价格。'
    ],
    scoreboard: { conservative: 5.2, balanced: 4.9, aggressive: 4.5, auditor: 5.3 }
  },
  {
    date: '2025-10-08',
    regime: '能源转型',
    prices: { gold: 3156, soybean: 1085, crude_oil: 68.5 },
    news: [
      '新能源替代预期压制长期原油需求前景。',
      '生物柴油政策提振大豆需求。',
      '黄金高位震荡，市场等待下一催化。'
    ],
    memory: [
      '2020 能源转型：结构性需求变化是长期趋势。',
      '2022 生物燃料：政策驱动可以改变供需平衡。',
      '2023 黄金整理：缺乏催化时价格回归区间。'
    ],
    scoreboard: { conservative: 5.4, balanced: 5.1, aggressive: 4.7, auditor: 5.5 }
  },
  {
    date: '2026-01-12',
    regime: '新年开局',
    prices: { gold: 3425, soybean: 1158, crude_oil: 82.1 },
    news: [
      '新年机构资金重新配置，黄金获大量流入。',
      '大豆天气炒作窗口开启，市场关注产区情况。',
      'OPEC+延长减产协议，原油获得支撑。'
    ],
    memory: [
      '2021 年初配置：资金流动可以驱动趋势形成。',
      '2012 天气行情：供给端意外往往在一季度发酵。',
      '2016 OPEC减产：供给管理短期内有效支撑价格。'
    ],
    scoreboard: { conservative: 5.6, balanced: 5.4, aggressive: 5.0, auditor: 5.7 }
  }
]);

const ACTIONS_BY_AGENT = Object.freeze({
  'conservative-hedger': ['BUY', 'BUY', 'HOLD', 'SELL', 'SELL', 'HOLD', 'HOLD', 'SELL', 'BUY', 'HOLD', 'SELL', 'BUY', 'SELL', 'HOLD', 'BUY', 'HOLD', 'BUY', 'BUY', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'SELL', 'BUY', 'HOLD', 'BUY', 'HOLD', 'SELL', 'BUY', 'HOLD', 'BUY', 'SELL', 'HOLD', 'BUY', 'HOLD', 'HOLD'],
  'balanced-strategist': ['HOLD', 'BUY', 'HOLD', 'BUY', 'SELL', 'BUY', 'HOLD', 'SELL', 'BUY', 'BUY', 'SELL', 'BUY', 'SELL', 'HOLD', 'BUY', 'SELL', 'BUY', 'BUY', 'HOLD', 'SELL', 'HOLD', 'BUY', 'SELL', 'BUY', 'SELL', 'BUY', 'HOLD', 'SELL', 'BUY', 'HOLD', 'BUY', 'SELL', 'HOLD', 'BUY', 'SELL', 'HOLD'],
  'aggressive-breakout': ['BUY', 'BUY', 'HOLD', 'HOLD', 'SELL', 'BUY', 'BUY', 'SELL', 'HOLD', 'BUY', 'SELL', 'HOLD', 'SELL', 'BUY', 'BUY', 'SELL', 'BUY', 'BUY', 'SELL', 'SELL', 'BUY', 'HOLD', 'SELL', 'BUY', 'SELL', 'BUY', 'BUY', 'SELL', 'HOLD', 'BUY', 'BUY', 'SELL', 'HOLD', 'BUY', 'SELL', 'HOLD'],
  'memory-auditor': ['HOLD', 'HOLD', 'HOLD', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'SELL', 'SELL', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD']
});

const TOOL_BY_STATION = Object.freeze({
  news: { name: '资讯抓取', icon: 'N' },
  memory: { name: '记忆检索', icon: 'M' },
  price: { name: '趋势读取', icon: 'P' },
  risk: { name: '风险校验', icon: 'R' },
  debate: { name: '智能体辩论', icon: 'D' },
  trade: { name: '交易指令', icon: 'T' }
});

const STATION_OFFSET_BY_AGENT = Object.freeze({
  'conservative-hedger': 0,
  'balanced-strategist': 2,
  'aggressive-breakout': 1,
  'memory-auditor': 3
});

const EXPOSURE_SCALE_BY_AGENT = Object.freeze({
  'conservative-hedger': 0.65,
  'balanced-strategist': 0.9,
  'aggressive-breakout': 1.25,
  'memory-auditor': 0.75
});

const TRAINING_TRADE_COUNT = 3;

function clampRoundIndex(roundIndex) {
  const numeric = Number.isFinite(roundIndex) ? Math.floor(roundIndex) : 0;
  const wrapped = numeric % ROUNDS.length;
  return wrapped < 0 ? wrapped + ROUNDS.length : wrapped;
}

function rethemeWorld(world) {
  const names = {
    store: '资讯采集台',
    library: '记忆档案馆',
    home_ne: '价格趋势墙',
    home_sw: '风险控制室',
    office: '交易执行门',
    cafe: '策略休息区',
    home_nw: '研究工作室'
  };
  if (!Array.isArray(world?.locations)) return;
  for (const location of world.locations) {
    if (names[location.id]) location.name = names[location.id];
  }
}

function actionLabel(action) {
  return action === 'BUY' ? '买入' : action === 'SELL' ? '卖出' : '观望';
}

function normalizeAction(action) {
  const raw = String(action || '').trim().toUpperCase();
  return raw === 'BUY' || raw === 'SELL' || raw === 'HOLD' ? raw : 'HOLD';
}

function clampConfidence(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 55;
  return Math.max(1, Math.min(99, Math.round(numeric)));
}

function buildDecision({ agentId, round, roundIndex }) {
  const profile = AGENT_PROFILES[agentId];
  const action = ACTIONS_BY_AGENT[agentId][roundIndex % ROUNDS.length];
  const commodity = COMMODITIES.find(item => item.id === profile.commodityBias) || COMMODITIES[0];
  const price = round.prices[commodity.id];
  const confidence = Math.max(
    42,
    Math.min(92, 58 + roundIndex * 5 + (action === 'HOLD' ? -6 : 7))
  );
  const exposure =
    action === 'BUY' ? '+1 做多' :
    action === 'SELL' ? '-1 减仓/反手' :
    '空仓观察';

  return {
    action,
    actionLabel: actionLabel(action),
    commodity: commodity.id,
    symbol: commodity.symbol,
    price,
    confidence,
    source: 'simulated',
    exposure,
    reason: `${actionLabel(action)} ${commodity.name}（${commodity.symbol}）：价格 ${price}，结合“${round.regime}”资讯、历史相似案例和${profile.role}风险规则后给出该动作。`,
    evidence: [
      round.news[roundIndex % round.news.length],
      `${commodity.name}趋势检查点：${price} ${commodity.unit}`,
      round.memory[(roundIndex + 1) % round.memory.length]
    ]
  };
}

function buildMemory({ agentId, round, roundIndex }) {
  const profile = AGENT_PROFILES[agentId];
  return {
    archive: profile.commodityBias,
    retrieved: round.memory.map((text, index) => ({
      id: `${agentId}-m${roundIndex}-${index}`,
      date: ROUNDS[Math.max(0, roundIndex - index)]?.date || round.date,
      weight: Number((0.86 - index * 0.13).toFixed(2)),
      text
    })),
    lesson: `${profile.role}将“${round.regime}”与历史记忆“${round.memory[0]}”进行类比`
  };
}

function buildStrategy({ agentId, roundIndex }) {
  const profile = AGENT_PROFILES[agentId];
  const season = Math.floor(roundIndex / 3) + 1;
  const patchNotes = [
    `第 ${season} 季：提高与当前市场阶段相似的历史案例权重`,
    profile.role === '激进型'
      ? '波动冲击后限制加仓次数'
      : '改变仓位前必须得到记忆模块确认'
  ];

  return {
    promptVersion: season,
    style: profile.style,
    patchNotes,
    nextMutation: roundIndex % 3 === 2
      ? '本轮验证结束后重写信号权重'
      : '继续收集证据，暂不改写提示词'
  };
}

function stationFor(agentId, roundIndex) {
  const agentOffset = STATION_OFFSET_BY_AGENT[agentId] ?? 0;
  return STATIONS[(roundIndex + agentOffset) % STATIONS.length];
}

function roundWithLocalPrices(round, loader) {
  const prices = { ...round.prices };
  const realPrices = {};
  let realCount = 0;

  if (loader?.isLoaded?.()) {
    for (const commodity of COMMODITIES) {
      const price = loader.getPriceAtDate(commodity.id, round.date);
      if (Number.isFinite(price)) {
        prices[commodity.id] = Number(price);
        realPrices[commodity.id] = Number(price);
        realCount += 1;
      }
    }
  }

  return {
    ...round,
    prices,
    dataSource:
      realCount === COMMODITIES.length ? 'local-real' :
      realCount > 0 ? 'mixed-real-scenario' :
      'scenario',
    realPrices
  };
}

function getHistoricalRounds() {
  try {
    const loader = getLocalDataLoader();
    return ROUNDS.map(round => roundWithLocalPrices(round, loader));
  } catch (error) {
    console.warn('[trading-demo] historical data unavailable:', error.message);
    return ROUNDS.map(round => ({ ...round, prices: { ...round.prices }, dataSource: 'scenario', realPrices: {} }));
  }
}

function clampScore(value) {
  return Number(Math.max(-18, Math.min(22, value)).toFixed(2));
}

function calculateTradeScore({ action, currentPrice, nextPrice, exposureScale }) {
  if (!Number.isFinite(currentPrice) || !Number.isFinite(nextPrice)) return 0;
  const priceMovePct = ((nextPrice - currentPrice) / Math.max(1, Math.abs(currentPrice))) * 100;
  if (action === 'HOLD') {
    return clampScore(Math.abs(priceMovePct) < 3 ? 0.6 : -Math.abs(priceMovePct) * 0.08);
  }
  const direction = action === 'SELL' ? -1 : 1;
  return clampScore(direction * priceMovePct * exposureScale);
}

function recommendationFor({ totalScore, testScore, maxDrawdown }) {
  if (testScore >= 4 && totalScore > 2 && maxDrawdown <= 18) {
    return {
      status: 'adopt',
      label: '采纳',
      text: '测试段仍能贡献收益，下一轮提高该策略采样概率。'
    };
  }
  if (totalScore < -4 || maxDrawdown > 18) {
    return {
      status: 'remove',
      label: '淘汰',
      text: '累计表现中收益/回撤不达标，下一轮降低权重或移除。'
    };
  }
  return {
    status: 'watch',
    label: '观察',
    text: '表现尚可但测试段优势不够稳定，保留并继续修正 prompt。'
  };
}

function average(values) {
  const nums = values.filter(Number.isFinite);
  if (!nums.length) return 0;
  return nums.reduce((sum, value) => sum + value, 0) / nums.length;
}

function buildAgentActionDistribution(trades) {
  const distribution = { BUY: 0, SELL: 0, HOLD: 0 };
  for (const trade of trades) {
    if (Object.prototype.hasOwnProperty.call(distribution, trade.action)) {
      distribution[trade.action] += 1;
    }
  }
  return distribution;
}

function buildFailurePoints(trades) {
  return trades
    .filter(trade => Number(trade.scoreDelta || 0) < 0)
    .slice()
    .sort((a, b) => Number(a.scoreDelta || 0) - Number(b.scoreDelta || 0))
    .slice(0, 3)
    .map(trade => ({
      round: Number(trade.index || 0) + 1,
      date: trade.date,
      exitDate: trade.exitDate,
      regime: trade.regime,
      action: trade.action,
      actionLabel: trade.actionLabel || actionLabel(trade.action),
      symbol: trade.symbol,
      scoreDelta: Number(Number(trade.scoreDelta || 0).toFixed(2)),
      entry: trade.entry,
      exit: trade.exit,
      reason: `第 ${Number(trade.index || 0) + 1} 轮 ${trade.actionLabel || actionLabel(trade.action)} ${trade.symbol} 后记 ${Number(trade.scoreDelta || 0).toFixed(2)} 分。`
    }));
}

function buildFailureSummary({ role, trades, failures, worstTrade }) {
  if (!trades.length) return `${role} 尚未形成可评分交易，等待更多轮次。`;
  if (!failures.length) return `${role} 当前没有亏损交易，重点观察后续轮次的稳定性。`;
  return `${role} 累计 ${failures.length}/${trades.length} 轮失分，最大失分来自第 ${Number(worstTrade.index || 0) + 1} 轮 ${worstTrade.actionLabel || actionLabel(worstTrade.action)} ${worstTrade.symbol}。`;
}

function buildRepairPlan({ item, failures }) {
  const plans = [];
  if (failures.length > 0) plans.push('把最大失分回合加入记忆检索，遇到相似价格结构时先降权。');
  if (Number(item.maxDrawdown || 0) > 8) plans.push('降低连续同向开仓权重，先控制回撤再追求收益。');
  if (Number(item.testScore || 0) < Number(item.trainingScore || 0)) plans.push('提高测试段样本权重，避免只适配前段行情。');
  if (!plans.length) plans.push('保留当前策略骨架，继续累计样本后再调整 prompt。');
  return plans.slice(0, 2).join(' ');
}

function buildAgentBreakdown(item) {
  const trades = Array.isArray(item.trades) ? item.trades : [];
  const failures = trades.filter(trade => Number(trade.scoreDelta || 0) < 0);
  const wins = trades.filter(trade => Number(trade.scoreDelta || 0) > 0);
  const worstTrade = failures
    .slice()
    .sort((a, b) => Number(a.scoreDelta || 0) - Number(b.scoreDelta || 0))[0] || null;
  const bestTrade = trades
    .slice()
    .sort((a, b) => Number(b.scoreDelta || 0) - Number(a.scoreDelta || 0))[0] || null;

  return {
    agentId: item.agentId,
    role: item.role,
    style: item.style,
    symbol: item.symbol,
    totalScore: Number(item.totalScore || 0),
    rawScore: Number(item.rawScore ?? item.totalScore ?? 0),
    trainingScore: Number(item.trainingScore || 0),
    testScore: Number(item.testScore || 0),
    maxDrawdown: Number(item.maxDrawdown || 0),
    hitRate: Number(item.hitRate || 0),
    tradeCount: trades.length,
    winCount: wins.length,
    lossCount: failures.length,
    failureRate: trades.length ? Number(((failures.length / trades.length) * 100).toFixed(1)) : 0,
    actionDistribution: buildAgentActionDistribution(trades),
    recommendation: item.recommendation?.status || 'watch',
    recommendationLabel: item.recommendation?.label || '观察',
    recommendationText: item.recommendation?.text || '',
    bestTrade: bestTrade ? {
      round: Number(bestTrade.index || 0) + 1,
      actionLabel: bestTrade.actionLabel || actionLabel(bestTrade.action),
      symbol: bestTrade.symbol,
      scoreDelta: Number(Number(bestTrade.scoreDelta || 0).toFixed(2))
    } : null,
    worstTrade: worstTrade ? {
      round: Number(worstTrade.index || 0) + 1,
      actionLabel: worstTrade.actionLabel || actionLabel(worstTrade.action),
      symbol: worstTrade.symbol,
      scoreDelta: Number(Number(worstTrade.scoreDelta || 0).toFixed(2))
    } : null,
    failurePoints: buildFailurePoints(trades),
    failureSummary: buildFailureSummary({ role: item.role, trades, failures, worstTrade }),
    repairPlan: buildRepairPlan({ item, failures })
  };
}

function buildEvaluationAnalysis({ rankings, completedTradeCount, rounds }) {
  const ranked = Array.isArray(rankings) ? rankings.slice() : [];
  const best = ranked[0] || null;
  const worst = ranked[ranked.length - 1] || null;
  const allTrades = ranked.flatMap(item => Array.isArray(item.trades) ? item.trades : []);
  const actionDistribution = { BUY: 0, SELL: 0, HOLD: 0 };
  for (const trade of allTrades) {
    if (Object.prototype.hasOwnProperty.call(actionDistribution, trade.action)) {
      actionDistribution[trade.action] += 1;
    }
  }

  const topTrades = Array.isArray(best?.trades) ? best.trades : [];
  const topEquityCurve = [
    {
      date: rounds[0]?.date || '--',
      value: 0,
      phase: 'start',
      label: '起点'
    },
    ...topTrades.map(trade => ({
      date: trade.exitDate || trade.date,
      value: Number(Number(trade.equity || 0).toFixed(2)),
      phase: trade.phase,
      action: trade.action,
      scoreDelta: Number(Number(trade.scoreDelta || 0).toFixed(2))
    }))
  ];

  const trainingLeaders = ranked
    .slice()
    .sort((a, b) => Number(b.trainingScore || 0) - Number(a.trainingScore || 0));
  const testLeaders = ranked
    .slice()
    .sort((a, b) => Number(b.testScore || 0) - Number(a.testScore || 0));
  const averageHitRate = Number(average(ranked.map(item => Number(item.hitRate))).toFixed(1));
  const averageDrawdown = Number(average(ranked.map(item => Number(item.maxDrawdown))).toFixed(2));
  const alphaSpread = Number((Number(best?.totalScore || 0) - Number(worst?.totalScore || 0)).toFixed(2));
  const bestTrain = trainingLeaders[0] || best;
  const bestTest = testLeaders[0] || best;
  const worstDrawdown = ranked
    .slice()
    .sort((a, b) => Number(b.maxDrawdown || 0) - Number(a.maxDrawdown || 0))[0] || worst;

  const conclusions = [];
  if (best) {
    conclusions.push(`${best.role}当前综合得分最高，适合作为下一轮策略采样的主候选。`);
  }
  if (bestTrain && bestTest) {
    conclusions.push(`训练段优势来自${bestTrain.role}，测试段表现最好的是${bestTest.role}，用于判断策略是否泛化。`);
  }
  if (worstDrawdown) {
    conclusions.push(`${worstDrawdown.role}最大回撤为 ${Number(worstDrawdown.maxDrawdown || 0).toFixed(2)}，是后续 prompt 修正的主要风险样本。`);
  }

  return {
    sampleCount: completedTradeCount,
    completedRoundCount: completedTradeCount,
    totalScenarioRounds: Math.max(0, rounds.length - 1),
    totalAgentDecisions: allTrades.length,
    trainingTrades: Math.min(completedTradeCount, TRAINING_TRADE_COUNT),
    testTrades: Math.max(0, completedTradeCount - TRAINING_TRADE_COUNT),
    agentCount: ranked.length,
    scope: `累计统计至第 ${completedTradeCount} 轮，共 ${allTrades.length} 条智能体交易决策。`,
    bestAgentId: best?.agentId || null,
    bestRole: best?.role || null,
    worstAgentId: worst?.agentId || null,
    worstRole: worst?.role || null,
    averageHitRate,
    averageDrawdown,
    alphaSpread,
    actionDistribution,
    scoreBars: ranked.map(item => ({
      agentId: item.agentId,
      role: item.role,
      symbol: item.symbol,
      totalScore: Number(item.totalScore || 0),
      trainingScore: Number(item.trainingScore || 0),
      testScore: Number(item.testScore || 0),
      maxDrawdown: Number(item.maxDrawdown || 0),
      hitRate: Number(item.hitRate || 0),
      tradeCount: Array.isArray(item.trades) ? item.trades.length : 0,
      lossCount: Array.isArray(item.trades) ? item.trades.filter(trade => Number(trade.scoreDelta || 0) < 0).length : 0,
      recommendation: item.recommendation?.status || 'watch'
    })),
    agentBreakdowns: ranked.map(buildAgentBreakdown),
    topEquityCurve,
    conclusions
  };
}

function scoreAgent({ agentId, rounds, completedTradeCount }) {
  const profile = AGENT_PROFILES[agentId];
  const commodity = COMMODITIES.find(item => item.id === profile.commodityBias) || COMMODITIES[0];
  const exposureScale = EXPOSURE_SCALE_BY_AGENT[agentId] || 1;
  const trades = [];
  let equity = 0;
  let peak = 0;
  let maxDrawdown = 0;

  for (let i = 0; i < completedTradeCount; i += 1) {
    const current = rounds[i];
    const next = rounds[i + 1];
    if (!current || !next) continue;
    const action = ACTIONS_BY_AGENT[agentId][i % ROUNDS.length];
    const currentPrice = Number(current.prices?.[commodity.id]);
    const nextPrice = Number(next.prices?.[commodity.id]);
    const delta = calculateTradeScore({ action, currentPrice, nextPrice, exposureScale });
    equity = Number((equity + delta).toFixed(2));
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, Number((peak - equity).toFixed(2)));
    trades.push({
      index: i,
      phase: i < TRAINING_TRADE_COUNT ? 'training' : 'test',
      date: current.date,
      exitDate: next.date,
      regime: current.regime,
      action,
      actionLabel: actionLabel(action),
      symbol: commodity.symbol,
      commodity: commodity.id,
      entry: currentPrice,
      exit: nextPrice,
      scoreDelta: delta,
      equity
    });
  }

  const trainingScore = trades
    .filter(item => item.phase === 'training')
    .reduce((sum, item) => sum + item.scoreDelta, 0);
  const testScore = trades
    .filter(item => item.phase === 'test')
    .reduce((sum, item) => sum + item.scoreDelta, 0);
  const totalScore = trades.reduce((sum, item) => sum + item.scoreDelta, 0);
  const evaluatedTrades = trades.length || 1;
  const hitRate = trades.filter(item => item.scoreDelta > 0).length / evaluatedTrades;
  const recommendation = recommendationFor({
    totalScore,
    testScore,
    maxDrawdown
  });

  return {
    agentId,
    role: profile.role,
    style: profile.style,
    symbol: commodity.symbol,
    commodity: commodity.id,
    totalScore: Number(totalScore.toFixed(2)),
    trainingScore: Number(trainingScore.toFixed(2)),
    testScore: Number(testScore.toFixed(2)),
    maxDrawdown: Number(maxDrawdown.toFixed(2)),
    hitRate: Number((hitRate * 100).toFixed(1)),
    trades,
    lastTrade: trades[trades.length - 1] || null,
    recommendation
  };
}

// Build evaluation based on actual LLM decisions stored in agent.decision
function buildLlmEvaluation({ worldState, rounds, roundIndex }) {
  const completedTradeCount = Math.max(1, Math.min(roundIndex + 1, rounds.length - 1));
  const ledger = Array.isArray(worldState.meta?.trading?.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger
    : [];
  const ledgerByRound = new Map();
  for (const entry of ledger) {
    if (!entry || !entry.agentId || !Number.isFinite(Number(entry.roundIndex))) continue;
    ledgerByRound.set(`${entry.agentId}:${Number(entry.roundIndex)}`, entry);
  }
  const rankings = AGENT_IDS.map(agentId => {
    const profile = AGENT_PROFILES[agentId];
    const defaultCommodity = COMMODITIES.find(item => item.id === profile.commodityBias) || COMMODITIES[0];
    const exposureScale = EXPOSURE_SCALE_BY_AGENT[agentId] || 1;
    const trades = [];
    let equity = 0;
    let peak = 0;
    let maxDrawdown = 0;

    for (let i = 0; i < completedTradeCount; i += 1) {
      const current = rounds[i];
      const next = rounds[i + 1];
      const ledgerEntry = ledgerByRound.get(`${agentId}:${i}`);
      if (!current || !next || !ledgerEntry) continue;
      const commodity = COMMODITIES.find(item =>
        item.id === ledgerEntry.commodity ||
        item.symbol === ledgerEntry.commodity ||
        item.symbol === ledgerEntry.symbol
      ) || defaultCommodity;
      const action = normalizeAction(ledgerEntry.action);
      const currentPrice = Number(current.prices?.[commodity.id]);
      const nextPrice = Number(next.prices?.[commodity.id]);
      if (!Number.isFinite(currentPrice) || !Number.isFinite(nextPrice)) continue;

      const delta = calculateTradeScore({ action, currentPrice, nextPrice, exposureScale });
      equity = Number((equity + delta).toFixed(2));
      peak = Math.max(peak, equity);
      maxDrawdown = Math.max(maxDrawdown, Number((peak - equity).toFixed(2)));

      trades.push({
        index: i,
        phase: i < TRAINING_TRADE_COUNT ? 'training' : 'test',
        date: current.date,
        exitDate: next.date,
        regime: current.regime,
        action,
        actionLabel: actionLabel(action),
        symbol: commodity.symbol,
        commodity: commodity.id,
        entry: currentPrice,
        exit: nextPrice,
        scoreDelta: delta,
        equity,
        confidence: ledgerEntry.confidence,
        source: 'llm'
      });
    }
    
    const trainingScore = trades.filter(item => item.phase === 'training').reduce((sum, item) => sum + item.scoreDelta, 0);
    const testScore = trades.filter(item => item.phase === 'test').reduce((sum, item) => sum + item.scoreDelta, 0);
    const totalScore = trades.reduce((sum, item) => sum + item.scoreDelta, 0);
    const evaluatedTrades = trades.length || 1;
    const hitRate = trades.filter(item => item.scoreDelta > 0).length / evaluatedTrades;
    const recommendation = recommendationFor({ totalScore, testScore, maxDrawdown });
    
    return {
      agentId,
      role: profile.role,
      style: profile.style,
      symbol: trades[trades.length - 1]?.symbol || defaultCommodity.symbol,
      commodity: trades[trades.length - 1]?.commodity || defaultCommodity.id,
      totalScore: Number(totalScore.toFixed(2)),
      trainingScore: Number(trainingScore.toFixed(2)),
      testScore: Number(testScore.toFixed(2)),
      maxDrawdown: Number(maxDrawdown.toFixed(2)),
      hitRate: Number((hitRate * 100).toFixed(1)),
      trades,
      lastTrade: trades[trades.length - 1] || null,
      recommendation,
      rawScore: totalScore,
      rawTrainingScore: trainingScore,
      rawTestScore: testScore
    };
  }).sort((a, b) => b.totalScore - a.totalScore);
  
  // Normalize scores (subtract mean)
  const meanTotal = rankings.reduce((sum, item) => sum + item.totalScore, 0) / rankings.length;
  const meanTraining = rankings.reduce((sum, item) => sum + item.trainingScore, 0) / rankings.length;
  const meanTest = rankings.reduce((sum, item) => sum + item.testScore, 0) / rankings.length;
  rankings.forEach(item => {
    item.totalScore = Number((item.totalScore - meanTotal).toFixed(2));
    item.trainingScore = Number((item.trainingScore - meanTraining).toFixed(2));
    item.testScore = Number((item.testScore - meanTest).toFixed(2));
  });
  rankings.sort((a, b) => b.totalScore - a.totalScore);
  
  // Update recommendations based on new rankings
  rankings.forEach((item, index) => {
    if (index === 0) {
      item.recommendation = {
        status: 'adopt',
        label: '采纳',
        text: '模型累计决策中排名第一，建议采纳该策略。'
      };
    } else if (index === rankings.length - 1 || item.maxDrawdown > 18) {
      item.recommendation = {
        status: 'remove',
        label: '淘汰',
        text: '模型累计决策中收益/回撤不达标。'
      };
    } else {
      item.recommendation = {
        status: 'watch',
        label: '观察',
        text: '模型表现尚可但需要更多回合验证。'
      };
    }
  });
  
  return {
    byAgent: Object.fromEntries(rankings.map(item => [item.agentId, item])),
    rankings,
    method: '基于模型真实决策的累计评分',
    dataSource: '模型累计决策',
    trainingWindow: `${rounds[0]?.date || '--'} → ${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'}`,
    testWindow: `${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'} → ${rounds[rounds.length - 1]?.date || '--'}`,
    analysis: buildEvaluationAnalysis({ rankings, completedTradeCount, rounds }),
    pool: {
      adopt: rankings.filter(item => item.recommendation.status === 'adopt').length,
      watch: rankings.filter(item => item.recommendation.status === 'watch').length,
      remove: rankings.filter(item => item.recommendation.status === 'remove').length
    }
  };
}

function buildEvaluation({ rounds, roundIndex }) {
  const completedTradeCount = Math.max(1, Math.min(roundIndex + 1, rounds.length - 1));
  const rankings = AGENT_IDS
    .map(agentId => scoreAgent({ agentId, rounds, completedTradeCount }))
    .sort((a, b) => b.totalScore - a.totalScore);
  const meanTotal = rankings.reduce((sum, item) => sum + item.totalScore, 0) / rankings.length;
  const meanTraining = rankings.reduce((sum, item) => sum + item.trainingScore, 0) / rankings.length;
  const meanTest = rankings.reduce((sum, item) => sum + item.testScore, 0) / rankings.length;
  rankings.forEach(item => {
    item.rawScore = item.totalScore;
    item.rawTrainingScore = item.trainingScore;
    item.rawTestScore = item.testScore;
    item.totalScore = Number((item.totalScore - meanTotal).toFixed(2));
    item.trainingScore = Number((item.trainingScore - meanTraining).toFixed(2));
    item.testScore = Number((item.testScore - meanTest).toFixed(2));
  });
  rankings.sort((a, b) => b.totalScore - a.totalScore);
  rankings.forEach((item, index) => {
    if (index === 0) {
      item.recommendation = {
        status: 'adopt',
        label: '采纳',
        text: '当前累计排名第一，下一轮提高该策略采样概率。'
      };
    } else if (index === rankings.length - 1 || item.maxDrawdown > 18) {
      item.recommendation = {
        status: 'remove',
        label: '淘汰',
        text: '收益/回撤排名靠后，下一轮降低权重或移除该策略。'
      };
    } else {
      item.recommendation = {
        status: 'watch',
        label: '观察',
        text: '保留策略但不加权，继续通过记忆和 prompt 补丁修正。'
      };
    }
  });
  const byAgent = Object.fromEntries(rankings.map(item => [item.agentId, item]));
  const dataSource = rounds.some(round => round.dataSource === 'local-real' || round.dataSource === 'mixed-real-scenario')
    ? '真实价格曲线'
    : '内置情景价格';

  return {
    method: '累计评分：价格曲线固定，智能体的买入/卖出/观望时间点决定收益；面板显示相对策略池的 alpha 分，训练段用于修正策略，测试段用于验证泛化。',
    dataSource,
    completedTradeCount,
    trainingWindow: `${rounds[0]?.date || '--'} → ${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'}`,
    testWindow: `${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'} → ${rounds[rounds.length - 1]?.date || '--'}`,
    rankings,
    byAgent,
    analysis: buildEvaluationAnalysis({ rankings, completedTradeCount, rounds }),
    pool: {
      adopt: rankings.filter(item => item.recommendation.status === 'adopt').length,
      watch: rankings.filter(item => item.recommendation.status === 'watch').length,
      remove: rankings.filter(item => item.recommendation.status === 'remove').length
    }
  };
}

function applyTradingGameRound({ worldState, roundIndex = 0, nowMs = Date.now(), skipPresetScoring = false }) {
  ensureWorldState(worldState);
  rethemeWorld(worldState.world);

  const idx = clampRoundIndex(roundIndex);
  const historicalRounds = getHistoricalRounds();
  const round = historicalRounds[idx];
  const previousLlmLedger = Array.isArray(worldState.meta?.trading?.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger.slice()
    : [];
  
  const baselineEvaluation = buildEvaluation({ rounds: historicalRounds, roundIndex: idx });
  const evaluation = skipPresetScoring
    ? {
      ...baselineEvaluation,
      method: 'LLM真实决策生成中：先显示累计策略基线统计；模型返回后自动覆盖为真实模型决策评分。',
      dataSource: `${baselineEvaluation.dataSource} · LLM待返回`
    }
    : baselineEvaluation;
  const timeline = historicalRounds.slice(0, idx + 1).map((entry, entryIndex) => ({
    index: entryIndex,
    date: entry.date,
    regime: entry.regime,
    event: entry.news[0],
    score: entry.scoreboard,
    dataSource: entry.dataSource
  }));

  worldState.meta.trading = {
    mode: 'futures-agent-simulation',
    currentRound: idx,
    currentDate: round.date,
    regime: round.regime,
    commodities: COMMODITIES,
    prices: round.prices,
    news: round.news,
    dataSource: round.dataSource,
    priceSource: evaluation.dataSource,
    evaluation,
    timeline,
    llmDecisionLedger: previousLlmLedger,
    llm: {
      enabled: false,
      provider: null,
      model: DEFAULT_LLM_MODEL,
      status: 'simulated'
    },
    updatedAt: new Date(nowMs).toISOString()
  };
  worldState.meta.claude = {
    enabled: false,
    sessionsObserved: AGENT_IDS.length,
    lastSnapshotAt: new Date(nowMs).toISOString()
  };

  for (const agentId of AGENT_IDS) {
    const profile = AGENT_PROFILES[agentId];
    const station = stationFor(agentId, idx);
    const decision = skipPresetScoring ? null : buildDecision({ agentId, round, roundIndex: idx });
    const memory = buildMemory({ agentId, round, roundIndex: idx });
    const strategy = buildStrategy({ agentId, roundIndex: idx });
    const scoreSummary = evaluation ? evaluation.byAgent[agentId] : null;

    const agent = {
      id: agentId,
      sessionId: agentId,
      name: profile.role,
      role: profile.role,
      zone: station.id,
      activity: '决策中',
      status: 'Working',
      lastEventAt: new Date(nowMs).toISOString(),
      model: profile.model,
      repoLabel: '期货实验室',
      repoRoot: '/期货智能体模拟系统',
      cwd: `/期货智能体模拟系统/${profile.role}`,
      gitBranch: `提示词-v${strategy.promptVersion}`,
      hasTranscript: false,
      tool: decision ? {
        ...TOOL_BY_STATION[station.id],
        inputPreview: `${decision.symbol} ${round.date}`
      } : TOOL_BY_STATION[station.id],
      decision,
      memory,
      strategy,
      score: {
        total: scoreSummary?.totalScore ?? 0,
        training: scoreSummary?.trainingScore ?? 0,
        test: scoreSummary?.testScore ?? 0,
        drawdown: scoreSummary?.maxDrawdown ?? 0,
        hitRate: scoreSummary?.hitRate ?? 0,
        recommendation: scoreSummary?.recommendation || null
      },
      cost: {
        usd: Number((0.002 + idx * 0.0007 + AGENT_IDS.indexOf(agentId) * 0.0003).toFixed(4)),
        input: 900 + idx * 120,
        output: 360 + idx * 80,
        cacheWrite: 0,
        cacheRead: 120 + idx * 20,
        messageCount: idx + 2,
        model: profile.model
      },
      lastAssistantSnippet: decision ? `${decision.reason} 记忆模块提示：${memory.retrieved[0].text}` : `等待LLM决策... 记忆模块提示：${memory.retrieved[0].text}`
    };
    worldState.agents[agentId] = agent;

    const avatar = ensureAvatar(worldState, agentId, {
      preferredPosition: { x: station.x, y: station.y }
    });
    avatar.displayName = profile.role;
    avatar.state = 'working';
    avatar.status = 'Working';
    avatar.moving = true;
    avatar.hatHue = Math.abs(profile.color.split('').reduce((sum, ch) => sum + ch.charCodeAt(0), 0)) % 360;
    avatar.toolIcon = TOOL_BY_STATION[station.id].icon;
    avatar.model = profile.model;
    avatar.buildingLabel = station.label;
    avatar.buildingKey = station.locationId || station.id;
    avatar.gitBranch = agent.gitBranch;
    avatar.repoLabel = agent.repoLabel;
    avatar.destination = {
      x: station.x,
      y: station.y,
      stationId: station.id,
      locationId: station.locationId,
      locationName: station.label,
      stationLabel: station.label,
      stationKind: station.id === 'debate' ? 'rest' : 'work',
      stationActivity: station.activity,
      intent: { kind: station.id === 'trade' ? 'at_desk' : 'at_leisure' }
    };
    avatar.intent = avatar.destination.intent;
    avatar.bubbleText = decision
      ? `${decision.actionLabel} ${decision.symbol} · ${decision.confidence}%`
      : `等待LLM决策 ${profile.commodityBias.toUpperCase()}`;
    avatar.lastUpdatedAt = new Date(nowMs).toISOString();
  }

  return worldState;
}

function commodityForDecision(profile, decision) {
  const requested = decision?.commodity;
  return COMMODITIES.find(item => item.id === requested || item.symbol === requested) ||
    COMMODITIES.find(item => item.id === profile.commodityBias) ||
    COMMODITIES[0];
}

function applyLlmDecisionToAgent({
  worldState,
  agentId,
  llmDecision,
  round,
  nowMs = Date.now(),
  model,
  provider
}) {
  const agent = worldState.agents?.[agentId];
  const avatar = worldState.avatars?.[agentId];
  const profile = AGENT_PROFILES[agentId];
  if (!agent || !avatar || !profile || !llmDecision) return false;

  const action = normalizeAction(llmDecision.action);
  const commodity = commodityForDecision(profile, llmDecision);
  const price = round.prices[commodity.id];
  const confidence = clampConfidence(llmDecision.confidence);
  const evidence = Array.isArray(llmDecision.evidence) && llmDecision.evidence.length
    ? llmDecision.evidence.map(item => String(item)).slice(0, 5)
    : agent.decision.evidence;
  const reason = String(llmDecision.reason || '').trim() ||
    `${actionLabel(action)} ${commodity.name}：真实模型结合资讯、价格走势和记忆后给出该动作。`;

  const resolvedModel = llmDecision.model || model || agent.model || DEFAULT_LLM_MODEL;
  const resolvedProvider = llmDecision.provider || provider || 'llm';
  agent.model = resolvedModel;
  agent.decision = {
    ...agent.decision,
    action,
    actionLabel: actionLabel(action),
    commodity: commodity.id,
    symbol: commodity.symbol,
    price,
    confidence,
    source: 'llm',
    provider: resolvedProvider,
    model: resolvedModel,
    reason,
    evidence,
    usage: llmDecision.usage || null,
    attempts: Array.isArray(llmDecision.attempts) ? llmDecision.attempts : []
  };
  agent.memory = {
    ...agent.memory,
    lesson: String(llmDecision.memoryLesson || '').trim() || agent.memory.lesson
  };
  if (Array.isArray(llmDecision.strategyPatchNotes) && llmDecision.strategyPatchNotes.length > 0) {
    agent.strategy = {
      ...agent.strategy,
      patchNotes: llmDecision.strategyPatchNotes.map(item => String(item)).slice(0, 5)
    };
  }
  if (llmDecision.usage) {
    agent.cost = {
      ...agent.cost,
      input: Number(llmDecision.usage.promptTokens || agent.cost?.input || 0),
      output: Number(llmDecision.usage.completionTokens || agent.cost?.output || 0),
      messageCount: (agent.cost?.messageCount || 0) + 1,
      model: agent.model
    };
  }
  agent.lastEventAt = new Date(nowMs).toISOString();
  agent.lastAssistantSnippet = `${reason} 记忆模块提示：${agent.memory.lesson}`;

  avatar.model = resolvedModel;
  avatar.gitBranch = agent.gitBranch;
  avatar.bubbleText = `${agent.decision.actionLabel} ${agent.decision.symbol} · ${confidence}%`;
  avatar.lastUpdatedAt = new Date(nowMs).toISOString();
  return true;
}

function recordLlmDecision({ worldState, agentId, roundIndex, round, nowMs = Date.now() }) {
  const agent = worldState.agents?.[agentId];
  if (!agent?.decision || agent.decision.source !== 'llm') return;
  if (!worldState.meta) worldState.meta = {};
  if (!worldState.meta.trading) worldState.meta.trading = {};
  const ledger = Array.isArray(worldState.meta.trading.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger.filter(entry =>
      !(entry.agentId === agentId && Number(entry.roundIndex) === Number(roundIndex))
    )
    : [];

  ledger.push({
    agentId,
    roundIndex,
    date: round?.date || agent.decision.date || null,
    action: agent.decision.action,
    actionLabel: agent.decision.actionLabel || actionLabel(agent.decision.action),
    commodity: agent.decision.commodity,
    symbol: agent.decision.symbol,
    confidence: agent.decision.confidence,
    model: agent.decision.model,
    provider: agent.decision.provider,
    reason: agent.decision.reason,
    recordedAt: new Date(nowMs).toISOString()
  });
  ledger.sort((a, b) => Number(a.roundIndex) - Number(b.roundIndex) || String(a.agentId).localeCompare(String(b.agentId)));
  worldState.meta.trading.llmDecisionLedger = ledger;
}

async function updateTradingGameWithLlm({
  worldState,
  roundIndex = 0,
  llmClient,
  nowMs = Date.now(),
  onProgress = null
}) {
  if (!llmClient || typeof llmClient.decide !== 'function') {
    return { updated: 0, failed: 0 };
  }

  const idx = clampRoundIndex(roundIndex);
  const historicalRounds = getHistoricalRounds();
  const round = historicalRounds[idx];
  const failures = [];
  let updated = 0;
  const provider = llmClient.provider || 'llm';
  const model = llmClient.model || DEFAULT_LLM_MODEL;
  const timeoutMs = !llmClient.handlesTimeouts && Number.isFinite(Number(llmClient.timeoutMs))
    ? Number(llmClient.timeoutMs)
    : 0;

  async function decideWithOptionalTimeout(input) {
    const promise = llmClient.decide(input);
    if (!timeoutMs || timeoutMs <= 0) return promise;
    let timeout = null;
    try {
      return await Promise.race([
        promise,
        new Promise((_, reject) => {
          timeout = setTimeout(() => {
            reject(new Error(`LLM decision timed out after ${timeoutMs}ms.`));
          }, timeoutMs);
        })
      ]);
    } finally {
      if (timeout) clearTimeout(timeout);
    }
  }

  if (worldState.meta?.trading) {
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: 'running',
      updatedAt: new Date(nowMs).toISOString()
    };
  }

  for (const agentId of AGENT_IDS) {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    if (!agent || !profile) continue;
    try {
      const llmDecision = await decideWithOptionalTimeout({
        agentId,
        profile,
        round,
        roundIndex: idx,
        commodities: COMMODITIES,
        simulatedDecision: agent.decision,
        memory: agent.memory,
        strategy: agent.strategy
      });
      if (applyLlmDecisionToAgent({
        worldState,
        agentId,
        llmDecision,
        round,
        nowMs,
        model,
        provider
      })) {
        recordLlmDecision({ worldState, agentId, roundIndex: idx, round, nowMs });
        updated += 1;
        if (typeof onProgress === 'function') onProgress({ agentId, updated, failed: failures.length });
      }
    } catch (err) {
      failures.push({ agentId, message: err.message });
      if (typeof onProgress === 'function') onProgress({ agentId, updated, failed: failures.length });
    }
  }

  // After LLM decisions, recalculate scores based on actual LLM decisions
  if (updated > 0 && worldState.meta?.trading) {
    const idx = clampRoundIndex(roundIndex);
    const historicalRounds = getHistoricalRounds();
    const round = historicalRounds[idx];
    
    // Build evaluation based on LLM decisions
    const llmEvaluation = buildLlmEvaluation({ worldState, rounds: historicalRounds, roundIndex: idx });
    
    worldState.meta.trading.evaluation = llmEvaluation;
    worldState.meta.trading.priceSource = '模型累计决策';
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: failures.length === 0 ? 'live' : updated > 0 ? 'partial' : 'error',
      updatedAt: new Date(nowMs).toISOString(),
      errors: failures
    };
    worldState.meta.trading.updatedAt = new Date(nowMs).toISOString();
    
    // Update agent scores with LLM-based evaluation
    for (const agentId of AGENT_IDS) {
      const agent = worldState.agents?.[agentId];
      const scoreSummary = llmEvaluation.byAgent[agentId];
      if (agent && scoreSummary) {
        agent.score = {
          total: scoreSummary.totalScore,
          training: scoreSummary.trainingScore,
          test: scoreSummary.testScore,
          drawdown: scoreSummary.maxDrawdown,
          hitRate: scoreSummary.hitRate,
          recommendation: scoreSummary.recommendation
        };
      }
    }
  } else if (worldState.meta?.trading) {
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: failures.length === 0 ? 'live' : updated > 0 ? 'partial' : 'error',
      updatedAt: new Date(nowMs).toISOString(),
      errors: failures
    };
    worldState.meta.trading.updatedAt = new Date(nowMs).toISOString();
  }

  return { updated, failed: failures.length, failures };
}

function createTradingGameDemo({
  worldState,
  broadcastState,
  tickMs = 4500,
  now = () => Date.now(),
  llmClient = null,
  onLlmError = null
}) {
  let roundIndex = 0;
  let timer = null;
  let inFlight = false;
  let running = false;

  function scheduleNextTick() {
    if (!running) return;
    if (timer) clearTimeout(timer);
    timer = setTimeout(tick, tickMs);
    if (timer.unref) timer.unref();
  }

  function tick() {
    if (llmClient && inFlight) {
      scheduleNextTick();
      return;
    }
    const currentRound = roundIndex;
    // Skip preset scoring when LLM is enabled - we'll score after LLM decisions
    applyTradingGameRound({ worldState, roundIndex: currentRound, nowMs: now(), skipPresetScoring: Boolean(llmClient) });
    roundIndex = (roundIndex + 1) % ROUNDS.length;
    if (llmClient && !inFlight) {
      inFlight = true;
      if (worldState.meta?.trading) {
        worldState.meta.trading.llm = {
          enabled: true,
          provider: llmClient.provider || 'llm',
          model: llmClient.model || DEFAULT_LLM_MODEL,
          status: 'running',
          updatedAt: new Date(now()).toISOString()
        };
      }
      if (typeof broadcastState === 'function') broadcastState();
      updateTradingGameWithLlm({
        worldState,
        roundIndex: currentRound,
        llmClient,
        nowMs: now(),
        onProgress: () => {
          if (typeof broadcastState === 'function') broadcastState();
        }
      }).then(() => {
        if (typeof broadcastState === 'function') broadcastState();
      }).catch(err => {
        if (worldState.meta?.trading) {
          worldState.meta.trading.llm = {
            enabled: true,
            provider: llmClient.provider || 'llm',
            model: llmClient.model || DEFAULT_LLM_MODEL,
            status: 'error',
            error: err.message,
            updatedAt: new Date(now()).toISOString()
          };
        }
        if (typeof onLlmError === 'function') onLlmError(err);
      }).finally(() => {
        inFlight = false;
        scheduleNextTick();
      });
    } else if (typeof broadcastState === 'function') {
      broadcastState();
      scheduleNextTick();
    }
  }

  return {
    start() {
      if (running) return;
      running = true;
      tick();
    },
    stop() {
      running = false;
      if (!timer) return;
      clearTimeout(timer);
      timer = null;
    },
    tick
  };
}

module.exports = {
  AGENT_IDS,
  AGENT_PROFILES,
  COMMODITIES,
  ROUNDS,
  STATIONS,
  DEFAULT_LLM_MODEL,
  getHistoricalRounds,
  buildEvaluation,
  applyTradingGameRound,
  updateTradingGameWithLlm,
  createTradingGameDemo
};
