# NIST Compliance Workflow: Automated Security Update Monitor

**Stop manually tracking NIST security updates.** This tool automatically monitors NIST publications, finds what matters for your development team, and creates ready-to-review compliance reports.

Perfect for IT teams, security professionals, and organizations that need to stay current with cybersecurity frameworks like NIST SP 800-53, 800-171, and 800-218.

## What This Tool Does

Think of this as your personal NIST research assistant. It:

1. **Searches** the latest NIST cybersecurity publications
2. **Analyzes** which updates are relevant to software development teams
3. **Summarizes** complex security guidance into actionable recommendations
4. **Creates** GitHub pull requests with professional compliance reports
5. **Saves you hours** of manual research every week

## Who Should Use This

- **Security teams** who need to track NIST compliance requirements
- **Software development teams** working on government or regulated systems
- **IT managers** responsible for cybersecurity framework compliance
- **Compliance officers** who need regular NIST update reports
- **Anyone** who finds NIST publications overwhelming but necessary

## Quick Start (5 Minutes)

### Prerequisites

You'll need these accounts and tools:
- Python 3.11 or newer
- GitHub account (for storing reports)
- OpenAI account (for AI analysis) - optional but recommended
- Git installed on your computer

### Step 1: Get Your Repository

Clone this repository to your computer:

```bash
git clone https://github.com/Yeswanth2878/nist-compliance-reports.git
cd nist-compliance-reports
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 3: Set Up Your API Keys

Create a file called `.env` in the project folder:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your actual credentials:

```
# Required: Your OpenAI API key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required: GitHub token (get from https://github.com/settings/tokens)
GITHUB_TOKEN=github_pat_your-github-token-here

# Required: Your GitHub repository for reports
GITHUB_REPO=your-username/nist-compliance-reports

# Optional: Google Search (for enhanced article discovery)
GOOGLE_API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id
```

**Getting your API keys:**
- **OpenAI:** Sign up at OpenAI, go to API Keys, create a new key
- **GitHub:** Go to Settings > Developer Settings > Personal Access Tokens > Generate new token (need 'repo' permissions)

### Step 4: Test It

Run a quick test to make sure everything works:

```bash
# Test with a simple topic
python main.py --topic "cybersecurity framework" --max-articles 3
```

You should see the tool search for articles, analyze them, and create a summary.

### Step 5: Start the Web Service

```bash
# Start the web API
python main.py --server --port 8000
```

Visit `http://localhost:8000/docs` to see the interactive API documentation.

## How to Use

### Method 1: Command Line (Simple)

Run one-time reports directly from your terminal:

```bash
# Get updates on a specific topic
python main.py --topic "secure software development" --max-articles 5

# Get general NIST updates
python main.py --max-articles 10

# Focus on supply chain security
python main.py --topic "supply chain security" --max-articles 3
```

### Method 2: Web API (Advanced)

Start the web service and make API calls:

```bash
# Start the service
python main.py --server --port 8000
```

Then use curl or any API client:

```bash
curl -X POST "http://localhost:8000/workflow/run" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "DevOps security",
    "max_articles": 7
  }'
```

### Method 3: Docker (Production)

For production deployments:

```bash
# Build the container
docker build -t nist-workflow .

# Run with environment file
docker run -d --name nist-workflow --env-file .env -p 8000:8000 nist-workflow
```

## Understanding the Output

The tool creates comprehensive reports with:

**Executive Summary:** High-level overview of what's changed
**Latest Updates:** Specific NIST publications with dates and versions  
**Action Items:** Practical steps your team should take
**Control Mappings:** How updates relate to specific NIST controls (800-53, 800-171, 800-218)
**Implementation Guidance:** Concrete recommendations for your environment

Each report gets automatically published as a GitHub Pull Request, making it easy to:
- Review with your team
- Track compliance over time  
- Archive decisions and implementations

## Configuration Options

### Search Behavior

Control how the tool searches for content:

```python
# In main.py, modify these settings:
NIST_SEARCH_TERMS = [
    "NIST SP 800-53",           # Security controls
    "NIST SP 800-171",          # CUI protection  
    "NIST SP 800-218",          # Secure software development
    "cybersecurity framework",   # General framework updates
    "your custom terms here"     # Add your specific interests
]
```

### Relevance Filtering

Adjust which articles are considered relevant to your organization:

- The tool automatically filters for software development relevance
- Looks for keywords like: CI/CD, DevOps, SAST, DAST, containers, cloud security
- You can modify the keyword list in `_keyword_based_relevance()` method

### Output Customization

Modify the summary template in `_generate_fallback_summary()` to match your organization's needs.

## Scheduling Automated Reports

### Option 1: Cron Job (Linux/Mac)

```bash
# Edit your crontab
crontab -e

# Add this line for weekly reports every Monday at 9 AM
0 9 * * 1 cd /path/to/nist-workflow && python main.py --topic "weekly update" --max-articles 10
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (weekly/monthly)
4. Set action to run your Python script

### Option 3: GitHub Actions

Create `.github/workflows/nist-reports.yml`:

```yaml
name: Weekly NIST Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:      # Manual trigger

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Generate NIST report
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_REPO: ${{ github.repository }}
      run: python main.py --max-articles 15
```

## Troubleshooting

### "No NIST updates found"

**Cause:** The tool can't reach NIST websites or your search terms are too specific.

**Solutions:**
- Check your internet connection
- Try broader search terms like "cybersecurity" or "framework"
- The tool includes demo data as a fallback for testing

### "GitHub not configured"  

**Cause:** Your GitHub credentials aren't set up correctly.

**Solutions:**
- Verify your `.env` file has the correct `GITHUB_TOKEN` and `GITHUB_REPO`
- Make sure the repository exists and you have write access
- Check that your GitHub token has 'repo' permissions

### "OpenAI quota exceeded"

**Cause:** You've hit your OpenAI usage limits.

**Solutions:**
- The tool automatically falls back to keyword-based analysis
- Add credits to your OpenAI account for AI-powered summaries
- Consider using the tool less frequently

### Environment variables not loading

**Cause:** The `.env` file isn't being read properly.

**Solutions:**
- Make sure the `.env` file is in the same folder as `main.py`
- Check there are no extra spaces or quotes in your `.env` file
- Try setting environment variables directly in your terminal

## API Reference

### POST /workflow/run

Triggers a complete NIST compliance workflow.

**Request Body:**
```json
{
  "topic": "secure software development",
  "max_articles": 10
}
```

**Response:**
```json
{
  "status": "success",
  "summary_url": "https://github.com/user/repo/blob/branch/file.md",
  "pr_url": "https://github.com/user/repo/pull/123",
  "articles_processed": 8
}
```

### GET /health

Check if the service is running properly.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-17T10:30:00"
}
```

## Cost Considerations

**Free tier usage:**
- GitHub: Unlimited public repositories
- OpenAI: $5-20/month depending on usage
- Google Search: 100 queries/day free

**Typical monthly costs for a team:**
- Small team (weekly reports): $10-30/month
- Medium team (bi-weekly reports): $20-50/month  
- Enterprise (daily monitoring): $50-150/month

The tool is designed to be cost-effective by using intelligent fallbacks and caching.

## Security and Privacy

**Data handling:**
- No NIST content is permanently stored
- API keys are only used for their intended services
- All processing happens on your infrastructure

**Best practices:**
- Use environment variables for all secrets
- Regularly rotate your API keys
- Run on private networks in production
- Review generated reports before acting on recommendations

## Contributing

Found a bug or want to add a feature?

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Common improvements we welcome:**
- Additional NIST data sources
- Better content filtering
- New output formats (PDF, Slack, email)
- Integration with other compliance tools

## Support

**Having trouble?** Here's how to get help:

1. **Check the troubleshooting section** above
2. **Look at existing issues** on GitHub
3. **Create a new issue** with:
   - What you were trying to do
   - What happened instead
   - Your environment (OS, Python version)
   - Relevant log output

**For urgent issues:** Include "URGENT" in your issue title.

## License

This project is licensed under the MIT License. You're free to use, modify, and distribute it for both commercial and non-commercial purposes.

## Acknowledgments

Built with:
- **FastAPI** for the web framework
- **OpenAI** for intelligent content analysis  
- **NIST** for providing comprehensive cybersecurity guidance
- **BeautifulSoup** for web content extraction
- **PyGithub** for repository automation

Special thanks to the cybersecurity community for making compliance guidance accessible and actionable.

---

**Ready to automate your NIST compliance monitoring?** Start with the Quick Start guide above, and you'll have automated reports running in minutes.
