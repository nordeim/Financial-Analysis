# File: src/financial_analysis/data_providers/base_provider.py
# Purpose: Defines the abstract interface for all data providers.

from abc import ABC, abstractmethod
from typing import List, Tuple
from ..core.models import CompanyInfo, FinancialStatement

class DataProviderError(Exception):
    """Custom exception for errors related to data providers."""
    pass

class BaseDataProvider(ABC):
    """
    Abstract Base Class for a financial data provider.
    
    This class defines the contract that all data providers must adhere to,
    ensuring they can be used interchangeably by the DataService.
    """

    @abstractmethod
    def get_company_info(self, ticker: str) -> CompanyInfo:
        """
        Fetches general company information for a given ticker.

        Args:
            ticker: The stock ticker symbol.

        Returns:
            A CompanyInfo object populated with company details.
            
        Raises:
            DataProviderError: If the company information cannot be retrieved.
        """
        pass

    @abstractmethod
    def get_financial_statements(self, ticker: str, num_years: int) -> List[FinancialStatement]:
        """
        Fetches historical financial statements for a given ticker.

        Args:
            ticker: The stock ticker symbol.
            num_years: The number of historical years to retrieve.

        Returns:
            A list of FinancialStatement objects, one for each historical period.
            
        Raises:
            DataProviderError: If the financial statements cannot be retrieved.
        """
        pass
