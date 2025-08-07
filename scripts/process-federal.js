// scripts/process-federal.js
const xlsx = require('node-xlsx');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Utility functions
const formatPrice = (priceStr) => {
  if (!priceStr) return 0;
  // Remove R$, spaces, and convert comma to dot
  return parseFloat(priceStr.toString().replace(/[R$\s]/g, '').replace(',', '.')) || 0;
};

const formatDate = (dateStr) => {
  if (!dateStr) return null;
  // Convert DD/MM/YYYY to ISO format for better JSON handling
  const [day, month, year] = dateStr.split('/');
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
};

const processLotteryData = (data) => {
  return data.map(row => {
    const results = [];
    
    // Process each prize (1st through 5th)
    for (let i = 1; i <= 5; i++) {
      const valueKey = `${i}º prêmio`;
      const priceKey = `Valor ${i}º prêmio`;
      
      if (row[valueKey]) {
        results.push({
          index: i,
          value: row[valueKey].toString().padStart(6, '0'), // Ensure 6 digits
          price: formatPrice(row[priceKey])
        });
      }
    }
    
    return {
      contest: parseInt(row['Extração']) || 0,
      date: formatDate(row['Data Sorteio']),
      results: results
    };
  }).filter(item => item.contest > 0); // Remove invalid entries
};

const generateAPI = (processedData, outputDir) => {
  // Create directory structure
  const apiDir = path.join(outputDir, 'api', 'federal');
  fs.mkdirSync(apiDir, { recursive: true });
  
  // Sort by contest number (ascending)
  processedData.sort((a, b) => a.contest - b.contest);
  
  // Generate latest endpoint
  const latest = processedData[processedData.length - 1];
  fs.writeFileSync(
    path.join(apiDir, 'latest.json'),
    JSON.stringify(latest, null, 2)
  );
  
  // Generate individual contest endpoints
  processedData.forEach(contest => {
    const contestDir = path.join(apiDir, contest.contest.toString());
    fs.mkdirSync(contestDir, { recursive: true });
    
    // Full contest data
    fs.writeFileSync(
      path.join(contestDir, 'index.json'),
      JSON.stringify(contest, null, 2)
    );
    
    // Individual results
    contest.results.forEach(result => {
      const resultDir = path.join(contestDir, 'result');
      fs.mkdirSync(resultDir, { recursive: true });
      
      fs.writeFileSync(
        path.join(resultDir, `${result.index}.json`),
        JSON.stringify({
          value: result.value,
          price: result.price
        }, null, 2)
      );
    });
  });
  
  // Generate metadata
  const metadata = {
    lottery: 'federal',
    totalContests: processedData.length,
    latestContest: latest.contest,
    lastUpdated: new Date().toISOString(),
    availableEndpoints: [
      '/api/federal/latest/',
      '/api/federal/{contest}/',
      '/api/federal/{contest}/result/{index}'
    ]
  };
  
  fs.writeFileSync(
    path.join(outputDir, 'api', 'meta.json'),
    JSON.stringify(metadata, null, 2)
  );
  
  return metadata;
};

const main = async () => {
  try {
    console.log('🎲 Starting Federal lottery data processing...');
    
    // Download the Excel file
    console.log('📥 Downloading lottery data...');
    const response = await axios({
      method: 'GET',
      url: process.env.LOTTERY_URL || 'https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Federal',
      responseType: 'arraybuffer',
      timeout: 30000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    console.log(`✅ Downloaded ${response.data.length} bytes`);
    
    // Parse Excel file
    console.log('📊 Parsing Excel data...');
    const workbook = xlsx.parse(response.data);
    const worksheet = workbook[0]; // First sheet
    
    // Convert to JSON (skip header row)
    const headers = worksheet.data[0];
    const rawData = worksheet.data.slice(1).map(row => {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index];
      });
      return obj;
    });
    console.log(`📋 Found ${rawData.length} raw entries`);
    
    // Process the data
    console.log('🔄 Processing lottery data...');
    const processedData = processLotteryData(rawData);
    console.log(`✨ Processed ${processedData.length} valid contests`);
    
    // Generate API structure
    console.log('🏗️  Generating API endpoints...');
    const outputDir = './dist';
    const metadata = generateAPI(processedData, outputDir);
    
    // Create index.html for GitHub Pages
    const indexHtml = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lottery API - Federal</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .method { color: #2196F3; font-weight: bold; }
        pre { background: #f0f0f0; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🎲 Lottery API - Federal</h1>
    <p><strong>Last Updated:</strong> ${metadata.lastUpdated}</p>
    <p><strong>Total Contests:</strong> ${metadata.totalContests}</p>
    <p><strong>Latest Contest:</strong> ${metadata.latestContest}</p>
    
    <h2>📋 Available Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/latest/</h3>
        <p>Get the most recent lottery result</p>
        <a href="api/federal/latest.json" target="_blank">🔗 Try it</a>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/{contest}/</h3>
        <p>Get results for a specific contest number</p>
        <a href="api/federal/${metadata.latestContest}/index.json" target="_blank">🔗 Try latest (${metadata.latestContest})</a>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/{contest}/result/{index}</h3>
        <p>Get specific prize result (index: 1-5)</p>
        <a href="api/federal/${metadata.latestContest}/result/1.json" target="_blank">🔗 Try latest 1st prize</a>
    </div>
    
    <h2>📊 Response Format</h2>
    <pre>{
  "contest": 5123,
  "date": "2024-01-15",
  "results": [
    {
      "index": 1,
      "value": "005349",
      "price": 200000.00
    },
    {
      "index": 2,
      "value": "038031",
      "price": 8000.00
    }
  ]
}</pre>
    
    <p><em>🤖 This API is automatically updated twice daily via GitHub Actions</em></p>
</body>
</html>`;
    
    fs.writeFileSync(path.join(outputDir, 'index.html'), indexHtml);
    
    console.log('🎉 API generation completed successfully!');
    console.log(`📈 Generated endpoints for ${metadata.totalContests} contests`);
    console.log(`🔄 Latest contest: ${metadata.latestContest}`);
    
  } catch (error) {
    console.error('❌ Error processing lottery data:', error);
    process.exit(1);
  }
};

// Run the script
main();