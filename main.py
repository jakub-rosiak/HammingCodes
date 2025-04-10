import hamming


def parse_input(prompt):
    result = None
    while result is None:
        try:
            result = [int(digit) for digit in input(prompt)]
        except ValueError:
            print("Please enter a number")
    return result


def get_menu_choice(options):
    choice = None
    while choice not in options:
        choice = input("Enter your choice: ")
        if choice not in options:
            print(f"Invalid choice. Please enter one of: {', '.join(options)}")
    return choice


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


def display_binary_data(data, bits_per_group=8):
    """Display bytes data in binary format with specified bits per group"""
    bit_arrays = bytes_to_bit_arrays(data, bits_per_group)

    binary_representation = ""
    for bit_array in bit_arrays:
        binary_representation += "".join(map(str, bit_array)) + " "

    print("Binary representation:")
    print(binary_representation.strip())


def encode_file(encoding_type):
    input_file = input("Enter a file to encode: ")
    extension = ".1becc" if encoding_type == "1" else ".2becc"
    output_file = f"{input_file}{extension}"

    try:
        bit_list = []
        with open(input_file, "rb") as f:
            byte_data = f.read()
            for byte in byte_data:
                bit_list.append(byte)

        print(f"File loaded: {len(bit_list)} bytes read")

        if encoding_type == "1":
            encoded_data = hamming.encode(bit_list)
        else:
            encoded_data = hamming.encode_2bit(bit_list)

        with open(output_file, 'wb') as f:
            f.write(encoded_data)

        print(f"Encoding complete. Output saved to: {output_file}")

        # Display encoded data in binary format
        print("Encoded data:")
        display_binary_data(encoded_data)

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")


def encode_manual_input(encoding_type):
    print("Enter binary data (digits 0 and 1 only):")
    binary_input = parse_input("Binary input: ")

    bit_list = []
    for i in range(0, len(binary_input), 8):
        byte = binary_input[i:i + 8]
        while len(byte) < 8:
            byte.append(0)
        bit_list.append(byte)

    print(f"Manual input processed: {len(bit_list)} bytes")

    byte_values = [int("".join(map(str, bits)), 2) for bits in bit_list]
    data = bytes(byte_values)

    if encoding_type == "1":
        encoded_data = hamming.encode(data)
    else:
        encoded_data = hamming.encode_2bit(data)

    print("Encoded result:")
    print(encoded_data)

    # Display encoded data in binary format
    display_binary_data(encoded_data)


def decode_manual_input():
    print("Enter encoded binary data (digits 0 and 1 only):")
    binary_input = parse_input("Binary input: ")

    # Convert binary input to bytes
    byte_list = []
    for i in range(0, len(binary_input), 8):
        byte = binary_input[i:i + 8]
        while len(byte) < 8:
            byte.append(0)
        byte_value = int("".join(map(str, byte)), 2)
        byte_list.append(byte_value)

    encoded_data = bytes(byte_list)
    print(f"Manual input processed: {len(encoded_data)} bytes")

    # Determine encoding type
    print("Select encoding type:")
    print("1. 1-bit error correction")
    print("2. 2-bit error detection")
    encoding_type = get_menu_choice(["1", "2"])

    if encoding_type == "1":
        errors = hamming.check(encoded_data)
        if errors:
            print(f"Errors detected: {len(errors)} errors found")
            print("Error positions:", errors)
            print("Attempting to fix errors...")
            corrected_data = hamming.fix_errors(encoded_data, errors)
            print("Errors fixed, proceeding with decoding")
            decoded_data = hamming.decode(corrected_data)
        else:
            print("No errors detected in the data")
            decoded_data = hamming.decode(encoded_data)
    else:
        errors = hamming.check_2bit(encoded_data)
        if errors:
            print(f"Errors detected: {len(errors)} errors found")
            print("Error positions:", errors)
            print("Attempting to fix error...")
            corrected_data = hamming.fix_errors_2bit(encoded_data, errors)
            print("Error fixed, proceeding with decoding")
            decoded_data = hamming.decode_2bit(corrected_data)
        else:
            print("No errors detected in the data")
            decoded_data = hamming.decode_2bit(encoded_data)

    # Display the decoded data
    print("Decoded result as bytes:", decoded_data)

    # Display decoded data in binary format
    display_binary_data(decoded_data)


def check_and_decode_file():
    input_file = input("Enter a file to check and decode: ")

    try:
        with open(input_file, "rb") as f:
            encoded_data = f.read()

        if input_file.endswith(".1becc"):
            encoding_type = "1"
            output_file = input_file[:-6]
        elif input_file.endswith(".2becc"):
            encoding_type = "2"
            output_file = input_file[:-6]
        else:
            encoding_type = input("File extension not recognized. Enter encoding type (1 or 2): ")
            output_file = input("Enter output file name: ")

        if encoding_type == "1":
            errors = hamming.check(encoded_data)
            if errors:
                print(f"Errors detected: {len(errors)} errors found")
                print("Error positions:", errors)
                print("Attempting to fix errors...")
                corrected_data = hamming.fix_errors(encoded_data, errors)
                print("Errors fixed, proceeding with decoding")
                decoded_data = hamming.decode(corrected_data)
            else:
                print("No errors detected in the file")
                decoded_data = hamming.decode(encoded_data)
        else:
            errors = hamming.check_2bit(encoded_data)
            if errors:
                print(f"Errors detected: {len(errors)} errors found")
                print("Error positions:", errors)
                print("Attempting to fix error...")
                corrected_data = hamming.fix_errors_2bit(encoded_data, errors)
                print("Error fixed, proceeding with decoding")
                decoded_data = hamming.decode_2bit(corrected_data)
            else:
                print("No errors detected in the file")
                decoded_data = hamming.decode_2bit(encoded_data)

        with open(output_file, 'wb') as f:
            f.write(decoded_data)

        print(f"Decoding complete. Output saved to: {output_file}")

        # Display decoded data in binary format
        print("Decoded data:")
        display_binary_data(decoded_data)

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Error checking and decoding file: {str(e)}")


def encode_menu():
    print("\nSelect input method:")
    print("1. Encode a file")
    print("2. Manually enter binary input")

    input_choice = get_menu_choice(["1", "2"])

    print("\nSelect encoding type:")
    print("1. 1-bit error detection")
    print("2. 2-bit error detection")

    encoding_choice = get_menu_choice(["1", "2"])

    if input_choice == "1":
        encode_file(encoding_choice)
    else:
        encode_manual_input(encoding_choice)


def decode_menu():
    print("\nSelect input method:")
    print("1. Decode a file")
    print("2. Manually enter binary input")

    input_choice = get_menu_choice(["1", "2"])

    if input_choice == "1":
        check_and_decode_file()
    else:
        decode_manual_input()


def main():
    print("Hamming Code System")
    print("===================")

    while True:
        print("\nSelect operation:")
        print("1. Encode data")
        print("2. Check and decode data")
        print("3. Exit")

        operation = get_menu_choice(["1", "2", "3"])

        if operation == "1":
            encode_menu()
        elif operation == "2":
            decode_menu()
        else:
            print("Exiting program. Goodbye!")
            break


if __name__ == '__main__':
    main()