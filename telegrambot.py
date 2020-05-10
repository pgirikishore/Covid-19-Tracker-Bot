import requests
import datetime
import urllib.request, json
from functools import reduce
import time

class BotHandler:
    def __init__(self, token):
            self.token = token
            self.api_url = "https://api.telegram.org/bot{}/".format(token)

    #url = "https://api.telegram.org/bot<token>/"

    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update


token = '' #Token of your bot
magnito_bot = BotHandler(token) #Your bot's name



def main():
    new_offset = 0
    print('hi, now launching...')

    mess="/district - for daily district wise update\n" \
         "/state - for overall statewise wise update\n" \
         "/total - for total cases statistics in India"
    magnito_bot.send_message(magnito_bot.get_updates(new_offset)[0]['message']['chat']['id'],mess)

    while True:
        all_updates=magnito_bot.get_updates(new_offset)
        with urllib.request.urlopen("https://api.covid19india.org/districts_daily.json") as url:
            data = json.loads(url.read().decode())

        with urllib.request.urlopen("https://api.covid19india.org/data.json") as url:
            data1 = json.loads(url.read().decode())

        with urllib.request.urlopen("https://api.covid19india.org/state_district_wise.json") as url:
            data2 = json.loads(url.read().decode())

        if len(all_updates) > 0:
            for current_update in all_updates:
                print(current_update)
                first_update_id = current_update['update_id']
                if 'text' not in current_update['message']:
                    first_chat_text='New member'
                else:
                    first_chat_text = current_update['message']['text']
                first_chat_id = current_update['message']['chat']['id']
                if 'first_name' in current_update['message']:
                    first_chat_name = current_update['message']['chat']['first_name']
                elif 'new_chat_member' in current_update['message']:
                    first_chat_name = current_update['message']['new_chat_member']['username']
                elif 'from' in current_update['message']:
                    first_chat_name = current_update['message']['from']['first_name']
                else:
                    first_chat_name = "unknown"

                if first_chat_text == 'Hi':
                    magnito_bot.send_message(first_chat_id, 'How are you ' + first_chat_name)
                    new_offset = first_update_id + 1

                elif first_chat_text == "/district":
                    mess = "For State wise update enter the statename. Eg Karnataka\nFor District wise update enter the district name. Eg Ballari"
                    magnito_bot.send_message(first_chat_id, mess)
                    timeout = time.time() + 60*2
                    while True:
                        all_updates = magnito_bot.get_updates(new_offset)
                        if time.time()>timeout:
                            new_offset = first_update_id + 1
                            magnito_bot.send_message(first_chat_id,
                                                     "Timeout. You can run the /start command")
                            break

                        if len(all_updates) > 0:
                            for current_update in all_updates:
                                print(current_update)
                                first_update_id = current_update['update_id']
                                if 'text' not in current_update['message']:
                                    first_chat_text = 'New member'
                                else:
                                    first_chat_text = current_update['message']['text']
                                first_chat_id = current_update['message']['chat']['id']
                                if 'first_name' in current_update['message']:
                                    first_chat_name = current_update['message']['chat']['first_name']
                                elif 'new_chat_member' in current_update['message']:
                                    first_chat_name = current_update['message']['new_chat_member']['username']
                                elif 'from' in current_update['message']:
                                    first_chat_name = current_update['message']['from']['first_name']
                                else:
                                    first_chat_name = "unknown"


                        if first_chat_text in data["districtsDaily"]:
                            new_offset = first_update_id + 1
                            try:
                                for state in data["districtsDaily"]:
                                    if state == first_chat_text:
                                        for dist in data["districtsDaily"][state]:
                                            magnito_bot.send_message(first_chat_id,
                                                                     "{}\nactive: {}\nconfirmed: {}\ndeceased: {}\nrecovered: {}\ndate: {}\n\n".format(
                                                                         dist, data["districtsDaily"][state][dist][-1][
                                                                             "active"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "confirmed"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "deceased"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "recovered"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "date"]))
                                new_offset = first_update_id + 1

                            except:
                                magnito_bot.send_message(first_chat_id, 'Enter a valid state')
                                new_offset = first_update_id + 1

                            mess = "/district - for daily district wise update\n" \
                                   "/state - for overall statewise  wise update\n" \
                                   "/total - for total cases statistics in India"
                            magnito_bot.send_message(first_chat_id,
                                                     mess)
                            break

                        elif first_chat_text in reduce(lambda x, y: x + y,
                                                       [list(l.keys()) for l in list(data["districtsDaily"].values())]):
                            new_offset = first_update_id + 1
                            try:
                                for state in data["districtsDaily"]:
                                    for dist in data["districtsDaily"][state]:
                                        if dist in first_chat_text:
                                            magnito_bot.send_message(first_chat_id,
                                                                     "{}\nactive: {}\nconfirmed: {}\ndeceased: {}\nrecovered: {}\ndate: {}\n\n".format(
                                                                         dist,
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "active"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "confirmed"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "deceased"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "recovered"],
                                                                         data["districtsDaily"][state][dist][-1][
                                                                             "date"]))

                                new_offset = first_update_id + 1

                            except:
                                magnito_bot.send_message(first_chat_id, 'Enter a valid state')
                                new_offset = first_update_id + 1

                            mess = "/district - for daily district wise update\n" \
                                   "/state - for overall statewise  wise update\n" \
                                   "/total - for total cases statistics in India"
                            magnito_bot.send_message(first_chat_id,
                                                     mess)
                            break

                        else:
                            if first_chat_text != "/district":
                                new_offset = first_update_id + 1
                                magnito_bot.send_message(first_chat_id, "Incorrect key word")


                elif first_chat_text =="/total":
                    new_offset = first_update_id + 1
                    magnito_bot.send_message(first_chat_id,"Total\nConfirmed: {}\nActive: {}\nDeath:{}\n\n".format(data1["statewise"][0]["confirmed"],data1["statewise"][0]["active"],data1["statewise"][0]["deaths"]))
                    mess = "/district - for daily district wise update\n""/state - for overall statewise  wise update\n" \
                                   "/total - for total cases statistics in India"
                    magnito_bot.send_message(first_chat_id,
                                                     mess)

                elif first_chat_text =="/start":
                    new_offset = first_update_id + 1
                    mess = "/district - for daily district wise update\n" \
                                   "/state - for overall statewise  wise update\n" \
                                   "/total - for total cases statistics in India"
                    magnito_bot.send_message(first_chat_id,
                                                     mess)

                elif first_chat_text =="/state":
                    mess = "For State wise update enter the statename. Eg Karnataka"
                    magnito_bot.send_message(first_chat_id, mess)
                    timeout = time.time() + 60*2
                    while True:
                        all_updates = magnito_bot.get_updates(new_offset)
                        if time.time()>timeout:
                            new_offset = first_update_id + 1
                            magnito_bot.send_message(first_chat_id,"Timeout. You can run the /start command")
                            break

                        if len(all_updates) > 0:
                            for current_update in all_updates:
                                print(current_update)
                                first_update_id = current_update['update_id']
                                if 'text' not in current_update['message']:
                                    first_chat_text = 'New member'
                                else:
                                    first_chat_text = current_update['message']['text']
                                first_chat_id = current_update['message']['chat']['id']
                                if 'first_name' in current_update['message']:
                                    first_chat_name = current_update['message']['chat']['first_name']
                                elif 'new_chat_member' in current_update['message']:
                                    first_chat_name = current_update['message']['new_chat_member']['username']
                                elif 'from' in current_update['message']:
                                    first_chat_name = current_update['message']['from']['first_name']
                                else:
                                    first_chat_name = "unknown"


                        if first_chat_text in list(data2.keys()):
                            new_offset = first_update_id + 1
                            for state in data1["statewise"]:
                                if state["state"] == first_chat_text:
                                    magnito_bot.send_message(first_chat_id, "{}\nConfirmed: {}\nActive: {}\nDeath: {}\n\n".format(state["state"], state["confirmed"], state["active"], state["deaths"]))

                            new_offset = first_update_id + 1

                            mess = "/district - for daily district wise update\n" \
                                   "/state - for overall statewise  wise update\n" \
                                   "/total - for total cases statistics in India"
                            magnito_bot.send_message(first_chat_id,
                                                     mess)
                            break


                        else:
                            if first_chat_text != "/state":
                                new_offset = first_update_id + 1
                                magnito_bot.send_message(first_chat_id, "Incorrect key word")




                else:
                    new_offset = first_update_id + 1
                    magnito_bot.send_message(first_chat_id, "Incorrect key word")






if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()