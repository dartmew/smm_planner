import os
import pprint
from dotenv import load_dotenv
import sheets_api


from telebot.apihelper import ApiTelegramException
from requests.exceptions import ReadTimeout





def main():
    load_dotenv()
    spreadsheet_id = os.environ['SPREADSHEET_ID']

    client = sheets_api.get_client()
    records = sheets_api.get_all_records(client, spreadsheet_id)
    posts = sheets_api.filter_posts_by_status(records, sheets_api.STATUS_PENDING)
    #posts = sorted(posts, key=lambda x: x['age'])
    pprint.pprint(posts)


if __name__ == "__main__":
    main()



