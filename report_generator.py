"""
Report generator for creating markdown and HTML comparison reports
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict
import json

from .models import ComparisonResult, MatchPair, Feature
from .utils import format_percentage, ensure_directory

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comparison reports in multiple formats"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = config.get('output', {}).get('directory', 'outputs/comparison_reports')
        ensure_directory(self.output_dir)

    def generate(
        self,
        result: ComparisonResult,
        output_format: str = "both",
        output_path: str = None,
        recommendations: list = None
    ) -> Dict[str, str]:
        """
        Generate comparison report

        Args:
            result: ComparisonResult object
            output_format: 'markdown', 'html', or 'both'
            output_path: Custom output path (optional)
            recommendations: List of recommendations (optional)

        Returns:
            Dictionary with paths to generated files
        """
        logger.info(f"Generating {output_format} report...")

        generated_files = {}

        # Generate markdown
        if output_format in ['markdown', 'both']:
            md_path = self.generate_markdown(result, output_path, recommendations)
            generated_files['markdown'] = md_path

        # Generate HTML
        if output_format in ['html', 'both']:
            html_path = self.generate_html(result, output_path, recommendations)
            generated_files['html'] = html_path

        logger.info(f"Report generation complete: {generated_files}")
        return generated_files

    def generate_markdown(
        self,
        result: ComparisonResult,
        output_path: str = None,
        recommendations: list = None
    ) -> str:
        """Generate markdown report"""

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.output_dir}/comparison_{timestamp}.md"

        # Build report content
        content = self._build_markdown_content(result, recommendations)

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Markdown report saved: {output_path}")
        return output_path

    def generate_html(
        self,
        result: ComparisonResult,
        output_path: str = None,
        recommendations: list = None
    ) -> str:
        """Generate HTML report"""

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.output_dir}/comparison_{timestamp}.html"

        # Build HTML content
        content = self._build_html_content(result, recommendations)

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"HTML report saved: {output_path}")
        return output_path

    def _build_markdown_content(
        self,
        result: ComparisonResult,
        recommendations: list = None
    ) -> str:
        """Build markdown content"""

        stats = result.statistics

        md = f"""# BSS Requirements Comparison Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Documents Compared

- **New Requirements:** {result.new_document} ({result.new_features_count} features)
- **Existing Implementation:** {result.existing_document} ({result.existing_features_count} features)

---

## Executive Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| ✅ Exact Matches | {stats['exact_matches_count']} | {format_percentage(stats['exact_match_percentage'])} |
| ⚠️ Similar Features | {stats['similar_matches_count']} | {format_percentage(stats['similar_match_percentage'])} |
| 🆕 Delta (New Features) | {stats['delta_count']} | {format_percentage(stats['delta_percentage'])} |
| **📊 Reusability Score** | **{stats['exact_matches_count'] + stats['similar_matches_count']}** | **{format_percentage(stats['reusability_score'])}** |

---

## Detailed Analysis

### ✅ Exact Matches ({len(result.exact_matches)})

These features can be reused as-is from the existing implementation:

"""

        # Exact matches table
        if result.exact_matches:
            md += "\n| # | New Feature | Existing Feature | Similarity |\n"
            md += "|---|-------------|------------------|------------|\n"

            for i, match in enumerate(result.exact_matches, 1):
                md += f"| {i} | {match.new_feature.title} | {match.existing_feature.title} | {format_percentage(match.similarity_score * 100)} |\n"
        else:
            md += "\n*No exact matches found.*\n"

        # Similar features
        md += f"\n\n### ⚠️ Similar Features Requiring Adaptation ({len(result.similar_features)})\n\n"
        md += "These features have existing implementations but require modifications:\n\n"

        if result.similar_features:
            for i, match in enumerate(result.similar_features, 1):
                md += f"#### {i}. {match.new_feature.title}\n\n"
                md += f"**Existing Feature:** {match.existing_feature.title}\n\n"
                md += f"**Similarity:** {format_percentage(match.similarity_score * 100)}\n\n"

                if match.gap_analysis:
                    md += f"**Gap Analysis:**\n{match.gap_analysis}\n\n"

                md += "---\n\n"
        else:
            md += "*No similar features found.*\n\n"

        # Delta features
        md += f"\n### 🆕 Delta - New Features to Implement ({len(result.delta_features)})\n\n"
        md += "These features have no existing implementation and require fresh development:\n\n"

        if result.delta_features:
            for i, feature in enumerate(result.delta_features, 1):
                md += f"{i}. **{feature.title}**\n"
                if feature.description and feature.description != feature.title:
                    md += f"   - {feature.description}\n"
        else:
            md += "*No delta features - all requirements have existing implementations!*\n"

        # Recommendations
        if recommendations and self.config.get('report', {}).get('include_recommendations', True):
            md += "\n\n---\n\n## Strategic Recommendations\n\n"
            for rec in recommendations:
                md += f"{rec}\n"

        # Summary
        md += "\n\n---\n\n## Implementation Impact Summary\n\n"
        md += f"- **Can Reuse Immediately:** {len(result.exact_matches)} features ({format_percentage(stats['exact_match_percentage'])})\n"
        md += f"- **Needs Adaptation:** {len(result.similar_features)} features (~30-50% effort vs new)\n"
        md += f"- **Build from Scratch:** {len(result.delta_features)} features (100% effort)\n\n"
        md += f"**Estimated Effort Savings:** {format_percentage(stats['reusability_score'] * 0.7)} compared to building everything from scratch\n"

        return md

    def _build_html_content(
        self,
        result: ComparisonResult,
        recommendations: list = None
    ) -> str:
        """Build HTML content with styling"""

        stats = result.statistics

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BSS Requirements Comparison Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .document-info {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}

        .document-info h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-card.exact {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.similar {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.delta {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .stat-card.reuse {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}

        .stat-card .emoji {{
            font-size: 3em;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .stat-card .label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stat-card .percentage {{
            font-size: 1.3em;
            margin-top: 5px;
            opacity: 0.8;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 2em;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}

        table tr:hover {{
            background: #f5f5f5;
        }}

        .feature-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
        }}

        .feature-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .feature-card .similarity {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 10px 0;
        }}

        .feature-card .gap {{
            background: #fff;
            border: 1px solid #ddd;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
            font-style: italic;
        }}

        .delta-list {{
            list-style: none;
            padding: 0;
        }}

        .delta-list li {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4facfe;
            border-radius: 5px;
        }}

        .delta-list li strong {{
            color: #4facfe;
        }}

        .recommendations {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
        }}

        .recommendations h2 {{
            color: #d35400;
            border-bottom: 3px solid #d35400;
        }}

        .recommendations ol {{
            margin-top: 20px;
            padding-left: 20px;
        }}

        .recommendations li {{
            margin: 15px 0;
            font-size: 1.1em;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            margin-top: 40px;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .badge.exact {{ background: #38ef7d; color: white; }}
        .badge.similar {{ background: #f5576c; color: white; }}
        .badge.delta {{ background: #00f2fe; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BSS Requirements Comparison Report</h1>
            <p class="subtitle">AI-Powered Feature Analysis & Reusability Assessment</p>
            <p style="margin-top: 10px;">Generated: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        </div>

        <div class="content">
            <div class="document-info">
                <h3>📄 Documents Compared</h3>
                <p><strong>New Requirements:</strong> {result.new_document} <span class="badge delta">{result.new_features_count} features</span></p>
                <p><strong>Existing Implementation:</strong> {result.existing_document} <span class="badge delta">{result.existing_features_count} features</span></p>
            </div>

            <div class="stats-grid">
                <div class="stat-card exact">
                    <div class="emoji">✅</div>
                    <div class="value">{stats['exact_matches_count']}</div>
                    <div class="label">Exact Matches</div>
                    <div class="percentage">{format_percentage(stats['exact_match_percentage'])}</div>
                </div>

                <div class="stat-card similar">
                    <div class="emoji">⚠️</div>
                    <div class="value">{stats['similar_matches_count']}</div>
                    <div class="label">Similar Features</div>
                    <div class="percentage">{format_percentage(stats['similar_match_percentage'])}</div>
                </div>

                <div class="stat-card delta">
                    <div class="emoji">🆕</div>
                    <div class="value">{stats['delta_count']}</div>
                    <div class="label">New Features</div>
                    <div class="percentage">{format_percentage(stats['delta_percentage'])}</div>
                </div>

                <div class="stat-card reuse">
                    <div class="emoji">📊</div>
                    <div class="value">{format_percentage(stats['reusability_score'])}</div>
                    <div class="label">Reusability Score</div>
                    <div class="percentage">{stats['exact_matches_count'] + stats['similar_matches_count']} features</div>
                </div>
            </div>

            <div class="section">
                <h2>✅ Exact Matches ({len(result.exact_matches)})</h2>
                <p>These features can be reused as-is from the existing implementation:</p>
"""

        # Exact matches table
        if result.exact_matches:
            html += """
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>New Feature</th>
                            <th>Existing Feature</th>
                            <th>Similarity</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for i, match in enumerate(result.exact_matches, 1):
                html += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{match.new_feature.title}</td>
                            <td>{match.existing_feature.title}</td>
                            <td><span class="badge exact">{format_percentage(match.similarity_score * 100)}</span></td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
"""
        else:
            html += "<p><em>No exact matches found.</em></p>"

        # Similar features
        html += f"""
            </div>

            <div class="section">
                <h2>⚠️ Similar Features Requiring Adaptation ({len(result.similar_features)})</h2>
                <p>These features have existing implementations but require modifications:</p>
"""

        if result.similar_features:
            for i, match in enumerate(result.similar_features, 1):
                gap = match.gap_analysis or "No gap analysis available."
                html += f"""
                <div class="feature-card">
                    <h4>{i}. {match.new_feature.title}</h4>
                    <p><strong>Existing Feature:</strong> {match.existing_feature.title}</p>
                    <span class="similarity">{format_percentage(match.similarity_score * 100)} Similar</span>
                    <div class="gap">
                        <strong>Gap Analysis:</strong><br>
                        {gap}
                    </div>
                </div>
"""
        else:
            html += "<p><em>No similar features found.</em></p>"

        # Delta features
        html += f"""
            </div>

            <div class="section">
                <h2>🆕 Delta - New Features to Implement ({len(result.delta_features)})</h2>
                <p>These features have no existing implementation and require fresh development:</p>
"""

        if result.delta_features:
            html += '<ul class="delta-list">'
            for i, feature in enumerate(result.delta_features, 1):
                desc = f" - {feature.description}" if feature.description and feature.description != feature.title else ""
                html += f"""
                    <li><strong>{i}. {feature.title}</strong>{desc}</li>
"""
            html += '</ul>'
        else:
            html += "<p><em>No delta features - all requirements have existing implementations!</em></p>"

        html += "</div>"

        # Recommendations
        if recommendations and self.config.get('report', {}).get('include_recommendations', True):
            html += """
            <div class="recommendations">
                <h2>💡 Strategic Recommendations</h2>
                <ol>
"""
            for rec in recommendations:
                # Remove number prefix if exists
                rec_text = rec.strip()
                if rec_text and rec_text[0].isdigit():
                    rec_text = '.'.join(rec_text.split('.')[1:]).strip()
                html += f"                    <li>{rec_text}</li>\n"

            html += """
                </ol>
            </div>
"""

        # Summary
        html += f"""
            <div class="section">
                <h2>📈 Implementation Impact Summary</h2>
                <ul>
                    <li><strong>Can Reuse Immediately:</strong> {len(result.exact_matches)} features ({format_percentage(stats['exact_match_percentage'])})</li>
                    <li><strong>Needs Adaptation:</strong> {len(result.similar_features)} features (~30-50% effort vs new)</li>
                    <li><strong>Build from Scratch:</strong> {len(result.delta_features)} features (100% effort)</li>
                </ul>
                <p style="margin-top: 20px; font-size: 1.2em;"><strong>Estimated Effort Savings:</strong> <span style="color: #38ef7d; font-size: 1.3em;">{format_percentage(stats['reusability_score'] * 0.7)}</span> compared to building everything from scratch</p>
            </div>
        </div>

        <div class="footer">
            <p>Generated by Mavenir BSS Requirements Comparison System</p>
            <p>Powered by AI & CrewAI | {datetime.now().year}</p>
        </div>
    </div>
</body>
</html>
"""

        return html
