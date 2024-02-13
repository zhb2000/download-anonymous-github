#!/usr/bin/env python
import urllib.request
import urllib.parse
import os
import os.path
import json
import argparse
import re
from typing import Dict, Optional, Any, Iterable
import http.client


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'


def download_repo(repo_name: str, save_dir: str, skip_existing: bool):
    files_url = f'https://anonymous.4open.science/api/repo/{repo_name}/files/'
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    req = urllib.request.Request(files_url, headers=headers, method='GET')
    with urllib.request.urlopen(req) as response:
        response: http.client.HTTPResponse
        charset = response.headers.get_content_charset('utf-8')
        files_json = json.loads(response.read().decode(charset))
    file_list = list(parse_file_list(files_json, None))
    for file in file_list:
        file_url = f'https://anonymous.4open.science/api/repo/{repo_name}/file/{urllib.parse.quote(file)}'
        file_path = os.path.join(save_dir, file)
        if skip_existing and os.path.exists(file_path):
            print(f'Skipping {file} because it already exists at {file_path}')
            continue
        parent_dir = os.path.dirname(file_path)  # ensure save_path's directory exists
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        print(f'Downloading {file} to {file_path}')
        download_file(file_url, file_path)


def parse_file_list(files_json: Dict[str, Dict[str, Any]], prefix: Optional[str]) -> Iterable[str]:
    """
    The response of the files API is a JSON object with the following structure:

    ```json
    {
        "file1": {
            "size": 12345
        },
        "directory1": {
            "file2": {
                "size": 67890
            }
        }
    }
    ```

    This function uses DFS to parse the JSON object and yields the file paths.
    """
    for name, value in files_json.items():
        current_path = f'{prefix}/{name}' if prefix is not None else name
        assert isinstance(value, dict)
        if isinstance(value.get('size'), int):  # current_path is a file
            yield current_path
        else:  # current_path is a directory
            yield from parse_file_list(value, current_path)


def download_file(url: str, save_path: str):
    headers = {
        'User-Agent': USER_AGENT
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req) as response:
        response: http.client.HTTPResponse
        try:
            with open(f'{save_path}.temp', 'wb') as file:  # write to a temporary file first
                while True:
                    chunk = response.read(256 * 1024)  # 256 KB chunks
                    if len(chunk) == 0:
                        break
                    file.write(chunk)
            os.rename(f'{save_path}.temp', save_path)  # rename the temporary file to the final file
        except:
            if os.path.exists(f'{save_path}.temp'):
                os.remove(f'{save_path}.temp')  # remove the temporary file if an error occurs
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Download a repository from Anonymous GitHub (https://anonymous.4open.science/).'
    )
    parser.add_argument('url', help='the URL of the repository to download, e.g. https://anonymous.4open.science/r/repo-name/')
    parser.add_argument('save_dir', nargs='?', help='(optional) the directory to save the repository, using the repository name if not specified')
    parser.add_argument('--skip-existing', action='store_true', help='skip existing files in the save directory')
    args = parser.parse_args()
    match = re.match(r'https://anonymous\.4open\.science/r/([^/]+)/?', args.url)
    if match is None:
        print('URL is not a valid Anonymous GitHub repository.')
        return
    repo_name = match.group(1)
    download_repo(
        repo_name=repo_name,
        save_dir=args.save_dir if args.save_dir is not None else repo_name,
        skip_existing=args.skip_existing
    )


if __name__ == '__main__':
    main()
