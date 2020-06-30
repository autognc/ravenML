import os
import shutil
import boto3
from pathlib import Path
from queue import Queue
from threading import Thread

def copy_data_locally(source_dir, dest_dir=None,
                      condition_func=lambda filename: True,
                      num_threads=20):
    """Copies data from a local source into Jigsaw given some condition
    
    Args:
        source_dir (str or pathlib `Path`): the source directory from which
            data should be copied
        condition_func (function, optional): a function that uses the filename
            to determine whether data should be copied. This allows for only
            copying portions of the source data if desired. Defaults to True
            for all filenames.
        num_threads (int, optional): Defaults to 20. Number of threads
            performing concurrent copies.
    """
    # convert the source directory from a string to a pathlib Path if necessary
    if isinstance(source_dir, str):
        source_dir = Path(source_dir)

    if dest_dir is None:
        cwd = Path.cwd()
        data_dir = cwd / 'data'
        os.makedirs(data_dir, exist_ok=True)
    else:
        data_dir = dest_dir

    def copy_object(queue):
        while True:
            filepath = queue.get()
            if filepath is None:
                break
            shutil.copy(filepath, data_dir.absolute())
            queue.task_done()

    # create a queue for objects that need to be copied
    # and spawn threads to copy them concurrently
    copy_queue = Queue(maxsize=0)
    workers = []
    for worker in range(num_threads):
        worker = Thread(target=copy_object, args=(copy_queue, ))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)

    for file in source_dir.iterdir():
        if os.path.isfile(file) and condition_func(file.name) and not (data_dir / file.name).exists():
            copy_queue.put(file.absolute())

    copy_queue.join()
    for _ in range(num_threads):
        copy_queue.put(None)
    for worker in workers:
        worker.join()


def download_data_from_s3(bucket_name,
                          filter_vals=[''],
                          condition_func=lambda filename: True,
                          num_threads=20):
    """Downloads data from S3 into Jigsaw given some condition
    
    Args:
        bucket_name (str): the name of the S3 bucket to download from
        condition_func ([type], optional): a function that uses the filename
            to determine whether data should be downloaded. This allows for
            only downloading portions of the source data if desired. Defaults
            to True for all filenames.
        num_threads (int, optional): Defaults to 20. Number of threads
            performing concurrent downloads.
    """

    # simple method for threads to pull from a queue and download JSON files
    def download_object(queue):
        while True:
            obj = queue.get()
            if obj is None:
                break
            obj.Object().download_file(obj.key.split("/")[-1])
            # TODO: test for files with prefixes here
            queue.task_done()

    cwd = Path.cwd()
    data_dir = cwd / 'data'
    # try:
    os.makedirs(data_dir, exist_ok=True)
    # except FileExistsError:
        # pass
    os.chdir(data_dir)

    # create a queue for objects that need to be copied
    # and spawn threads to copy them concurrently
    download_queue = Queue(maxsize=0)
    workers = []
    for worker in range(num_threads):
        worker = Thread(target=download_object, args=(download_queue, ))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)

    # loop through the files in the bucket and add them to the queue if they
    # satisfy the condition_func
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    for prefix in filter_vals:
        for obj in bucket.objects.filter(Prefix=prefix):
            filename = obj.key.split("/")[-1]
            if condition_func(filename) and not (data_dir / filename).exists():
                download_queue.put(obj)

    # wait for the queue to be empty, then join all threads
    download_queue.join()
    for _ in range(num_threads):
        download_queue.put(None)
    for worker in workers:
        worker.join()

    os.chdir(cwd)

def upload_dataset(bucket_name, directory, num_threads=20):
    """Recursively uploads a directory to S3
    
    Args:
        bucket_name (str): the name of the S3 bucket to upload to
        directory (str): the absolute path of a directory whose contents
            should be uploaded to S3; the directory name is used as the S3
            prefix for all uploaded files
        num_threads (int, optional): Defaults to 20.
    """
    s3 = boto3.resource('s3')

    def upload_file(queue):
        while True:
            obj = queue.get()
            if obj is None:
                break
            abspath, s3_path = obj
            s3.meta.client.upload_file(abspath, bucket_name, s3_path)
            queue.task_done()

    # create a queue for objects that need to be uploaded
    # and spawn threads to upload them concurrently
    upload_queue = Queue(maxsize=0)
    workers = []
    for worker in range(num_threads):
        worker = Thread(target=upload_file, args=(upload_queue, ))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)

    for root, _, files in os.walk(directory):
        for file in files:
            abspath = os.path.join(root, file)
            relpath = os.path.relpath(abspath, directory)
            s3_path = os.path.basename(directory) + "/" + relpath
            upload_queue.put((abspath, s3_path))

    # wait for the queue to be empty, then join all threads
    upload_queue.join()
    for _ in range(num_threads):
        upload_queue.put(None)
    for worker in workers:
        worker.join()
