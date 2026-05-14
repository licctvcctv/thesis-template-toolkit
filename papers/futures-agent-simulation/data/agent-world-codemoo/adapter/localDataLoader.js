/**
 * 本地历史数据加载器
 * 从本地 JSON 文件加载真实的历史商品期货数据
 * 
 * 优点:
 * - 无需 API Key
 * - 无请求限制
 * - 快速响应
 * - 离线可用
 */

const fs = require('fs');
const path = require('path');

class LocalDataLoader {
  constructor(dataFilePath = null) {
    this.dataFilePath = dataFilePath || path.join(__dirname, '../data/commodities-historical.json');
    this.data = null;
    this.loadData();
  }

  /**
   * 加载本地数据文件
   */
  loadData() {
    try {
      const rawData = fs.readFileSync(this.dataFilePath, 'utf8');
      this.data = JSON.parse(rawData);
      console.log('[LocalDataLoader] 历史数据加载成功');
      console.log(`[LocalDataLoader] 数据源: Gold (${this.data.metadata.sources.gold}), Oil (${this.data.metadata.sources.crude_oil}), Soybean (${this.data.metadata.sources.soybean})`);
      console.log(`[LocalDataLoader] 最后更新: ${this.data.metadata.lastUpdated}`);
    } catch (error) {
      console.error('[LocalDataLoader] 加载数据失败:', error.message);
      this.data = null;
    }
  }

  /**
   * 重新加载数据
   */
  reload() {
    this.loadData();
  }

  /**
   * 获取商品的最新价格
   * @param {string} commodityId - 商品 ID (GOLD, CRUDE_OIL, SOYBEAN)
   * @returns {number|null} 最新价格
   */
  getLatestPrice(commodityId) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      console.error(`[LocalDataLoader] 未找到商品数据: ${commodityId}`);
      return null;
    }

    if (!commodity.data || commodity.data.length === 0) {
      return null;
    }

    // 返回最后一条记录的价格
    const latest = commodity.data[commodity.data.length - 1];
    return latest.price;
  }

  /**
   * 获取商品在特定日期的价格
   * @param {string} commodityId - 商品 ID
   * @param {string} date - 日期 (YYYY-MM-DD)
   * @returns {number|null} 价格
   */
  getPriceAtDate(commodityId, date) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      return null;
    }

    const record = commodity.data.find(item => item.date === date);
    
    if (record) {
      return record.price;
    }

    // 如果找不到精确日期,找最接近的日期
    return this.getClosestPrice(commodityId, date);
  }

  /**
   * 获取最接近指定日期的价格
   * @param {string} commodityId - 商品 ID
   * @param {string} targetDate - 目标日期
   * @returns {number|null} 价格
   */
  getClosestPrice(commodityId, targetDate) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      return null;
    }

    const target = new Date(targetDate);
    
    let closest = null;
    let minDiff = Infinity;

    for (const record of commodity.data) {
      const recordDate = new Date(record.date);
      const diff = Math.abs(recordDate - target);
      
      if (diff < minDiff) {
        minDiff = diff;
        closest = record;
      }
    }

    return closest ? closest.price : null;
  }

  /**
   * 获取历史价格数据
   * @param {string} commodityId - 商品 ID
   * @param {number} count - 获取数据点数量 (从最新开始)
   * @returns {Array} 历史价格数组 [{date, price}, ...]
   */
  getHistoricalPrices(commodityId, count = 10) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      return [];
    }

    const data = commodity.data.slice(-count); // 获取最后 N 条记录
    
    return data.map(item => ({
      date: item.date,
      price: item.price
    }));
  }

  /**
   * 获取日期范围内的价格数据
   * @param {string} commodityId - 商品 ID
   * @param {string} startDate - 开始日期 (YYYY-MM-DD)
   * @param {string} endDate - 结束日期 (YYYY-MM-DD)
   * @returns {Array} 价格数据数组
   */
  getPriceRange(commodityId, startDate, endDate) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      return [];
    }

    const start = new Date(startDate);
    const end = new Date(endDate);
    
    return commodity.data
      .filter(item => {
        const date = new Date(item.date);
        return date >= start && date <= end;
      })
      .map(item => ({
        date: item.date,
        price: item.price
      }));
  }

  /**
   * 批量获取多个商品的最新价格
   * @param {Array<string>} commodityIds - 商品 ID 数组
   * @returns {Object} {commodityId: price, ...}
   */
  getBatchPrices(commodityIds) {
    const results = {};
    
    for (const commodityId of commodityIds) {
      results[commodityId] = this.getLatestPrice(commodityId);
    }
    
    return results;
  }

  /**
   * 获取所有可用的商品列表
   * @returns {Array} 商品信息数组
   */
  getAvailableCommodities() {
    if (!this.data?.commodities) {
      return [];
    }

    return Object.keys(this.data.commodities).map(key => ({
      id: key,
      symbol: this.data.commodities[key].symbol,
      name: this.data.commodities[key].name,
      dataPoints: this.data.commodities[key].data.length,
      firstDate: this.data.commodities[key].data[0]?.date,
      lastDate: this.data.commodities[key].data[this.data.commodities[key].data.length - 1]?.date
    }));
  }

  /**
   * 获取数据统计信息
   * @param {string} commodityId - 商品 ID
   * @returns {Object} 统计信息
   */
  getStatistics(commodityId) {
    const normalizedId = commodityId.toUpperCase();
    const commodity = this.data?.commodities?.[normalizedId];
    
    if (!commodity) {
      return null;
    }

    const prices = commodity.data.map(item => item.price);
    
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const avg = prices.reduce((sum, p) => sum + p, 0) / prices.length;
    const latest = prices[prices.length - 1];
    const first = prices[0];
    const change = latest - first;
    const changePercent = (change / first) * 100;

    return {
      symbol: commodity.symbol,
      name: commodity.name,
      unit: this.data.metadata.units[commodityId.toLowerCase()] || 'USD',
      dataPoints: prices.length,
      firstDate: commodity.data[0].date,
      lastDate: commodity.data[commodity.data.length - 1].date,
      firstPrice: first,
      latestPrice: latest,
      minPrice: min,
      maxPrice: max,
      avgPrice: Math.round(avg * 100) / 100,
      totalChange: Math.round(change * 100) / 100,
      totalChangePercent: Math.round(changePercent * 100) / 100
    };
  }

  /**
   * 获取元数据
   * @returns {Object} 元数据
   */
  getMetadata() {
    return this.data?.metadata || null;
  }

  /**
   * 检查数据是否已加载
   * @returns {boolean}
   */
  isLoaded() {
    return this.data !== null;
  }
}

module.exports = LocalDataLoader;
