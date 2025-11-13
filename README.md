# Repoztář se soubory k úkolu druhé lekce programování pro VOŠ AIT2023

---

## 🧩 funkce `list_2D_manipulator.py`

**`list_2D_manipulator.py`** – hlavní pracovní soubor

Funkce tohoto souboru jsou zaměřeny na práci s dvourozměrnými datovými strukturami,  
zejména **seznam seznamů**.

### 📘 Příklad:
```python
[
    ["a", "b", "c"],
    [1, 2, 3],
    [4, 5, 6]
]
```

Některé funkce očekávají, že vaše 2D data budou mít v prvním řádku **hlavičku s popisem sloupců**,  
jiné funkce to nevyžadují.

---

## 🎯 Úkol
Vytvořit **unit testy** pro funkce v souboru `list_2D_manipulator.py`,  
které ověří, že funkce správně zpracovávají zadaná data.

---

## 📂 Datové soubory
Soubory `data_*` můžete využít jako **mock data** pro testování.

---

## 💾 Váš výstup
Soubor pojmenovaný:
```
test_list2d_PRIJMENI.py
```

Ve kterém budou **4 třídy**,  
každá bude obsahovat testy pro vaše **4 vylosované funkce**.

---

## 🧠 Pomocné soubory
S těmito soubory **není třeba žádná manipulace**,  
`list_2D_manipulator.py` je potřebuje ke svému běhu:

- `osutils.py` – pomocný soubor primárně pro práci se soubory a složkami  
- `utils.py` – pomocný soubor pro manipulaci s daty

---

## 🎲 Rozlosování

| Student | Funkce |
|----------|--------|
| **Augusta Daniel** | `sort_by_col`, `col_names_from_firts_row`, `deflatten_list_2D`, `replace_values_in_col_by_dict` |
| **Baumruk Filip** | `indexes_of_values`, `inhomogeneities_finder`, `dict_with_lists__sub_lists_to_list_2D`, `histogram_substring_evidences_in_cols` |
| **Chval Karel** | `dict_with_dicts_to_list_2D`, `flatten_list_2D`, `convert_values_on_rows`, `convert_tuple_of_tuples_to_list_of_lists` |
| **Klein Jan** | `value_to_float`, `index_of_value`, `convert_values_in_column`, `filter_rows_by_col_value` |
| **Mirvald Tomáš** | `one_col_to_list`, `check_header`, `create_duplicate_column`, `value_to_date` |
| **Opatrný Lukáš** | `value_length_histogram`, `homogenity_check`, `combine_lists_special`, `find_duplicate_values_from_col` |
| **Piškule Ondřej** | `longest_row_in_list_2D`, `swap_columns_feeder`, `insert_column`, `delete_columns` |
| **Pur Lukáš** | `three_columns_to_dict_of_dicts`, `two_columns_to_dict_ordered`, `enumerate_iter`, `dict_to_list_of_dicts` |
| **Ryba Matěj** | `unique_values_from_col`, `rows_by_unique_values_from_col`, `dict_to_two_column_list_of_list`, `one_row_from_list_to_dict` |
| **Rýdlo Jaromír** | `take_out_columns`, `swap_columns`, `intersection_of_two_cols`, `rearrange_cols` |
| **Rýdlo Petr** | `histogram_unicates_in_col`, `dict_with_lists_to_list_2D_only_values`, `histogram_rows_length`, `value_to_unicode` |
| **Sazima Jakub** | `two_columns_to_dict`, `replace_values_in_cols`, `indexes_of_values_as_dict`, `col_name_to_index` |
| **Šmíd Tomáš** | `replace_values_in_col_by_dict_values_in_other_col`, `value_to_int`, `dict_with_lists_to_list_2D`, `two_columns_to_dict_of_list` |

---
