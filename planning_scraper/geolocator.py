import re
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    """Structured address data."""
    full_address: str
    street: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    
    def __str__(self):
        return self.full_address


# UK postcode regex
POSTCODE_PATTERN = re.compile(
    r'([A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2})',
    re.IGNORECASE
)


def extract_postcode(address):
    """Extract UK postcode from address string.
    
    Args:
        address: Full address string
        
    Returns:
        Formatted postcode or None
        
    Example:
        >>> extract_postcode("123 Main St, London SW1A 1AA")
        'SW1A 1AA'
    """
    if not address:
        return None
    
    match = POSTCODE_PATTERN.search(address)
    if match:
        postcode = match.group(1).upper()
        postcode = postcode.replace(" ", "")
        if len(postcode) >= 4:
            return f"{postcode[:-3]} {postcode[-3:]}"
        return postcode
    
    return None


def clean_address(address):
    """Clean and standardize address string.
    
    Args:
        address: Raw address string
        
    Returns:
        Cleaned address string
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


def parse_address(address_string):
    """Parse an address string into components.
    
    Args:
        address_string: Full address string
        
    Returns:
        Address object with parsed components
    """
    if not address_string:
        return Address(full_address="")
    
    cleaned = address_string.strip()
    postcode = extract_postcode(cleaned)
    
    # Split into parts
    parts = re.split(r'[,\n]+', cleaned)
    parts = [p.strip() for p in parts if p.strip()]
    
    street = parts[0] if len(parts) > 0 else None
    city = parts[-2] if len(parts) > 2 else None
    
    return Address(
        full_address=cleaned,
        street=street,
        city=city,
        postcode=postcode
    )


def validate_postcode(postcode):
    """Validate UK postcode format.
    
    Args:
        postcode: Postcode string
        
    Returns:
        True if valid, False otherwise
    """
    if not postcode:
        return False
    return bool(POSTCODE_PATTERN.match(postcode.strip()))


def process_address_dataframe(df, address_column='address'):
    """Process addresses in a DataFrame.
    
    Args:
        df: DataFrame with address data
        address_column: Name of column containing addresses
        
    Returns:
        DataFrame with additional columns: postcode, street, city, cleaned_address
    """
    if address_column not in df.columns:
        print(f"Column '{address_column}' not found")
        return df
    
    print(f"Processing {len(df)} addresses...")
    
    # Extract postcodes
    df['postcode'] = df[address_column].apply(
        lambda x: extract_postcode(str(x)) if pd.notna(x) else None
    )
    
    # Parse addresses
    parsed = df[address_column].apply(
        lambda x: parse_address(str(x)) if pd.notna(x) else Address("")
    )
    
    df['street'] = parsed.apply(lambda x: x.street)
    df['city'] = parsed.apply(lambda x: x.city)
    df['cleaned_address'] = df[address_column].apply(
        lambda x: clean_address(str(x)) if pd.notna(x) else ""
    )
    
    valid_postcodes = df['postcode'].notna().sum()
    print(f"Extracted {valid_postcodes}/{len(df)} valid postcodes")
    
    return df


def deduplicate_addresses(addresses):
    """Remove duplicate addresses.
    
    Args:
        addresses: List of address strings
        
    Returns:
        List of unique addresses
    """
    seen = set()
    unique = []
    
    for addr in addresses:
        cleaned = clean_address(addr)
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            unique.append(addr)
    
    return unique


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371.0  # Earth radius in km
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
