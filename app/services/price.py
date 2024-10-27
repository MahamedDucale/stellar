# app/services/price.py
import requests
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('sms_crypto')

class GoldPriceService:
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io/v2"
        self.cache_time = 300  # Cache for 5 minutes
        self.last_update = None
        self.cached_price = None
        
        # Fallback price in case API fails
        self.fallback_price = 60.0  # $60 per gram

    def get_gold_price(self):
        """Get current gold price per gram in USD"""
        try:
            # Check cache
            if (self.cached_price and self.last_update and 
                (datetime.now() - self.last_update).seconds < self.cache_time):
                return self.cached_price

            # Fetch new price from Polygon
            endpoint = f"/aggs/ticker/C:XAUUSD/prev"
            params = {
                "apiKey": self.api_key,
                "adjusted": "true"
            }
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'OK' and data['results']:
                # Convert from USD/oz to USD/gram (1 troy oz = 31.1034768 grams)
                price_per_oz = data['results'][0]['c']  # Closing price
                price_per_gram = price_per_oz / 31.1034768
                
                self.cached_price = price_per_gram
                self.last_update = datetime.now()
                
                logger.info(f"Updated gold price: ${price_per_gram:.2f}/gram")
                return price_per_gram
            
            raise Exception("No price data available")

        except Exception as e:
            logger.error(f"Error fetching gold price: {str(e)}")
            return self.get_fallback_price()

    def get_fallback_price(self):
        """Get fallback price if API fails"""
        if self.cached_price:
            logger.info("Using cached price as fallback")
            return self.cached_price
        
        logger.info("Using default fallback price")
        return self.fallback_price

    def get_price_info(self):
        """Get detailed price information"""
        price = self.get_gold_price()
        return {
            'price_per_gram': price,
            'price_per_oz': price * 31.1034768,
            'timestamp': self.last_update or datetime.now(),
            'is_live': bool(self.last_update and 
                          (datetime.now() - self.last_update).seconds < self.cache_time),
            'source': 'Polygon.io' if self.last_update else 'Fallback'
        }