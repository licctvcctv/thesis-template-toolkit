#!/usr/bin/env node

/**
 * Process downloaded commodity data and create commodities-historical.json
 * Combines gold, WTI crude oil, and soybean futures data
 */

const fs = require('fs');
const path = require('path');

function parseCSV(content) {
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  const data = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    const row = {};
    headers.forEach((header, index) => {
      row[header.trim()] = values[index]?.trim() || '';
    });
    data.push(row);
  }
  
  return data;
}

function processGoldData(csvPath) {
  console.log('Processing gold data...');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const data = parseCSV(content);
  
  const monthlyData = [];
  for (const row of data) {
    if (row.Date && row.Price && row.Price !== '') {
      monthlyData.push({
        date: row.Date,
        price: parseFloat(row.Price)
      });
    }
  }
  
  console.log(`  ✓ Processed ${monthlyData.length} gold price records`);
  return monthlyData;
}

function processWTIData(csvPath) {
  console.log('Processing WTI crude oil data...');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const data = parseCSV(content);
  
  const monthlyData = [];
  for (const row of data) {
    if (row.Date && row.Price && row.Price !== '') {
      monthlyData.push({
        date: row.Date,
        price: parseFloat(row.Price)
      });
    }
  }
  
  console.log(`  ✓ Processed ${monthlyData.length} WTI oil price records`);
  return monthlyData;
}

function processSoybeanData(csvPath) {
  console.log('Processing soybean data...');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  
  // Find the Soybeans column index
  const soybeanIndex = headers.findIndex(h => h.trim() === 'Soybeans');
  if (soybeanIndex === -1) {
    throw new Error('Soybeans column not found in commodity prices data');
  }
  
  const monthlyData = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    const date = values[0]?.trim();
    const price = values[soybeanIndex]?.trim();
    
    if (date && price && price !== '' && !isNaN(parseFloat(price))) {
      monthlyData.push({
        date: date,
        price: parseFloat(price)
      });
    }
  }
  
  console.log(`  ✓ Processed ${monthlyData.length} soybean price records`);
  return monthlyData;
}

function main() {
  const dataDir = path.join(__dirname, '..', 'data');
  
  try {
    // Process each commodity
    const goldData = processGoldData(path.join(dataDir, 'gold-monthly.csv'));
    const wtiData = processWTIData(path.join(dataDir, 'wti-monthly.csv'));
    const soybeanData = processSoybeanData(path.join(dataDir, 'commodity-prices.csv'));
    
    // Create the final JSON structure
    const output = {
      metadata: {
        description: 'Historical commodity futures prices',
        sources: {
          gold: 'DataHub.io - Gold Prices (World Gold Council)',
          crude_oil: 'DataHub.io - WTI Crude Oil Prices (EIA)',
          soybean: 'DataHub.io - IMF Commodity Prices (Chicago Soybean Futures)'
        },
        units: {
          gold: 'USD per troy ounce',
          crude_oil: 'USD per barrel',
          soybean: 'USD per metric ton'
        },
        lastUpdated: new Date().toISOString()
      },
      commodities: {
        GOLD: {
          name: 'Gold Futures',
          symbol: 'GC',
          data: goldData
        },
        CRUDE_OIL: {
          name: 'WTI Crude Oil Futures',
          symbol: 'CL',
          data: wtiData
        },
        SOYBEAN: {
          name: 'Soybean Futures',
          symbol: 'ZS',
          data: soybeanData
        }
      }
    };
    
    // Write to file
    const outputPath = path.join(dataDir, 'commodities-historical.json');
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    
    console.log('\n✓ Successfully created commodities-historical.json');
    console.log(`\nData summary:`);
    console.log(`  Gold: ${goldData.length} records (${goldData[0]?.date} to ${goldData[goldData.length-1]?.date})`);
    console.log(`  WTI Oil: ${wtiData.length} records (${wtiData[0]?.date} to ${wtiData[wtiData.length-1]?.date})`);
    console.log(`  Soybean: ${soybeanData.length} records (${soybeanData[0]?.date} to ${soybeanData[soybeanData.length-1]?.date})`);
    
  } catch (error) {
    console.error('Error processing data:', error.message);
    process.exit(1);
  }
}

main();
