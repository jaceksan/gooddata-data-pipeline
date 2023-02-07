select *
from {{
  metrics.calculate(
    metric('avg_days_to_solve'),
    grain='week',
    dimensions=['pull_request_draft']
  )
}}
