"""Tests of margin bounding utility functions"""

import numpy as np
import numpy.testing as npt
import pytest

import hipscat.pixel_math as pm

from astropy.coordinates import SkyCoord
from regions import PixCoord

def test_get_margin_scale():
    """Check to make sure that get_margin_scale works as expected."""
    scale = pm.get_margin_scale(3, 0.1)
    
    expected = 1.0274748806654526

    assert scale == expected

def test_get_margin_scale_k_zero():
    """Make sure get_margin_scale works when k == 0"""
    scale = pm.get_margin_scale(0, 0.1)

    expected = 1.0034139979085752

    assert scale == expected

def test_get_margin_scale_k_high():
    """Make sure get_margin_scale works when k is a high order"""
    scale = pm.get_margin_scale(64, 0.1)

    expected = 9.89841281541636e+32

    assert scale == expected

def test_negative_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is < 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, -0.1)

    assert(
        str(value_error.value)
        == "margin_threshold must be greater than 0."
    )

def test_negative_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is == 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, 0.0)

    assert(
        str(value_error.value)
        == "margin_threshold must be greater than 0."
    )

def test_get_margin_bounds_and_wcs():
    """Make sure get_margin_bounds_and wcs works as expected."""
    # far out point, expect False
    test_ra1 = 42.
    test_dec1 = 1.

    # middle of our healpixel, expect True
    test_ra2 = 56.25
    test_dec2 = 14.49584495

    # actual point from Norder3/Npix4 of my
    # gaia test catalog, expect True
    # if k = 3 and pix = 4
    test_ra3 = 50.61225197
    test_dec3 = 14.4767556

    test_ra = np.array([test_ra1, test_ra2, test_ra3])
    test_dec = np.array([test_dec1, test_dec2, test_dec3])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    scale = pm.get_margin_scale(3, 0.1)
    polygon, wcs_margin = pm.get_margin_bounds_and_wcs(3, 4, scale)[0]

    assert polygon.area == 757886549.2645547

    x, y = wcs_margin.world_to_pixel(test_sc)

    pc = PixCoord(x, y)
    checks = polygon.contains(pc)

    expected = np.array([False, True, True])

    npt.assert_array_equal(checks, expected)


def test_get_margin_bounds_and_wcs_low_order():
    """Make sure get_margin_bounds_and wcs works as expected."""
    # far out point, expect False
    test_ra1 = 90.
    test_dec1 = -2.

    # middle of our healpixel, expect True
    test_ra2 = -100.
    test_dec2 = -45.

    test_ra = np.array([test_ra1, test_ra2])
    test_dec = np.array([test_dec1, test_dec2])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    scale = pm.get_margin_scale(0, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(0, 5, scale)

    assert len(bounds) == 16

    vals = []
    for p, w in bounds:
        x, y = w.world_to_pixel(test_sc)

        pc = PixCoord(x, y)
        vals.append(p.contains(pc))

    checks = np.array(vals).any(axis=0)
    
    expected = np.array([True, False])

    npt.assert_array_equal(checks, expected)

def test_get_margin_bounds_and_wcs_north_pole():
    """Make sure get_margin_bounds_and_wcs works at pixels along the north polar region"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 7, scale)

    assert len(bounds) == 4

def test_get_margin_bounds_and_wcs_south_pole():
    """Make sure get_margin_bounds_and_wcs works at pixels along the south polar region"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 36, scale)

    assert len(bounds) == 4

