# File: src/financial_analysis/reporting/base_reporter.py
# Purpose: Defines the abstract interface for all report generators.

from abc import ABC, abstractmethod
from ..core.models import CompanyAnalysis

class BaseReporter(ABC):
    """
    Abstract Base Class for a report generator.
    
    This class defines the contract that all report generators must adhere to,
    ensuring they can be used interchangeably by the main application orchestrator.
    """

    @abstractmethod
    def generate_report(self, analysis: CompanyAnalysis, output_path: str) -> None:
        """
        Generates a report from the given analysis data and saves it to a file.

        Args:
            analysis: The complete CompanyAnalysis object containing all data and insights.
            output_path: The full path where the generated report file should be saved.
        """
        pass
