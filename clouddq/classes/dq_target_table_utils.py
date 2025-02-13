# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from datetime import date

from google.cloud import bigquery


logger = logging.getLogger(__name__)


def load_target_table_from_bigquery(
    bigquery_client: bigquery.client.Client,
    invocation_id: str,
    partition_date: date,
    target_bigquery_summary_table: str,
    dq_summary_table_name: str,
):

    if bigquery_client.is_table_exists(target_bigquery_summary_table):

        job_config = bigquery.QueryJobConfig(
            destination=target_bigquery_summary_table,
            write_disposition="WRITE_APPEND",
            use_query_cache=False,
            use_legacy_sql=False,
        )

        query_string = f"""SELECT * FROM `{dq_summary_table_name}`
         WHERE invocation_id='{invocation_id}'
         and DATE(execution_ts)='{partition_date}'"""

        # Start the query, passing in the extra configuration.
        # Make an API request and wait for the job to complete
        bigquery_client.execute_query(
            query_string=query_string, job_config=job_config
        ).result()
        logger.info(
            f"Table {target_bigquery_summary_table} already exists "
            f"and query results are appended to the table."
        )

    else:

        query_string = f"""CREATE TABLE
        `{target_bigquery_summary_table}`
        PARTITION BY TIMESTAMP_TRUNC(execution_ts, DAY)
        CLUSTER BY table_id, column_id, rule_binding_id, rule_id
        AS
        SELECT * from `{dq_summary_table_name}`
        WHERE invocation_id='{invocation_id}'
        AND DATE(execution_ts)='{partition_date}'"""
        bigquery_client.execute_query(query_string=query_string)
        logger.info(
            f"Table created and dq summary results loaded to the "
            f"table {target_bigquery_summary_table}"
        )


class TargetTable:

    invocation_id: str = None
    bigquery_client: bigquery.client.Client = None

    def __init__(self, invocation_id: str, bigquery_client: bigquery.client.Client):
        self.invocation_id = invocation_id
        self.bigquery_client = bigquery_client

    def write_to_target_bq_table(
        self,
        partition_date: date,
        target_bigquery_summary_table: str,
        dq_summary_table_name: str,
    ):
        try:

            load_target_table_from_bigquery(
                bigquery_client=self.bigquery_client,
                invocation_id=self.invocation_id,
                partition_date=partition_date,
                target_bigquery_summary_table=target_bigquery_summary_table,
                dq_summary_table_name=dq_summary_table_name,
            )

        except Exception as error:

            raise error
