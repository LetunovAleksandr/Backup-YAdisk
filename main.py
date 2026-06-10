import requests
import os
import yadisk
import json
from requests import RequestException


class Backup:
    def __init__(self, token, text):
        self.token = token.strip()
        self.text = text
        self.name_folder = 'PYQA-134'
        self.response = None

    @staticmethod
    def get_api (path):
        api = f'https://cloud-api.yandex.net/v1{path}'
        return api

    def check_token(self):
        try:
            response = requests.get(
                self.get_api('/disk'),
                headers={'Authorization': f'OAuth {self.token}'}
            )
            if response.status_code == 200:
                print('Авторизация: Успешно')
                return True

            print(
                f'Ошибка авторизации. '
                f'Код: {response.status_code}. '
                f'Ответ: {response.json()["message"]}'
            )
            return False
        except RequestException as e:
            print(f'Ошибка запроса: {e}')
            return False


    def get_picture_cat(self):
        if self.response is None:
            self.response = requests.get(
                f'https://cataas.com/cat/says/{self.text}?json=true'
                )
        print('Изображение получено')
        return self.response

    def create_json(self):
        data = self.response.headers
        json_data = {
            f'{self.text}': {
                'Content-Length': data.get('Content-Length')
            }
        }

        if os.path.exists('data/pictures_data.json'):
            with open('data/pictures_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print('Файл "pictures_data.json" открыт')
                data.update(json_data)
                with open('data/pictures_data.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                    print('Данные записаны.')
        else:
            with open('data/pictures_data.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
                print('Файл "pictures_data.json" создан. Данные записаны.')

    def save_picture(self):
        response = self.response.json()
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {
            'path': f'/{self.name_folder}',
        }

        client = yadisk.Client(token=self.token)
        if client.is_dir(f'/{self.name_folder}'):
            params['path'] = f'/{self.name_folder}/{self.text}.jpeg'
            params.update({'url': response['url']})
            requests.post(self.get_api('/disk/resources/upload'), headers=headers, params=params)
            print(f'Изображение "{self.text}" загружено в папку {self.name_folder}.')
        else:
            requests.put(self.get_api('/disk/resources'), headers=headers, params=params)
            params['path'] = f'/{self.name_folder}/{self.text}.jpeg'
            params.update({'url': response['url']})
            requests.post(self.get_api('/disk/resources/upload'), headers=headers, params=params)
            print(f'Папка "{self.name_folder}" создана. Файл "{self.text}" загружен.')

picture_cat = Backup(input('Введите токен Яндекс диска: '), input('Введите текст для изображения: '))
if picture_cat.check_token():
    picture_cat.get_picture_cat()
    picture_cat.create_json()
    picture_cat.save_picture()