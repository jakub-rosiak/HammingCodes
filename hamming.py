from itertools import chain
import numpy as np

H_2BIT = [
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
]

# input list of bits, output bytes
def encode(data: bytes) -> bytes:
    bit_list = bytes_to_bit_arrays(data, 8)
    encoded_bytes = []
    for byte in bit_list:
        encoded_bytes.append(encode_byte(byte))

    return extend(encoded_bytes)

# inupt list of bits, output bytes
def encode_2bit(data: bytes) -> bytes:
    bit_list = bytes_to_bit_arrays(data, 8)
    encoded_bytes = []
    H = np.array(H_2BIT)

    for byte in bit_list:
        data_bits = np.array([int(b) for b in byte])
        parity_bits = (H[:, :8] @ data_bits) % 2
        codeword = np.concatenate((data_bits, parity_bits)).tolist()
        encoded_bytes.append(codeword)
    return extend(encoded_bytes)

# input list of bits, output list of bits
def encode_byte(byte):
    if len(byte) != 8:
        raise TypeError(f"Binary data must be 8 bits, got {len(byte)}")

    for bit in byte:
        if bit != 0 and bit != 1:
            raise TypeError("Data must be in binary format (0s and 1s)")

    array = to_empty_hamming_array(byte)

    for i in [1, 2, 4, 8]:
        controlled = get_parity_list(i, 12)
        parity_bit = 0
        for message_bit in controlled:
            parity_bit += array[message_bit]

        array[i - 1] = parity_bit % 2

    return array

#input position of parity bit, length of list, output list of bits controlled by parity bit
def get_parity_list(position, max_len):
    controlled = []
    for i in range(1, max_len + 1):
        if i & position:
            controlled.append(i - 1)
    return controlled

#input list of bits, output list of bits
def to_empty_hamming_array(array):
    return [0, 0, array[0], 0, array[1], array[2], array[3], 0, array[4], array[5], array[6], array[7]]

# input bytes, output byte array
def decode(encoded_data):
    hamming_arrays = bytes_to_bit_arrays(encoded_data, 12)

    decoded_bytes = bytearray()
    for array in hamming_arrays:
        corrected = check_and_correct(array)
        decoded = decode_byte(corrected)
        byte_value = int(''.join(map(str, decoded)), 2)
        decoded_bytes.append(byte_value)

    return decoded_bytes

# input bytes, output bytearray
def decode_2bit(encoded_data):
    bit_arrays = bytes_to_bit_arrays(encoded_data, 16)

    corrected_arrays, _ = correct_errors_2bit(bit_arrays)

    decoded_bytes = bytearray()
    for array in corrected_arrays:
        byte_value = int(''.join(map(str, array[:8])), 2)
        decoded_bytes.append(byte_value)

    return decoded_bytes

# input bit array, output bit array
def decode_byte(array):
    return [array[2], array[4], array[5], array[6], array[8], array[9], array[10], array[11]]

#input bytes, output list of bit positions
def check(encoded_data):
    hamming_arrays = bytes_to_bit_arrays(encoded_data, 12)

    error_positions = []
    for i, array in enumerate(hamming_arrays):
        error_position = get_error_position(array)
        if error_position != 0:
            error_positions.append((i, error_position - 1))

    return error_positions

#input bytes, output list of bit positions
def check_2bit(encoded_data):
    bit_arrays = bytes_to_bit_arrays(encoded_data, 16)

    error_positions = []
    H = np.array(H_2BIT)

    for i, codeword in enumerate(bit_arrays):
        syndrome = syndrome_check(codeword, H)

        if np.any(syndrome):
            error_indices = [j for j in range(len(codeword)) if np.array_equal(H[:, j], syndrome)]

            if not error_indices:
                for j in range(len(H[0])):
                    for k in range(j + 1, len(H[0])):
                        if np.array_equal(H[:, j] ^ H[:, k], syndrome):
                            error_positions.append((i, j))
                            error_positions.append((i, k))
                            break
            else:
                error_positions.append((i, error_indices[0]))

    return error_positions

#input encoded byte, parity check matirx, output vector
def syndrome_check(codeword, H):
    return (H @ codeword) % 2

#input list of lists of encoded bytes, output corrected list and list of corrected errors
def correct_errors_2bit(encoded_arrays):
    H = np.array(H_2BIT)
    corrected_arrays = []
    corrected_indices = []

    for codeword in encoded_arrays:
        codeword_np = np.array(codeword)
        syndrome = syndrome_check(codeword_np, H)
        corrected_bits = []

        if np.any(syndrome):
            error_indices = [i for i in range(len(codeword)) if np.array_equal(H[:, i], syndrome)]

            if error_indices:
                codeword_np[error_indices[0]] ^= 1
                corrected_bits.append(error_indices[0])
            else:
                for i in range(len(H[0])):
                    for j in range(i + 1, len(H[0])):
                        if np.array_equal(H[:, i] ^ H[:, j], syndrome):
                            codeword_np[i] ^= 1
                            codeword_np[j] ^= 1
                            corrected_bits.extend([i, j])
                            break
                    if corrected_bits:
                        break

        corrected_arrays.append(codeword_np.tolist())
        corrected_indices.append(corrected_bits)

    return corrected_arrays, corrected_indices

#input list of bits, output error position
def get_error_position(array):
    error_position = 0
    for i in [1, 2, 4, 8]:
        controlled = get_parity_list(i, len(array))
        parity = 0
        for message_bit in controlled:
            if message_bit < len(array):
                parity += array[message_bit]
        if parity % 2 != 0:
            error_position += i

    return error_position

#input list of bits, output
def check_and_correct(array):
    error_position = get_error_position(array)

    if error_position != 0 and error_position <= len(array):
        array[error_position - 1] ^= 1

    return array


def fix_errors(encoded_data, error_positions):
    data_bytes = bytearray(encoded_data)
    bit_arrays = bytes_to_bit_arrays(data_bytes, 12)

    for byte_idx, bit_idx in error_positions:
        if 0 <= byte_idx < len(bit_arrays) and 0 <= bit_idx < 12:
            start_bit = byte_idx * 12
            absolute_bit_pos = start_bit + bit_idx

            byte_pos = absolute_bit_pos // 8
            bit_in_byte = 7 - (absolute_bit_pos % 8)

            if byte_pos < len(data_bytes):
                data_bytes[byte_pos] ^= (1 << bit_in_byte)

    return bytes(data_bytes)


def fix_errors_2bit(encoded_data, error_positions):
    data_bytes = bytearray(encoded_data)
    bit_arrays = bytes_to_bit_arrays(data_bytes, 16)

    for byte_idx, bit_idx in error_positions:
        if 0 <= byte_idx < len(bit_arrays) and 0 <= bit_idx < 16:
            start_bit = byte_idx * 16
            absolute_bit_pos = start_bit + bit_idx

            byte_pos = absolute_bit_pos // 8
            bit_in_byte = 7 - (absolute_bit_pos % 8)

            if byte_pos < len(data_bytes):
                data_bytes[byte_pos] ^= (1 << bit_in_byte)

    return bytes(data_bytes)


def byte_to_bit_array(byte):
    return [int(bit) for bit in f'{byte:08b}']


def bytes_to_bit_arrays(data, bits_per_array):
    all_bits = []
    for byte in data:
        all_bits.extend(byte_to_bit_array(byte))

    result = []
    for i in range(0, len(all_bits), bits_per_array):
        if i + bits_per_array <= len(all_bits):
            result.append(all_bits[i:i + bits_per_array])

    return result


def extend(array):
    all_bits = list(chain.from_iterable(array))

    packed_bytes = bytearray()
    for i in range(0, len(all_bits), 8):
        byte_bits = all_bits[i:i + 8]

        if len(byte_bits) < 8:
            byte_bits += [0] * (8 - len(byte_bits))
        byte_value = int(''.join(map(str, byte_bits)), 2)
        packed_bytes.append(byte_value)
    return bytes(packed_bytes)