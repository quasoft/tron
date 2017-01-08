#!/usr/bin/env python3
import time
from collections import OrderedDict

import requests
from lxml import html
import datetime
from server import config
from server.providers.base import BaseWeatherProvider
from server import utils


class SinoptikProvider(BaseWeatherProvider):
    """
    Implements a provider of weather data via website of sinoptik.
    Acquire permission from sinoptik if you want to use their data.
    """

    id = "sinoptik"
    """Unique ID of provider"""

    hourly_url = "http://m.sinoptik.bg/%s/hourly"
    """Points to mobile page for hourly forecast in a specific Bulgarian location"""

    bulgarian_locations_url = "http://sinoptik.bg/locations/europe/bulgaria"

    locations = []
    """List of IDs for locations in sinoptik web service"""

    def __init__(self):
        self.populate_default_locations()

    def get_location_by_id(self, name):
        return next((c for c in self.locations if c['id'] == name), None)

    def get_location_by_name(self, name):
        return next((c for c in self.locations if c['name'] == name), None)

    def get_location_id_by_name(self, name):
        location = self.get_location_by_name(name)
        return location['id']

    def covers_location(self, location_id=None, location_name=None):
        """
        Check if the provider has weather data for the specified location.
        :param location_id: ID of location - specific for each provider
        :param location_name: Human readable name of location
        :return: True if provider has weather data for that location
        """
        if location_id:
            return self.get_location_by_id(location_id)

        if location_name:
            return self.get_location_by_name(location_name)

        return False

    def download_data(self, location_id=None, location_name=None):
        """
        Download weather data for a specified location by its ID or name.
        :param location_id: ID of location - specific for each provider
        :param location_name: Human readable name of location
        :return: Dictionary with hourly weather data in the following format:
                 {"HH:mm": [temperature, precipation_chance, precipation_intensity], "HH:mm": ...}

                 Example return:
                 {"20:00": ["6℃", "3%", "0.0 mm"], "21:00":[]}
        """

        now = datetime.datetime.now()

        if not location_id:
            # Get location ID by name
            location_id = self.get_location_id_by_name(location_name)

        if not location_id:
            raise ValueError("SinoptikProvider.download_data(): No location ID specified")

        # Retrieve HTML of hourly web page for that location
        url = self.hourly_url % location_id
        doc = utils.get_html(url)

        # Parse HTML and extract the weather data we need
        temp = doc.xpath('.//span[contains(@class, \'max-temp\')]/text()')
        rain_probability = doc.xpath('.//p[starts-with(text(),"Вероятност за валежи:")]/b/text()')
        rain_intensity = doc.xpath('.//p[starts-with(text(),"Количество валежи:")]/b/text()')

        # Group data by hour
        hour = int(now.strftime("%H"))
        hours = [str((hour + i) % 24) + ':00' for i in range(24)]
        rain = zip(temp, rain_probability, rain_intensity)
        data = OrderedDict(zip(hours, rain))

        return data

    def download_locations(self):
        """
        Scraps sinoptik website for location names and their corresponding IDs
        :return: List of dictionaries with location id and name as values.
        """
        self.locations = []

        locations_str = ""

        # Use only letters for available locations on sinoptik.bg
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'З', 'И', 'К', 'Л', 'М', 'Н',
                   'О', 'П', 'Р', 'С', 'Т', 'У', 'Х', 'Ц', 'Ч', 'Ш', 'Я']

        for l in letters:
            # This is the URL where locations are listed, grouped by letter:
            url = 'http://sinoptik.bg/locations/europe/bulgaria/%s?locations' % l

            # Pretend it's an ajax request, or no data would be sent back
            headers = {
                'User-Agent': config.desktop_user_agent,
                'X-Requested-With': "XMLHttpRequest",
                'Referrer': "http://sinoptik.bg/locations/europe/bulgaria",
            }
            page = requests.get(url, headers=headers).text
            doc = html.fromstring(page)

            # Pretend it's a human clicking on letters
            time.sleep(0.5)

            # Parse HTML and extract location IDs
            """This is how HTML looks like (whitespace reformatted):
            <div class="worldContent">
                <div class="worldCol">
                    <ul>
                        <li>
                            <a href="http://sinoptik.bg/avren-bulgaria-100733587">
                            Аврен</a>
                        </li>
                        ...
                    </ul>
                </div>
            </div>
            """
            anchors = doc.xpath('.//div[contains(@class, \'worldContent\')]/div/ul/li/a')
            for a in anchors:
                name = a.text.strip()
                href = a.get('href')
                id = href.rsplit('/', 1)[-1]

                # Add data for this location
                loc = OrderedDict()
                loc['name'] = name
                loc['id'] = id

                self.locations.append(loc)

                locations_str += "{'name': \"%s\", 'id': \"%s\"},\n" % (name, id)

        return locations_str

    def populate_default_locations(self):
        self.locations = [
            {'name': "Аврен", 'id': "avren-bulgaria-100733587"},
            {'name': "Айтос", 'id': "aytos-bulgaria-100733579"},
            {'name': "Аксаково", 'id': "aksakovo-bulgaria-100733716"},
            {'name': "Албена", 'id': "albena-bulgaria-100733702"},
            {'name': "Алфатар", 'id': "alfatar-bulgaria-100733679"},
            {'name': "Антон", 'id': "anton-bulgaria-100733660"},
            {'name': "Антоново", 'id': "antonovo-bulgaria-100733657"},
            {'name': "Априлци", 'id': "apriltsi-bulgaria-100733649"},
            {'name': "Ардино", 'id': "ardino-bulgaria-100733638"},
            {'name': "Асеновград", 'id': "asenovgrad-bulgaria-100733618"},
            {'name': "Ахтопол", 'id': "akhtopol-bulgaria-100733722"},
            {'name': "Балчик", 'id': "balchik-bulgaria-100733515"},
            {'name': "Баните", 'id': "banite-bulgaria-100733474"},
            {'name': "Банско", 'id': "bansko-bulgaria-100733462"},
            {'name': "Батак", 'id': "batak-bulgaria-100733433"},
            {'name': "Батановци", 'id': "batanovtsi-bulgaria-100726489"},
            {'name': "Безбог", 'id': "bezbog-bulgaria-307000001"},
            {'name': "Белене", 'id': "belene-bulgaria-100733359"},
            {'name': "Белица", 'id': "belitsa-bulgaria-100733322"},
            {'name': "Белмекен", 'id': "belmeken-bulgaria-307000004"},
            {'name': "Белово", 'id': "belovo-bulgaria-100733286"},
            {'name': "Белоградчик", 'id': "belogradchik-bulgaria-100733309"},
            {'name': "Белослав", 'id': "beloslav-bulgaria-100725213"},
            {'name': "Берковица", 'id': "berkovitsa-bulgaria-100733264"},
            {'name': "Благоевград", 'id': "blagoevgrad-bulgaria-100733191"},
            {'name': "Бобовдол", 'id': "bobovdol-bulgaria-100733151"},
            {'name': "Бобошево", 'id': "boboshevo-bulgaria-100733153"},
            {'name': "Божурище", 'id': "bozhurishte-bulgaria-100732954"},
            {'name': "Бойница", 'id': "boynitsa-bulgaria-100732973"},
            {'name': "Бойчиновци", 'id': "boychinovtsi-bulgaria-100732986"},
            {'name': "Болярово", 'id': "bolyarovo-bulgaria-100733092"},
            {'name': "Борино", 'id': "borino-bulgaria-100733067"},
            {'name': "Борован", 'id': "borovan-bulgaria-100733058"},
            {'name': "Боровец", 'id': "borovets-bulgaria-100733055"},
            {'name': "Борово", 'id': "borovo-bulgaria-100733043"},
            {'name': "Ботевград", 'id': "botevgrad-bulgaria-100733014"},
            {'name': "Братя Даскалови", 'id': "bratya-daskalovi-bulgaria-100732920"},
            {'name': "Брацигово", 'id': "bratsigovo-bulgaria-100732924"},
            {'name': "Брегово", 'id': "bregovo-bulgaria-100732915"},
            {'name': "Брезник", 'id': "breznik-bulgaria-100732883"},
            {'name': "Брезово", 'id': "brezovo-bulgaria-100732874"},
            {'name': "Брусарци", 'id': "brusartsi-bulgaria-100732862"},
            {'name': "Бургас", 'id': "burgas-bulgaria-100732770"},
            {'name': "Бухово", 'id': "bukhovo-bulgaria-100732825"},
            {'name': "Бяла", 'id': "byala-bulgaria-100732720"},
            {'name': "Бяла", 'id': "byala-bulgaria-100732721"},
            {'name': "Бяла Слатина", 'id': "byala-slatina-bulgaria-100732704"},
            {'name': "Бяла Черква", 'id': "byala-cherkva-bulgaria-100732717"},
            {'name': "Варвара", 'id': "varvara-bulgaria-307000007"},
            {'name': "Варна", 'id': "varna-bulgaria-100726050"},
            {'name': "Велики Преслав", 'id': "veliki-preslav-bulgaria-100727987"},
            {'name': "Велико Търново", 'id': "veliko-turnovo-bulgaria-100725993"},
            {'name': "Велинград", 'id': "velingrad-bulgaria-100725988"},
            {'name': "Венец", 'id': "venets-bulgaria-100725967"},
            {'name': "Ветово", 'id': "vetovo-bulgaria-100725935"},
            {'name': "Ветрино", 'id': "vetrino-bulgaria-100725924"},
            {'name': "Видин", 'id': "vidin-bulgaria-100725905"},
            {'name': "Вихрен", 'id': "vihren-bulgaria-307000008"},
            {'name': "Враца", 'id': "vratsa-bulgaria-100725712"},
            {'name': "Вълчедръм", 'id': "vulchedrum-bulgaria-100725683"},
            {'name': "Вълчидол", 'id': "vulchidol-bulgaria-100725679"},
            {'name': "Върбица", 'id': "vurbitsa-bulgaria-100725649"},
            {'name': "Вършец", 'id': "vurshets-bulgaria-100725623"},
            {'name': "Габрово", 'id': "gabrovo-bulgaria-100731549"},
            {'name': "Гара Хитрино", 'id': "gara-khitrino-bulgaria-100731520"},
            {'name': "Генерал Тошево", 'id': "general-toshevo-bulgaria-100731464"},
            {'name': "Георги-Дамяново", 'id': "georgi-damyanovo-bulgaria-100731458"},
            {'name': "Главиница", 'id': "glavinitsa-bulgaria-100731415"},
            {'name': "Годеч", 'id': "godech-bulgaria-100731384"},
            {'name': "Горна Малина", 'id': "gorna-malina-bulgaria-100731239"},
            {'name': "Горна Оряховица", 'id': "gorna-oryahovitsa-bulgaria-100731233"},
            {'name': "Гоце Делчев", 'id': "gotse-delchev-bulgaria-100731108"},
            {'name': "Грамада", 'id': "gramada-bulgaria-100731056"},
            {'name': "Гулянци", 'id': "gulyantsi-bulgaria-100730982"},
            {'name': "Гурково", 'id': "gurkovo-bulgaria-100730969"},
            {'name': "Гърмен", 'id': "gurmen-bulgaria-100730960"},
            {'name': "Две могили", 'id': "dve-mogili-bulgaria-100731771"},
            {'name': "Дебелец", 'id': "debelets-bulgaria-100732359"},
            {'name': "Девин", 'id': "devin-bulgaria-100732285"},
            {'name': "Девня", 'id': "devnya-bulgaria-100732280"},
            {'name': "Джебел", 'id': "dzhebel-bulgaria-100731741"},
            {'name': "Димитровград", 'id': "dimitrovgrad-bulgaria-100732263"},
            {'name': "Димово", 'id': "dimovo-bulgaria-100732253"},
            {'name': "Добринище", 'id': "dobrinishte-bulgaria-307000009"},
            {'name': "Добрич", 'id': "dobrich-bulgaria-100726418"},
            {'name': "Долна Баня", 'id': "dolna-banya-bulgaria-100732145"},
            {'name': "Долна Митрополия", 'id': "dolna-mitropoliya-bulgaria-100732122"},
            {'name': "Долни Дъбник", 'id': "dolni-dubnik-bulgaria-100732099"},
            {'name': "Долни чифлик", 'id': "dolni-chiflik-bulgaria-100731453"},
            {'name': "Долно Камарци", 'id': "dolno-kamarci-bulgaria-307000010"},
            {'name': "Доспат", 'id': "dospat-bulgaria-100732015"},
            {'name': "Драгоман", 'id': "dragoman-bulgaria-100731961"},
            {'name': "Дряново", 'id': "dryanovo-bulgaria-100731882"},
            {'name': "Дулово", 'id': "dulovo-bulgaria-100731818"},
            {'name': "Дунавци", 'id': "dunavtsi-bulgaria-100731809"},
            {'name': "Дупница", 'id': "dupnitsa-bulgaria-100726872"},
            {'name': "Дуранкулак", 'id': "durankulak-bulgaria-100731803"},
            {'name': "Дългопол", 'id': "dulgopol-bulgaria-100731822"},
            {'name': "Елена", 'id': "elena-bulgaria-100731696"},
            {'name': "Елин Пелин", 'id': "elin-pelin-bulgaria-100731675"},
            {'name': "Елхово", 'id': "elkhovo-bulgaria-100731670"},
            {'name': "Емона", 'id': "emona-bulgaria-100731653"},
            {'name': "Етрополе", 'id': "etropole-bulgaria-100731626"},
            {'name': "Завет", 'id': "zavet-bulgaria-100725435"},
            {'name': "Земен", 'id': "zemen-bulgaria-100725402"},
            {'name': "Златарица", 'id': "zlataritsa-bulgaria-100725295"},
            {'name': "Златица", 'id': "zlatitsa-bulgaria-100725283"},
            {'name': "Златни пясъци", 'id': "golden-sands-bulgaria-106355004"},
            {'name': "Златоград", 'id': "zlatograd-bulgaria-100725271"},
            {'name': "Ивайловград", 'id': "ivaylovgrad-bulgaria-100730837"},
            {'name': "Иваново", 'id': "ivanovo-bulgaria-100730852"},
            {'name': "Иракли", 'id': "irakli-bulgaria-307000002"},
            {'name': "Искър", 'id': "iskur-bulgaria-100728348"},
            {'name': "Исперих", 'id': "isperikh-bulgaria-100730866"},
            {'name': "Ихтиман", 'id': "ikhtiman-bulgaria-100730919"},
            {'name': "Каварна", 'id': "kavarna-bulgaria-100730518"},
            {'name': "Казанлък", 'id': "kazanlak-bulgaria-100730496"},
            {'name': "Кайнарджа", 'id': "kaynardzha-bulgaria-100730504"},
            {'name': "Калофер", 'id': "kalofer-bulgaria-100730744"},
            {'name': "Калояново", 'id': "kaloyanovo-bulgaria-100730733"},
            {'name': "Камено", 'id': "kameno-bulgaria-100730680"},
            {'name': "Каолиново", 'id': "kaolinovo-bulgaria-100730651"},
            {'name': "Карлово", 'id': "karlovo-bulgaria-100730565"},
            {'name': "Карнобат", 'id': "karnobat-bulgaria-100730559"},
            {'name': "Каспичан", 'id': "kaspichan-bulgaria-100730542"},
            {'name': "Кермен", 'id': "kermen-bulgaria-100730478"},
            {'name': "Килифарево", 'id': "kilifarevo-bulgaria-100730367"},
            {'name': "Кирково", 'id': "kirkovo-bulgaria-100730355"},
            {'name': "Китен", 'id': "kiten-bulgaria-100730338"},
            {'name': "Клисура", 'id': "klisura-bulgaria-100730301"},
            {'name': "Кнежа", 'id': "knezha-bulgaria-100730287"},
            {'name': "Ковачевци", 'id': "kovachevtsi-bulgaria-100730051"},
            {'name': "Козлодуй", 'id': "kozloduy-bulgaria-100730013"},
            {'name': "Койнаре", 'id': "koynare-bulgaria-100730040"},
            {'name': "Копривщица", 'id': "koprivshtitsa-bulgaria-100730159"},
            {'name': "Костинброд", 'id': "kostinbrod-bulgaria-100730084"},
            {'name': "Котел", 'id': "kotel-bulgaria-100730073"},
            {'name': "Кочериново", 'id': "kocherinovo-bulgaria-100730268"},
            {'name': "Кранево", 'id': "kranevo-bulgaria-100729984"},
            {'name': "Кресна", 'id': "kresna-bulgaria-100729942"},
            {'name': "Криводол", 'id': "krivodol-bulgaria-100729909"},
            {'name': "Кричим", 'id': "krichim-bulgaria-100729936"},
            {'name': "Крумовград", 'id': "krumovgrad-bulgaria-100729896"},
            {'name': "Крушари", 'id': "krushari-bulgaria-100729880"},
            {'name': "Кубрат", 'id': "kubrat-bulgaria-100729839"},
            {'name': "Кула", 'id': "kula-bulgaria-100729825"},
            {'name': "Кърджали", 'id': "kardzhali-bulgaria-100729794"},
            {'name': "Кюстендил", 'id': "kyustendil-bulgaria-100729730"},
            {'name': "Левски", 'id': "levski-bulgaria-100729636"},
            {'name': "Лесичево", 'id': "lesichevo-bulgaria-100729667"},
            {'name': "Летница", 'id': "letnitsa-bulgaria-100729646"},
            {'name': "Ловеч", 'id': "lovech-bulgaria-100729559"},
            {'name': "Лозенец", 'id': "lozenets-bulgaria-100729541"},
            {'name': "Лозница", 'id': "loznitsa-bulgaria-100729530"},
            {'name': "Лом", 'id': "lom-bulgaria-100729581"},
            {'name': "Луковит", 'id': "lukovit-bulgaria-100729507"},
            {'name': "Лъки", 'id': "luki-bulgaria-100729509"},
            {'name': "Любимец", 'id': "lyubimets-bulgaria-100729466"},
            {'name': "Люлин", 'id': "lyulin-bulgaria-307000011"},
            {'name': "Лясковец", 'id': "lyaskovets-bulgaria-100729489"},
            {'name': "Мадан", 'id': "madan-bulgaria-100729439"},
            {'name': "Маджарово", 'id': "madzharovo-bulgaria-100729428"},
            {'name': "Макреш", 'id': "makresh-bulgaria-100729401"},
            {'name': "Малко Търново", 'id': "malko-turnovo-bulgaria-100729322"},
            {'name': "Мальовица", 'id': "maliovitsa-bulgaria-307000005"},
            {'name': "Медковец", 'id': "medkovets-bulgaria-100729174"},
            {'name': "Мездра", 'id': "mezdra-bulgaria-100729134"},
            {'name': "Мелник", 'id': "melnik-bulgaria-100729159"},
            {'name': "Мизия", 'id': "miziya-bulgaria-100729040"},
            {'name': "Минерални бани", 'id': "mineralni-bani-bulgaria-100729073"},
            {'name': "Мирково", 'id': "mirkovo-bulgaria-100729064"},
            {'name': "Монтана", 'id': "montana-bulgaria-100729114"},
            {'name': "Мусала", 'id': "musala-bulgaria-305021306"},
            {'name': "Мъглиж", 'id': "muglizh-bulgaria-100728928"},
            {'name': "Невестино", 'id': "nevestino-bulgaria-100728818"},
            {'name': "Неделино", 'id': "nedelino-bulgaria-100728851"},
            {'name': "Несебър", 'id': "nesebur-bulgaria-100728825"},
            {'name': "Николаево", 'id': "nikolaevo-bulgaria-100728795"},
            {'name': "Никола-Козлево", 'id': "nikola-kozlevo-bulgaria-100728791"},
            {'name': "Никопол", 'id': "nikopol-bulgaria-100728782"},
            {'name': "Нова Загора", 'id': "nova-zagora-bulgaria-100728742"},
            {'name': "Нови пазар", 'id': "novi-pazar-bulgaria-100728734"},
            {'name': "Ново село", 'id': "novo-selo-bulgaria-100728709"},
            {'name': "Обзор", 'id': "obzor-bulgaria-100728674"},
            {'name': "Омуртаг", 'id': "omurtag-bulgaria-100728634"},
            {'name': "Опака", 'id': "opaka-bulgaria-100728631"},
            {'name': "Опан", 'id': "opan-bulgaria-100728627"},
            {'name': "Оряхово", 'id': "oryakhovo-bulgaria-100728565"},
            {'name': "Павел баня", 'id': "pavel-banya-bulgaria-100728389"},
            {'name': "Павликени", 'id': "pavlikeni-bulgaria-100728385"},
            {'name': "Пазарджик", 'id': "pazardzhik-bulgaria-100728378"},
            {'name': "Пампорово", 'id': "pamporovo-bulgaria-211002088"},
            {'name': "Панагюрище", 'id': "panagyurishte-bulgaria-100728448"},
            {'name': "Перник", 'id': "pernik-bulgaria-100728330"},
            {'name': "Перущица", 'id': "perushtitsa-bulgaria-100728321"},
            {'name': "Петрич", 'id': "petrich-bulgaria-100728288"},
            {'name': "Пещера", 'id': "peshtera-bulgaria-100728317"},
            {'name': "Пирдоп", 'id': "pirdop-bulgaria-100728251"},
            {'name': "Плевен", 'id': "pleven-bulgaria-100728203"},
            {'name': "Плиска", 'id': "pliska-bulgaria-100728199"},
            {'name': "Пловдив", 'id': "plovdiv-bulgaria-100728193"},
            {'name': "Полски Тръмбеш", 'id': "polski-trumbesh-bulgaria-100728124"},
            {'name': "Поморие", 'id': "pomorie-bulgaria-100728108"},
            {'name': "Попово", 'id': "popovo-bulgaria-100728075"},
            {'name': "Пордим", 'id': "pordim-bulgaria-100728056"},
            {'name': "Правец", 'id': "pravets-bulgaria-100728011"},
            {'name': "Приморско", 'id': "primorsko-bulgaria-100727964"},
            {'name': "Провадия", 'id': "provadiya-bulgaria-100727921"},
            {'name': "Равда", 'id': "ravda-bulgaria-100727759"},
            {'name': "Раднево", 'id': "radnevo-bulgaria-100727838"},
            {'name': "Радомир", 'id': "radomir-bulgaria-100727832"},
            {'name': "Разград", 'id': "razgrad-bulgaria-100727696"},
            {'name': "Разлог", 'id': "razlog-bulgaria-100727689"},
            {'name': "Ракитово", 'id': "rakitovo-bulgaria-100727801"},
            {'name': "Раковски", 'id': "rakovski-bulgaria-100727791"},
            {'name': "Резово", 'id': "rezovo-bulgaria-100727649"},
            {'name': "Рила", 'id': "rila-bulgaria-100727628"},
            {'name': "Роман", 'id': "roman-bulgaria-100727598"},
            {'name': "Рудозем", 'id': "rudozem-bulgaria-100727552"},
            {'name': "Руен", 'id': "ruen-bulgaria-100727547"},
            {'name': "Ружинци", 'id': "ruzhintsi-bulgaria-100727495"},
            {'name': "Русе", 'id': "ruse-bulgaria-100727523"},
            {'name': "Садово", 'id': "sadovo-bulgaria-100727479"},
            {'name': "Самоков", 'id': "samokov-bulgaria-100727462"},
            {'name': "Самуил", 'id': "samuil-bulgaria-100727455"},
            {'name': "Сандански", 'id': "sandanski-bulgaria-100727447"},
            {'name': "Сапарева баня", 'id': "sapareva-banya-bulgaria-100727441"},
            {'name': "Сарафово", 'id': "sarafovo-bulgaria-100727434"},
            {'name': "Сатовча", 'id': "satovcha-bulgaria-100727423"},
            {'name': "Свети Влас", 'id': "sveti-vlas-bulgaria-100725816"},
            {'name': "Свиленград", 'id': "svilengrad-bulgaria-100726546"},
            {'name': "Свищов", 'id': "svishtov-bulgaria-100726534"},
            {'name': "Своге", 'id': "svoge-bulgaria-100726524"},
            {'name': "Севлиево", 'id': "sevlievo-bulgaria-100727337"},
            {'name': "Сеново", 'id': "senovo-bulgaria-100727358"},
            {'name': "Септември", 'id': "septemvri-bulgaria-100727354"},
            {'name': "Силистра", 'id': "silistra-bulgaria-100727221"},
            {'name': "Симеоновград", 'id': "simeonovgrad-bulgaria-100727217"},
            {'name': "Симитли", 'id': "simitli-bulgaria-100727212"},
            {'name': "Синеморец", 'id': "sinemorets-bulgaria-100727201"},
            {'name': "Ситово", 'id': "sitovo-bulgaria-100727175"},
            {'name': "Славяново", 'id': "slavyanovo-bulgaria-100727087"},
            {'name': "Сливен", 'id': "sliven-bulgaria-100727079"},
            {'name': "Сливница", 'id': "slivnitsa-bulgaria-100727069"},
            {'name': "Сливо Поле", 'id': "slivo-pole-bulgaria-100727067"},
            {'name': "Слънчев бряг", 'id': "sunny-beach-bulgaria-106355005"},
            {'name': "Смолян", 'id': "smolyan-bulgaria-100727030"},
            {'name': "Смядово", 'id': "smyadovo-bulgaria-100727025"},
            {'name': "Созопол", 'id': "sozopol-bulgaria-100726963"},
            {'name': "София", 'id': "sofia-bulgaria-100727011"},
            {'name': "Средец", 'id': "sredets-bulgaria-100731016"},
            {'name': "Стамболийски", 'id': "stamboliyski-bulgaria-100726890"},
            {'name': "Стамболово", 'id': "stambolovo-bulgaria-100726888"},
            {'name': "Стара Загора", 'id': "stara-zagora-bulgaria-100726848"},
            {'name': "Стара Кресна", 'id': "stara-kresna-bulgaria-100726863"},
            {'name': "Стражица", 'id': "strazhitsa-bulgaria-100726727"},
            {'name': "Стралджа", 'id': "straldzha-bulgaria-100726748"},
            {'name': "Стрелча", 'id': "strelcha-bulgaria-100726723"},
            {'name': "Струмяни", 'id': "strumyani-bulgaria-100726693"},
            {'name': "Суворово", 'id': "suvorovo-bulgaria-100726591"},
            {'name': "Сунгурларе", 'id': "sungurlare-bulgaria-100726629"},
            {'name': "Сухиндол", 'id': "sukhindol-bulgaria-100726643"},
            {'name': "Съединение", 'id': "suedinenie-bulgaria-100726657"},
            {'name': "Твърдица", 'id': "tvurditsa-bulgaria-100726130"},
            {'name': "Тервел", 'id': "tervel-bulgaria-100726474"},
            {'name': "Тетевен", 'id': "teteven-bulgaria-100726464"},
            {'name': "Тодорка", 'id': "todorka-bulgaria-307000012"},
            {'name': "Тончевци", 'id': "tonchevtsi-bulgaria-100726409"},
            {'name': "Тополовград", 'id': "topolovgrad-bulgaria-100726384"},
            {'name': "Трекляно", 'id': "treklyano-bulgaria-100726352"},
            {'name': "Троян", 'id': "troyan-bulgaria-100726320"},
            {'name': "Трън", 'id': "trun-bulgaria-100726307"},
            {'name': "Трявна", 'id': "tryavna-bulgaria-100726287"},
            {'name': "Тутракан", 'id': "tutrakan-bulgaria-100726141"},
            {'name': "Търговище", 'id': "turgovishte-bulgaria-100726174"},
            {'name': "Угърчин", 'id': "ugurchin-bulgaria-100726114"},
            {'name': "Узана", 'id': "uzana-bulgaria-307000003"},
            {'name': "Хаджидимово", 'id': "khadzhidimovo-bulgaria-100730464"},
            {'name': "Хайредин", 'id': "khayredin-bulgaria-100730425"},
            {'name': "Харманли", 'id': "kharmanli-bulgaria-100730442"},
            {'name': "Хасково", 'id': "haskovo-bulgaria-100730435"},
            {'name': "Хисаря", 'id': "khisarya-bulgaria-100730419"},
            {'name': "Царево", 'id': "tsarevo-bulgaria-100729125"},
            {'name': "Цар Калоян", 'id': "tsar-kaloyan-bulgaria-100730415"},
            {'name': "Ценово", 'id': "tsenovo-bulgaria-100726245"},
            {'name': "Чавдар", 'id': "chavdar-bulgaria-100732655"},
            {'name': "Челопеч", 'id': "chelopech-bulgaria-100732636"},
            {'name': "Чепеларе", 'id': "chepelare-bulgaria-100732627"},
            {'name': "Червен бряг", 'id': "cherven-bryag-bulgaria-100732491"},
            {'name': "Черни връх", 'id': "cherni-vrah-bulgaria-307000006"},
            {'name': "Черноморец", 'id': "chernomorets-bulgaria-100732519"},
            {'name': "Черноочене", 'id': "chernoochene-bulgaria-100732517"},
            {'name': "Чипровци", 'id': "chiprovtsi-bulgaria-100732456"},
            {'name': "Чирпан", 'id': "chirpan-bulgaria-100732452"},
            {'name': "Чупрене", 'id': "chuprene-bulgaria-100732400"},
            {'name': "Шабла", 'id': "shabla-bulgaria-100727329"},
            {'name': "Шипка", 'id': "shipka-bulgaria-100727291"},
            {'name': "Шумен", 'id': "shumen-bulgaria-100727233"},
            {'name': "Ябланица", 'id': "yablanitsa-bulgaria-100725611"},
            {'name': "Якимово", 'id': "yakimovo-bulgaria-100725588"},
            {'name': "Якоруда", 'id': "yakoruda-bulgaria-100725586"},
            {'name': "Ямбол", 'id': "yambol-bulgaria-100725578"},
        ]


if __name__ == '__main__':
    sinoptik = SinoptikProvider()
    locations_str = sinoptik.download_locations()

    print("Sinoptik locations:")
    print("-------------------")
    print(locations_str)
    print("")

    print("Downloaded data for Велико Търново:")
    print("-----------------------------------")
    data = sinoptik.download_data(location_name="Велико Търново")
    print(data)

    print("Find provider by id:")
    print("--------------------")
    print(SinoptikProvider.find_provider(provider_id="sinoptik"))

    print("Find provider by location name:")
    print("----------------------")
    print(SinoptikProvider.find_provider(location_name="Велико Търново"))
