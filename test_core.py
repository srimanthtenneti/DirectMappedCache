import cocotb
from cocotb.triggers import RisingEdge, Timer
import random

# Function to generate a random 22-bit address
def random_address():
    return random.randint(0, (1 << 22) - 1)  # Ensure it's within the 22-bit range

# Clock generator coroutine
async def clock_gen(dut):
    """Generate clock pulses."""
    while True:
        dut.clk.value = 0
        await Timer(5, units='ns')  # Set clock period to 10ns
        dut.clk.value = 1
        await Timer(5, units='ns')

@cocotb.test()
async def test_direct_mapped_cache(dut):
    """Test the DirectMappedCache Verilog module."""

    # Start clock generation
    cocotb.start_soon(clock_gen(dut))

    # Reset the design
    dut.resetn.value = 0
    await RisingEdge(dut.clk)  # Wait for clock edge
    dut.resetn.value = 1
    await RisingEdge(dut.clk)

    # Test 1: Write to cache and check for a cache hit
    write_address = random_address()  # Random 22-bit address to write
    write_data = 0xDEADBEEF  # Random data to write

    dut.address.value       = write_address
    dut.write_data.value    = write_data
    dut.write_enable.value  = 1
    dut.read_enable.value   = 0

    # Perform the write operation
    await RisingEdge(dut.clk)
    dut.write_enable.value = 0  # Disable write after one cycle

    await RisingEdge(dut.clk)
    assert dut.hit.value == 0, "Write should result in a cache miss initially"
    
    # Test 2: Read from cache and check for a cache hit
    dut.address.value       = write_address
    dut.write_enable.value  = 0
    dut.read_enable.value   = 1

    # Perform the read operation
    await RisingEdge(dut.clk)
    dut.read_enable.value = 0  # Disable read after one cycle

    await RisingEdge(dut.clk)
    assert dut.hit.value == 1, "Read should result in a cache hit"
    assert dut.read_data.value == write_data, f"Read data {dut.read_data.value} does not match written data {write_data}"

    # Test 3: Test cache miss with a different address
    miss_address = random_address()  # Generate another random 22-bit address
    dut.address.value = miss_address
    dut.write_enable.value = 0
    dut.read_enable.value = 1

    # Perform the read operation for a cache miss
    await RisingEdge(dut.clk)
    dut.read_enable.value = 0  # Disable read after one cycle

    await RisingEdge(dut.clk)
    assert dut.hit.value == 0, "Read should result in a cache miss"

    # Test 4: Write and read to/from different addresses
    addresses = [random_address() for _ in range(10)]  # Generate 10 random 22-bit addresses
    data = [random.randint(0, 0xFFFFFFFF) for _ in range(10)]

    for addr, dat in zip(addresses, data):
        # Write data to cache
        dut.address.value = addr
        dut.write_data.value = dat
        dut.write_enable.value = 1
        dut.read_enable.value = 0
        await RisingEdge(dut.clk)
        dut.write_enable.value = 0
        await RisingEdge(dut.clk)

        # Verify cache miss initially
        assert dut.hit.value == 0, "Initially should be a cache miss"

        # Read data from cache
        dut.address.value = addr
        dut.read_enable.value = 1
        await RisingEdge(dut.clk)
        dut.read_enable.value = 0
        await RisingEdge(dut.clk)

        # Verify cache hit and correct read data
        assert dut.hit.value == 1, f"Read from address {hex(addr)} should result in a cache hit"
        assert dut.read_data.value == dat, f"Read data {dut.read_data.value} does not match written data {dat}"
