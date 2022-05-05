# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного
# пользователя(input или argparse), сохранить JSON-вывод в файле *.json;
# написать функцию, возвращающую(return) список репозиториев.


import json
import requests
import time

REPOS_PATH = "github_repo.json"


class GitHubUser:
    def __init__(self, username):
        self.username = username
        self.url = f'https://api.github.com/users/{self.username}/repos'

    def get_url(self):
        return self.url

    @staticmethod
    def get_user_repo(url_user):
        while True:
            time.sleep(1)
            repo_info = requests.get(url_user)
            repo_info_json = repo_info.json()
            if repo_info.status_code == 200:
                return repo_info_json
            break

    @staticmethod
    def return_list_repositories(data):
        repositories_list = []
        for i in data:
            repositories_list.append(i['name'])
        return repositories_list

    @staticmethod
    def save_repositories(repos_info, path):
        with open(path, "w") as f:
            json.dump(repos_info, f, indent=2)
        print(f'Список репозиториев сохранен в файл {path}.')

    def pipeline(self, path):
        try:
            url = self.get_url()
            data = self.get_user_repo(url)
            print(f'Список репозиториев пользователя {self.username}: {self.return_list_repositories(data)}')
            self.save_repositories(data, path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        user_input = input("Введите имя пользователя GitHub: ")
        github = GitHubUser(user_input)
        github.pipeline(REPOS_PATH)
    except Exception as e:
        print(e)
