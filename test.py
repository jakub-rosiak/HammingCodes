import unittest
import random
from itertools import combinations
import numpy as np
from io import BytesIO

# Import the module (assuming it's saved as hamming_code.py)
# Replace with proper import if the module has a different name
import hamming
from hamming import (encode, decode, encode_2bit, decode_2bit, check, check_2bit, fix_errors, fix_errors_2bit)


class TestErrorCorrection(unittest.TestCase):
    def setUp(self):
        # Test data
        self.test_data = b"Hello, World! This is a test message for error correction."

    def flip_bit(self, data, byte_idx, bit_idx):
        """Flip a specific bit in the byte array."""
        data_bytes = bytearray(data)
        data_bytes[byte_idx] ^= (1 << (7 - bit_idx % 8))
        return bytes(data_bytes)

    def test_single_bit_error_hamming(self):
        """Test that all possible single bit errors can be corrected with Hamming code."""
        # Encode the original data
        encoded_data = encode(self.test_data)

        # For each byte in the encoded data
        for byte_idx in range(len(encoded_data)):
            # For each bit in the byte
            for bit_idx in range(8):
                # Create a copy with a single bit error
                corrupted_data = self.flip_bit(encoded_data, byte_idx, bit_idx)

                # Check if error is detected
                error_positions = check(corrupted_data)
                self.assertGreater(len(error_positions), 0, f"Error not detected at byte {byte_idx}, bit {bit_idx}")

                # Fix the error
                corrected_data = fix_errors(corrupted_data, error_positions)

                # Decode and verify
                decoded_data = decode(corrected_data)
                self.assertEqual(decoded_data, self.test_data,
                                 f"Failed to correct error at byte {byte_idx}, bit {bit_idx}")

    def test_single_bit_error_2bit(self):
        """Test that all possible single bit errors can be corrected with 2-bit code."""
        # Encode the original data
        encoded_data = encode_2bit(self.test_data)

        # For each byte in the encoded data
        for byte_idx in range(len(encoded_data)):
            # For each bit in the byte
            for bit_idx in range(8):
                # Create a copy with a single bit error
                corrupted_data = self.flip_bit(encoded_data, byte_idx, bit_idx)

                # Check if error is detected
                error_positions = check_2bit(corrupted_data)
                self.assertGreater(len(error_positions), 0, f"Error not detected at byte {byte_idx}, bit {bit_idx}")

                # Fix the error
                corrected_data = fix_errors_2bit(corrupted_data, error_positions)

                # Decode and verify
                decoded_data = decode_2bit(corrected_data)
                self.assertEqual(decoded_data, self.test_data,
                                 f"Failed to correct error at byte {byte_idx}, bit {bit_idx}")

    def test_double_bit_error_2bit(self):
        """Test that all possible double bit errors can be corrected with 2-bit code."""
        # Use a smaller test data for double bit tests (it would be too many combinations otherwise)
        small_test_data = b"Hello!"
        encoded_data = encode_2bit(small_test_data)

        # Calculate total number of bits
        total_bits = len(encoded_data) * 8

        # Get all combinations of 2 bit positions
        for (pos1, pos2) in combinations(range(min(100, total_bits)),
                                         2):  # Limit to first 100 bits to keep test manageable
            # Calculate byte and bit indices for both positions
            byte_idx1, bit_idx1 = pos1 // 8, pos1 % 8
            byte_idx2, bit_idx2 = pos2 // 8, pos2 % 8

            # Skip if either index is out of range
            if byte_idx1 >= len(encoded_data) or byte_idx2 >= len(encoded_data):
                continue

            # Create a copy with double bit errors
            corrupted_data = self.flip_bit(encoded_data, byte_idx1, bit_idx1)
            corrupted_data = self.flip_bit(corrupted_data, byte_idx2, bit_idx2)

            # Check if errors are detected
            error_positions = check_2bit(corrupted_data)

            # We expect 2 error positions to be returned
            self.assertEqual(len(error_positions), 2,
                             f"Expected to detect 2 errors, got {len(error_positions)} for bits at ({byte_idx1}, {bit_idx1}) and ({byte_idx2}, {bit_idx2})")

            # Fix the errors
            corrected_data = fix_errors_2bit(corrupted_data, error_positions)

            # Decode and verify
            decoded_data = decode_2bit(corrected_data)
            self.assertEqual(decoded_data, small_test_data,
                             f"Failed to correct errors at ({byte_idx1}, {bit_idx1}) and ({byte_idx2}, {bit_idx2})")

    def test_random_bit_errors_hamming(self):
        """Test random single bit errors with Hamming code."""
        # Number of random tests
        num_tests = 50
        encoded_data = encode(self.test_data)

        for _ in range(num_tests):
            byte_idx = random.randint(0, len(encoded_data) - 1)
            bit_idx = random.randint(0, 7)

            # Create a copy with a single bit error
            corrupted_data = self.flip_bit(encoded_data, byte_idx, bit_idx)

            # Check, fix, and verify
            error_positions = check(corrupted_data)
            corrected_data = fix_errors(corrupted_data, error_positions)
            decoded_data = decode(corrected_data)

            self.assertEqual(decoded_data, self.test_data,
                             f"Failed to correct random error at byte {byte_idx}, bit {bit_idx}")

    def test_random_double_bit_errors_2bit(self):
        """Test random double bit errors with 2-bit code."""
        # Number of random tests
        num_tests = 30
        encoded_data = encode_2bit(self.test_data)

        for _ in range(num_tests):
            # Get two different random positions
            total_bits = min(100, len(encoded_data) * 8)  # Limit to first 100 bits
            pos1, pos2 = random.sample(range(total_bits), 2)

            byte_idx1, bit_idx1 = pos1 // 8, pos1 % 8
            byte_idx2, bit_idx2 = pos2 // 8, pos2 % 8

            # Skip if either index is out of range
            if byte_idx1 >= len(encoded_data) or byte_idx2 >= len(encoded_data):
                continue

            # Create a copy with double bit errors
            corrupted_data = self.flip_bit(encoded_data, byte_idx1, bit_idx1)
            corrupted_data = self.flip_bit(corrupted_data, byte_idx2, bit_idx2)

            # Check, fix, and verify
            error_positions = check_2bit(corrupted_data)
            corrected_data = fix_errors_2bit(corrupted_data, error_positions)
            decoded_data = decode_2bit(corrected_data)

            self.assertEqual(decoded_data, self.test_data,
                             f"Failed to correct random errors at ({byte_idx1}, {bit_idx1}) and ({byte_idx2}, {bit_idx2})")

    def test_error_patterns(self):
        """Test specific known error patterns."""
        # Test with a simple message
        simple_msg = b"ABC"

        # Test Hamming code
        encoded = encode(simple_msg)

        # Corrupt specific bits - single bit error
        corrupted = self.flip_bit(encoded, 0, 0)  # Flip the most significant bit of first byte
        error_positions = check(corrupted)
        corrected = fix_errors(corrupted, error_positions)
        decoded = decode(corrected)
        self.assertEqual(decoded, simple_msg, "Failed to correct specific single bit error in Hamming code")

        # Test 2-bit code
        encoded_2bit = encode_2bit(simple_msg)

        # Corrupt two specific bits
        corrupted = self.flip_bit(encoded_2bit, 0, 0)
        corrupted = self.flip_bit(corrupted, 0, 3)
        error_positions = check_2bit(corrupted)
        corrected = fix_errors_2bit(corrupted, error_positions)
        decoded = decode_2bit(corrected)
        self.assertEqual(decoded, simple_msg, "Failed to correct specific double bit error in 2-bit code")


if __name__ == "__main__":
    unittest.main()