create database cicd_dev;

\c cicd_dev

create schema cicd_input_stage;
create schema cicd_output_stage;

create user cicd password 'cicd123';
grant all on schema cicd_input_stage to cicd;
grant all on schema cicd_output_stage to cicd;
grant all on all tables in schema cicd_input_stage to cicd;
grant all on all tables in schema cicd_output_stage to cicd;
alter default privileges in schema cicd_input_stage grant all on tables to cicd;

grant create on database cicd_dev to cicd;
