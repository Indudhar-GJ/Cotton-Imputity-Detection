def convert_to_hex(numbers):
    return ''.join(f'{num:04X}' for num in numbers)

# Taking input from the user
numbers = list(map(int, input("Enter numbers separated by spaces: ").split()))

# Convert to hex string
hex_string = convert_to_hex(numbers)

# Output
print("Input (Decimal):", numbers)
print("Output (Hex):", hex_string)

