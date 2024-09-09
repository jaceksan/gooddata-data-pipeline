--
{% macro get_db_entity_name(entity_name, node) -%}

    {%- if target.type == "snowflake" -%}

        {{ entity_name.upper() }}

    {%- else -%}

        {{ entity_name }}

    {%- endif -%}

{%- endmacro %}