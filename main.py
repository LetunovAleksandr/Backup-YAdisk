import requests
import os
import json
from requests import RequestException


class Backup:
    def __init__(self, token, text):
        self.token = token.strip()
        self.text = text
        self.name_folder = 'PYQA-134'
        self.response = None

    @property
    def headers(self):
        return {
            'Authorization': f'OAuth {self.token}'
        }

    @staticmethod
    def get_api (path):
        return f'https://cloud-api.yandex.net/v1{path}'

    def check_token(self):
        try:
            self.token.encode('ascii')
        except UnicodeEncodeError:
            print('Неверный токен.')
            return False

        try:
            response = requests.get(
                self.get_api('/disk'),
                headers=self.headers
            )
            if response.status_code == 200:
                print('Авторизация: Успешно.')
                return True

            print(
                f'Ошибка авторизации. '
                f'Код: {response.status_code}. '
                f'Ответ: {response.json()["message"]}'
            )
            return False
        except RequestException as e:
            print(f'Ошибка запроса: {e}.')
            return False


    def get_picture_cat(self):
        if self.response is None:
            self.response = requests.get(
                f'https://cataas.com/cat/says/{self.text}?json=true',
                timeout=10
            )
            if self.response.status_code != 200:
               raise ValueError(
                   f"Ошибка получения изображения {self.response.status_code}. "
               )
            else:
                print('Изображение получено.')
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
                print('Файл "pictures_data.json" открыт.')
                data.update(json_data)
                with open('data/pictures_data.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                    print('Данные записаны.')
        else:
            with open('data/pictures_data.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
                print('Файл "pictures_data.json" создан. Данные записаны.')

    def create_folder(self, name_folder):
        params = {
            'path': f'/{name_folder}',
        }
        folder_response = requests.get(
            self.get_api('/disk/resources'),
            headers=self.headers,
            params=params,
            timeout=10
        )
        if folder_response.status_code == 200:
            print (f'Папка "{name_folder}" существует.')

        else:
            requests.put(
                self.get_api('/disk/resources'),
                headers=self.headers,
                params=params,
                timeout=10
            )
            print(f'Папка "{name_folder}" создана.')


    def save_picture(self):
        response = self.response.json()
        params = {
            'path': f'/{self.name_folder}/{self.text}.jpeg',
            'url': response['url']
        }
        self.create_folder(self.name_folder)
        save_picture = requests.post(
            self.get_api('/disk/resources/upload'),
            headers=self.headers,
            params=params,
            timeout=10
        )
        if save_picture.status_code in (200, 201, 202):
            print(f'Изображение "{self.text}" загружено в папку "{self.name_folder}".')
        else:
            print(save_picture.status_code, save_picture.text)

    def backup(self):
        if picture_cat.check_token():
            picture_cat.get_picture_cat()
            picture_cat.create_json()
            picture_cat.save_picture()


if __name__ == '__main__':
    picture_cat = Backup(
        input('Введите токен Яндекс диска: '),
        input('Введите текст для изображения: ')
    )
    picture_cat.backup()