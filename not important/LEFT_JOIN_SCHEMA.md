# LEFT JOIN Schema: interactions + metadata

## Goal
Build `df_interactions` by keeping all interaction rows and adding metadata when available.

## Tables Involved

### 1) `interactions_raw` (left table)
Main rating table.

Important columns:
- `user_id_mapping`
- `book_id_mapping`
- `book_id`
- `title`
- `Actual Rating`

### 2) `metadata_dedup` (right table)
Metadata table after removing duplicates on `book_id_mapping`.

Important columns used in join:
- `book_id_mapping`
- `description`
- `genre`
- `name`
- `num_pages`
- `ratings_count`

## Join Key
- Key: `book_id_mapping`

## Join Type
- `LEFT JOIN`

Meaning:
- Keep every row from `interactions_raw`
- If metadata exists for the same `book_id_mapping`, append it
- If not, metadata fields become `NaN`

## Visual Schema

```text
interactions_raw (LEFT)                       metadata_dedup (RIGHT)
+-------------------------+                  +-------------------------+
| user_id_mapping         |                  | book_id_mapping         |
| book_id_mapping   ------+----------------->| description             |
| book_id                 |      ON          | genre                   |
| title                   |  book_id_mapping | name                    |
| Actual Rating           |                  | num_pages               |
+-------------------------+                  | ratings_count           |
                                             +-------------------------+

                    LEFT JOIN result -> df_interactions
+--------------------------------------------------------------------------------+
| user_id_mapping | book_id_mapping | book_id | title | Actual Rating | ...meta |
|                                                    + description             |
|                                                    + genre                   |
|                                                    + name                    |
|                                                    + num_pages               |
|                                                    + ratings_count           |
+--------------------------------------------------------------------------------+
```

## Code Used

```python
meta_cols_for_join = [
    "book_id_mapping", "description", "genre", "name", "num_pages", "ratings_count"
]

df_interactions = interactions_raw.merge(
    metadata_dedup[meta_cols_for_join],
    on="book_id_mapping",
    how="left",
)
```

## Why deduplicate metadata first?
If `metadata_raw` has repeated `book_id_mapping`, the join can multiply rows (cardinality explosion).

So we do:

```python
metadata_dedup = metadata_raw.drop_duplicates(subset="book_id_mapping", keep="first")
```

## Sanity Checks

```python
rows_before_join = len(interactions_raw)
rows_after_join = len(df_interactions)
assert rows_after_join == rows_before_join
```

This confirms the LEFT JOIN did not create extra rows.

## Final Rename Step
After join, columns are standardized for modeling:

```python
df_interactions = df_interactions.rename(columns={
    "Actual Rating": "rating",
    "name": "author",
})
```
