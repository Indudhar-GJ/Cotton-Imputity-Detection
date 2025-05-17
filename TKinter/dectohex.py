def hex_to_str(hex_val: str) -> str:
    """Convert a hex string (e.g., '0x01080009') to a binary-safe string."""
    hex_str = hex_val.lower().replace("0x", "")
    return bytes.fromhex(hex_str).decode('latin1')

def str_to_hex(s: str) -> int:
    """Convert the binary-safe string back to an integer (hex-style)."""
    return int.from_bytes(s.encode('latin1'), byteorder='big')

original_hex = '0x01080009'

# Convert to DB string
db_string = hex_to_str(original_hex)
print("DB string:", db_string)

# Convert back to integer
restored_int = str_to_hex(db_string)
print("Restored int:", restored_int)
print("Hex format:", hex(restored_int))
print("Type:", type(restored_int))
