# NIST SP 800 Compliance Update Workflow

**An Agentic AI system that automatically finds, analyzes, and reports on NIST security updates for software development teams.**

This tool solves a simple problem: keeping up with NIST cybersecurity requirements is time-consuming and confusing. Instead of manually checking for updates, this system does it automatically and tells you exactly what matters for your development team.

## What This Does

The system performs five main tasks automatically:

**1. Finds Latest Updates**
- Searches the internet for new NIST SP 800-series publications
- Looks at official NIST sources and relevant security sites
- You can search for specific topics or let it find general updates

**2. Extracts Content**  
- Pulls the full text from NIST documents and articles
- Converts everything to clean, readable Markdown format

**3. Filters for Relevance**
- Uses AI to identify content relevant to software development teams
- Focuses on things like CI/CD security, code review practices, container security
- Ignores generic policy stuff that doesn't affect developers

**4. Creates Summaries**
- Generates clear, one-page reports in plain English
- Shows what's new, why it matters, and what you should do about it
- Maps updates to specific NIST controls (SP 800-53, 800-171, 800-218)
- Includes direct links to original sources

**5. Publishes Results**
- Automatically creates GitHub Pull Requests with the reports
- Each report is ready for team review and discussion
- Keeps a history of all compliance updates over time

## Quick Start

**You need:**
- Python 3.11+
- GitHub account (for storing reports)
- OpenAI API key (for AI analysis)

**Setup (5 minutes):**

1. Clone this repository
```bash
git clone https://github.com/your-username/nist-compliance-workflow
cd nist-compliance-workflow
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create your `.env` file with API keys
```bash
cp .env.example .env
# Edit .env with your actual keys
```

4. Test it
```bash
python main.py --topic "cybersecurity framework" --max-articles 5
```

That's it. The system will find NIST updates, analyze them, and create a report in your GitHub repository.

## How to Use It

**Command Line (Simple)**
```bash
# Get updates on a specific topic
python main.py --topic "secure software development" --max-articles 10

# Get general NIST updates  
python main.py --max-articles 15
```

**Web API (Advanced)**
```bash
# Start the web service
python main.py --server --port 8000

# Make API calls
curl -X POST "http://localhost:8000/workflow/run" \
  -H "Content-Type: application/json" \
  -d '{"topic": "DevOps security", "max_articles": 8}'
```

**Docker (Production)**
```bash
# Build and run
docker build -t nist-workflow .
docker run -d --env-file .env -p 8000:8000 nist-workflow
```

## Where to Find Your Reports

**Main Output: GitHub Pull Requests**
- Go to `https://github.com/your-username/nist-compliance-reports/pulls`
- Each run creates a new PR with a complete compliance report
- Reports include analysis, recommendations, and action items

**API Responses**
- Web API returns direct links to the generated reports
- Click the `pr_url` to see the full analysis

The real value is in those GitHub pull requests - they contain professional compliance reports that your team can review and act on.

**Sample Outputs Available**
- Check the branches of this repository to see real examples
- Each branch contains actual reports generated from successful test runs
- Examples include different topics like "cybersecurity framework", "secure software development", and "DevOps security"
- These show exactly what your reports will look like after the system processes NIST updates

## What You Get

Each report includes:

- **Executive Summary**: What's changed and why it matters
- **Latest Updates**: New NIST publications with dates and versions
- **Action Items**: Specific steps for your development team
- **Control Mappings**: How updates relate to NIST SP 800-53, 800-171, and 800-218
- **Source Citations**: Direct links to original NIST documents

## Configuration

**API Keys Required:**
```bash
# In your .env file:
OPENAI_API_KEY=your-openai-key        # For AI analysis
GITHUB_TOKEN=your-github-token        # For creating reports  
GITHUB_REPO=username/repo-name        # Where to store reports
```

**Optional Enhancements:**
```bash
GOOGLE_API_KEY=your-google-key        # For better search results
SEARCH_ENGINE_ID=your-search-id       # Google Custom Search
```

**Sample search Engine id : 933ef038d2c96438c which is personalised to search in NIST relaated websites**
## Technical Details

**Built With:**
- FastAPI for the web interface
- OpenAI for intelligent content analysis
- PyGithub for automated report publishing
- BeautifulSoup for content extraction
- Docker for easy deployment

**Architecture:**
- Containerized service that can run anywhere
- REST API with interactive documentation
- Automated fallbacks if external services fail
- Keyword-based analysis when AI isn't available

## Deployment Options

**Local Development:**
```bash
python main.py --server --port 8000
```

**Docker Container:**
```bash
docker build -t nist-workflow .
docker run -d --env-file .env -p 8000:8000 nist-workflow
```

**Scheduled Automation:**
- Add cron jobs for weekly reports
- Use GitHub Actions for automated scheduling
- Deploy to cloud services for 24/7 monitoring

## Troubleshooting

**"No NIST updates found"**
- Check your internet connection
- Try broader search terms
- The system includes demo data for testing

**"GitHub not configured"**
- Verify your `.env` file has correct GitHub credentials
- Make sure the target repository exists
- Check that your GitHub token has proper permissions

**Environment variables not loading**
- Ensure `.env` file is in the same directory as `main.py`
- Restart the service after changing environment variables
- Check for typos in variable names

## What's Next

This foundation enables several powerful enhancements:

- **Conversational Interface**: Ask questions like "What NIST updates affect our Docker setup?"
- **Interactive Dashboard**: Visual compliance tracking and team collaboration
- **Smart Integration**: Connect with Slack, Jira, and security tools
- **Custom Analysis**: Train the AI on your specific environment and needs

The current system provides solid automated NIST monitoring. These future features would make it feel more like having a knowledgeable compliance assistant on your team.

## Contributing

Found a bug or want to add features? Pull requests welcome.


---

**Ready to automate your NIST compliance tracking?** Follow the Quick Start guide above and you'll have reports running in minutes.






