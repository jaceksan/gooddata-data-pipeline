WITH repositories_data AS (
    SELECT
        -- Extract the organization from the repo_url
        {{ extract_org_name("repo_url") }} AS org_name
    FROM {{ ref('repos') }}
)

-- Select the distinct organizations
-- TODO: Either propagate this to other tables and add repo_id to this
SELECT DISTINCT
    org_name
FROM repositories_data