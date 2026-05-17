import os
import sys
import datetime
import requests

def main():
    token = os.environ.get('RELEASE_TOKEN')
    if not token:
        print('ERROR: RELEASE_TOKEN not set')
        sys.exit(1)

    tag = 'v' + datetime.datetime.now().strftime('%Y.%m.%d-%H%M%S')
    print(f'Tag: {tag}')

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    print('Creating release...')
    data = {
        'tag_name': tag,
        'name': f'e-battle {tag}',
        'body': 'Automatic release',
        'draft': False,
        'prerelease': False
    }
    response = requests.post(
        'https://api.github.com/repos/le700/e-battle/releases',
        headers=headers,
        json=data
    )
    print(f'Status code: {response.status_code}')
    print(f'Response: {response.text}')

    if response.status_code != 201:
        print('Failed to create release')
        sys.exit(1)

    release_data = response.json()
    upload_url = release_data['upload_url'].replace('{?name,label}', '')
    print(f'Upload URL: {upload_url}')

    dist_dir = 'dist'
    if not os.path.exists(dist_dir):
        print(f'Error: {dist_dir} directory not found')
        sys.exit(1)

    for filename in os.listdir(dist_dir):
        filepath = os.path.join(dist_dir, filename)
        if os.path.isfile(filepath):
            print(f'Uploading {filename}...')
            with open(filepath, 'rb') as f:
                upload_response = requests.post(
                    f'{upload_url}?name={filename}',
                    headers=headers,
                    data=f
                )
            print(f'Upload status: {upload_response.status_code}')
            if upload_response.status_code == 201:
                print(f'Successfully uploaded {filename}')
            else:
                print(f'Failed to upload {filename}: {upload_response.text}')

    print('Done!')

if __name__ == '__main__':
    main()
