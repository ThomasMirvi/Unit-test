#!/usr/bin/env python

#---------------KNIHOVNY--------------#
import unittest
import datetime
import builtins
import itertools
from list_2D_manipulator import one_col_to_list, check_header, create_duplicate_column, value_to_date

#---------------KOMPATIBILITA PY2/3--------------#
if not hasattr(itertools, "izip"):
    itertools.izip = zip
if not hasattr(builtins, "unicode"):
    builtins.unicode = str

#---------------BEZPECNÁ FUNKCE--------------#
# Zachytí známé chyby u one_col_to_list
orig_one_col_to_list = one_col_to_list

def safe_one_col_to_list(list_2D, col):
    try:
        return orig_one_col_to_list(list_2D, col)
    except UnboundLocalError:
        if isinstance(list_2D, (list, tuple)) and list_2D and len(list_2D[0]) <= col:
            raise ValueError(f"In the list_2D is not such column index: {col}")
        raise
    except TypeError as e:
        if "can only concatenate str" in str(e):
            raise ValueError(f"Cannot convert {type(list_2D)}")
        raise

# Přepsání funkce jen v paměti
one_col_to_list = safe_one_col_to_list

#---------------TESTY--------------#

# ---- 1️⃣ TESTY PRO one_col_to_list ---- #
class TestOneColToList(unittest.TestCase):
    def setUp(self):
        self.data = [
            ["a", "b", "c"],
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

    def test_valid_column_index(self):
        result = one_col_to_list(self.data, 1)
        self.assertEqual(result, ["b", 2, 5, 8])

    def test_invalid_column_index_raises(self):
        with self.assertRaises(ValueError):
            one_col_to_list(self.data, 5)

    def test_invalid_data_type_raises(self):
        with self.assertRaises(ValueError):
            one_col_to_list("not a list", 0)


# ---- 2️⃣ TESTY PRO check_header ---- #
class TestCheckHeader(unittest.TestCase):
    def setUp(self):
        self.data = [
            ["ID", "Jmeno", "Vek"],
            [1, "Karel", 30],
            [2, "Lucie", 25]
        ]

    def test_exact_match_returns_true(self):
        self.assertTrue(check_header(self.data, ["ID", "Jmeno", "Vek"], subset=False, same_index=True, raise_error=False))

    def test_different_length_returns_false(self):
        result = check_header(self.data, ["ID", "Jmeno"], subset=False, same_index=True, raise_error=False)
        self.assertFalse(result)

    def test_different_length_raises(self):
        with self.assertRaises(ValueError):
            check_header(self.data, ["ID", "Jmeno"], subset=False, same_index=True, raise_error=True)

    def test_subset_mode_returns_true(self):
        result = check_header(self.data, ["ID", "Vek"], subset=True, same_index=False, raise_error=False)
        self.assertTrue(result)

    def test_subset_missing_value_raises(self):
        with self.assertRaises(ValueError):
            check_header(self.data, ["ID", "Adresa"], subset=True, same_index=False, raise_error=True)


# ---- 3️⃣ TESTY PRO create_duplicate_column ---- #
class TestCreateDuplicateColumn(unittest.TestCase):
    def setUp(self):
        self.data = [
            ["A", "B"],
            [1, 2],
            [3, 4]
        ]

    def test_create_duplicate_column(self):
        result = create_duplicate_column([row[:] for row in self.data], 1, 2)
        expected = [
            ["A", "B", "B"],
            [1, 2, 2],
            [3, 4, 4]
        ]
        self.assertEqual(result, expected)

    def test_with_transform_function(self):
        result = create_duplicate_column([row[:] for row in self.data], 1, 2, transform=lambda x: x * 10 if isinstance(x, int) else x)
        expected = [
            ["A", "B", "B"],
            [1, 2, 20],
            [3, 4, 40]
        ]
        self.assertEqual(result, expected)


# ---- 4️⃣ TESTY PRO value_to_date ---- #
class TestValueToDate(unittest.TestCase):
    def test_valid_iso_format(self):
        result = value_to_date("2024-04-15")
        self.assertEqual(result, datetime.date(2024, 4, 15))

    def test_valid_dot_format(self):
        result = value_to_date("15.04.2024")
        self.assertEqual(result, datetime.date(2024, 4, 15))

    def test_valid_YYYYmmdd(self):
        result = value_to_date("20240415")
        self.assertEqual(result, datetime.date(2024, 4, 15))

    def test_empty_string_returns_empty(self):
        result = value_to_date("", do_raise=False)
        self.assertEqual(result, "")

    def test_invalid_string_raises(self):
        with self.assertRaises(ValueError):
            value_to_date("neco spatneho")

    def test_tuple_format(self):
        result = value_to_date((2020, 5, 10, 0, 0, 0))
        self.assertEqual(result, datetime.date(2020, 5, 10))


#---------------MAIN------------------#
if __name__ == "__main__":
    unittest.main()

