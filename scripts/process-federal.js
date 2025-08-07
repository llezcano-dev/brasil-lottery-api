// scripts/process-federal.js
const XLSX = require('xlsx');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Utility functions
const formatPrice = (priceStr) => {
  if (!priceStr) return 0;
  return parseFloat(priceStr.toString().replace(/[R$\s]/g, '').replace(',', '.')) || 0;
};

const formatDate = (dateStr) => {
  if (!dateStr) return null;
  const [day, month, year] = dateStr.split('/');
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
};

const downloadExcelFile = (url) => {
  return new Promise((resolve, reject) => {
    console.log('📥 Downloading Excel file...');
    
    const request = https.get(url, {
      headers: {
        'User-Agent': 'curl/7.68.0',
        'Accept': '*/*'
      }
    }, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`));
        return;
      }
      
      const chunks = [];
      response.on('data', chunk => chunks.push(chunk));
      response.on('end', () => {
        const buffer = Buffer.concat(chunks);
        console.log(`✅ Downloaded ${buffer.length} bytes`);
        resolve(buffer);
      });
    });
    
    request.on('error', reject);
    request.setTimeout(30000, () => {
      request.destroy();
      reject(new Error('Download timeout'));
    });
  });
};

const parseExcelData = (buffer) => {
  console.log('📊 Parsing Excel data...');
  
  // Save file for debugging
  fs.writeFileSync('./debug-federal.xlsx', buffer);
  console.log('💾 Saved debug file as debug-federal.xlsx');
  
  try {
    // Read Excel file with XLSX
    console.log('📊 Reading Excel file with XLSX...');
    const workbook = XLSX.read(buffer, { 
      type: 'buffer',
      cellText: false,
      cellDates: true
    });
    
    console.log('📊 Workbook info:', {
      sheetNames: workbook.SheetNames,
      sheetCount: workbook.SheetNames.length
    });
    
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    
    // Get sheet range info
    const range = worksheet['!ref'];
    console.log(`📊 Sheet range: ${range}`);
    
    if (!range) {
      throw new Error('No range found in worksheet');
    }
    
    // Parse the range to understand the data structure
    const decoded = XLSX.utils.decode_range(range);
    console.log('📊 Decoded range:', {
      startRow: decoded.s.r,
      endRow: decoded.e.r,
      startCol: decoded.s.c,
      endCol: decoded.e.c,
      totalRows: decoded.e.r - decoded.s.r + 1,
      totalCols: decoded.e.c - decoded.s.c + 1
    });
    
    // Try to read as array of arrays first
    console.log('📊 Converting to array format...');
    const arrayData = XLSX.utils.sheet_to_json(worksheet, { 
      header: 1,
      raw: false,
      dateNF: 'dd/mm/yyyy'
    });
    
    console.log(`📊 Array format found ${arrayData.length} rows`);
    
    if (arrayData.length < 2) {
      throw new Error(`Only found ${arrayData.length} rows in array format`);
    }
    
    // Debug: show first few rows
    console.log('📊 First 5 rows:');
    arrayData.slice(0, 5).forEach((row, index) => {
      console.log(`Row ${index}:`, row?.slice(0, 6)); // Show first 6 columns
    });
    
    // Convert array data to objects
    const headers = arrayData[0];
    console.log('📊 Headers:', headers);
    
    if (!headers || headers.length === 0) {
      throw new Error('No headers found');
    }
    
    const dataRows = arrayData.slice(1);
    console.log(`📊 Processing ${dataRows.length} data rows...`);
    
    const rawData = dataRows.map((row, rowIndex) => {
      const obj = {};
      headers.forEach((header, colIndex) => {
        obj[header] = row[colIndex];
      });
      
      // Debug first few objects
      if (rowIndex < 3) {
        const sampleKeys = Object.keys(obj).slice(0, 4);
        const sampleData = {};
        sampleKeys.forEach(key => sampleData[key] = obj[key]);
        console.log(`📊 Row ${rowIndex + 1} object:`, sampleData);
      }
      
      return obj;
    }).filter(row => {
      // Check if row has meaningful data (not just empty cells)
      const hasSignificantData = Object.values(row).some(val => 
        val != null && 
        val !== '' && 
        val !== undefined &&
        String(val).trim() !== ''
      );
      return hasSignificantData;
    });
    
    console.log(`📋 Successfully parsed ${rawData.length} valid data rows`);
    
    if (rawData.length === 0) {
      // If no data found, let's inspect the raw cells
      console.log('🔍 No data found, inspecting raw cells...');
      
      // Check some specific cells
      for (let row = 0; row < Math.min(10, decoded.e.r + 1); row++) {
        for (let col = 0; col < Math.min(6, decoded.e.c + 1); col++) {
          const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
          const cell = worksheet[cellAddress];
          if (cell) {
            console.log(`Cell ${cellAddress}:`, cell.v || cell.w || cell);
          }
        }
      }
      
      throw new Error('No valid data rows found after parsing');
    }
    
    return rawData;
    
  } catch (error) {
    console.error('❌ Excel parsing error:', error.message);
    throw new Error(`Failed to parse Excel file: ${error.message}`);
  }
};

const processLotteryData = (rawData) => {
  console.log('🔄 Processing lottery data...');
  
  const processedData = rawData.map(row => {
    const results = [];
    
    // Process each prize (1st through 5th)
    for (let i = 1; i <= 5; i++) {
      const valueKey = `${i}º prêmio`;
      const priceKey = `Valor ${i}º prêmio`;
      
      if (row[valueKey]) {
        results.push({
          index: i,
          value: row[valueKey].toString().padStart(6, '0'),
          price: formatPrice(row[priceKey])
        });
      }
    }
    
    return {
      contest: parseInt(row['Extração']) || 0,
      date: formatDate(row['Data Sorteio']),
      results: results
    };
  }).filter(item => item.contest > 0 && item.results.length > 0);
  
  console.log(`✨ Processed ${processedData.length} valid contests`);
  return processedData;
};

const generateAPIEndpoints = (processedData, outputDir) => {
  console.log('🏗️  Generating API endpoints...');
  
  const apiDir = path.join(outputDir, 'api', 'federal');
  fs.mkdirSync(apiDir, { recursive: true });
  
  if (processedData.length === 0) {
    console.log('⚠️ No valid data to generate API endpoints');
    return {
      lottery: 'federal',
      totalContests: 0,
      latestContest: null,
      lastUpdated: new Date().toISOString(),
      error: 'No valid contest data found'
    };
  }
  
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

const generateIndexPage = (metadata, outputDir) => {
  console.log('📄 Generating index page...');
  
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
    <p><strong>Latest Contest:</strong> ${metadata.latestContest || 'N/A'}</p>
    
    <h2>📋 Available Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/latest/</h3>
        <p>Get the most recent lottery result</p>
        <a href="api/federal/latest.json" target="_blank">🔗 Try it</a>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/{contest}/</h3>
        <p>Get results for a specific contest number</p>
        ${metadata.latestContest ? `<a href="api/federal/${metadata.latestContest}/index.json" target="_blank">🔗 Try latest (${metadata.latestContest})</a>` : ''}
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/federal/{contest}/result/{index}</h3>
        <p>Get specific prize result (index: 1-5)</p>
        ${metadata.latestContest ? `<a href="api/federal/${metadata.latestContest}/result/1.json" target="_blank">🔗 Try latest 1st prize</a>` : ''}
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
};

const main = async () => {
  try {
    console.log('🎲 Starting Federal lottery data processing...');
    
    const downloadUrl = process.env.LOTTERY_URL || 'https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Federal';
    
    // Download Excel file
    const buffer = await downloadExcelFile(downloadUrl);
    
    // Parse Excel data
    const rawData = parseExcelData(buffer);
    
    // Process the data
    const processedData = processLotteryData(rawData);
    
    // Generate API structure
    const outputDir = './dist';
    const metadata = generateAPIEndpoints(processedData, outputDir);
    
    // Generate documentation page
    generateIndexPage(metadata, outputDir);
    
    console.log('🎉 API generation completed successfully!');
    console.log(`📈 Generated endpoints for ${metadata.totalContests} contests`);
    console.log(`🔄 Latest contest: ${metadata.latestContest}`);
    
  } catch (error) {
    console.error('❌ Error processing lottery data:', error.message);
    process.exit(1);
  }
};

// Run the script
main();