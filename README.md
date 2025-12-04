AI-Powered tool for comparing telecom BSS (Business Support Systems) requirements across different customer implementations using LLM and CrewAI.

## Overview

This system helps telecom BSS teams compare new customer requirements against existing implementations to identify:
- ✅ **Exact Matches**: Features that can be reused as-is
- ⚠️ **Similar Features**: Features that need adaptation
- 🆕 **Delta**: Completely new features requiring fresh implementation

## Features

- 🤖 **AI-Powered Comparison**: Uses OpenAI embeddings and GPT-4 for intelligent feature matching
- 🎯 **Semantic Similarity**: Goes beyond keyword matching to understand feature intent
- 📊 **Beautiful Reports**: Generates professional HTML and Markdown reports
- 💡 **Strategic Recommendations**: CrewAI agents provide implementation guidance
- 🚀 **Fast & Scalable**: Handles documents with 100+ features efficiently
- 📈 **Reusability Metrics**: Calculates effort savings and ROI

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Document Parser                             │
│         (Markdown/Structured Text)                       │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│         LLM Comparison Engine (CrewAI)                   │
│   - Feature Extraction Agent                             │
│   - Similarity Analysis Agent                            │
│   - Report Compiler Agent                                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│            Report Generator                              │
│         (HTML/Markdown/JSON)                             │
└─────────────────────────────────────────────────────────┘
```

## Installation

### Step 1: Create Virtual Environment

```powershell
# Windows
python -m venv hackathon
.\hackathon\Scripts\activate

# Linux/Mac
python3 -m venv hackathon
source hackathon/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Configuration

Edit `config/config.yaml` to customize:
- LLM model and parameters
- Similarity thresholds
- Report formatting
- Output settings

```yaml
llm:
  model: "gpt-4"
  temperature: 0.3

comparison:
  exact_match_threshold: 0.95
  similar_match_threshold: 0.70
```

## Usage

### Basic Comparison

Compare Sprint requirements against Verizon implementation:

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md
```

### Generate Both HTML and Markdown

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --format both
```

### Custom Output Location

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --output reports/sprint_vs_verizon.html
```

### Batch Comparison

Compare against multiple existing implementations:

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing-dir data/
```

### Adjust Similarity Threshold

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --threshold 0.75
```

### Fast Mode (Skip AI Recommendations)

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --no-recommendations
```

### Verbose Output

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --verbose
```

## Document Format

### Supported Formats

The system supports structured markdown documents with features listed as:

**Numbered Lists** (Recommended):
```markdown
1. **Feature Name**
   Description of the feature with details...

2. **Another Feature**
   More details...
```

**Headers**:
```markdown
## Feature Name
Description...

## Another Feature
Description...
```

**Bullet Points**:
```markdown
- **Feature Name**: Description...
- **Another Feature**: Description...
```

## Output Reports

### HTML Report

Professional, interactive HTML report with:
- Executive summary dashboard
- Color-coded statistics cards
- Detailed match tables
- Gap analysis for similar features
- Strategic recommendations
- Implementation impact summary

### Markdown Report

Clean markdown format suitable for:
- Version control (Git)
- Documentation wikis
- Technical reviews
- Email distribution

## Project Structure

```
Hackathonhackathon/
├── src/
│   ├── __init__.py
│   ├── models.py              # Data models
│   ├── parser.py              # Document parser
│   ├── comparison_engine.py   # AI comparison engine
│   ├── comparator.py          # Main orchestrator
│   ├── report_generator.py    # Report generation
│   └── utils.py               # Utilities
├── cli/
│   └── compare_requirements.py # CLI interface
├── config/
│   └── config.yaml            # Configuration
├── data/
│   ├── requirements_sprint.md     # Sample new requirements
│   ├── implemented_verizon.md    # Sample implementation
│   └── implemented_att.md        # Another sample
├── outputs/
│   └── comparison_reports/    # Generated reports
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── PROJECT_README.md         # This file
```

## How It Works

### 1. Document Parsing
- Extracts features from markdown files
- Supports numbered lists, headers, bullet points
- Normalizes text for comparison

### 2. AI Comparison
- Creates embeddings using OpenAI `text-embedding-ada-002`
- Calculates semantic similarity (cosine similarity)
- Categorizes matches based on thresholds:
  - ≥95% = Exact match
  - 70-95% = Similar (needs adaptation)
  - <70% = Delta (new feature)

### 3. Gap Analysis
- For similar features, GPT-4 analyzes the gaps
- Identifies what needs to be added/modified
- Provides actionable insights

### 4. Strategic Recommendations
- CrewAI agents analyze overall comparison
- Generate implementation strategy
- Prioritization suggestions
- Risk assessment

### 5. Report Generation
- Beautiful HTML with charts and styling
- Markdown for technical teams
- Exportable statistics

## Example Output

```
================================================================================
COMPARISON COMPLETE
================================================================================

📊 Results:
  ✅ Exact Matches: 10 (40.0%)
  ⚠️  Similar Features: 5 (20.0%)
  🆕 Delta (New): 10 (40.0%)
  📈 Reusability Score: 60.0%

📄 Reports generated:
  - HTML: outputs/comparison_reports/comparison_20251130_120000.html

================================================================================
```

## API Usage (Python)

```python
from src.comparator import FeatureComparator
from src.report_generator import ReportGenerator

# Initialize
comparator = FeatureComparator("config/config.yaml")

# Compare documents
result = comparator.compare_documents(
    "data/requirements_sprint.md",
    "data/implemented_verizon.md"
)

# Generate report
report_gen = ReportGenerator(comparator.config)
files = report_gen.generate(result, output_format="html")

print(f"Reusability: {result.statistics['reusability_score']:.1f}%")
```

## Testing

Run sample comparison:

```bash
python cli/compare_requirements.py \
  --new data/requirements_sprint.md \
  --existing data/implemented_verizon.md \
  --verbose
```

Expected output:
- Comparison report in `outputs/comparison_reports/`
- Log file: `comparison.log`

## Troubleshooting

### Error: "No features extracted"
- Check document format (numbered lists work best)
- Ensure file is markdown (.md)
- Verify features have clear structure

### Error: "API key not found"
- Set `OPENAI_API_KEY` in `.env` file
- Verify environment is activated

### Low similarity scores
- Adjust threshold with `--threshold` flag
- Check if features use different terminology
- Review gap analysis for insights

## Performance

- **Small documents** (10-20 features): ~30 seconds
- **Medium documents** (50-100 features): ~2-3 minutes
- **Large documents** (100+ features): ~5-10 minutes

*Times include AI processing and report generation*

## Cost Estimation

OpenAI API costs (approximate):
- Small comparison (20 features): ~$0.10
- Medium comparison (50 features): ~$0.25
- Large comparison (100 features): ~$0.50

*Prices based on GPT-4 and embedding API rates*

## Future Enhancements

- [ ] Web UI for non-technical users
- [ ] Support for Word/PDF documents
- [ ] Integration with JIRA/Confluence
- [ ] Batch processing automation
- [ ] Custom ML model training
- [ ] Multi-language support

## License

Proprietary - hackathon Systems

## Support

For issues or questions:
- Create issue in project repository
- Contact: BSS Development Team
- Email: bss-dev@hackathon.com

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Acknowledgments

- OpenAI for GPT-4 and embeddings API
- CrewAI framework for multi-agent orchestration
- LangChain for LLM integration

---

**Built for hackathon AI Hackathon 2025**
