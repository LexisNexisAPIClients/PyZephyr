import sys
import json


def save_credentials_as_json_file(file_name='client_credentials.json'):
    with open(file_name, 'w') as f:
        json.dump(
            {
                "zephyr2":
                    {
                        "client_id": "kellykxPAT",
                        "client_secret": "v72ccpu5molsa6lxb2i4cnwxwxuwqrvd32av3xos44pgqxuqoiqa"
                    },
            },
            f, indent=4
        )


if __name__ == "__main__":
    save_credentials_as_json_file()
