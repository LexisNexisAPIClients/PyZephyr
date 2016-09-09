import sys
import json


def save_configuration_as_json_file(file_name='vsts_config.json'):
    with open(file_name, 'w') as f:
        json.dump(
            {
                "scheme": "https",
                "netloc": "tfs-glo-lexisadvance.analytics.visualstudio.com",
                "odata":  "/DefaultCollection/NL/_odata",
            },
            f, indent=4
        )

if __name__ == "__main__":
    save_configuration_as_json_file()
