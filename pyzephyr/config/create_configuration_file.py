import sys
import json


def save_configuration_as_json_file(file_name='lexis_config.json'):
    with open(file_name, 'w') as f:
        json.dump(
            {
                "redirect_url": "http://127.0.0.1:4999/callback",
                "auth_page_path": "/oauth/v2/authorize",
                "token_path": "/oauth/v2/token",
                "location":
                    {
                            "auth":
                                {
                                    "scheme": "https",
                                    "netloc": "auth-api.lexisnexis.com",
                                },
                            "services-api":
                                {
                                    "scheme": "https",
                                    "netloc": "services-api.lexisnexis.com",
                                },
                            "dev_auth":
                                {
                                    "scheme": "http",
                                    "netloc": "dvc7720.lexisnexis.com:39143",
                                },
                            "dev_services-api":
                                {
                                    "scheme": "http",
                                    "netloc": "",
                                },
                            "cert_auth":
                                {
                                    "scheme": "http",
                                    "netloc": "",
                                },
                            "cert_services-api":
                                {
                                    "scheme": "http",
                                    "netloc": "",
                                },
                    }
            },
            f, indent=4
        )


if __name__ == "__main__":
    save_configuration_as_json_file(file_name=sys.argv[1])
