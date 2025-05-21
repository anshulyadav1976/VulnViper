# File: secureaudit/reporter/markdown_writer.py
import json

def write_markdown_report(results, out_path):
    """
    Generate a markdown report from analysis results.
    """
    lines = ["# Security Audit Report\n"]
    for r in results:
        lines.append(f"## {r['file']} - {r['name']} ({r['type']})\n")
        lines.append(f"**Lines:** {r['start_line']}–{r['end_line']}\n")
        if 'summary' in r:
            lines.append(f"**Summary:** {r['summary']}\n")
        if 'vulnerabilities' in r:
            vuln = r['vulnerabilities'] if isinstance(r['vulnerabilities'], list) else [r['vulnerabilities']]
            lines.append("**Vulnerabilities:**\n")
            for v in vuln:
                lines.append(f"- {v}\n")
        if 'recommendations' in r:
            recs = r['recommendations'] if isinstance(r['recommendations'], list) else [r['recommendations']]
            lines.append("**Recommendations:**\n")
            for rec in recs:
                lines.append(f"- {rec}\n")
        lines.append("---\n")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in lines)