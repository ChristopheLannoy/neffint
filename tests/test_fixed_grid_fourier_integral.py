#   Copyright 2023 neffint
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

from typing import Callable

import numpy as np
import pytest
from numpy.typing import ArrayLike

from neffint.fixed_grid_fourier_integral import (
    fourier_integral_fixed_sampling_pchip, _phi_and_psi)


def test_phi_and_psi():
    """Test phi_and_psi against calculation using the analytical formula using 200 decimal digit precision with mpmath."""
    input_x = np.array([1e-9, 1, 1e9, 1e18], dtype=np.float64)

    # Set tolerance to 10*machine precision
    comparison_tolerance = 10 * np.finfo(input_x.dtype).eps

    # Expected outputs generated with mpmath at 200 decimal digit precision
    expected_phi = np.array([
        0.5 + 3.5e-10j,
        0.37392456407295215539 + 0.31553567661778005804j,
        5.4584344944869956752e-10 - 8.3788718136390234542e-10j,
        -9.9296932074040507621e-19 - 1.1837199021871073261e-19j
    ])

    expected_psi = np.array([
        -0.0833333333333333333 - 5e-11j,
        -0.06739546857228461362 - 0.046145700566923663667j,
        8.3788717918052853757e-19 + 5.4584345480024828642e-19j,
        1.1837199021871073658e-37 - 9.9296932074040507374e-37j
    ])

    output_phi, output_psi = _phi_and_psi(input_x)

    assert output_phi == pytest.approx(expected_phi, rel=comparison_tolerance, abs=comparison_tolerance)
    assert output_psi == pytest.approx(expected_psi, rel=comparison_tolerance, abs=comparison_tolerance)


@pytest.mark.parametrize(("input_func", "expected_transform"), [
    ( lambda f: 1 / np.sqrt( 2 * np.pi * f),                        lambda t: np.sqrt(np.pi / (2 * t)) ),
    ( lambda f: np.array([[1,2],[3,4]]) / np.sqrt( 2 * np.pi * f),  lambda t: np.array([[1,2],[3,4]]) * np.sqrt(np.pi / (2 * t)) ), # Test dimension handling
    ( lambda f: 1 / (1 + (2 * np.pi * f)**2),                       lambda t: np.pi / 2 * np.exp(-t) ),
])
def test_fourier_integral_fixed_sampling_pchip(input_func: Callable[[ArrayLike], ArrayLike], expected_transform: Callable[[ArrayLike], ArrayLike]):
    """Test Fourier integral accuracy on function with an analytically known Fourier transform."""
    input_frequencies = np.logspace(-10,20,1000)
    input_times = np.logspace(-15, 0, 50)

    input_func_arr = np.array([input_func(freq) for freq in input_frequencies])

    output_transform_arr = fourier_integral_fixed_sampling_pchip(
        times=input_times,
        frequencies=input_frequencies,
        func_values=input_func_arr,
        inf_correction_term=True,
    )

    expected_transform_arr = np.array([expected_transform(time) for time in input_times])

    assert np.real(output_transform_arr) == pytest.approx(expected_transform_arr, rel=1e-4)
