#!/usr/bin/env python3
#
#    Copyright (c) 2022 Project CHIP Authors
#    All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# TODO: Implement the decode method

CODES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
         'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
         'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
         'U', 'V', 'W', 'X', 'Y', 'Z', '-', '.']
RADIX = len(CODES)
BASE38_CHARS_NEEDED_IN_CHUNK = [2, 4, 5]
MAX_BYTES_IN_CHUNK = 3


def encode(bytes):
    total_bytes = len(bytes)
    qrcode = ''

    for i in range(0, total_bytes, MAX_BYTES_IN_CHUNK):
        if (i + MAX_BYTES_IN_CHUNK) > total_bytes:
            bytes_in_chunk = total_bytes - i
        else:
            bytes_in_chunk = MAX_BYTES_IN_CHUNK

        value = 0
        for j in range(i, i + bytes_in_chunk):
            value = value + (bytes[j] << (8 * (j - i)))

        base38_chars_needed = BASE38_CHARS_NEEDED_IN_CHUNK[bytes_in_chunk - 1]
        while base38_chars_needed > 0:
            qrcode += CODES[int(value % RADIX)]
            value = int(value / RADIX)
            base38_chars_needed -= 1

    return qrcode


def decode(base38_string):
    # Remove optional prefix if included by caller (e.g., 'MT:')
    if base38_string.startswith('MT:'):
        base38_string = base38_string[3:]

    # Validate characters and map to values
    code_to_val = {c: i for i, c in enumerate(CODES)}
    try:
        values = [code_to_val[c] for c in base38_string]
    except KeyError as e:
        raise ValueError(f"Invalid Base38 character: {e.args[0]}")

    n = len(values)
    if n == 0:
        return bytearray()

    # Determine last chunk size in base38 chars: 5 for 3 bytes, 4 for 2 bytes, 2 for 1 byte
    rem = n % 5
    if rem == 0:
        last_chunk_chars = 5
    elif rem in (2, 4):
        last_chunk_chars = rem
    else:
        raise ValueError('Invalid Base38 length; remainder must be 0, 2, or 4')

    chunks = []
    i = 0
    # All chunks except the last have 5 chars
    while i + 5 <= n - last_chunk_chars:
        chunks.append(values[i:i+5])
        i += 5
    # Append last chunk
    chunks.append(values[i:n])

    out = bytearray()
    for chunk in chunks:
        # Recreate the integer value; digits are little-endian within the chunk
        v = 0
        pow_radix = 1
        for d in chunk:
            v += d * pow_radix
            pow_radix *= RADIX

        # Map chunk length to number of bytes
        if len(chunk) == 5:
            num_bytes = 3
        elif len(chunk) == 4:
            num_bytes = 2
        elif len(chunk) == 2:
            num_bytes = 1
        else:
            raise ValueError('Invalid Base38 chunk size')

        for b in range(num_bytes):
            out.append((v >> (8 * b)) & 0xFF)

    return out
