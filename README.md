# Python-Yandexdirect
Небольшая библиотека позволяет обращаться к методам Api Яндекс директа.
Адаптировано к использованию на Google AppEngine.
Это форк вот этого [проекта](https://bitbucket.org/umonkey/python-yandexdirect) на bitbucket.org/umonkey/

# Официальная документация
* [API Яндекс.Директ](http://api.yandex.ru/direct/doc/)
* [OAuth сервер Яндекса](https://oauth.yandex.ru/)

# Установка
    git clone git://github.com/Gasoid/python-yandexdirect.git

# Использование
## OAuth авторизация
    import yandexdirect
    # Сначала регистрируем приложение на Яндекс OAuth-сервере
    # Вам дадут application_id, и token для приложения
    # Теперь надо дать доступ вашему приложению к директу
    # проходим OAuth авторизацию
    client = yandexdirect.Client(app_id,login,auth_token)
    
    print client.get_auth_url() # Надо пройти по этой ссылке и посмотреть code
    
    print client.get_token_by_code(code) # вот здесь получаем пользовательский токен

## Работа с методами
    import yandexdirect
    client = yandexdirect.Client(app_id, login, user_token) # нужны логин пользователя в яндекс директе, пользовательский токен
    
    # Список кампаний в директе
    campaigns = client.GetCampaignsList(clients=[login])
    for campaign in campaigns:
        print campaign['Name']
    
    campaign = campaigns[0]
    # Список объявлений в кампании
    banners = client.GetBanners([campaign['CampaignID']])

Все методы и возвращаемые данные есть в документации API Яндекса.Директа

Реализованные методы:

* GetBanners
* GetBalance
* GetBannerPhrases
* GetVersion
* Ping
* GetClientInfo
* GetClientsList
* GetSubClients
* GetCampaignsList
* UpdatePrices
* SetAutoPrice

