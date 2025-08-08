import json
import os
import shutil
import glob
from datetime import datetime

def create_github_pages():
    """Create GitHub Pages structure with API documentation."""
    
    # Create docs directory for GitHub Pages
    docs_dir = "docs"
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    os.makedirs(docs_dir)
    
    # Copy API files to docs
    if os.path.exists("v1"):
        shutil.copytree("v1", os.path.join(docs_dir, "v1"))
    
    # Create main index.html
    create_main_index(docs_dir)
    
    # Create API documentation
    create_api_docs(docs_dir)
    
    print(f"GitHub Pages structure created in {docs_dir}/")

def create_main_index(docs_dir):
    """Create main index.html page."""
    
    # Get available APIs
    api_types = []
    api_dir = os.path.join(docs_dir, "v1/lotteries")
    
    if os.path.exists(api_dir):
        for item in os.listdir(api_dir):
            item_path = os.path.join(api_dir, item)
            if os.path.isdir(item_path):
                index_file = os.path.join(item_path, "index.json")
                if os.path.exists(index_file):
                    try:
                        with open(index_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            api_types.append({
                                "type": item,
                                "count": data.get("count", 0),
                                "latest": data.get("latest_draw", {})
                            })
                    except:
                        pass
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brazilian Lottery API</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .endpoints {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }}
        .endpoint {{
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        .method {{
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            margin-right: 10px;
            font-weight: bold;
            font-size: 0.8em;
        }}
        .url {{
            color: #495057;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        .update-time {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
            color: #6c757d;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎲 Brazilian Lottery API</h1>
        <p>Static API for Brazilian lottery results - Updated automatically</p>
    </div>
    
    <div class="endpoints">
        <h2>🔗 API Endpoints</h2>
        <p>All endpoints return JSON data. CORS is enabled for browser requests.</p>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/v1/lotteries/{{lottery}}/index.json</span>
        </div>
        <p>Returns index with all available draws for a lottery type.</p>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/v1/lotteries/{{lottery}}/draws/{{number}}.json</span>
        </div>
        <p>Returns specific draw results by number.</p>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/v1/lotteries/{{lottery}}/draws/latest.json</span>
        </div>
        <p>Returns the most recent draw results.</p>
        
        <h3>Example URLs:</h3>
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url"><a href="v1/lotteries/federal/draws/1.json">api/federal/draws/1.json</a></span>
        </div>
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url"><a href="v1/lotteries/federal/draws/latest.json">api/federal/draws/latest.json</a></span>
        </div>
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url"><a href="v1/lotteries/federal/index.json">api/federal/index.json</a></span>
        </div>
    </div>
    
    <div class="update-time">
        Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
    </div>
    
    <div class="footer">
        <p>Data source: <a href="https://loterias.caixa.gov.br/" target="_blank">Caixa Econômica Federal</a></p>
        <p>This API is automatically updated daily via GitHub Actions</p>
    </div>
</body>
</html>"""

    with open(os.path.join(docs_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html_content)

def create_api_docs(docs_dir):
    """Create _config.yml for GitHub Pages."""
    
    config_content = """# GitHub Pages configuration
plugins:
  - jekyll-optional-front-matter

# CORS headers for API files
include:
  - "v1/**/*.json"

# Serve JSON files with correct MIME type
defaults:
  - scope:
      path: "v1"
    values:
      layout: null
"""
    
    with open(os.path.join(docs_dir, "_config.yml"), 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # Create .nojekyll to bypass Jekyll processing for API files
    with open(os.path.join(docs_dir, ".nojekyll"), 'w') as f:
        f.write("")

def main():
    """Main function."""
    print("Creating GitHub Pages structure...")
    create_github_pages()
    print("GitHub Pages structure created successfully!")

if __name__ == "__main__":
    main()
