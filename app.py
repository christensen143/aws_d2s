import boto3
import datetime
import getopt
import os
import sys
import time
from timeit import default_timer as timer


start = timer()

def command_line_args(argv):
  global old_instance_id
  global instance_region_name
  global instance_url
  global hosted_zone_name
  try:
    opts, args = getopt.getopt(argv,"hi:r:u:z:",["instance-id=", "region-name=", "instance-url=", "hosted-zone-name="])
  except getopt.GetoptError:
    print('useage: python3 app.py -i <Instance ID> -r <Region Name> -u <Instance Route53 URL (Optional)> -z <Route53 hosted zone name>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('useage: python3 app.py -i <Instance ID> -r <Region Name> -u <Instance Route53 URL (Optional)> -z <Route53 hosted zone name (Optional)>')
      sys.exit()
    elif opt in ("-i", "--instance-id"):
      old_instance_id = arg
    elif opt in ("-r", "--region-name"):
      instance_region_name = arg
    elif opt in ("-u", "--instance-url"):
      instance_url = arg
    elif opt in ("-z", "--hosted_zone_name"):
      hosted_zone_name = arg

command_line_args(sys.argv[1:])

# Setup boto3 and instance variables
ec2 = boto3.resource('ec2', region_name=instance_region_name)
client = boto3.client('ec2')
instance = ec2.Instance(old_instance_id)
route53 = boto3.client('route53')

# Variables
# Variables for date and time
currentDT = datetime.datetime.now()
currentdate = currentDT.strftime("%Y%m%d-%H%M%S")

# Get the instance name for imagename
for tags in instance.tags:
  if tags["Key"] == 'Name':
    instancename = tags["Value"]

imagename = '{0}_{1}'.format(instancename, currentdate)

# Get subnet id of original instance
subnetid = instance.subnet_id

# Get security groups for original instance
secgroups = [d['GroupId'] for d in instance.security_groups if 'GroupId' in d]

# Get private ip address of original instance
ipaddress = instance.private_ip_address

# Get instance type for original instance
instancetype = instance.instance_type

# Get the key name for the instance
keyname = instance.key_name

# Get tags for original instance
tags = instance.tags
tag_specification = [{'ResourceType': 'instance', 'Tags': tags},]

def get_hosted_zone_id(dnsname):
  global host_id
  response = route53.list_hosted_zones_by_name(DNSName=dnsname, MaxItems='1')
  for zone in response["HostedZones"]:
    host_id = zone['Id']
    host_id = host_id.replace("/hostedzone/", "")

def change_dns_record(hostedzoneid, source, target, record_type, ttl):
  try:
    response = route53.change_resource_record_sets(
      HostedZoneId=hostedzoneid,
      ChangeBatch= {
        'Comment': 'add %s -> %s' % (source, target),
        'Changes': [
          {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
              'Name': source,
              'Type': record_type,
              'TTL': ttl,
              'ResourceRecords': [{'Value': target}]
            }
          }
        ]
      }
    )
  except Exception as e:
    print(e)

# Shutdown original instance
print("\nStopping instance " + instance.id + "...\n")
instance.stop()
instance.wait_until_stopped()
print("Instance " + instance.id + " has been stopped\n")

# Create image of original instance
# Output is variable for image
print("Creating image " + imagename + "...\n")
images = instance.create_image (
  # InstanceId=instanceid,
  Name=imagename
)

imageid = images.id
image = ec2.Image(str(images.id))
image.wait_until_exists(Filters=[{'Name': 'state', 'Values': ['available']}])
print("Image " + imagename + " has been created.\n")

# Create new instance with image from original instance
print("Creating new instance based on image " + imagename + "...\n")
instances = ec2.create_instances (
  ImageId=imageid,
  MinCount=1,
  MaxCount=1,
  InstanceType=instancetype,
  KeyName=keyname,
  SecurityGroupIds=secgroups,
  SubnetId=subnetid,
  # PrivateIpAddress=ipaddress,
  TagSpecifications=tag_specification
)
instances[0].wait_until_running()
for instance in instances:
  new_ipaddress = instance.private_ip_address
  print("Instance " + instance.id + " has been created.\n")

if instance_url and hosted_zone_name:
  print("Updating Route53 DNS...\n")
  get_hosted_zone_id(hosted_zone_name)
  change_dns_record(host_id, instance_url, new_ipaddress, 'A', 60)
  print("Route53 DNS has been updated.\n")
else:
  print("Route53 not updated.\n")

elapsed_time = timer() - start
print("This script took " + str(elapsed_time) + " to complete.")
