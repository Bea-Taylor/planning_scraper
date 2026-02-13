"""Geographic location and address processing utilities.

This module provides functions for geocoding addresses, extracting postcodes,
and processing location data from planning applications.
"""

import re
from typing import Optional, Tuple, Dict, Any
import pandas as pd
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class Address:
    """Structured address data."""
    
    full_address: str
    street: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __str__(self) -> str:
        """Return full address string."""
        return self.full_address


class GeoLocater:
    """Geographic location and address processing utility."""
    
    # UK postcode regex pattern
    POSTCODE_PATTERN = re.compile(
        r'([A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2})',
        re.IGNORECASE
    )
    
    # Common address separators
    ADDRESS_SEPARATORS = [',', '\n', '  ']
    
    @staticmethod
    def extract_postcode(address: str) -> Optional[str]:
        """Extract UK postcode from address string.
        
        Args:
            address: Full address string
            
        Returns:
            Formatted postcode or None if not found
            
        Examples:
            >>> GeoLocater.extract_postcode("123 Main St, London SW1A 1AA")
            'SW1A 1AA'
            >>> GeoLocater.extract_postcode("No postcode here")
            None
        """
        if not address:
            return None
        
        match = GeoLocater.POSTCODE_PATTERN.search(address)
        if match:
            postcode = match.group(1).upper()
            # Ensure proper spacing (before last 3 characters)
            postcode = postcode.replace(" ", "")
            if len(postcode) >= 4:
                return f"{postcode[:-3]} {postcode[-3:]}"
            return postcode
        
        return None
    
    @staticmethod
    def parse_address(address_string: str) -> Address:
        """Parse an address string into components.
        
        Args:
            address_string: Full address string
            
        Returns:
            Address object with parsed components
            
        Examples:
            >>> addr = GeoLocater.parse_address("123 Main St, Westminster, London SW1A 1AA")
            >>> addr.postcode
            'SW1A 1AA'
        """
        if not address_string:
            return Address(full_address="")
        
        # Clean the address
        cleaned = address_string.strip()
        
        # Extract postcode
        postcode = GeoLocater.extract_postcode(cleaned)
        
        # Split address into parts
        parts = re.split(r'[,\n]+', cleaned)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Try to identify components
        street = parts[0] if len(parts) > 0 else None
        city = parts[-2] if len(parts) > 2 else None
        
        return Address(
            full_address=cleaned,
            street=street,
            city=city,
            postcode=postcode
        )
    
    @staticmethod
    def clean_address(address: str) -> str:
        """Clean and standardize address string.
        
        Args:
            address: Raw address string
            
        Returns:
            Cleaned address string
            
        Examples:
            >>> GeoLocater.clean_address("  123  Main   St  ,  London  ")
            '123 Main St, London'
        """
        if not address:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', address.strip())
        
        # Standardize separators
        cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
        
        # Remove trailing/leading commas
        cleaned = cleaned.strip(', ')
        
        return cleaned
    
    @staticmethod
    def validate_postcode(postcode: str) -> bool:
        """Validate UK postcode format.
        
        Args:
            postcode: Postcode string
            
        Returns:
            True if valid UK postcode format, False otherwise
            
        Examples:
            >>> GeoLocater.validate_postcode("SW1A 1AA")
            True
            >>> GeoLocater.validate_postcode("INVALID")
            False
        """
        if not postcode:
            return False
        
        return bool(GeoLocater.POSTCODE_PATTERN.match(postcode.strip()))
    
    @staticmethod
    def geocode_address(address: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode an address to latitude/longitude.
        
        Note: This is a placeholder. In production, you would integrate with
        a geocoding service like Google Maps API, Nominatim, or Postcodes.io.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding fails
            
        Examples:
            >>> lat, lon = GeoLocater.geocode_address("SW1A 1AA")
            >>> # Returns coordinates if service is configured
        """
        logger.warning(
            "Geocoding not implemented. Please integrate with a geocoding service."
        )
        return None, None
    
    @staticmethod
    def geocode_postcode(postcode: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode a UK postcode to latitude/longitude.
        
        Note: This is a placeholder. In production, integrate with Postcodes.io
        or similar service.
        
        Args:
            postcode: UK postcode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding fails
            
        Examples:
            >>> lat, lon = GeoLocater.geocode_postcode("SW1A 1AA")
            >>> # Returns coordinates from postcodes.io if implemented
        """
        if not GeoLocater.validate_postcode(postcode):
            logger.warning(f"Invalid postcode format: {postcode}")
            return None, None
        
        # Placeholder - integrate with postcodes.io API
        logger.warning(
            f"Geocoding for postcode {postcode} not implemented. "
            "Consider using postcodes.io API."
        )
        return None, None
    
    @staticmethod
    def calculate_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
            
        Examples:
            >>> dist = GeoLocater.calculate_distance(51.5074, -0.1278, 51.5155, -0.0922)
            >>> print(f"{dist:.2f} km")
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Earth's radius in kilometers
        R = 6371.0
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    @staticmethod
    def process_address_dataframe(df: pd.DataFrame, address_column: str = 'address') -> pd.DataFrame:
        """Process addresses in a DataFrame, extracting postcodes and components.
        
        Args:
            df: DataFrame with address data
            address_column: Name of column containing addresses
            
        Returns:
            DataFrame with additional columns: postcode, street, city, cleaned_address
            
        Examples:
            >>> df = pd.DataFrame({'address': ['123 Main St, London SW1A 1AA']})
            >>> df = GeoLocater.process_address_dataframe(df)
            >>> df['postcode'].iloc[0]
            'SW1A 1AA'
        """
        if address_column not in df.columns:
            logger.error(f"Column '{address_column}' not found in DataFrame")
            return df
        
        logger.info(f"Processing {len(df)} addresses...")
        
        # Extract postcodes
        df['postcode'] = df[address_column].apply(
            lambda x: GeoLocater.extract_postcode(str(x)) if pd.notna(x) else None
        )
        
        # Parse addresses
        parsed_addresses = df[address_column].apply(
            lambda x: GeoLocater.parse_address(str(x)) if pd.notna(x) else Address("")
        )
        
        df['street'] = parsed_addresses.apply(lambda x: x.street)
        df['city'] = parsed_addresses.apply(lambda x: x.city)
        df['cleaned_address'] = df[address_column].apply(
            lambda x: GeoLocater.clean_address(str(x)) if pd.notna(x) else ""
        )
        
        # Log statistics
        valid_postcodes = df['postcode'].notna().sum()
        logger.info(f"Extracted {valid_postcodes}/{len(df)} valid postcodes")
        
        return df
    
    @staticmethod
    def deduplicate_addresses(addresses: list) -> list:
        """Remove duplicate addresses while preserving order.
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of unique addresses in original order
            
        Examples:
            >>> addresses = ["123 Main St", "456 Oak Ave", "123 Main St"]
            >>> GeoLocater.deduplicate_addresses(addresses)
            ['123 Main St', '456 Oak Ave']
        """
        seen = set()
        unique_addresses = []
        
        for addr in addresses:
            cleaned = GeoLocater.clean_address(addr)
            if cleaned and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                unique_addresses.append(addr)
        
        logger.info(f"Reduced {len(addresses)} addresses to {len(unique_addresses)} unique")
        return unique_addresses
    
    @staticmethod
    def find_addresses_near_postcode(
        df: pd.DataFrame,
        target_postcode: str,
        radius_km: float = 1.0
    ) -> pd.DataFrame:
        """Find addresses within a radius of a target postcode.
        
        Note: Requires geocoded coordinates in the DataFrame.
        
        Args:
            df: DataFrame with latitude and longitude columns
            target_postcode: Target postcode
            radius_km: Radius in kilometers
            
        Returns:
            Filtered DataFrame with addresses within radius
        """
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            logger.error("DataFrame must have 'latitude' and 'longitude' columns")
            return df
        
        # Geocode target postcode
        target_lat, target_lon = GeoLocater.geocode_postcode(target_postcode)
        
        if target_lat is None or target_lon is None:
            logger.warning(f"Could not geocode target postcode: {target_postcode}")
            return df
        
        # Calculate distances
        def calc_dist(row):
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                return float('inf')
            return GeoLocater.calculate_distance(
                target_lat, target_lon,
                row['latitude'], row['longitude']
            )
        
        df['distance_km'] = df.apply(calc_dist, axis=1)
        
        # Filter by radius
        filtered_df = df[df['distance_km'] <= radius_km].copy()
        logger.info(
            f"Found {len(filtered_df)} addresses within {radius_km}km "
            f"of {target_postcode}"
        )
        
        return filtered_df.sort_values('distance_km')
