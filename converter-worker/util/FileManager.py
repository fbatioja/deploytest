import os
import pathlib
import shutil
from abc import abstractmethod, ABC

import boto3
import magic

BUCKET = os.environ.get("BUCKET", '')


class FileManager:
    path = 'Files'

    @staticmethod
    def get_instance():
        if BUCKET == '':
            return LocalFileManager()
        else:
            return AwsS3()

    @abstractmethod
    def save_file(self, file_upload, filename, userId):
        pass

    @abstractmethod
    def delete_file(self, filename, userId):
        pass

    @abstractmethod
    def get_file(self, filename, userId):
        pass

    def send_file(self, destination_path, target_name, userId):
        pass

    def clean_local_files(self, filename, userId):
        pass

    def _get_filename(self, filename, userId):
        return os.path.join(self.path, str(userId), filename)


class LocalFileManager(FileManager):
    path = os.path.join(os.path.dirname(__file__), f"../Files")

    def get_file(self, filename, userId):
        filepath = self._get_filename(filename, userId)
        return filepath

    def save_file(self, file, filename, userId):
        if not os.path.exists(f"{self.path}/{userId}"):
            os.mkdir(os.path.join(self.path, userId))

        filepath = self._get_filename(filename, userId)
        file_location = os.path.join(self.path, filepath)
        with open(file_location, "wb+") as file_save:
            file_save.write(file.read())

    def delete_file(self, filename, userId):
        filepath = self._get_filename(filename, userId)
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            raise FileNotFoundError


class AwsS3(FileManager):
    def __init__(self) -> None:
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(BUCKET)

    def save_file(self, file_upload, filename, userId):
        key = self._get_filename(filename, userId)
        self.bucket.put_object(
            Key=key,
            Body=file_upload,
        )

    def delete_file(self, filename, userId):
        filename = self._get_filename(filename, userId)
        self.bucket.delete_key(filename)

    def get_file(self, filename, userId):
        filepath = self._get_filename(filename, userId)
        if not os.path.exists(f"./{self.path}/{userId}"):
            os.mkdir(f"./{self.path}/{userId}/")

        self.bucket.download_file(filepath, filepath)
        return filepath

    def send_file(self, filepath, filename, userId):
        self.save_file(open(filepath), filename, userId)

    def clean_local_files(self, filename, userId):
        filepath = self._get_filename(filename, userId)
        shutil.rmtree(os.path.dirname(filepath))
