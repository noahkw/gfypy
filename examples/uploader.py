import json
import os
from argparse import ArgumentParser
from collections import namedtuple
from configparser import ConfigParser
from glob import glob
from os.path import splitext, basename

from gfypy import Gfypy

Uploadable = namedtuple('Uploadable', ['title', 'path'])

if __name__ == '__main__':
    parser = ArgumentParser(description='Gfycat CLI uploader')
    parser.add_argument('config', metavar='config-file')
    parser.add_argument('files', nargs='+')
    parser.add_argument('--tags', '-t', nargs='*', help='Which tags sections to use from the config.')
    parser.add_argument('--extra-tags', '-e', nargs='*', help='Which extra tags to add.',
                        dest='extra_tags')
    parser.add_argument('--dry-run', '-d', action='store_true', dest='dry_run',
                        help='Doesn\'t actually upload anything.')
    parser.add_argument('--sort', '-s', action='store_true', dest='sort',
                        help='Sorts the files to upload by the suffix after "-".')

    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config, encoding='utf-8')
    credentials = config['credentials']

    tags = args.extra_tags if args.extra_tags else []
    sections = args.tags if args.tags else []

    for tags_section in sections:
        try:
            section = config['tags'][tags_section]
            tags.extend(json.loads(section))
        except KeyError as e:
            raise KeyError(f'{tags_section} was not found in config file.')

    gfypy = Gfypy(credentials['client_id'], credentials['client_secret'], '../creds.json')
    gfypy.authenticate()

    if os.name == 'nt':
        files = []
        # windows shell globbing
        for file in args.files:
            files += glob(file)
    else:
        files = args.files

    uploadables = [Uploadable(splitext(basename(file))[0], file) for file in files]
    if args.sort:
        uploadables.sort(key=lambda x: int(x.title.split('-')[1]))

    print(f'Uploading files with the following tags: {tags}')

    for uploadable in uploadables:
        print(f'Title: {uploadable.title}; Path: {uploadable.path}')
        if not args.dry_run:
            gfypy.upload_from_file(uploadable.path, title=uploadable.title, tags=tags)
