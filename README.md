markdown

# 🤖 AI Data Analyst

**Interactive Data Analysis & Visualization Powered by Groq AI (Llama 4 Scout)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 What is this?

An intelligent data analysis tool that lets you upload CSV files and generate graphs using natural language. Just describe what chart you want, and the AI creates it for you - with interactive hover, zoom, and pan features!

**Example**: Upload sales data → Type "bar chart of revenue by region" → Get an interactive graph instantly.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **AI-Powered Graphs** | Generate visualizations from natural language descriptions |
| 📈 **Interactive Charts** | Plotly graphs with hover, zoom, pan, and download as HTML |
| 💰 **Smart Type Detection** | Automatically identifies percentages, money values, and counts |
| 🔒 **Secure Execution** | Code validation prevents malicious operations |
| ⚡ **Cached Responses** | Faster performance for repeated queries |
| 📊 **Multiple Formats** | Matplotlib, Seaborn, or Plotly visualizations |
| 💬 **Chat History** | Keep track of all generated graphs |

## 🎯 Quick Demo

User: "Show me a histogram of employee salaries"
AI: Generates interactive histogram with proper binning and labels

User: "Create a scatter plot of revenue vs profit with trend line"
AI: Creates scatter plot with OLS trend line and hover tooltips

User: "Bar chart of sales by department"
AI: Produces color-coded bar chart with value labels
text


## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Llama 4 Scout (Groq)
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy
- **Security**: AST-based code validation

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/tutorio.git
cd tutorio

2. Install dependencies
bash

pip install -r requirements.txt

3. Set up API key

Create a .streamlit/secrets.toml file:
toml

GROQ_API_KEY="your_groq_api_key_here"

Get your free API key from Groq Console
4. Run the app
bash

streamlit run app.py

🚀 Usage Guide
Step 1: Upload Data

    Click "Browse files" in the sidebar

    Select any CSV file

    AI automatically detects and converts data types

Step 2: Describe Graph
text

Examples:
• "Bar chart of sales by region"
• "Histogram of age distribution"
• "Scatter plot with trend line"
• "Line chart over time"
• "Box plot of salaries by department"

Step 3: Get Results

    Interactive graph appears instantly

    Download as HTML (Plotly) or PNG (Matplotlib)

    View the generated code

    Continue the conversation with more requests

📁 Project Structure
text

tutorio/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── .streamlit/
│   ├── secrets.toml      # API keys (git-ignored)
│   └── secrets.template.toml
├── ai/                   # AI graph generation
├── chat/                 # Chat history management
├── classifiers/          # Column type detection
├── converters/           # Data conversion logic
├── security/             # Code validation
└── utils/                # Helper functions

🔒 Security Features

    ✅ AST-based code validation

    ✅ Restricted Python imports (no os, sys, subprocess)

    ✅ CSV injection protection

    ✅ Maximum code length limits

    ✅ Dangerous pattern detection

    ✅ No file system access

🎨 Example Graphs You Can Create
Graph Type	Example Query
Bar Chart	"Average salary by department"
Histogram	"Distribution of customer ages"
Scatter Plot	"Revenue vs Marketing Spend"
Line Chart	"Monthly sales trend"
Box Plot	"Salary ranges by job title"
Pie Chart	"Market share by product"
Heatmap	"Correlation between variables"
Area Chart	"Cumulative growth over time"
🤝 Contributing

Contributions are welcome! Here's how:

    Fork the repository

    Create a feature branch (git checkout -b feature/AmazingFeature)

    Commit changes (git commit -m 'Add AmazingFeature')

    Push to branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📝 License

Distributed under the MIT License. See LICENSE file for more information.
🙏 Acknowledgments

    Groq for providing fast AI inference

    Streamlit for the amazing framework

    Plotly for interactive visualizations

⚠️ Important Notes

    API Key Security: Never commit secrets.toml to version control

    Rate Limits: Groq free tier: 30 requests per minute, 6,000 tokens per minute

    File Size: Maximum 100,000 rows and 100 columns

    Data Privacy: Your data never leaves your machine (API calls only for graph generation)

🐛 Troubleshooting
"No module named 'plotly'"
bash

pip install plotly

"API key not found"

Create .streamlit/secrets.toml with your Groq API key
"Graph generation failed"

    Check your internet connection

    Verify API key is valid

    Try a simpler graph description

"CSV upload fails"

    Ensure file is valid CSV format

    Check for special characters

    Reduce file size if too large

📞 Support

    📧 Issues: GitHub Issues

    💬 Discussions: GitHub Discussions

🌟 Star History

If you find this useful, please star the repository! ⭐

Built with 🧠 by DeepSeek | Powered by Groq AI
text


## Also create a `LICENSE` file (optional but recommended):

```markdown
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
