# Brazilian Lottery API

🎲 Automated static API for Brazilian lottery results, powered by GitHub Actions and GitHub Pages.

## Features

- ✅ **Automated daily updates** via GitHub Actions
- ✅ **Static API** served via GitHub Pages
- ✅ **Latest endpoint** for most recent results
- ✅ **Multiple lottery types** support
- ✅ **Clean JSON structure** with ISO dates and numeric values
- ✅ **CORS enabled** for browser requests

## API Endpoints

Base URL: `https://yourusername.github.io/your-repo-name/`

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{lottery}/index.json` | List all contests for a lottery |
| GET | `/api/{lottery}/contest/{number}.json` | Get specific contest by number |
| GET | `/api/{lottery}/contest/latest.json` | Get latest contest results |

### Example URLs

- `https://yourusername.github.io/your-repo/api/federal/contest/1.json`
- `https://yourusername.github.io/your-repo/api/federal/contest/latest.json` 
- `https://yourusername.github.io/your-repo/api/federal/index.json`

## Setup Instructions

### 1. Repository Setup

1. **Create a new GitHub repository**
2. **Clone and add files:**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

3. **Add all the Python scripts** to your repository:
   - `lottery_downloader.py`
   - `xlsx_to_csv.py` (your existing script)
   - `csv_to_api.py` (your updated script)
   - `create_latest_endpoint.py`
   - `create_github_pages.py`

4. **Add the workflow file** at `.github/workflows/update-lottery-api.yml`

### 2. GitHub Pages Setup

1. **Enable GitHub Pages:**
   - Go to your repo → Settings → Pages
   - Source: "GitHub Actions"
   - Save

2. **Repository permissions:**
   - Go to Settings → Actions → General
   - Workflow permissions: "Read and write permissions"
   - Allow GitHub Actions to create and approve pull requests: ✅

### 3. File Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── update-lottery-api.yml
├── lottery_downloader.py
├── xlsx_to_csv.py
├── csv_to_api.py
├── create_latest_endpoint.py
├── create_github_pages.py
└── README.md
```

### 4. First Run

1. **Push your code:**
   ```bash
   git add .
   git commit -m "Add lottery API automation"
   git push origin main
   ```

2. **Manual trigger** (optional):
   - Go to Actions tab in your GitHub repo
   - Click "Update Lottery API"
   - Click "Run workflow"

3. **Check your API:**
   - Visit: `https://yourusername.github.io/your-repo/`
   - Your API will be available at: `https://yourusername.github.io/your-repo/api/`

## JSON Response Format

```json
{
  "contest": "123",
  "date": "2024-01-15",
  "results": [
    {
      "index": 1,
      "value": "012345",
      "reward": 200000.0
    },
    {
      "index": 2,
      "value": "067890",
      "reward": 8000.0
    }
  ]
}
```

## Automation Schedule

- **Daily updates** at 2 AM UTC
- **Manual trigger** available in GitHub Actions
- **Automatic deployment** to GitHub Pages

## Adding More Lotteries

To add more lottery types, modify the workflow file:

```yaml
- name: Download lottery data
  run: |
    python lottery_downloader.py Federal federal
    python lottery_downloader.py Megasena megasena
    python lottery_downloader.py Lotofacil lotofacil

- name: Convert Excel to CSV
  run: |
    python xlsx_to_csv.py federal.xlsx federal.csv
    python xlsx_to_csv.py megasena.xlsx megasena.csv
    python xlsx_to_csv.py lotofacil.xlsx lotofacil.csv

- name: Generate API files
  run: |
    python csv_to_api.py federal.csv
    python csv_to_api.py megasena.csv
    python csv_to_api.py lotofacil.csv
```

## CORS Support

The API includes CORS headers for browser requests. You can fetch data directly from JavaScript:

```javascript
// Fetch latest federal lottery results
fetch('https://yourusername.github.io/your-repo/api/federal/contest/latest.json')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Troubleshooting

### Workflow fails
- Check Actions tab for error messages
- Ensure all Python scripts are in the repository
- Verify GitHub Pages is enabled with "GitHub Actions" source

### API not accessible  
- Wait 5-10 minutes after workflow completion
- Check if GitHub Pages deployment succeeded
- Verify the URL format matches your repository name

### Missing latest endpoint
- Ensure `create_latest_endpoint.py` runs after API generation
- Check if contest data exists in the generated files

## Data Source

Data is sourced from [Caixa Econômica Federal](https://loterias.caixa.gov.br/) official API.

## License

MIT License - Feel free to use and modify as needed.