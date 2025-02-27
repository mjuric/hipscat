"""Tests of partition info functionality"""
import os

import numpy.testing as npt
import pandas as pd
import pytest

from hipscat.catalog import PartitionInfo
from hipscat.io import file_io, paths
from hipscat.pixel_math import HealpixPixel


def test_load_partition_info_small_sky(small_sky_dir):
    """Instantiate the partition info for catalog with 1 pixel"""
    partition_info_file = paths.get_parquet_metadata_pointer(small_sky_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 1
    expected = [HealpixPixel(0, 11)]
    assert order_pixel_pairs == expected


def test_load_partition_info_from_metadata(small_sky_dir, small_sky_source_dir, small_sky_source_pixels):
    """Instantiate the partition info for catalogs via the `_metadata` file"""
    metadata_file = paths.get_parquet_metadata_pointer(small_sky_dir)
    partitions = PartitionInfo.read_from_file(metadata_file)
    assert partitions.get_healpix_pixels() == [HealpixPixel(0, 11)]

    metadata_file = paths.get_parquet_metadata_pointer(small_sky_source_dir)
    partitions = PartitionInfo.read_from_file(metadata_file)
    assert partitions.get_healpix_pixels() == small_sky_source_pixels

    partitions = PartitionInfo.read_from_file(metadata_file, strict=True)
    assert partitions.get_healpix_pixels() == small_sky_source_pixels


def test_load_partition_info_from_metadata_fail(tmp_path):
    empty_dataframe = pd.DataFrame()
    metadata_filename = os.path.join(tmp_path, "empty_metadata.parquet")
    empty_dataframe.to_parquet(metadata_filename)
    with pytest.raises(ValueError, match="missing Norder"):
        PartitionInfo.read_from_file(metadata_filename)

    with pytest.raises(ValueError, match="at least one column"):
        PartitionInfo.read_from_file(metadata_filename, strict=True)

    non_healpix_dataframe = pd.DataFrame({"data": [0], "Npix": [45]})
    metadata_filename = os.path.join(tmp_path, "non_healpix_metadata.parquet")
    non_healpix_dataframe.to_parquet(metadata_filename)
    with pytest.raises(ValueError, match="missing Norder"):
        PartitionInfo.read_from_file(metadata_filename)

    with pytest.raises(ValueError, match="empty file path"):
        PartitionInfo.read_from_file(metadata_filename, strict=True)


def test_load_partition_info_small_sky_order1(small_sky_order1_dir):
    """Instantiate the partition info for catalog with 4 pixels"""
    partition_info_file = paths.get_parquet_metadata_pointer(small_sky_order1_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 4
    expected = [
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]
    assert order_pixel_pairs == expected


def test_load_partition_no_file(tmp_path):
    wrong_path = os.path.join(tmp_path, "_metadata")
    wrong_pointer = file_io.get_file_pointer_from_path(wrong_path)
    with pytest.raises(FileNotFoundError):
        PartitionInfo.read_from_file(wrong_pointer)

    wrong_path = os.path.join(tmp_path, "partition_info.csv")
    wrong_pointer = file_io.get_file_pointer_from_path(wrong_path)
    with pytest.raises(FileNotFoundError):
        PartitionInfo.read_from_csv(wrong_pointer)


def test_get_highest_order(small_sky_order1_dir):
    """test the `get_highest_order` method"""
    partition_info_file = paths.get_parquet_metadata_pointer(small_sky_order1_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    highest_order = partitions.get_highest_order()

    assert highest_order == 1


def test_write_to_file(tmp_path, small_sky_pixels):
    """Write out the partition info to file and make sure we can read it again."""
    partition_info_pointer = paths.get_parquet_metadata_pointer(tmp_path)
    partition_info = PartitionInfo.from_healpix(small_sky_pixels)
    partition_info.write_to_file(partition_info_pointer)

    new_partition_info = PartitionInfo.read_from_csv(partition_info_pointer)

    # We're not using parquet metadata, so we don't force a re-sorting.
    assert partition_info.get_healpix_pixels() == new_partition_info.get_healpix_pixels()


def test_write_to_file_sorted(tmp_path, pixel_list_depth_first, pixel_list_breadth_first):
    """Write out the partition info to file and make sure that it's sorted by breadth-first healpix,
    even though the original pixel list is in Norder-major sorting (depth-first)."""
    partition_info = PartitionInfo.from_healpix(pixel_list_depth_first)
    npt.assert_array_equal(pixel_list_depth_first, partition_info.get_healpix_pixels())
    partition_info.write_to_metadata_files(tmp_path)

    partition_info_pointer = paths.get_parquet_metadata_pointer(tmp_path)
    new_partition_info = PartitionInfo.read_from_file(partition_info_pointer)

    npt.assert_array_equal(pixel_list_breadth_first, new_partition_info.get_healpix_pixels())
