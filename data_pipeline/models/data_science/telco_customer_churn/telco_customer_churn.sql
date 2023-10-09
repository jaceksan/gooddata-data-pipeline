with final as (
  select
    "{{ get_db_entity_name('customerID') }}" as customerid,
    "{{ get_db_entity_name('gender') }}" as gender,
    "{{ get_db_entity_name('SeniorCitizen') }}" as seniorcitizen,
    "{{ get_db_entity_name('Partner') }}" as partner,
    "{{ get_db_entity_name('Dependents') }}" as dependents,
    "{{ get_db_entity_name('tenure') }}" as tenure,
    "{{ get_db_entity_name('PhoneService') }}" as phoneservice,
    "{{ get_db_entity_name('MultipleLines') }}" as multiplelines,
    "{{ get_db_entity_name('InternetService') }}" as internetservice,
    "{{ get_db_entity_name('OnlineSecurity') }}" as onlinesecurity,
    "{{ get_db_entity_name('OnlineBackup') }}" as onlinebackup,
    "{{ get_db_entity_name('DeviceProtection') }}" as deviceprotection,
    "{{ get_db_entity_name('TechSupport') }}" as techsupport,
    "{{ get_db_entity_name('StreamingTV') }}" as streamingtv,
    "{{ get_db_entity_name('StreamingMovies') }}" as streamingmovies,
    "{{ get_db_entity_name('Contract') }}" as contract,
    "{{ get_db_entity_name('PaperlessBilling') }}" as paperlessbilling,
    "{{ get_db_entity_name('PaymentMethod') }}" as paymentmethod,
    "{{ get_db_entity_name('TotalCharges') }}" as totalcharges,
    "{{ get_db_entity_name('Churn') }}" as churn,
    CAST("{{ get_db_entity_name('MonthlyCharges') }}" AS DECIMAL(15, 2)) as monthlycharges
  from {{ var("input_schema_data_science") }}.telco_customer_churn
)

select * from final
