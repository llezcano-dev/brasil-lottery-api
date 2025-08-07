# 🎲 Brasil Lottery API

A static API for Brazilian lottery results, automatically updated via GitHub Actions.

## 📋 API Endpoints

Base URL: `https://yourusername.github.io/brasil-lottery-api`

### Get Latest Result
```
GET /api/federal/latest/
```

### Get Specific Contest
```
GET /api/federal/{contest}/
```

### Get Specific Prize Result
```
GET /api/federal/{contest}/result/{index}
```
Where `index` is 1-5 (1st through 5th prize)

## 📊 Response Format

### Contest Data
```json
{
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
}
```

### Individual Prize
```json
{
  "value": "005349",
  "price": 200000.00
}
```

## 🚀 Setup

1. **Fork this repository**

2. **Enable GitHub Pages**
   - Go to Settings > Pages
   - Source: GitHub Actions

3. **Configure the workflow** (optional)
   - Edit `.github/workflows/update-lottery-api.yml`
   - Modify the cron schedule if needed

4. **Run the workflow**
   - Go to Actions tab
   - Run "Update Lottery API" manually or wait for scheduled run

## 🔄 How it Works

1. **Data Source**: Downloads Excel file from Caixa API
2. **Processing**: Converts Excel data to JSON format
3. **API Generation**: Creates static JSON files for each endpoint
4. **Deployment**: Deploys to GitHub Pages automatically

## 📅 Update Schedule

The API updates automatically twice daily at:
- 8:00 AM UTC (5:00 AM BRT)
- 8:00 PM UTC (5:00 PM BRT)

You can also trigger updates manually from the Actions tab.

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Generate API locally
npm run build

# Serve locally
npm run dev
```

Visit `http://localhost:3000` to see your API.

## 📁 Generated Structure

```
dist/
├── index.html                    # API documentation
├── api/
│   ├── meta.json                # API metadata
│   └── federal/
│       ├── latest.json          # Latest result
│       ├── 1/
│       │   ├── index.json       # Contest 1 data
│       │   └── result/
│       │       ├── 1.json       # 1st prize
│       │       ├── 2.json       # 2nd prize
│       │       └── ...
│       ├── 2/
│       │   └── ...
│       └── ...
```

## 🎯 Features

- ✅ **Zero server costs** - Static files hosted on GitHub Pages
- ✅ **Automatic updates** - Runs via GitHub Actions
- ✅ **Fast response times** - CDN-cached JSON files
- ✅ **RESTful API** - Clean, predictable endpoints
- ✅ **Historical data** - Access to all past contests
- ✅ **Individual prizes** - Query specific prize positions

## 🌐 CORS

All endpoints include CORS headers, so you can use this API from any frontend application.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `npm run dev`
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Note**: This API is for educational/personal use. The lottery data belongs to Caixa Econômica Federal.