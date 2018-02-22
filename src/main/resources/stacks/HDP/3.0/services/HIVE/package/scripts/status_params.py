#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

# Ambari Commons & Resource Management Imports
from ambari_commons import OSCheck
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import format
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.script.script import Script


# a map of the Ambari role to the component name
# for use with <stack-root>/current/<component>
SERVER_ROLE_DIRECTORY_MAP = {
  'HIVE_METASTORE' : 'hive-metastore',
  'HIVE_SERVER' : 'hive-server2',
  'HIVE_CLIENT' : 'hive-client',
  'HIVE_SERVER_INTERACTIVE' : 'hive-server2-hive2'
}


# Either HIVE_METASTORE, HIVE_SERVER, HIVE_CLIENT
role = default("/role", None)
component_directory = Script.get_component_from_role(SERVER_ROLE_DIRECTORY_MAP, "HIVE_CLIENT")
component_directory_interactive = Script.get_component_from_role(SERVER_ROLE_DIRECTORY_MAP, "HIVE_SERVER_INTERACTIVE")

config = Script.get_config()

stack_root = Script.get_stack_root()
stack_version_unformatted = config['clusterLevelParams']['stack_version']
stack_version_formatted_major = format_stack_version(stack_version_unformatted)

hive_pid_dir = config['configurations']['hive-env']['hive_pid_dir']
hive_pid = format("{hive_pid_dir}/hive-server.pid")
hive_interactive_pid = format("{hive_pid_dir}/hive-interactive.pid")
hive_metastore_pid = format("{hive_pid_dir}/hive.pid")

process_name = 'mysqld'
if OSCheck.is_suse_family() or OSCheck.is_ubuntu_family():
  daemon_name = 'mysql'
elif OSCheck.is_redhat_family() and int(OSCheck.get_os_major_version()) >= 7:
  daemon_name = 'mariadb'
else:
  daemon_name = 'mysqld'

# Security related/required params
hostname = config['agentLevelParams']['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
tmp_dir = Script.get_tmp_dir()
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hive_user = config['configurations']['hive-env']['hive_user']

# default configuration directories
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hive_etc_dir_prefix = "/etc/hive"
hive_interactive_etc_dir_prefix = "/etc/hive2"

hive_server_conf_dir = "/etc/hive/conf.server"
hive_server_interactive_conf_dir = "/etc/hive2/conf.server"

hive_home_dir = format("{stack_root}/current/{component_directory}")
hive_conf_dir = format("{stack_root}/current/{component_directory}/conf")
hive_client_conf_dir = format("{stack_root}/current/{component_directory}/conf")

if check_stack_feature(StackFeature.CONFIG_VERSIONING, stack_version_formatted_major):
  hive_server_conf_dir = format("{stack_root}/current/{component_directory}/conf/")
  hive_conf_dir = hive_server_conf_dir

# if stack version supports hive serve interactive
if check_stack_feature(StackFeature.HIVE_SERVER_INTERACTIVE, stack_version_formatted_major):
  hive_server_interactive_conf_dir = format("{stack_root}/current/{component_directory_interactive}/conf/")

hive_config_dir = hive_client_conf_dir

if 'role' in config and config['role'] in ["HIVE_SERVER", "HIVE_METASTORE", "HIVE_SERVER_INTERACTIVE"]:
  hive_config_dir = hive_server_conf_dir
  
stack_name = default("/clusterLevelParams/stack_name", None)
