# TODO: could this be valuable?

start = time()
logging.info("Uploading files to Minio...")
upload_files_to_minio()
logging.info(f"Upload complete. Time taken: {time() - start:.2f} seconds")

def upload_files_to_minio():
    # Create the bucket if it doesn't already exist
    logging.info(f"Creating Minio bucket {BUCKET_NAME}")
    try:
        S3_CONNECTION.create_bucket(Bucket=BUCKET_NAME)
    except Exception as e:
        if "BucketAlreadyOwnedByYou" in str(e):
            logging.info(f"Bucket {BUCKET_NAME} already exists")
        else:
            raise Exception(f"Error creating bucket: {e}")
    bucket = S3_CONNECTION.Bucket(BUCKET_NAME)

    # Upload files
    for file_name in FILES:
        file_path = FILE_PATH / file_name
        logging.info(f"Uploading {file_path.name} to Minio bucket {BUCKET_NAME}")
        file_name = file_path.name
        bucket.upload_file(file_path, file_name)
        print(f"Uploaded {file_name} to Minio bucket {BUCKET_NAME}")
