{% macro extract_org_name(url_column) %}
{% if target.type == 'postgres' %}
  -- In Postgres, use regexp_matches to extract the organization part from the URL
  substring({{ url_column }} from '^https://github\.com/([^/]+)/')
{% elif target.type == 'snowflake' %}
  -- In Snowflake, use regexp_substr to extract the organization part
  regexp_substr({{ url_column }}, '^https://github\.com/([^/]+)', 1, 1, 'e', 1)
{% elif target.type == 'duckdb' %}
  -- In DuckDB, use regexp_extract to extract the organization part
  regexp_extract({{ url_column }}, '^https://github\.com/([^/]+)/.*', 1)
{% else %}
  {{ exceptions.raise_compiler_error("Unsupported database!") }}
{% endif %}
{% endmacro %}