# File: src/financial_analysis/services/data_service.py
# Purpose: Orchestrates one or more data providers to fetch financial data.

import logging
from typing import List, Tuple, Optional

from ..data_providers.base_provider import BaseDataProvider, DataProviderError
from ..core.models import CompanyInfo, FinancialStatement

logger = logging.getLogger(__name__)

class DataService:
    """
    A service responsible for fetching financial data by orchestrating one or
    more data providers. It implements a fallback mechanism.
    """

    def __init__(self, providers: List[BaseDataProvider]):
        """
        Initializes the DataService with a list of data providers.
        
        Args:
            providers: A list of data provider instances, ordered by priority.
        """
        if not providers:
            raise ValueError("DataService must be initialized with at least one provider.")
        self.providers = providers

    def fetch_company_financials(
        self, ticker: str, num_years: int
    ) -> Tuple[CompanyInfo, List[FinancialStatement]]:
        """
        Fetches company info and financial statements using the configured providers.
        
        It will try the providers in the order they were given. If one fails,
        it will log the error and try the next one.

        Args:
            ticker: The stock ticker symbol.
            num_years: The number of historical years of statements to fetch.

        Returns:
            A tuple containing the CompanyInfo object and a list of
            FinancialStatement objects.
            
        Raises:
            DataProviderError: If all configured providers fail to retrieve the data.
        """
        last_error: Optional[Exception] = None
        
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            logger.info(f"Attempting to fetch data for '{ticker}' using {provider_name}.")
            try:
                company_info = provider.get_company_info(ticker)
                statements = provider.get_financial_statements(ticker, num_years)
                
                logger.info(f"Successfully fetched data for '{ticker}' using {provider_name}.")
                return company_info, statements
                
            except DataProviderError as e:
                logger.warning(f"Provider {provider_name} failed for '{ticker}': {e}")
                last_error = e
                continue # Try the next provider
        
        # If the loop completes without returning, all providers have failed.
        logger.error(f"All data providers failed for ticker '{ticker}'.")
        raise DataProviderError(f"Could not retrieve data for '{ticker}' from any source.") from last_error
