import boto3
import datetime
import os
import sys
import time
from timeit import default_timer as timer


start = timer()
# Setup boto3 and instance variables
ec2 = boto3.resource('ec2', region_name=os.environ['AWS_DEFAULT_REGION'])
client = boto3.client('ec2')
instance = ec2.Instance(''.join(sys.argv[1:]))

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

# Shutdown original instance
print("Stopping instance " + instance.id + "...")
instance.stop()
instance.wait_until_stopped()
print("Instance " + instance.id + " has been stopped")

# Create image of original instance
# Output is variable for image
print("Creating image " + imagename + "...")
images = instance.create_image (
  # InstanceId=instanceid,
  Name=imagename
)

imageid = images.id
image = ec2.Image(str(images.id))
image.wait_until_exists(Filters=[{'Name': 'state', 'Values': ['available']}])
print("Image " + imagename + " has been created.")

# Terminate original instance
print("Terminating instance " + instance.id + "..." )
instance.terminate()
instance.wait_until_terminated()
print("Instance " + instance.id + " has been terminated.")

# Create new instance with image from original instance
print("Creating new instance based on image " + imagename + "...")
instances = ec2.create_instances (
  ImageId=imageid,
  MinCount=1,
  MaxCount=1,
  InstanceType=instancetype,
  KeyName=keyname,
  SecurityGroupIds=secgroups,
  SubnetId=subnetid,
  PrivateIpAddress=ipaddress,
  TagSpecifications=tag_specification
)
instances[0].wait_until_running()
for instance in instances:
  print("Instance " + instance.id + " has been created.")

elapsed_time = timer() - start
print("This script took " + str(elapsed_time) + " to complete.")