"""
"""
from __future__ import annotations
import io
import typing
from pathlib import Path

ImageSizeMap = typing.Dict[str, typing.Tuple[int, int]]


async def upload_file_to_s3(boto_session, settings, file, upload_key: str):
    # base_path = settings.base_path
    # media_location = settings.media_location
    async with boto_session.create_client(
        "s3",
        region_name=settings.do_region_name,
        endpoint_url=settings.do_endpoint_url,
        aws_access_key_id=settings.do_access_key_id,
        aws_secret_access_key=settings.do_secret_access_key,
    ) as client:
        if isinstance(file, io.BytesIO):
            body = file
        else:
            body = await file.read()
        await client.put_object(
            Bucket=settings.do_spaces_root_name,
            Key=upload_key,
            Body=body,
        )


# async def convert_and_upload_file(
#     boto_session, settings, text_source, upload_key
# ):
#     text = text_source.source
#     voice = text_source.voice or "Joanna"
#     # accent = text_source.accent

#     async with boto_session.create_client(
#         "polly",
#         region_name=settings.region_name,
#         aws_access_key_id=settings.aws_access_key_id,
#         aws_secret_access_key=settings.aws_secret_access_key,
#     ) as polly_client:
#         response = await polly_client.synthesize_speech(
#             VoiceId=voice,
#             OutputFormat="mp3",
#             Text=text,
#             # Engine="standard",
#             # LanguageCode="en-US",
#         )
#         async with response["AudioStream"] as stream:
#             async with boto_session.create_client(
#                 "s3",
#                 region_name=settings.do_region_name,
#                 endpoint_url=settings.do_endpoint_url,
#                 aws_access_key_id=settings.do_access_key_id,
#                 aws_secret_access_key=settings.do_secret_access_key,
#             ) as s3client:
#                 body = await stream.read()
#                 await s3client.put_object(
#                     Bucket=settings.do_spaces_root_name,
#                     Key=upload_key,
#                     Body=body,
#                 )


# async def drop_s3_objects(boto_session, settings, upload_key):
#     async with boto_session.create_client(
#         "s3",
#         region_name=settings.do_region_name,
#         endpoint_url=settings.do_endpoint_url,
#         aws_access_key_id=settings.do_access_key_id,
#         aws_secret_access_key=settings.do_secret_access_key,
#     ) as s3client:
#         await s3client.delete_object(
#             Bucket=settings.do_spaces_root_name, Key=upload_key
#         )


# async def download_file_from_spaces(boto_client, bucket: str, key: str):
#     response = await boto_client.get_object(Bucket=bucket, Key=key)
#     async with response["Body"] as stream:
#         return await stream.read()


# async def download_file(key: str, boto_session, settings):
#     async with boto_session.create_client(
#         "s3",
#         region_name=settings.do_region_name,
#         endpoint_url=settings.do_endpoint_url,
#         aws_access_key_id=settings.do_access_key_id,
#         aws_secret_access_key=settings.do_secret_access_key,
#     ) as client:
#         return await download_file_from_spaces(
#             client, settings.do_spaces_root_name, key
#         )


# async def upload_json(key: str, boto_session, settings, data):
#     async with boto_session.create_client(
#         "s3",
#         region_name=settings.do_region_name,
#         endpoint_url=settings.do_endpoint_url,
#         aws_access_key_id=settings.do_access_key_id,
#         aws_secret_access_key=settings.do_secret_access_key,
#     ) as client:
#         await client.put_object(
#             Bucket=settings.do_spaces_root_name,
#             Key=key,
#             Body=data,
#         )
