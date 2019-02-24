import boto3
session=boto3.Session(profile_name='ravi')
s3=session.resource('s3')
for i in s3.buckets.all():
    print(i)
