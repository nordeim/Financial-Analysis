# File: src/financial_analysis/services/data_service.py
# Purpose: Orchestrates one or more data providers to fetch and enrich financial data. (Updated)

import logging
from typing import List, Tuple, Optional

from ..data_providers.base_provider import BaseDataProvider, DataProviderError
from ..core.models import CompanyInfo, FinancialStatement

logger = logging.getLogger(__name__)

class DataService:
    """
    A service responsible for fetching financial data by orchestrating one or
    more data providers. It implements a fallback and data enrichment strategy.
    """

    def __init__(self, providers: List[BaseDataProvider]):
        """
        Initializes the DataService with a list of data providers.
        
        Args:
            providers: A list of data provider instances, ordered by priority.
                       The first provider is considered the primary source for statements.
        """
        if not providers:
            raise ValueError("DataService must be initialized with at least one provider.")
        self.providers = providers

    def fetch_company_financials(
        self, ticker: str, num_years: int
    ) -> Tuple[CompanyInfo, List[FinancialStatement]]:
        """
        Fetches company info and financial statements using an enrichment strategy.
        
        1. It attempts to fetch financial statements from providers in their prioritized order.
        2. The first provider to return statements is considered the primary source.
        3. It then attempts to fetch CompanyInfo from ALL providers to enrich the
           metadata, filling in missing fields like 'sector' or 'industry'.

        Args:
            ticker: The stock ticker symbol.
            num_years: The number of historical years of statements to fetch.

        Returns:
            A tuple containing the merged CompanyInfo object and a list of
            FinancialStatement objects from the primary source.
            
        Raises:
            DataProviderError: If no configured provider can return financial statements.
        """
        company_info: Optional[CompanyInfo] = None
        statements: List[FinancialStatement] = []
        last_statement_error: Optional[Exception] = None

        # --- Step 1: Fetch financial statements from the first available provider ---
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            logger.info(f"Attempting to fetch STATEMENTS for '{ticker}' using {provider_name}.")
            try:
                # Get the base company info and statements from this provider
                company_info = provider.get_company_info(ticker)
                statements = provider.get_financial_statements(ticker, num_years)
                
                logger.info(f"Successfully fetched primary statements for '{ticker}' using {provider_name}.")
                break  # Exit loop on first success
                
            except DataProviderError as e:
                logger.warning(f"Could not fetch statements from {provider_name}: {e}")
                last_statement_error = e
                company_info = None # Reset info if statements failed
                continue
        
        if not statements or not company_info:
            logger.error(f"All providers failed to return financial statements for '{ticker}'.")
            raise DataProviderError(f"Could not retrieve financial statements for '{ticker}' from any source.") from last_statement_error

        # --- Step 2: Enrich company info using all available providers ---
        # The company_info from the successful statement provider is our base.
        merged_info_dict = company_info.model_dump()

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            try:
                logger.info(f"Attempting to ENRICH company info for '{ticker}' using {provider_name}.")
                enrichment_info = provider.get_company_info(ticker)
                
                # Iterate through the fields of the enrichment data
                for key, value in enrichment_info.model_dump().items():
                    # If our base data is missing this field and the enrichment one has it, add it.
                    if merged_info_dict.get(key) is None and value is not None:
                        logger.debug(f"Enriching '{key}' with value from {provider_name}.")
                        merged_info_dict[key] = value

            except DataProviderError as e:
                logger.warning(f"Could not fetch enrichment info from {provider_name}, skipping. Error: {e}")
                continue
        
        # Create the final, enriched CompanyInfo object
        final_company_info = CompanyInfo(**merged_info_dict)
        
        logger.info(f"Completed data fetching and enrichment for '{ticker}'.")
        return final_company_info, statements
