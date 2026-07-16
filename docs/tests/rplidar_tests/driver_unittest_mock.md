# Unit Testing with Mocking

## Introduction

When developing software that interacts with hardware, it is often impractical to rely on the actual hardware for testing. This is where mocking comes in. Mocking allows you to create simulated versions of your hardware interfaces, enabling you to test your code without needing the physical device.

## Why do we use mocking?
Let's say you want to test the driver layer's `get_info()` method, which communicates with the RPLIDAR S2L hardware. If you used the actual hardware in your tests, you would need to have the device connected and powered on every time you run your tests. Additionally, a serial port mush exist and be available for the tests to run. This can make your tests slow, flaky, and dependent on external factors. By using mocking, you can simulate the behavior of the hardware and test your code in isolation.

One way to achieve simulating hardware behavior is by building your own mock classes that mimic the behavior of the hardware interfaces. For instance, in this project, we have created mock classes for the transport layers of the RPLIDAR S2L driver. These mock classes can be used to simulate the behavior of the hardware, allowing you to test your code without needing the actual device. In the `test_driver.py` file, we have implemented the following mock classes:

```python
import serial

class MockTransport:
    """ A mock transport class that simulates the behavior of the RPLidarTransport class for testing purposes. """
    def __init__(
            self,
            responses: list[bytes] | None = None,
            fail_on_write: bool = False, 
            fail_on_read: bool = False,
    ):
        self.responses = list(responses or [])
        self.fail_on_write = fail_on_write
        self.fail_on_read = fail_on_read
        self.written = b""

    def write(self, data) -> int:
        if self.fail_on_write:
            raise serial.SerialException("Simulated write failure.")
        
        self.written += data
        return len(data)
    
    def read(self, size: int) -> bytes:
        if self.fail_on_read:
            raise serial.SerialException("Simulated read failure.")
        
        if not self.responses:
            return b""
        
        response = self.responses.pop(0)
        return response[:size]

class OSErrorTransport:
    def __init__(
            self,
            fail_on_write: bool = False,
            fail_on_read: bool = False,
    ):
        self.fail_on_write = fail_on_write
        self.fail_on_read = fail_on_read

    def write(self, data: bytes) -> int:
        if self.fail_on_write:
            raise OSError("Simulated device disconnection.")
    
    def read(self, size: int) -> bytes:
        if self.fail_on_read:
            raise OSError("Simulated device disconnection.")
```
- `MockTransport`: This class simulates the behavior of the RPLidarTransport class. It can be configured to return predefined responses or simulate failures on write and read operations.
- `OSErrorTransport`: This class simulates a transport layer that raises an OSError to mimic a device disconnection scenario. It can be configured to raise an OSError on write and read

However, this can be time-consuming and may not cover all edge cases. A more efficient approach is to use the `unittest.mock` library, which provides a flexible and powerful way to create mock objects and control their behavior. 

## What is `unittest.mock`?
`unittest.mock` is a powerful library for testing in Python. It allows you to replace parts of your system under test and make assertions about how they have been used. This is particularly useful for testing code that interacts with external systems, such as hardware devices, without needing to have the actual hardware present. Its core features include:
- Simulating Behavior: This allows the return of specific predefined values or trigger specific exceptions without executing the actual code.
- Tracking Interactions: This allows you to record every function call, and verify how many times a dependency was called, with what arguments, and in what order.
- Decouple Testing: This allows you to test your code in isolation, eliminating network latencies or hardware requirements, and ensuring that your tests are fast and reliable.

## `unittest.mock` Core Tools

### Mock Class
The `Mock` class is the base class to build simulated objects. It is a flexible mock object that is intended to be used as a replacement for any object in your code. It can be configured to return specific values, raise exceptions, and track how it was called. `Mock` objects are callable and can create attributes and methods on the fly. This makes them very versatile for testing purposes.

```python
class unittest.mock.Mock(spec=None, side_effect=None, return_value=DEFAULT, wraps=None, name=None, spec_set=None, unsafe=False, **kwargs)
```

For more information on the `Mock` class, refer to the [official documentation](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock).

#### Using `Mock` to Simulate In Driver Layer Testing
In the context of testing the driver layer, we can use `Mock` to simulate the behavior of the transport layer. For example, we can create a mock transport object that returns predefined responses for the `get_info()`, `get_health()`, and `get_samplerate()` methods. This allows us to test the driver layer's methods without needing the actual hardware present. We can also simulate failures in the transport layer, such as timeouts or communication errors, to ensure that the driver layer handles these scenarios gracefully.

__Creating a mock transport object:__

```python
from unittest.mock import Mock

# Create a mock transport object
mock_transport = Mock() 
```

__Verifying Method Calls:__
```python
mock_transport = Mock()

driver = RPLidarDriver(transport=mock_transport)

# Call the get_info() method
driver.get_info()

mock_transport.write.assert_called_once_with (b'\xA5\x50')  # Verify that the write method was called with the correct command
mock_transport.read.assert_called_once()  # Verify that the read method was called once
```
__Returning Predefined Responses:__ We can configure the mock transport object to return specific responses when its methods are called. For example, we can set up the `read` method to return a predefined response for the `get_info()` method. Without having to write a custom mock class such as `MockTransport`, we can use the `return_value` attribute of the mock object to specify what should be returned when the method is called.

```python
# Configure the mock transport to return a predefined response for get_info()
mock_transport.read.return_value = b'\x00\x01\x02\x03'  # This is a placeholder for the actual response bytes that would be returned by the hardware.
```

__Side Effects:__ The `side_effect` attribute allows you to specify a function or an iterable that will be called or returned when the mock is called. This is useful for simulating different behaviors, such as raising exceptions or returning different values on subsequent calls.

__Raising Exceptions:__
```python
import serial
mock_transport.write.side_effect = serial.SerialException("Simulated write failure.")
```
__Multiple Return Values:__
Since `driver.get_info()` may call `transport.read()` multiple times, we can use an iterable as the `side_effect` to return different values on each call.

```python
# Returns different values on subsequent calls
mock_transport.read.side_effect = [
    descriptor_response, 
    data_response
]  
```

__Asserting Calls:__ The `assert_called_with()` and `assert_called_once_with()` methods allow you to verify that the mock was called with specific arguments. This is useful for ensuring that your code is interacting with the mock as expected, since `Mocks` remembers how they were used. You can also use `assert_called()` and `assert_not_called()` to check if the mock was called at all.

```python
mock_transport.write.assert_called_once_with(b'\xA5\x50') # Verify that the write method was called with the correct command
mock_transport.read.assert_called_once() # Verify that the read method was called once
```

__call_count:__ The `call_count` attribute allows you to check how many times the mock was called. This is useful for verifying that your code is making the expected number of calls to the mock.

```python
mock_transport.write.call_count  # Returns the number of times the write method was called
assert mock_transport.write.call_count == 1  # Verify that the write method was called exactly once
```

__call_args__: The `call_args` attribute allows you to inspect the arguments that were passed to the mock during its last call. This is useful for verifying that your code is passing the correct arguments to the mock.

```python
mock_transport.write.call_args  # Returns the arguments that were passed to the write method during its last call
assert mock_transport.write.call_args == ((b'\xA5\x50')) 
```
Or suppose you want to know what packet was written to the transport layer during the last call, you can print the `call_args` attribute to see the arguments that were passed to the mock during its last call. This can be useful for debugging and verifying that your code is interacting with the mock as expected.

```python
print(mock_transport.write.call_args)  # Might Output: call(b'\xA5\x50')
```

__call_args_list__: The `call_args_list` attribute allows you to inspect the arguments that were passed to the mock during all of its calls. This is useful for verifying that your code is passing the correct arguments to the mock over multiple calls.

```python
mock_transport.write.call_args_list  # Returns a list of all the arguments that were passed to the write method during all of its calls
assert mock_transport.write.call_args_list == [
    call(b'\xA5\x25'),
    call(b'\xA5\x50'),
]
```
This is useful for testing scenarios such as scan start/stop.

__patch():__ The `patch()` function is a decorator or context manager that allows you to temporarily replace an object in your code with a mock. This is useful for testing code that interacts with external systems, such as hardware devices, without needing to have the actual hardware present. You can use `patch()` to replace the transport layer with a mock transport object during your tests.

Suppose the `RPLidarDriver` class has a method that is defined with a `time.sleep()`. Instead of waiting for the actual sleep duration during testing, you can use `patch()` to replace `time.sleep()` with a mock that does nothing. The `time.sleep()` in your code is still called by the driver, but Python will use the mock instead of the actual `time.sleep()` function, allowing your tests to run faster.
```python
from unittest.mock import patch

@patch(
    "rtrpp.sensors.rplidar.driver.time.sleep", return_value=None
)
def test_stop(mock_sleep):
    driver = RPLidarDriver(transport=mock_transport)
    driver.stop()
    mock_sleep.assert_called_once_with(0.001)  # Verify that time.sleep() was called once with the expected argument

```