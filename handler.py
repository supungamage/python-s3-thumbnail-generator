import boto3
import io
from PIL import Image, ImageOps
import os

s3 = boto3.client('s3')
size = int(os.environ['THUMBNAIL_SIZE'])

def s3_thumbnail_generator(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    image = get_s3_image(bucket, key)
    thumbnail = create_thumbnail(image)
    thumbnail_key = new_filename(key)
    url = upload_s3(bucket, thumbnail_key, thumbnail)
    return url

def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    imageContent = response['Body'].read()

    file = io.io.BytesIO(imageContent)
    img = Image.open(file)
    return img

def create_thumbnail(image):
    return ImageOps.fit(image, (size, size), Image.ANTIALIAS)

def new_filename(key):
    filename = os.path.splitext(key)[0]
    return filename + "_thumbnail.png"

def upload_to_s3(bucket, key, image):
    out_thumbnail = io.StringIO()
    image.save(out_thumbnail, 'PNG')
    out_thumbnail.seek(0)

    response = s3.put_object(
        ACL='public-read',
        Body=out_thumbnail,
        Bucket=bucket,
        ContentType='image/png',
        Key=key
    )
    print(response)
    print(s3.meta.endpoint_url)
    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)
    return url