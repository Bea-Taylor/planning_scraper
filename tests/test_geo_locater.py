#!/usr/bin/env python3
"""Tests for geo_locater module."""

import unittest
import pandas as pd
from pipeline.geo_locater import GeoLocater, Address


class TestGeoLocater(unittest.TestCase):
    """Tests for geographic location utilities."""
    
    def test_extract_postcode_valid(self):
        """Test extracting valid UK postcodes."""
        test_cases = [
            ("123 Main St, London SW1A 1AA", "SW1A 1AA"),
            ("Westminster, London, SW1A1AA", "SW1A 1AA"),
            ("Address with EC1A 1BB postcode", "EC1A 1BB"),
            ("N1 9GU is the postcode", "N1 9GU"),
        ]
        
        for address, expected in test_cases:
            with self.subTest(address=address):
                result = GeoLocater.extract_postcode(address)
                self.assertEqual(result, expected)
    
    def test_extract_postcode_invalid(self):
        """Test extracting from addresses without postcodes."""
        test_cases = [
            "No postcode here",
            "123 Main Street",
            "",
            None,
        ]
        
        for address in test_cases:
            with self.subTest(address=address):
                result = GeoLocater.extract_postcode(address)
                self.assertIsNone(result)
    
    def test_validate_postcode_valid(self):
        """Test validating valid UK postcodes."""
        valid_postcodes = [
            "SW1A 1AA",
            "EC1A 1BB",
            "N1 9GU",
            "W1A 0AX",
        ]
        
        for postcode in valid_postcodes:
            with self.subTest(postcode=postcode):
                self.assertTrue(GeoLocater.validate_postcode(postcode))
    
    def test_validate_postcode_invalid(self):
        """Test validating invalid postcodes."""
        invalid_postcodes = [
            "INVALID",
            "12345",
            "",
            None,
            "SW1A",
        ]
        
        for postcode in invalid_postcodes:
            with self.subTest(postcode=postcode):
                self.assertFalse(GeoLocater.validate_postcode(postcode))
    
    def test_parse_address(self):
        """Test parsing address into components."""
        address = "123 Main Street, Westminster, London SW1A 1AA"
        parsed = GeoLocater.parse_address(address)
        
        self.assertIsInstance(parsed, Address)
        self.assertEqual(parsed.postcode, "SW1A 1AA")
        self.assertIsNotNone(parsed.street)
        self.assertIsNotNone(parsed.city)
    
    def test_parse_address_empty(self):
        """Test parsing empty address."""
        parsed = GeoLocater.parse_address("")
        self.assertIsInstance(parsed, Address)
        self.assertEqual(parsed.full_address, "")
    
    def test_clean_address(self):
        """Test address cleaning."""
        test_cases = [
            ("  123  Main   St  ,  London  ", "123 Main St, London"),
            ("Address,With,Commas", "Address, With, Commas"),
            ("  Extra   Spaces  ", "Extra Spaces"),
            ("", ""),
        ]
        
        for dirty, clean in test_cases:
            with self.subTest(dirty=dirty):
                result = GeoLocater.clean_address(dirty)
                self.assertEqual(result, clean)
    
    def test_calculate_distance(self):
        """Test distance calculation between coordinates."""
        # London to Paris (approx 344 km)
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522
        
        distance = GeoLocater.calculate_distance(
            london_lat, london_lon, paris_lat, paris_lon
        )
        
        # Should be approximately 344 km (allow ±10 km margin)
        self.assertGreater(distance, 330)
        self.assertLess(distance, 360)
    
    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        lat, lon = 51.5074, -0.1278
        
        distance = GeoLocater.calculate_distance(lat, lon, lat, lon)
        
        # Distance should be essentially 0
        self.assertAlmostEqual(distance, 0, places=5)
    
    def test_process_address_dataframe(self):
        """Test processing addresses in DataFrame."""
        df = pd.DataFrame({
            'address': [
                '123 Main St, London SW1A 1AA',
                '456 Oak Ave, Westminster EC1A 1BB',
                'No postcode address'
            ]
        })
        
        result_df = GeoLocater.process_address_dataframe(df)
        
        # Check new columns exist
        self.assertIn('postcode', result_df.columns)
        self.assertIn('cleaned_address', result_df.columns)
        self.assertIn('street', result_df.columns)
        
        # Check postcodes extracted
        self.assertEqual(result_df['postcode'].iloc[0], 'SW1A 1AA')
        self.assertEqual(result_df['postcode'].iloc[1], 'EC1A 1BB')
        self.assertIsNone(result_df['postcode'].iloc[2])
    
    def test_process_address_dataframe_missing_column(self):
        """Test processing DataFrame with missing address column."""
        df = pd.DataFrame({'other_column': ['value']})
        
        result_df = GeoLocater.process_address_dataframe(df, 'address')
        
        # Should return original DataFrame unchanged
        self.assertEqual(list(result_df.columns), ['other_column'])
    
    def test_deduplicate_addresses(self):
        """Test address deduplication."""
        addresses = [
            "123 Main St, London",
            "456 Oak Ave, London",
            "123 Main St, London",  # Duplicate
            "  123 Main St, London  ",  # Duplicate with spaces
        ]
        
        unique = GeoLocater.deduplicate_addresses(addresses)
        
        self.assertEqual(len(unique), 2)
        self.assertIn("123 Main St, London", unique)
        self.assertIn("456 Oak Ave, London", unique)
    
    def test_address_str_method(self):
        """Test Address __str__ method."""
        addr = Address(
            full_address="123 Main St, London SW1A 1AA",
            postcode="SW1A 1AA"
        )
        
        self.assertEqual(str(addr), "123 Main St, London SW1A 1AA")


class TestAddressDataclass(unittest.TestCase):
    """Tests for Address dataclass."""
    
    def test_address_creation(self):
        """Test creating Address object."""
        addr = Address(
            full_address="123 Main St",
            street="123 Main St",
            city="London",
            postcode="SW1A 1AA",
            latitude=51.5074,
            longitude=-0.1278
        )
        
        self.assertEqual(addr.full_address, "123 Main St")
        self.assertEqual(addr.street, "123 Main St")
        self.assertEqual(addr.city, "London")
        self.assertEqual(addr.postcode, "SW1A 1AA")
        self.assertEqual(addr.latitude, 51.5074)
        self.assertEqual(addr.longitude, -0.1278)
    
    def test_address_optional_fields(self):
        """Test Address with only required fields."""
        addr = Address(full_address="123 Main St")
        
        self.assertEqual(addr.full_address, "123 Main St")
        self.assertIsNone(addr.street)
        self.assertIsNone(addr.city)
        self.assertIsNone(addr.postcode)
        self.assertIsNone(addr.latitude)
        self.assertIsNone(addr.longitude)


if __name__ == "__main__":
    unittest.main()
