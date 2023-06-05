import instaloader
import os
import requests

def get_current_ip(cur_session):
    x = cur_session.get('https://ifconfig.io/ip', stream=True)
    return x.content.decode().replace('\n', '')

def set_transport(use_proxy=False):
    if use_proxy:
        # Задаем параметры прокси
        proxy_host = '77.125.8.222'
        proxy_port = '3123'
        proxy_username = 'myprx'
        proxy_password = 'aa1122334455'

        # Создаем сессию с настройками прокси
        session = requests.Session()
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            # 'https': f'https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
        }

        os.environ["HTTP_PROXY"]  = proxies['http']
        os.environ["HTTPS_PROXY"] = proxies['http']

        return session
    else:
        return requests

def get_parsed_result(post_url: str, username: str = '', password:str = '') -> dict:
    transport = set_transport(use_proxy=True)

    # Получаем текущий IP-адрес
    transport_ip = get_current_ip(transport)

    # Создаем экземпляр класса Instaloader
    loader = instaloader.Instaloader()

    # Получаем код поста из ссылки
    shortcode = post_url.split("/")[-2]

    # Устанавливаем сессию для Instaloader
    loader.download_session = transport

    if username and password:
        # Аутентифицируемся в Instagram
        loader.login(username, password)

    # Загружаем пост по идентификатору
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    if not os.path.exists(shortcode):
        os.makedirs(shortcode)

    # Сохраняем все фотографии
    counter = 0
    for node in post.get_sidecar_nodes():
        url = node.display_url
        filename = f"{shortcode}_{counter + 1}.jpg"
        filepath = os.path.join(shortcode, filename)
        response = transport.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(response.content)
        counter += 1
    file_count = counter

    # Получаем основную информацию о посте
    caption = post.caption
    likes = post.likes
    media_url = post.url
    author = post.owner_profile.username
    location = post.location
    created_at = post.date_local

    # Получаем комментарии
    comments = []
    # for comment in post.get_comments():
    #     comments.append(comment.text)

    # # Сохраняем комментарии в файл
    # comments_filepath = os.path.join(shortcode, "comments.txt")
    # with open(comments_filepath, "w", encoding="utf-8") as file:
    #     file.write("\n".join(comments))

    return {
        'caption': caption,
        'likes': likes,
        'comments': comments,
        'media_url': media_url,
        'author': author,
        'location': location,
        'created_at': created_at,
        'comments_filepath': '',    # comments_filepath
        'file_count': file_count,
        'shortcode': shortcode,
        'transport_ip': transport_ip,
    }


if __name__ == '__main__':
    post_url = "https://www.instagram.com/p/CqkJmsnNcRH/"
    res = get_parsed_result(post_url)   # Используй username, password для входа в аккаунт инстаграмма
    print(res)


