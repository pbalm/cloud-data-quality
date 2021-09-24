-- Copyright 2021 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
WITH
high_watermark_filter AS (
SELECT
IFNULL(MAX(execution_ts), TIMESTAMP("1970-01-01 00:00:00")) as high_watermark
FROM amandeep_dev_lake_raw.dq_summary
WHERE table_id = 'amandeep_dev_lake_raw.asset_bucket'
AND column_id = 'value'
AND rule_binding_id = 'T1_DQ_1_VALUE_NOT_NULL'
AND progress_watermark IS TRUE
),
data AS (
SELECT
*,
COUNT(1) OVER () as num_rows_validated
FROM
amandeep_dev_lake_raw.asset_bucket  d
,high_watermark_filter
WHERE
CAST(d.ts AS TIMESTAMP)
> high_watermark_filter.high_watermark
AND
True
),
validation_results AS (
SELECT
CURRENT_TIMESTAMP() AS execution_ts,
'T1_DQ_1_VALUE_NOT_NULL' AS rule_binding_id,
'NOT_NULL_SIMPLE' AS rule_id,
'amandeep_dev_lake_raw.asset_bucket' AS table_id,
'value' AS column_id,
value AS column_value,
num_rows_validated AS num_rows_validated,
CASE
WHEN TRIM(value) != '' THEN TRUE
ELSE
FALSE
END AS simple_rule_row_is_valid,
CAST(NULL AS STRING) AS complex_rule_validation_errors_count
FROM
data
),
all_validation_results AS (
SELECT
r.execution_ts AS execution_ts,
r.rule_binding_id AS rule_binding_id,
r.rule_id AS rule_id,
r.table_id AS table_id,
r.column_id AS column_id,
r.simple_rule_row_is_valid AS simple_rule_row_is_valid,
r.complex_rule_validation_errors_count AS complex_rule_validation_errors_count,
r.column_value AS column_value,
r.num_rows_validated AS rows_validated,
'{}' AS metadata_json_string,
'' AS configs_hashsum,
CONCAT(r.rule_binding_id, '_', r.rule_id, '_', to_utc_timestamp(to_date(r.execution_ts), 'US/Pacific'), '_', True) AS dq_run_id,
TRUE AS progress_watermark
FROM
validation_results r
)
SELECT
*
FROM
all_validation_results