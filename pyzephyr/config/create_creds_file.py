import sys
import json


def save_credentials_as_json_file(file_name='client_credentials.json'):
    with open(file_name, 'w') as f:
        json.dump(
            {
                "credentials":
                    {
                            "kyle_1":
                                {
                                    "client_id": "6G6ZFBN3A2U3RB2S69HMOY0XOLN0JY",
                                    "client_secret": "OBZISGIQDCP6C06G83NRPZHLOV2UZY9CEALMJA1F"
                                },
                            "kellykx_1":
                                {
                                    "client_id": "25FGGL7RKTI6IK8IQD5LFK5LT8U8YM",
                                    "client_secret": "W1SWOB8TNJLJTPT0XDUHUKDMUWDAOE83TDP6IQDV"

                                },
                            "kellykx_2":
                                {
                                    "client_id": "MCMO4NVVES2IY4ELLUS38707DO4LYI",
                                    "client_secret": "C9USYMWRPGSSJK15C6G0XFCDFZ0R935859K05UV4"
                                },
                            "kellykx_3":
                                {
                                    "client_id": "CEAVJC04VI42NS3CZ3KSMR2LQ2YDGM",
                                    "client_secret": "9FB8ZAZCT01KZDEY49ZM64RKC2H98ZZ9J6R4CM4X"
                                },
                    }
            },
            f, indent=4
        )


if __name__ == "__main__":
    save_credentials_as_json_file(file_name=sys.argv[1])


