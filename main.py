import requests
import os
import yadisk
import json

class Backup:
    def __init__(self, token, text):
        self.token = token
        self.text = text
        self.name_folder = 'PYQA-134'
        self.response = None
    @staticmethod
    def get_api (path):
        api = f'https://cloud-api.yandex.net/v1{path}'
        return api

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
                'Content-Length': dict(data)['Content-Length']
            }
        }

        if os.path.exists('data/pictures_data.json'):
            with open('data/pictures_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print('Файл открыт')
                data.update(json_data)
                with open('data/pictures_data.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                    print('Данные записаны')
        else:
            with open('data/pictures_data.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
                print('Файл создан, данные записаны')

    def save_picture(self):
        response = self.response.json()
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {
            'path': f'/{self.name_folder}',
        }
        client = yadisk.Client(token=self.token)
        if client.is_dir(f'/{self.name_folder}'):
            params['path'] = f'/{self.name_folder}/{self.text}.jpeg'
            params.update({'url': response['url']})
            requests.post(self.get_api('/disk/resources/upload'), headers=headers, params=params)
            print('Папка существует на диске. Изображение сохранено.')
        else:
            requests.put(self.get_api('/disk/resources'), headers=headers, params=params)
            params['path'] = f'/{self.name_folder}/{self.text}.jpeg'
            params.update({'url': response['url']})
            requests.post(self.get_api('/disk/resources/upload'), headers=headers, params=params)
            print('Папка создана. Файл сохранен.')

picture_cat1 = Backup(input('Введите токен Яндекс диска: '), input('Введите текст для изображения: '))
picture_cat1.get_picture_cat()
picture_cat1.create_json()
picture_cat1.save_picture()