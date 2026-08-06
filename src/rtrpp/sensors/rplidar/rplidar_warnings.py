class RPLidarHealthWarning(UserWarning):
    """Warning emitted when the RPLidar reports a non-fatal health risk."""


# Test warning emission
# with pytest.warns(RPLidarHealthWarning):
#     driver.reset()

# assert driver.working_state is prot.RPLidarWorkingState.IDLE
