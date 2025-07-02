# File: src/data_retriever.py
import aiohttp
import yfinance as yf
import asyncio
from utils.logger import get_logger
import time

logger = get_logger(__name__)

class DataRetriever:
    SEC_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
    SEC_CIK_API = "https://data.sec.gov/submissions/CIK{cik}.json"
    SEC_FILINGS_API = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"

    HEADERS = {"User-Agent": "Financial Analyzer 1.0 (your-email@company.com)"}

    async def get_cik_and_name(self, ticker):
        # Get CIK and company name for ticker
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(self.SEC_TICKER_MAP_URL) as resp:
                data = await resp.json()
                for info in data.values():
                    if info["ticker"].lower() == ticker.lower():
                        cik = str(info["cik_str"])
                        name = info["title"]
                        logger.info(f"Found CIK {cik} for {ticker}: {name}")
                        return cik, name
        raise Exception(f"CIK not found for ticker {ticker}")

    async def get_financial_filings(self, cik):
        # Download latest company facts (XBRL) from SEC
        padded = cik.zfill(10)
        url = self.SEC_FILINGS_API.format(cik_padded=padded)
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    logger.info(f"SEC filings retrieved for CIK {cik}")
                    return await resp.json()
                else:
                    logger.warning("SEC filings not found, falling back to Yahoo Finance scraping")
                    return None

    async def get_market_data(self, ticker):
        # Use yfinance for market data
        stock = yf.Ticker(ticker)
        info = stock.info
        logger.info(f"Fetched market data for {ticker}")
        return info
