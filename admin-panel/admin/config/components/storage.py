import os


# S3-compatible storage for FileField/ImageField uploads. Backed by MinIO in dev;
# swapping to AWS S3, Cloudflare R2 or Backblaze B2 is a single env change.
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_ENDPOINT_URL = os.environ.get('MINIO_ENDPOINT')
AWS_ACCESS_KEY_ID = os.environ.get('MINIO_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('MINIO_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('MINIO_BUCKET', 'posters')

# Public host used to build URLs returned to the browser. In dev this is the
# gateway path that proxies to MinIO; in prod it is the CDN or the S3 host.
# Leave unset to fall back to AWS_S3_ENDPOINT_URL (Django-internal calls only).
AWS_S3_CUSTOM_DOMAIN = os.environ.get('MINIO_PUBLIC_HOST')

# Protocol prefix django-storages prepends to the custom domain. Must include
# the trailing colon (e.g. 'http:', 'https:').
AWS_S3_URL_PROTOCOL = os.environ.get('MINIO_PUBLIC_PROTOCOL', 'https:')

# MinIO does not support virtual-hosted bucket addressing without extra DNS setup.
AWS_S3_ADDRESSING_STYLE = 'path'

AWS_S3_SIGNATURE_VERSION = 's3v4'

# Access is governed by the bucket policy provisioned in the minio stack,
# not by per-object ACLs.
AWS_DEFAULT_ACL = None

# Bucket is publicly readable, so generated URLs do not need signed query params.
AWS_QUERYSTRING_AUTH = False
