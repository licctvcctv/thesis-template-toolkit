#!/usr/bin/env node

/**
 * Download historical commodity data from DataHub.io
 * - Gold prices (monthly, 1833-present)
 * - WTI Crude Oil prices (monthly, 1986-present)
 * - Soybeans prices (monthly, 1990-present) from IMF commodity dataset
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const DATA_SOURCES = [
  {
    name: 'gold',
    url: 'https://datahub.io/core/gold-prices/_r/-/data/monthly-processed.csv',
    outputFile: 'gold-monthly.csv'
  },
  {
    name: 'wti-oil',
    url: 'https://datahub.io/core/oil-prices/_r/-/data/wti-monthly.csv',
    outputFile: 'wti-monthly.csv'
  },
  {
    name: 'commodities',
    url: 'https://datahub.io/core/commodity-prices/_r/-/data/commodity-prices_v2.csv',
    outputFile: 'commodity-prices.csv'
  }
];

function downloadFile(url, outputPath) {
  return new Promise((resolve, reject) => {
    console.log(`Downloading ${url}...`);
    
    https.get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // Follow redirect
        return downloadFile(response.headers.location, outputPath)
          .then(resolve)
          .catch(reject);
      }
      
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      
      const fileStream = fs.createWriteStream(outputPath);
      response.pipe(fileStream);
      
      fileStream.on('finish', () => {
        fileStream.close();
        console.log(`✓ Downloaded to ${outputPath}`);
        resolve();
      });
      
      fileStream.on('error', (err) => {
        fs.unlink(outputPath, () => {});
        reject(err);
      });
    }).on('error', reject);
  });
}

async function main() {
  const dataDir = path.join(__dirname, '..', 'data');
  
  // Ensure data directory exists
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  
  console.log('Starting commodity data download...\n');
  
  for (const source of DATA_SOURCES) {
    try {
      const outputPath = path.join(dataDir, source.outputFile);
      await downloadFile(source.url, outputPath);
    } catch (error) {
      console.error(`✗ Failed to download ${source.name}:`, error.message);
      process.exit(1);
    }
  }
  
  console.log('\n✓ All downloads completed successfully!');
  console.log('\nNext steps:');
  console.log('1. Run: node scripts/process-commodity-data.js');
  console.log('2. This will create data/commodities-historical.json');
}

main().catch(console.error);
