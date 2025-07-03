# File: src/financial_analysis/reporting/text_reporter.py
# Purpose: Generates a comprehensive, human-readable text-based report.

import logging
import textwrap
from .base_reporter import BaseReporter
from ..core.models import CompanyAnalysis

logger = logging.getLogger(__name__)

class TextReporter(BaseReporter):
    """Generates a professional, formatted report in a .txt file."""

    def generate_report(self, analysis: CompanyAnalysis, output_path: str) -> None:
        logger.info(f"Generating text report for {analysis.company_info.ticker} to {output_path}")
        try:
            report_content = self._build_report_string(analysis)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info("Successfully generated text report.")
        except IOError as e:
            logger.error(f"Failed to write text report to {output_path}: {e}")

    def _build_report_string(self, analysis: CompanyAnalysis) -> str:
        """Constructs the full report string from various formatted sections."""
        sections = [
            self._format_header(analysis),
            self._format_summary(analysis),
            self._format_ratios_table(analysis),
            self._format_detailed_analysis(analysis),
            self._format_financial_statements(analysis),
            self._format_disclaimer(analysis)
        ]
        return "\n\n".join(sections)

    def _format_header(self, analysis: CompanyAnalysis) -> str:
        info = analysis.company_info
        date_str = analysis.analysis_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        return (
            f"FINANCIAL ANALYSIS REPORT\n"
            f"{'=' * 25}\n"
            f"Company:         {info.name} ({info.ticker})\n"
            f"Sector:          {info.sector or 'N/A'}\n"
            f"Industry:        {info.industry or 'N/A'}\n"
            f"Analysis Date:   {date_str}"
        )

    def _format_summary(self, analysis: CompanyAnalysis) -> str:
        qual_analysis = analysis.qualitative_analysis
        overall = textwrap.fill(qual_analysis.get('overall_summary', 'Not available.'), width=80)
        
        strengths = "\n".join([f"  • {s}" for s in qual_analysis.get('key_strengths', [])])
        concerns = "\n".join([f"  • {c}" for c in qual_analysis.get('key_concerns', [])])

        return (
            f"EXECUTIVE SUMMARY\n"
            f"{'-' * 25}\n"
            f"Overall Assessment:\n{overall}\n\n"
            f"Key Strengths:\n{strengths or '  None identified.'}\n\n"
            f"Key Areas for Attention:\n{concerns or '  None identified.'}"
        )

    def _format_ratios_table(self, analysis: CompanyAnalysis) -> str:
        header = f"FINANCIAL RATIOS SNAPSHOT\n{'-' * 25}"
        if not analysis.historical_ratios:
            return f"{header}\nNo ratio data available."

        ratios = analysis.historical_ratios[:4] # Show up to 4 recent years
        years = [f"FY{r.fiscal_year}" for r in ratios]
        
        lines = [f"{'Metric':<22}" + "".join([f"{y:>12}" for y in years])]
        lines.append(f"{'-'*22}" + "".join([f"{'-'*12}" for y in years]))

        ratio_keys = [
            ("Current Ratio", "current_ratio", ".2f"), ("Quick Ratio", "quick_ratio", ".2f"),
            ("Net Margin", "net_margin", ".2%"), ("ROE", "roe", ".2%"),
            ("Debt-to-Equity", "debt_to_equity", ".2f")
        ]
        for name, key, fmt in ratio_keys:
            values = [getattr(r, key, None) for r in ratios]
            value_strs = [f"{v:{fmt}}" if v is not None else "N/A" for v in values]
            lines.append(f"{name:<22}" + "".join([f"{s:>12}" for s in value_strs]))
            
        return f"{header}\n" + "\n".join(lines)

    def _format_detailed_analysis(self, analysis: CompanyAnalysis) -> str:
        header = f"DETAILED ANALYSIS\n{'-' * 25}"
        qual_analysis = analysis.qualitative_analysis
        
        sections = []
        for key in ["liquidity", "profitability", "leverage", "efficiency"]:
            title = key.replace('_', ' ').title() + " Analysis"
            text = qual_analysis.get(key, "Not available.")
            wrapped_text = textwrap.fill(text, width=80, initial_indent='  ', subsequent_indent='  ')
            sections.append(f"{title}:\n{wrapped_text}")
        
        return f"{header}\n\n" + "\n\n".join(sections)

    def _format_financial_statements(self, analysis: CompanyAnalysis) -> str:
        # This can be expanded to show more detail if needed
        return (
            f"FINANCIAL DATA\n{'-' * 25}\n"
            f"Detailed financial statement data is available in the Excel report."
        )

    def _format_disclaimer(self, analysis: CompanyAnalysis) -> str:
        sources = ", ".join(analysis.data_sources_used)
        return (
            f"IMPORTANT DISCLAIMERS\n"
            f"{'=' * 25}\n"
            f"• This report was automatically generated and is for educational/demonstration purposes ONLY.\n"
            f"• This is NOT financial advice. Always consult with a qualified financial professional.\n"
            f"• Data accuracy is not guaranteed. Verify all data independently before making decisions.\n"
            f"• Data Sources Used: {sources}"
        )
