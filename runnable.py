def find_strings_in_binary_file(file_path, min_length=4):
    with open(file_path, 'rb') as file:
        data = file.read()

    current_string = b''
    strings = []

    for byte in data:
        if 32 <= byte <= 126 or byte == 10 or byte == 13:
            current_string += bytes([byte])
        else:
            if len(current_string) >= min_length:
                strings.append(current_string.decode('utf-8', errors='ignore'))
            current_string = b''

    if len(current_string) >= min_length:
        strings.append(current_string.decode('utf-8', errors='ignore'))
        print("String found!")

    return strings

if __name__ == "__main__":
    file_path = "karakuri.bin"
    found_strings = find_strings_in_binary_file(file_path)

    print("Found Strings:")
    for string in found_strings:
        print(string)