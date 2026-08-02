import boto3
import os

from .base import Storage


class s3_storage(Storage):
    def __init__(self):
        self.s3 = boto3.client("s3")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def save(self, filename, contents):
        self.s3.put_object(Bucket = self.bucket_name, Key = filename, Body = contents)

    def get(self, filename):
        response =  self.s3.get_object(Bucket=self.bucket_name,Key=filename)
        return response['Body'].read()
         
    def delete(self, filename):
            self.s3.delete_object(Bucket=self.bucket_name,Key=filename)
        
    def rename(self, old_name, new_name):
         old_contents = self.get(old_name)

         self.save(new_name, old_contents)
         self.delete(old_name)

    def list_files(self):
         response = self.s3.list_objects_v2(Bucket=self.bucket_name)
         content = []
         if "Contents" in response:
            for obj in response["Contents"]:
                content.append(obj["Key"])

         return content

    def get_size(self, filename):
         response = self.s3.get_object(Bucket=self.bucket_name,Key=filename)
         return response["ContentLength"]

