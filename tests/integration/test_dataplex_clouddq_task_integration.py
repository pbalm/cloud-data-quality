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

import pytest
from clouddq.integration.dq_dataplex import CloudDqDataplex
import json
import time
import datetime


task_id = f"test-task-1-{datetime.datetime.utcnow()}".replace(" ", "utc").replace(":", "-").replace(".", "-")

class TestDataplexIntegration:

    @pytest.fixture
    def test_dq_dataplex(self):

        dataplex_endpoint = "https://dataplex.googleapis.com"
        location_id = "us-central1"
        lake_name = "amandeep-dev-lake"
        project_id = "dataplex-clouddq"

        return CloudDqDataplex(dataplex_endpoint, project_id, location_id, lake_name)


    def test_create_bq_dataplex_task_check_status_code_equals_200(self, test_dq_dataplex):
        """
        This test is for dataplex clouddq task api integration for bigquery
        :return:
        """
        print(f"Dataplex batches task id is {task_id}")
        trigger_spec_type: str = "ON_DEMAND"
        task_description: str = "clouddq task"
        data_quality_spec_file_paths = [
            "gs://dataplex-clouddq-api-integration/clouddq-configs.zip"
        ]
        result_dataset_name: str = "dataplex_clouddq"
        result_table_name: str = "target_table_dataplex"

        response = test_dq_dataplex.create_clouddq_task(
                    task_id,
                    trigger_spec_type,
                    task_description,
                    data_quality_spec_file_paths,
                    result_dataset_name,
                    result_table_name)

        print(f"CloudDQ task creation response is {response.text}")
        assert response.status_code == 200


    def test_task_status_success(self, test_dq_dataplex):

        """
        This test is for getting the success status for CloudDQ Dataplex Task
        :return:
        """
        print(f"Dataplex batches task id is {task_id}")
        task_status = test_dq_dataplex.get_clouddq_task_status(task_id)
        print(f"CloudDQ task status is {task_status}")

        while (task_status != 'SUCCEEDED' and task_status != 'FAILED'):
            print(time.ctime())
            time.sleep(30)
            task_status = test_dq_dataplex.get_clouddq_task_status(task_id)
            print(task_status)

        assert task_status == 'SUCCEEDED'


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, '-vv', '-rP']))
