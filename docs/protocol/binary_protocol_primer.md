# Binary Protocol Primer
A binary protocol defines how two devices exchange information using sequences of bytes. Each byte has a predefined meaning, allowing both devices to interpret commands and responses consistently.

## Bytes and Bit Numbering
A byte is a sequence of 8 bits, and each bit can be numbered from 0 to 7, where bit 0 is the least significant bit (LSB) and bit 7 is the most significant bit (MSB). The numbering of bits in a byte is as follows:

```text
7 6 5 4 3 2 1 0
```

The Most Significant Bit (MSB) is the leftmost bit (bit 7), and the Least Significant Bit (LSB) is the rightmost bit (bit 0). The MSB represents the highest value in the byte, while the LSB represents the lowest value. For example, in the byte `0xA5`:
```text
7 6 5 4 3 2 1 0
1 0 1 0 0 1 0 1
```
The MSB is `1` which represents the value `128`, and the LSB is `1` which represents the value `1`. The total value of the byte can be calculated as:
```
(1 * 128) + (0 * 64) + (1 * 32) + (0 * 16) + (0 * 8) + (1 * 4) + (0 * 2) + (1 * 1) = 165
```

## Endianess
Endianess refers to the order in which bytes are arranged in memory. There are two common types of endianess: big-endian and little-endian. In big-endian, the most significant byte is stored at the lowest memory address, while in little-endian, the least significant byte is stored at the lowest memory address. For example, the 16-bit value `0x1234` can be represented in memory as follows:
- Big-endian: `0x12 0x34`
- Little-endian: `0x34 0x12`

## Bitwise Operations
Bitwise operations are used to manipulate individual bits within a byte. The most common bitwise operations are:
- AND (`&`): Compares each bit of two bytes and returns `1` if both bits are `1`, otherwise returns `0`. 
- OR (`|`): Compares each bit of two bytes and returns `1` if at least one of the bits is `1`, otherwise returns `0`. 
- XOR (`^`): Compares each bit of two bytes and returns `1` if the bits are different, otherwise returns `0`. 
- NOT (`~`): Inverts each bit of a byte, changing `1` to `0` and `0` to `1`.
- Left Shift (`<<`): Shifts the bits of a byte to the left by a specified number of positions, filling the rightmost bits with `0`.
- Right Shift (`>>`): Shifts the bits of a byte to the right by a specified number of positions, filling the leftmost bits with `0`. 

## Bit Masks
A bit mask is a binary pattern used to isolate or modify specific bits within a byte. By applying a bitwise AND operation with a mask, you can extract specific bits from a byte. For example, to extract the least significant bit (LSB) from a byte, you can use the mask `0x01`:
```python
byte = 0xA5  # 10100101 in binary
lsb = byte & 0x01  # Extracts the least significant bit
print(lsb)  # Output: 1
```

## Sequence Unpacking
In Python, you can unpack a sequence of bytes into individual variables using tuple unpacking. For example, if you have a bytes objects representing a data packet, you can unpack it as follows:
```python
packet = b'\xA5\x95\x12\xC8\x03'
b0, b1, b2, b3, b4 = packet
```

## Fixed-Point Representation
Fixed-point representation is a way to represent real numbers using integers. In this representation, a fixed number of bits are allocated for the integer part and a fixed number of bits are allocated for the fractional part. For example, in Q6 format, 6 bits are used for the fractional part, and the remaining bits are used for the integer part. To convert a fixed-point number to a floating point number, you can divide the integer value by `2^n`, where `n` is the number of bits allocated for the fractional part. For example, to convert a Q6 fixed-point number to a floating-point number, you can divide the integer by `2^6` (or `64.0`):
```python
fixed_point_value = 0x1295  # Q6 fixed-point representation
floating_point_value = fixed_point_value / 64.0  # Converts to floating-point representation
print(floating_point_value)  # Output: 18.328125
```

## Building integers from multiple bytes
To build an integer from multiple bytes, you can use bitwise operations and shifting. For example, to build a 16-bit integer from two bytes, you can shift the upper byte left by 8 bits and then perform a bitwise OR operation with the lower byte:
```python
upper_byte = 0x12
lower_byte = 0x34
integer_value = (upper_byte << 8) | lower_byte  # Combines the upper and lower bytes into a single 16-bit integer
print(integer_value)  # Output: 4660

integer_value_two = lower_byte | (upper_byte << 8)  # Combines the lower and upper bytes into a single 16-bit integer
print(integer_value_two)  # Output: 4660
```



## RPLidar SCAN Mode Response Data Packet Walkthrough

The RPLidar SCAN mode response data packet consists of 5 bytes, each with a specific meaning. The following table describes the structure of the data packet:

```text
Byte 0: quality + start flags
Byte 1: lower angle bits + check bit
Byte 2: upper angle bits
Byte 3: lower distance bits
Byte 4: upper distance bits
```

Using the unpacked bytes from the data packet, we can extract the relevant information using bitwise operations and shifting. The following code snippet demonstrates how to extract the start flag, not start flag, quality, check bit, angle in degrees, and distance in millimeters from the data packet:
```python
b0, b1, b2, b3, b4 = packet

start_flag = b0 & 0x01
not_start_flag = (b0 >> 1) & 0x01
quality = b0 >> 2

check_bit = b1 & 0x01

angle_q6 = ((b2 << 8) | b1) >> 1
angle_degrees = angle_q6 / 64.0

distance_q2 = (b4 << 8) | b3
distance_mm = distance_q2 / 4.0
```

Suppose we have a data packet with the following bytes:
```
A5 95 12 C8 03
```
In Python, the packet arrives as a bytes object:

```python
packet = b'\xA5\x95\x12\xC8\x03'
```

### Unpacking the Packet

We can unpack the sequence of bytes in the packet into its individual bytes:

```python
b0, b1, b2, b3, b4 = packet
```

This is equivalent to:
```python
b0 = packet[0]
b1 = packet[1]
b2 = packet[2] 
b3 = packet[3]
b4 = packet[4]
```

### Extracting data byte by byte

__Byte 0: Quality and Start Flags__:
The RPLidar SCAN mode response protocol states that the within the first byte, the least significant bit (LSB) is the start flag, the next bit is the inverse of the start flag, and the remaining bits represent the quality of the measurement.

```text
7 6 5 4 3 2 1 0
Quality Quality Quality Quality NotStartFlag StartFlag
```

Suppose that the first byte `b0` is `0xA5` (which is `10100101` in binary). The byte can be broken down as follows:
```text
7 6 5 4 3 2 1 0
1 0 1 0 0 1 0 1
```

But we want to extract the start flag, not start flag, and quality from this byte. We can do this using bitwise operations:

```python
start_flag = b0 & 0x01  # Extracts the least significant bit
not_start_flag = (b0 >> 1) & 0x01  # Shifts right by 1 and extracts the next bit
quality = b0 >> 2  # Shifts right by 2 to get the quality bits
```

What the first line does is it performs a bitwise AND operation between `b0` and `0x01`:
```code
  10100101
& 00000001
-----------
  00000001
```
If `b0` is `0xA6`, the result of `start_flag` will be:
```code 
    10100110
& 00000001
-----------
    00000000
```
Thus, `start_flag` will be `0`, indicating that data packet is a result of a contining scan, not a new scan. The `not_start_flag` will be `1`, indicating that this is not the start of a new scan. The `quality` will be `0x29` (or `41` in decimal), which indicates the quality of the measurement.

The next bit of the first byte is the inverse of the start flag, which for the case of `b0 = 0xA5` (or `10100101` in binary) will be `0`. To extract the inverse of the start flag, we can shift the byte right by 1 and then perform a bitwise AND operation with `0x01`:
```python
not_start_flag = (b0 >> 1) & 0x01
```

Lastly, the remaining bits of the first byte represent the quality of the measurement. To extract the quality, we can shift the byte right by 2. 
```python
quality = b0 >> 2
```
For the case of `b0 = 0xA5`, the quality will be `0x29` (or `41` in decimal), which indicates the quality of the measurement. The operation range for quality is from `0` to `63`, where `0` indicates a failed measurement and `63` indicates a perfect measurement. The quality value can be used to filter out low-quality measurements from the LiDAR data.

__Byte 1: Lower Angle Bits and Check Bit__:
The second byte contains the lower angle bits and a check bit. The check bit is the least significant bit (LSB) of the byte, and the remaining bits represent the lower angle bits.

```python
check_bit = b1 & 0x01  # Extracts the least significant bit
lower_angle_bits = b1 >> 1  # Shifts right by 1 to get the lower angle bits
```

Note: The check bit is used to verify the integrity of the data packet. If the check bit is `1`, it indicates that the data packet is valid, and if it is `0`, it indicates that the data packet is invalid. The lower angle bits can be combined with the upper angle bits from byte 2 to calculate the angle of the measurement.

__Byte 2: Upper Angle Bits__:
The third byte contains the upper angle bits. To extract the upper angle bits, we can simply read the byte as is:
```python
upper_angle_bits = b2  # The entire byte represents the upper angle bits
```

However, a more common approach is to extract the lower and upper angle bits and combine them to get the full angle value. Suppose the lower angle bits are `0x95` (or `149` in decimal) and the upper angle bits are `0x12` (or `18` in decimal). We can combine the shifted upper angle bits with the lower angle bits using a bitwise OR operation:

```python
angle_q6 = ((b2 << 8) | b1) >> 1
```

Breaking it down the `b2` value is shifted left by 8 bits to make room for the lower angle bits:
```python
b2 << 8  # Shift the upper angle bits left by 8 bits
```
This process ensures that the value of `b2` will move to the left by 8 bits, and will append 8 zeros to the right to make room for the lower angle bits. 
```
00010010 00000000
```

Ultimately, the lower angle bits are combined with the shifted upper angle bits using a bitwise OR operation:
```python
(b2 << 8) | b1 >> 1  # Combines the shifted upper angle bits with the lower angle bits and shifts the result right by 1 to get the final angle value in Q6 format
```
This operation will result in a 16-bit value that represents the angle in Q6 format, and in this case the value of angle_q6 will be `0x1295` (or `00010010 01001010` in binary).

Since the angle is represented in Q6 format, we can convert it to degrees by dividing the value by `64.0`:
```python
angle_degrees = angle_q6 / 64.0  # Converts the angle from Q6 format to degrees
```

__Byte 3 and Byte 4: Lower and Upper Distance Bits__:
The fourth and fifth bytes contain the lower and upper distance bits, respectively. To extract the distance, we can combine the two bytes into a single 16-bit value and then convert it to millimeters by dividing by `4.0`:
```python
distance_q2 = (b4 << 8) | b3  # Combines the upper and lower distance bits into a single 16-bit value
distance_mm = distance_q2 / 4.0  # Converts the distance from Q2 format to millimeters
```

## Summary
To summarize, for this binary protocol, we can extract the received data packet into its individual bytes, and then use bitwise operations and shifting to extract the start flag, not start flag, quality, check bit, angle, and distance from the packet. The big picture here is:
1. Extracting individual bits can be done by using masks (&) and shifts (>>).
2. Combining multiple bytes can be done by shifting (<<) and using bitwise OR (|).
3. Converting the fixed-point representation to a floating-point representation can be done by dividing by the appropriate factor (e.g., 64.0 for Q6 format and 4.0 for Q2 format).




