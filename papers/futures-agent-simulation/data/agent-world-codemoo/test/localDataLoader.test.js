/**
 * 本地数据加载器测试
 * 
 * 运行测试: node test/localDataLoader.test.js
 */

const { test, describe } = require('node:test');
const assert = require('node:assert');
const LocalDataLoader = require('../adapter/localDataLoader');
const RealDataAdapter = require('../adapter/realDataAdapter');

describe('LocalDataLoader', () => {
  test('应该能够创建加载器实例', () => {
    const loader = new LocalDataLoader();
    assert.ok(loader);
    assert.ok(loader.isLoaded());
  });

  test('应该能够获取最新价格', () => {
    const loader = new LocalDataLoader();
    
    const goldPrice = loader.getLatestPrice('gold');
    const oilPrice = loader.getLatestPrice('crude_oil');
    const soybeanPrice = loader.getLatestPrice('soybean');
    
    assert.ok(typeof goldPrice === 'number');
    assert.ok(typeof oilPrice === 'number');
    assert.ok(typeof soybeanPrice === 'number');
    
    assert.ok(goldPrice > 0);
    assert.ok(oilPrice > 0);
    assert.ok(soybeanPrice > 0);
    
    console.log('最新价格:');
    console.log('  黄金:', goldPrice);
    console.log('  原油:', oilPrice);
    console.log('  大豆:', soybeanPrice);
  });

  test('应该能够获取特定日期的价格', () => {
    const loader = new LocalDataLoader();
    
    const goldPrice = loader.getPriceAtDate('gold', '2022-03-01');
    assert.ok(typeof goldPrice === 'number');
    assert.ok(goldPrice > 0);
    
    console.log('2022-03-01 黄金价格:', goldPrice);
  });

  test('应该能够获取历史价格', () => {
    const loader = new LocalDataLoader();
    
    const history = loader.getHistoricalPrices('gold', 5);
    assert.ok(Array.isArray(history));
    assert.strictEqual(history.length, 5);
    
    assert.ok(history[0].date);
    assert.ok(typeof history[0].price === 'number');
    
    console.log('黄金最近5个月价格:');
    history.forEach(item => {
      console.log(`  ${item.date}: ${item.price}`);
    });
  });

  test('应该能够批量获取价格', () => {
    const loader = new LocalDataLoader();
    
    const prices = loader.getBatchPrices(['gold', 'crude_oil', 'soybean']);
    
    assert.ok(prices.gold);
    assert.ok(prices.crude_oil);
    assert.ok(prices.soybean);
    
    console.log('批量价格:', prices);
  });

  test('应该能够获取可用商品列表', () => {
    const loader = new LocalDataLoader();
    
    const commodities = loader.getAvailableCommodities();
    
    assert.ok(Array.isArray(commodities));
    assert.strictEqual(commodities.length, 3);
    
    console.log('可用商品:');
    commodities.forEach(c => {
      console.log(`  ${c.name} (${c.symbol}): ${c.dataPoints} 个数据点`);
      console.log(`    日期范围: ${c.firstDate} 到 ${c.lastDate}`);
    });
  });

  test('应该能够获取统计信息', () => {
    const loader = new LocalDataLoader();
    
    const stats = loader.getStatistics('gold');
    
    assert.ok(stats);
    assert.ok(stats.symbol);
    assert.ok(stats.name);
    assert.ok(typeof stats.minPrice === 'number');
    assert.ok(typeof stats.maxPrice === 'number');
    assert.ok(typeof stats.avgPrice === 'number');
    
    console.log('黄金统计信息:');
    console.log(`  符号: ${stats.symbol}`);
    console.log(`  名称: ${stats.name}`);
    console.log(`  数据点: ${stats.dataPoints}`);
    console.log(`  日期范围: ${stats.firstDate} 到 ${stats.lastDate}`);
    console.log(`  价格范围: ${stats.minPrice} - ${stats.maxPrice}`);
    console.log(`  平均价格: ${stats.avgPrice}`);
    console.log(`  总变化: ${stats.totalChange} (${stats.totalChangePercent}%)`);
  });

  test('应该能够获取日期范围内的价格', () => {
    const loader = new LocalDataLoader();
    
    const range = loader.getPriceRange('crude_oil', '2020-01-01', '2020-12-31');
    
    assert.ok(Array.isArray(range));
    assert.ok(range.length > 0);
    
    console.log(`2020年原油价格 (${range.length} 个数据点):`);
    range.forEach(item => {
      console.log(`  ${item.date}: ${item.price}`);
    });
  });

  test('应该能够获取元数据', () => {
    const loader = new LocalDataLoader();
    
    const metadata = loader.getMetadata();
    
    assert.ok(metadata);
    assert.ok(metadata.sources);
    assert.ok(metadata.lastUpdated);
    
    console.log('数据元信息:');
    console.log(`  来源: Gold (${metadata.sources.gold}), Oil (${metadata.sources.crude_oil}), Soybean (${metadata.sources.soybean})`);
    console.log(`  最后更新: ${metadata.lastUpdated}`);
    console.log(`  说明: ${metadata.description}`);
  });
});

describe('RealDataAdapter (使用本地数据)', () => {
  test('应该能够创建适配器', () => {
    const adapter = new RealDataAdapter(true);
    assert.ok(adapter);
    assert.strictEqual(adapter.useRealData, true);
  });

  test('应该能够获取回合数据 (真实数据)', async () => {
    const adapter = new RealDataAdapter(true);
    const round = await adapter.getRoundData(0);
    
    assert.ok(round);
    assert.ok(round.dataSource === 'real' || round.dataSource === 'simulated');
    assert.ok(round.prices);
    
    console.log('回合 0 数据:');
    console.log(`  日期: ${round.date}`);
    console.log(`  数据源: ${round.dataSource}`);
    console.log(`  价格:`, round.prices);
  });

  test('应该能够获取历史趋势', async () => {
    const adapter = new RealDataAdapter(true);
    const trend = await adapter.getHistoricalTrend('gold', 3);
    
    assert.ok(Array.isArray(trend));
    assert.strictEqual(trend.length, 3);
    
    console.log('黄金历史趋势:');
    trend.forEach(item => {
      console.log(`  ${item.date}: ${item.price}`);
    });
  });

  test('应该能够获取状态', () => {
    const adapter = new RealDataAdapter(true);
    const status = adapter.getStatus();
    
    assert.ok(status);
    assert.strictEqual(status.useRealData, true);
    assert.strictEqual(status.dataLoaded, true);
    assert.ok(status.metadata);
    assert.ok(Array.isArray(status.availableCommodities));
    
    console.log('适配器状态:');
    console.log(`  使用真实数据: ${status.useRealData}`);
    console.log(`  数据已加载: ${status.dataLoaded}`);
    console.log(`  可用商品数: ${status.availableCommodities.length}`);
  });

  test('应该能够获取商品统计', () => {
    const adapter = new RealDataAdapter(true);
    const stats = adapter.getCommodityStats('crude_oil');
    
    assert.ok(stats);
    assert.ok(stats.symbol);
    
    console.log('原油统计:');
    console.log(`  最新价格: ${stats.latestPrice}`);
    console.log(`  价格范围: ${stats.minPrice} - ${stats.maxPrice}`);
  });

  test('应该能够切换数据源', async () => {
    const adapter = new RealDataAdapter(false);
    
    // 使用模拟数据
    let round = await adapter.getRoundData(0);
    assert.strictEqual(round.dataSource, 'simulated');
    
    // 切换到真实数据
    adapter.setDataSource(true);
    round = await adapter.getRoundData(0);
    assert.ok(round.dataSource === 'real' || round.dataSource === 'simulated');
    
    console.log('数据源切换测试通过');
  });
});

console.log('运行本地数据加载器测试...\n');
