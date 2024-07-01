{# DuckDB specific implementation to create a primary key #}
{%- macro duckdb__create_primary_key(table_relation, column_names, verify_permissions, quote_columns=false, constraint_name=none, lookup_cache=none) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{# DuckDB specific implementation to create a unique key #}
{%- macro duckdb__create_unique_key(table_relation, column_names, verify_permissions, quote_columns=false, constraint_name=none, lookup_cache=none) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{# DuckDB specific implementation to create a foreign key #}
{%- macro duckdb__create_foreign_key(pk_table_relation, pk_column_names, fk_table_relation, fk_column_names, verify_permissions, quote_columns, constraint_name, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{# DuckDB specific implementation to create a not null constraint #}
{%- macro duckdb__create_not_null(table_relation, column_names, verify_permissions, quote_columns, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{#- This macro is used in create macros to avoid duplicate PK/UK constraints
    and to skip FK where no PK/UK constraint exists on the parent table -#}
{%- macro duckdb__unique_constraint_exists(table_relation, column_names, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{#- This macro is used in create macros to avoid duplicate FK constraints -#}
{%- macro duckdb__foreign_key_exists(table_relation, column_names, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{%- macro duckdb__have_references_priv(table_relation, verify_permissions, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{%- macro duckdb__have_ownership_priv(table_relation, verify_permissions, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{%- macro duckdb__lookup_table_privileges(table_relation, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{%- macro duckdb__lookup_table_columns(table_relation, lookup_cache) -%}
    {%- do log("Not yet implemented", info=true) -%}
{%- endmacro -%}



{%- macro duckdb__get_create_index_sql(table_relation, lookup_cache) -%}
    {%- do log("Skipping creation of indexes, they are not supported by DuckDB", info=true) -%}
{%- endmacro -%}
