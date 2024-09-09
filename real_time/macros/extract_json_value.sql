--
{% macro extract_json_value(json_column_name, json_path, target_column_name, data_type) -%}

    {%- set db_entity_name = get_db_entity_name(json_column_name) -%}

    {%- if target.type == "snowflake" -%}

        CAST(json_extract_path_text(to_json(parse_json("{{ db_entity_name }}")), '{{ json_path }}') AS {{ data_type }}) AS {{ target_column_name }}

    {%- elif target.type == "vertica" -%}

        CAST((public.MapJSONExtractor("{{ db_entity_name }}"))['{{ json_path }}'] AS {{ data_type }}) AS {{ target_column_name }}

    {%- elif target.type in ("postgres") -%}

        CAST(json_extract_path_text("{{ db_entity_name }}"::JSON, '{{ json_path }}') AS {{ data_type }}) AS {{ target_column_name }}

    {%- elif target.type in ("duckdb") -%}

        CAST(json_extract_path_text("{{ db_entity_name }}"::JSON, '$.{{ json_path }}') AS {{ data_type }}) AS {{ target_column_name }}

    {%- else -%}

        {{ exceptions.raise_compiler_error("Invalid `target.type`. Got: " ~ target.type) }}

    {%- endif -%}

{%- endmacro %}