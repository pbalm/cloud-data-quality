#!/bin/bash
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

# set -o errexit
# set -o nounset
# set -o pipefail

set -x

# get diagnostic info
which python3
python3 --version
python3 -m pip --version

# create temporary virtualenv
python3 -m venv /tmp/clouddq_test_env
source /tmp/clouddq_test_env/bin/activate

# install clouddq wheel into temporary env
python3 -m pip install .

# set project id
export PROJECT_ID=$(gcloud config get-value project)

# smoke test clouddq commands
python3 clouddq --help
python3 clouddq ALL configs --dbt_profiles_dir=tests/resources/test_dbt_profiles_dir --debug --dry_run --skip_sql_validation
python3 clouddq ALL configs --dbt_profiles_dir=tests/resources/test_dbt_profiles_dir --debug --dbt_path=dbt --dry_run --skip_sql_validation

# test clouddq in isolated directory with minimal file dependencies
TEST_DIR=/tmp/clouddq-test-pip
rm -rf "$TEST_DIR"
mkdir "$TEST_DIR"
cp -r configs "$TEST_DIR"
cp tests/resources/test_dbt_profiles_dir/profiles.yml "$TEST_DIR"
cd "$TEST_DIR"
python3 -m clouddq ALL configs --dbt_profiles_dir="$TEST_DIR" --debug --dry_run --skip_sql_validation