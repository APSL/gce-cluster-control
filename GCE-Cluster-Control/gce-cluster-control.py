#!/usr/bin/env python

## Usage:
# gce-cluster-control.py [-h] -g GROUP [-s STATDIR]
#
# GCE Disk Snapshot Maker
# 
# optional arguments:
#   -h, --help                         show this help message and exit
#   -g, --group GROUP                  The GCE instance group name to manage
#   -z ZONE, --zone ZONE               The GCE zone of the disk to be imaged
#   -n, --number NUMBER                The number of instance we want in the instance-group
#   -s STATDIR, --statdir STATDIR      Directory where to write the status file
#

import os
import sh
import sys
import time
import syslog
import argparse
import subprocess

# GLOBAL VARIABLES

# Variables related to the script itself
script = os.path.realpath(__file__)
script_name = os.path.splitext(os.path.basename(script))[0]
script_ext = os.path.splitext(os.path.basename(script))[1]
script_path = os.path.dirname(script)

# Generic variables
gce_instance_group=''
gce_zone=''
status_dir='/tmp/gce-cluster-control'
status_filename=''
last_error='Successful execution.'

# SHELL commands
gcloud = sh.Command('gcloud')

# CONSTANTS
RESULT_OK = 0
RESULT_ERR = 1

def set_last_error(error_msg):
  global last_error
  last_error = error_msg

def write_log(msg,msg_type=syslog.LOG_INFO):
  try:
    print msg
    syslog.syslog(msg_type, msg)
  except Exception as ex:
    print 'Logging exception: %s' % ex

def change_instances_asigned(gce_zone, gce_group, number):
  write_log('Changing size for group "'+gce_group+'" to '+number+' instances.')
  try:
    result = gcloud('compute', 'instance-groups', 'managed', 'resize', gce_group, '--size', number, '--zone', gce_zone)
    #write_log('Size changed for: ' + gce_group)
  except Exception as ex:
    set_last_error('GCloud execution error: %s' % ex.stderr)
    write_log(last_error,syslog.LOG_ERR)
    return RESULT_ERR
  return RESULT_OK

def get_gce_instance_groups():
  instance_groups_list = None
  result = None
  try:
    result = gcloud('compute', 'instance-groups', 'list', '--uri')
  except Exception as ex:
    set_last_error('GCloud execution error: %s' % ex.stderr)
    write_log(last_error,syslog.LOG_ERR)
  if result is not None:
    instance_groups_list = result.stdout.strip().split('\n')
    for iIndex in range(len(instance_groups_list)):
      instance_groups_list[iIndex] = os.path.splitext(os.path.basename(instance_groups_list[iIndex]))[0]
  return instance_groups_list

def get_gce_zones():
  zone_list = None
  result = None
  try:
    result = gcloud('compute', 'zones', 'list', '--uri')
  except Exception as ex:
    set_last_error('GCloud execution error: %s' % ex.stderr)
    write_log(last_error,syslog.LOG_ERR)
  if result is not None:
    zone_list = result.stdout.strip().split('\n')
    for iIndex in range(len(zone_list)):
      zone_list[iIndex] = os.path.splitext(os.path.basename(zone_list[iIndex]))[0]
  return zone_list

def save_status_file(filename, status):
  try:
    status_lines = []
    status_lines.append('TIMESTAMP=' + str(long(time.time())))
    status_lines.append('STATUS=' + str(status))
    status_lines.append('LAST_ERROR=' + last_error.replace('\n','\t'))
    with open(filename, 'w') as status_file:
      for aLine in status_lines:
        status_file.write(aLine + '\n')
  except Exception as ex:
    write_log('Exception while saving the status file: %s' % ex, syslog.LOG_ERR)

# Command line arguments
parser = argparse.ArgumentParser(description='GCE Cluster Control')
parser.add_argument('-z', '--zone', help='The GCE zone', required=True)
parser.add_argument('-g', '--group', help='The GCE instance group name to manage', required=True)
parser.add_argument('-n', '--number', help='The number of instances we want to be assigned to the cluster', required=True)
parser.add_argument('-s', '--statdir', help='Directory where to write the status file', required=False, default=status_dir)

args = vars(parser.parse_args())

gce_zone = args['zone']
gce_group = args['group']
number = args['number']
status_dir = args['statdir']
status_filename = status_dir+'/'+gce_group+'.status'

# Check status directory
try:
  if not(os.path.isdir(status_dir)):
    os.makedirs(status_dir)
except Exception as ex:
  set_last_error('Error accessing the status directory: %s' % ex)
  write_log(last_error, syslog.LOG_ERR)
  sys.exit(RESULT_ERR)

available_groups = get_gce_instance_groups()
if gce_group not in available_groups:
  set_last_error('The group "'+gce_group+'" does not exist.')
  write_log(last_error,syslog.LOG_ERR)
  save_status_file(status_filename,RESULT_ERR)
  sys.exit(RESULT_ERR)

available_zones = get_gce_zones()
if gce_zone not in available_zones:
  set_last_error('The zone "'+gce_zone+'" does not exist.')
  write_log(last_error,syslog.LOG_ERR)
  save_status_file(status_filename,RESULT_ERR)
  sys.exit(RESULT_ERR)
  
result = change_instances_asigned(gce_zone, gce_group, number)

save_status_file(status_filename,result)
sys.exit(result)

