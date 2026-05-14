/**
 * 真实数据适配器
 * 使用本地历史数据文件提供真实的商品期货价格
 */

const LocalDataLoader = require('./localDataLoader');
const { ROUNDS, COMMODITIES } = require('./tradingGameDemo');

class RealDataAdapter {
  constructor(useRealData = false) {
    this.useRealData = useRealData;
    this.localData = new LocalDataLoader();
    this.priceCache = {};
    this.lastUpdate = null;
  }

  /**
   * 获取当前回合数据
   * @param {number} roundIndex - 回合索引
   * @returns {Promise<Object>} 回合数据
   */
  async getRoundData(roundIndex) {
    // 如果不使用真实数据或超出模拟数据范围,返回模拟数据
    if (!this.useRealData || roundIndex >= ROUNDS.length) {
      return {
        ...ROUNDS[roundIndex % ROUNDS.length],
        dataSource: 'simulated'
      };
    }

    try {
      // 获取基础模拟数据
      const baseRound = ROUNDS[roundIndex];
      
      // 尝试从本地数据获取该日期附近的真实价格
      const realPrices = this.getRealPricesForDate(baseRound.date);
      
      // 如果获取成功,合并真实价格
      if (realPrices && Object.keys(realPrices).length > 0) {
        const updatedPrices = {};
        let hasRealData = false;
        
        for (const commodityId of ['gold', 'soybean', 'crude_oil']) {
          if (realPrices[commodityId] && realPrices[commodityId] > 0) {
            updatedPrices[commodityId] = realPrices[commodityId];
            hasRealData = true;
          } else {
            // 如果没有真实数据,使用模拟数据
            updatedPrices[commodityId] = baseRound.prices[commodityId];
          }
        }
        
        if (hasRealData) {
          return {
            ...baseRound,
            prices: updatedPrices,
            dataSource: 'real'
          };
        }
      }
    } catch (error) {
      console.error('[RealDataAdapter] 获取真实数据失败,使用模拟数据:', error.message);
    }

    // 失败时返回模拟数据
    return {
      ...ROUNDS[roundIndex % ROUNDS.length],
      dataSource: 'simulated'
    };
  }

  /**
   * 获取指定日期的真实价格数据
   * @param {string} date - 日期 (YYYY-MM-DD)
   * @returns {Object} {commodityId: price, ...}
   */
  getRealPricesForDate(date) {
    if (!this.localData.isLoaded()) {
      console.error('[RealDataAdapter] 本地数据未加载');
      return {};
    }

    try {
      const prices = {};
      
      // 获取每个商品在该日期的价格
      for (const commodityId of ['gold', 'crude_oil', 'soybean']) {
        const price = this.localData.getPriceAtDate(commodityId, date);
        if (price !== null) {
          prices[commodityId] = price;
        }
      }
      
      console.log(`[RealDataAdapter] 获取 ${date} 的价格:`, prices);
      return prices;
    } catch (error) {
      console.error('[RealDataAdapter] 获取价格失败:', error.message);
      return {};
    }
  }

  /**
   * 获取最新的真实价格数据
   * @returns {Object} {commodityId: price, ...}
   */
  getRealPrices() {
    if (!this.localData.isLoaded()) {
      console.error('[RealDataAdapter] 本地数据未加载');
      return {};
    }

    try {
      const prices = this.localData.getBatchPrices(['gold', 'crude_oil', 'soybean']);
      console.log('[RealDataAdapter] 最新价格:', prices);
      return prices;
    } catch (error) {
      console.error('[RealDataAdapter] 获取价格失败:', error.message);
      return {};
    }
  }

  /**
   * 获取历史价格趋势
   * @param {string} commodityId - 商品 ID (gold, soybean, crude_oil)
   * @param {number} count - 数据点数量
   * @returns {Promise<Array>} 历史价格数组
   */
  async getHistoricalTrend(commodityId, count = 6) {
    if (!this.useRealData || !this.localData.isLoaded()) {
      // 返回模拟历史数据
      return ROUNDS.slice(0, count).map(round => ({
        date: round.date,
        price: round.prices[commodityId]
      }));
    }

    try {
      return this.localData.getHistoricalPrices(commodityId, count);
    } catch (error) {
      console.error(`[RealDataAdapter] 获取 ${commodityId} 历史趋势失败:`, error.message);
      
      // 失败时返回模拟数据
      return ROUNDS.slice(0, count).map(round => ({
        date: round.date,
        price: round.prices[commodityId]
      }));
    }
  }

  /**
   * 切换数据源
   * @param {boolean} useReal - 是否使用真实数据
   */
  setDataSource(useReal) {
    this.useRealData = useReal;
    console.log(`[RealDataAdapter] 数据源切换为: ${useReal ? '真实数据' : '模拟数据'}`);
  }

  /**
   * 重新加载本地数据
   */
  reloadData() {
    this.localData.reload();
    console.log('[RealDataAdapter] 本地数据已重新加载');
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.priceCache = {};
    this.lastUpdate = null;
    console.log('[RealDataAdapter] 缓存已清除');
  }

  /**
   * 获取数据源状态
   * @returns {Object} 状态信息
   */
  getStatus() {
    const commodities = this.localData.getAvailableCommodities();
    
    return {
      useRealData: this.useRealData,
      dataLoaded: this.localData.isLoaded(),
      metadata: this.localData.getMetadata(),
      availableCommodities: commodities,
      statistics: {
        gold: this.localData.getStatistics('gold'),
        crude_oil: this.localData.getStatistics('crude_oil'),
        soybean: this.localData.getStatistics('soybean')
      }
    };
  }

  /**
   * 获取商品统计信息
   * @param {string} commodityId - 商品 ID
   * @returns {Object} 统计信息
   */
  getCommodityStats(commodityId) {
    return this.localData.getStatistics(commodityId);
  }
}

module.exports = RealDataAdapter;
