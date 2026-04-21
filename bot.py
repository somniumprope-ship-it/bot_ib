import html
import logging
import os

import access
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, TelegramAPIError
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в .env")

# Confluence: раздел «ИБ в лицах» — название и ссылка (в .env: CONFLUENCE_IB_FACES_SECTION, CONFLUENCE_IB_FACES_URL)
CONFLUENCE_IB_FACES_URL = os.getenv("CONFLUENCE_IB_FACES_URL", "").strip()
CONFLUENCE_IB_FACES_SECTION = os.getenv("CONFLUENCE_IB_FACES_SECTION", "ИБ в лицах").strip()


def _about_faces_text() -> str:
    intro = (
        "В этом разделе можно познакомиться с командой ИБ, ее ролями и зонами "
        "ответственности.\n\n"
        "Найти информацию можно в разделе Confluence: "
    )
    if CONFLUENCE_IB_FACES_URL:
        return (
            intro
            + f'<a href="{CONFLUENCE_IB_FACES_URL}">{CONFLUENCE_IB_FACES_SECTION}</a>'
        )
    return intro + CONFLUENCE_IB_FACES_SECTION


ABOUT_FACES_TEXT = _about_faces_text()

# Confluence: онбординг «новый сотрудник» (CONFLUENCE_ONBOARDING_EMPLOYEE_SECTION, CONFLUENCE_ONBOARDING_EMPLOYEE_URL)
CONFLUENCE_ONBOARDING_EMPLOYEE_URL = os.getenv("CONFLUENCE_ONBOARDING_EMPLOYEE_URL", "").strip()
CONFLUENCE_ONBOARDING_EMPLOYEE_SECTION = os.getenv(
    "CONFLUENCE_ONBOARDING_EMPLOYEE_SECTION",
    "Онбординг нового сотрудника",
).strip()


def _about_onboarding_employee_self_text() -> str:
    intro = (
        "Здесь можно найти инструкции, обязательные материалы и полезные памятки "
        "для старта.\n\n"
        "Найти информацию можно в разделе Confluence: "
    )
    if CONFLUENCE_ONBOARDING_EMPLOYEE_URL:
        return (
            intro
            + f'<a href="{CONFLUENCE_ONBOARDING_EMPLOYEE_URL}">'
            f"{CONFLUENCE_ONBOARDING_EMPLOYEE_SECTION}</a>"
        )
    return intro + CONFLUENCE_ONBOARDING_EMPLOYEE_SECTION


ABOUT_ONBOARDING_EMPLOYEE_SELF_TEXT = _about_onboarding_employee_self_text()

# Confluence: онбординг для руководителя (CONFLUENCE_ONBOARDING_MANAGER_SECTION, CONFLUENCE_ONBOARDING_MANAGER_URL)
CONFLUENCE_ONBOARDING_MANAGER_URL = os.getenv("CONFLUENCE_ONBOARDING_MANAGER_URL", "").strip()
CONFLUENCE_ONBOARDING_MANAGER_SECTION = os.getenv(
    "CONFLUENCE_ONBOARDING_MANAGER_SECTION",
    "Онбординг для руководителей",
).strip()


def _about_onboarding_manager_text() -> str:
    intro = (
        "Здесь собраны материалы для руководителей: что важно рассказать сотруднику, "
        "какие доступы проверить и какие обучения назначить.\n\n"
        "Найти информацию можно в разделе Confluence: "
    )
    if CONFLUENCE_ONBOARDING_MANAGER_URL:
        return (
            intro
            + f'<a href="{CONFLUENCE_ONBOARDING_MANAGER_URL}">'
            f"{CONFLUENCE_ONBOARDING_MANAGER_SECTION}</a>."
        )
    return intro + CONFLUENCE_ONBOARDING_MANAGER_SECTION + "."


ABOUT_ONBOARDING_MANAGER_TEXT = _about_onboarding_manager_text()

# Confluence: поиск учебного материала (CONFLUENCE_MATERIALS_SECTION, CONFLUENCE_MATERIALS_URL)
CONFLUENCE_MATERIALS_URL = os.getenv("CONFLUENCE_MATERIALS_URL", "").strip()
CONFLUENCE_MATERIALS_SECTION = os.getenv(
    "CONFLUENCE_MATERIALS_SECTION",
    "Учебные материалы по ИБ",
).strip()


def _about_material_search_text() -> str:
    intro = (
        "Здесь можно найти обучающие материалы по основным темам информационной "
        "безопасности.\n\n"
        "Раздел подойдет, если вы хотите разобраться в теме глубже или освежить "
        "знания.\n\n"
        "Найти информацию можно в разделе Confluence: "
    )
    if CONFLUENCE_MATERIALS_URL:
        return (
            intro
            + f'<a href="{CONFLUENCE_MATERIALS_URL}">{CONFLUENCE_MATERIALS_SECTION}</a>.'
        )
    return intro + CONFLUENCE_MATERIALS_SECTION + "."


ABOUT_MATERIAL_SEARCH_TEXT = _about_material_search_text()


def _material_subpage_text(
    body: str,
    section_env: str,
    url_env: str,
    default_section: str,
) -> str:
    """Три абзаца пользователя + строка Confluence (раздел и ссылка из .env)."""
    section = os.getenv(section_env, default_section).strip()
    url = os.getenv(url_env, "").strip()
    tail = "\n\nНайти информацию можно в разделе Confluence: "
    if url:
        return body.rstrip() + tail + f'<a href="{url}">{section}</a>.'
    return body.rstrip() + tail + section + "."


ABOUT_MATERIAL_GLOSSARY_TEXT = _material_subpage_text(
    (
        "Здесь собраны основные термины и сокращения, которые используются во внутренней "
        "документации по ИБ.\n\n"
        "Это поможет быстрее ориентироваться в материалах и понимать единый язык команды."
    ),
    "CONFLUENCE_MATERIAL_GLOSSARY_SECTION",
    "CONFLUENCE_MATERIAL_GLOSSARY_URL",
    "Глоссарий",
)

ABOUT_MATERIAL_WEBINARS_TEXT = _material_subpage_text(
    (
        "В этом разделе собраны записи вебинаров и встреч по темам ИБ.\n\n"
        "Здесь удобно посмотреть материалы в своем темпе и вернуться к важным темам позже."
    ),
    "CONFLUENCE_MATERIAL_WEBINARS_SECTION",
    "CONFLUENCE_MATERIAL_WEBINARS_URL",
    "Записи вебинаров",
)

ABOUT_MATERIAL_MEMOS_TEXT = _material_subpage_text(
    (
        "Здесь собраны короткие памятки с основными правилами и полезными рекомендациями "
        "по ИБ.\n\n"
        "Это быстрый способ вспомнить главное без чтения длинных инструкций."
    ),
    "CONFLUENCE_MATERIAL_MEMOS_SECTION",
    "CONFLUENCE_MATERIAL_MEMOS_URL",
    "Памятки",
)

ABOUT_MATERIAL_CASES_TEXT = _material_subpage_text(
    (
        "В этом разделе собраны практические кейсы и примеры ситуаций, связанных с ИБ.\n\n"
        "Они помогают понять, как правила работают в реальных рабочих сценариях."
    ),
    "CONFLUENCE_MATERIAL_CASES_SECTION",
    "CONFLUENCE_MATERIAL_CASES_URL",
    "Кейсы",
)

ABOUT_MATERIAL_COMICS_TEXT = _material_subpage_text(
    (
        "Здесь собраны наглядные материалы и комиксы по темам информационной "
        "безопасности.\n\n"
        "Такой формат помогает проще и быстрее запомнить важные правила."
    ),
    "CONFLUENCE_MATERIAL_COMICS_SECTION",
    "CONFLUENCE_MATERIAL_COMICS_URL",
    "Комиксы",
)

ABOUT_MATERIAL_QUIZZES_TEXT = _material_subpage_text(
    (
        "В этом разделе можно пройти квизы и викторины по темам ИБ и проверить свои "
        "знания.\n\n"
        "Это хороший способ закрепить материал в легком и понятном формате."
    ),
    "CONFLUENCE_MATERIAL_QUIZZES_SECTION",
    "CONFLUENCE_MATERIAL_QUIZZES_URL",
    "Квизы / викторины",
)

ABOUT_MATERIAL_INFOGRAPHICS_TEXT = _material_subpage_text(
    (
        "Здесь собрана инфографика с основными правилами, схемами и короткими пояснениями "
        "по ИБ.\n\n"
        "Раздел удобен, когда нужно быстро понять суть темы с первого взгляда."
    ),
    "CONFLUENCE_MATERIAL_INFOGRAPHICS_SECTION",
    "CONFLUENCE_MATERIAL_INFOGRAPHICS_URL",
    "Инфографика",
)


def _confluence_block_after_body(
    body: str,
    confluence_intro: str,
    section_env: str,
    url_env: str,
    default_section: str,
) -> str:
    """Текст + строка про Confluence с произвольной формулировкой перед ссылкой."""
    section = os.getenv(section_env, default_section).strip()
    url = os.getenv(url_env, "").strip()
    block = body.rstrip() + "\n\n" + confluence_intro
    if url:
        return block + f'<a href="{url}">{section}</a>.'
    return block + section + "."


REPORT_INCIDENT_SUBMIT_TEXT = _confluence_block_after_body(
    "Если произошел инцидент или вы заметили подозрительную ситуацию, важно сразу "
    "сообщить об этом ответственным контактным лицам.",
    "Их контакты и зоны ответственности можно найти в разделе Confluence: ",
    "CONFLUENCE_REPORT_INCIDENT_SUBMIT_SECTION",
    "CONFLUENCE_REPORT_INCIDENT_SUBMIT_URL",
    "Контакты при инциденте",
)

REPORT_INCIDENT_PHISHING_TEXT = _confluence_block_after_body(
    "Если вы получили подозрительное письмо, не переходите по ссылкам и не открывайте "
    "вложения.",
    "Сразу сообщите об этом ответственным лицам — контакты и инструкция доступны в Confluence: ",
    "CONFLUENCE_INCIDENT_PHISHING_SECTION",
    "CONFLUENCE_INCIDENT_PHISHING_URL",
    "Фишинговое письмо",
)

REPORT_INCIDENT_LOST_LAPTOP_TEXT = _confluence_block_after_body(
    "Если вы потеряли ноутбук или другое рабочее устройство, важно немедленно сообщить "
    "об этом по установленному каналу.",
    "Инструкцию и контакты ответственных можно найти в Confluence: ",
    "CONFLUENCE_INCIDENT_LOST_LAPTOP_SECTION",
    "CONFLUENCE_INCIDENT_LOST_LAPTOP_URL",
    "Потеря ноутбука",
)

REPORT_INCIDENT_MISDELIVERY_TEXT = _confluence_block_after_body(
    "Если информация была отправлена не тому получателю, не ждите, что ситуация "
    "решится сама.",
    "Чем быстрее вы сообщите об этом, тем проще снизить риски — инструкция и контакты "
    "есть в Confluence: ",
    "CONFLUENCE_INCIDENT_MISDELIVERY_SECTION",
    "CONFLUENCE_INCIDENT_MISDELIVERY_URL",
    "Отправка данных не туда",
)

REPORT_INCIDENT_SUSPICIOUS_LINK_TEXT = _confluence_block_after_body(
    "Если вы открыли подозрительную ссылку или страницу, важно сразу сообщить об этом, "
    "даже если на первый взгляд ничего не произошло.",
    "Найти дальнейшие действия и контакты можно в Confluence: ",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_LINK_SECTION",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_LINK_URL",
    "Подозрительная ссылка",
)

REPORT_INCIDENT_SUSPICIOUS_ATTACHMENT_TEXT = _confluence_block_after_body(
    "Если вы открыли вложение из сомнительного письма, не предпринимайте "
    "самостоятельных действий и сразу сообщите об инциденте.",
    "Инструкция и контакты ответственных размещены в Confluence: ",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_ATTACHMENT_SECTION",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_ATTACHMENT_URL",
    "Подозрительное вложение",
)

REPORT_INCIDENT_INFECTED_DEVICE_TEXT = _confluence_block_after_body(
    "Если устройство начало вести себя необычно: появились ошибки, всплывающие окна, "
    "зависания или неизвестные программы, сообщите об этом как можно скорее.",
    "Порядок действий и контакты ответственных есть в Confluence: ",
    "CONFLUENCE_INCIDENT_INFECTED_DEVICE_SECTION",
    "CONFLUENCE_INCIDENT_INFECTED_DEVICE_URL",
    "Заражение устройства",
)

REPORT_INCIDENT_LOST_MEDIA_TEXT = _confluence_block_after_body(
    "Если вы потеряли рабочий телефон, токен, пропуск или носитель информации, важно "
    "сразу сообщить об этом ответственным лицам.",
    "Инструкция по дальнейшим действиям размещена в Confluence: ",
    "CONFLUENCE_INCIDENT_LOST_MEDIA_SECTION",
    "CONFLUENCE_INCIDENT_LOST_MEDIA_URL",
    "Утеря телефона / токена / носителя",
)

REPORT_INCIDENT_COMPROMISED_ACCOUNT_TEXT = _confluence_block_after_body(
    "Если вы заметили подозрительную активность в своей учетной записи или думаете, "
    "что доступ мог получить кто-то другой, немедленно сообщите об этом.",
    "Контакты и инструкция доступны в Confluence: ",
    "CONFLUENCE_INCIDENT_COMPROMISED_ACCOUNT_SECTION",
    "CONFLUENCE_INCIDENT_COMPROMISED_ACCOUNT_URL",
    "Компрометация учётной записи",
)

REPORT_INCIDENT_SHARED_PASSWORD_TEXT = _confluence_block_after_body(
    "Если вы передали пароль, код из СМС или другой служебный доступ третьим лицам, "
    "важно сразу сообщить об этом.\n\n"
    "Чем раньше об этом узнают ответственные, тем быстрее можно снизить риски.",
    "Контакты и инструкция доступны в Confluence: ",
    "CONFLUENCE_INCIDENT_SHARED_PASSWORD_SECTION",
    "CONFLUENCE_INCIDENT_SHARED_PASSWORD_URL",
    "Утечка пароля или кода",
)

REPORT_INCIDENT_SUSPICIOUS_ACTIVITY_TEXT = _confluence_block_after_body(
    "Если вы заметили что-то необычное в системе, письмах, файлах или доступах, лучше "
    "сообщить об этом сразу.\n\n"
    "Даже если тревога окажется ложной, это безопаснее, чем промолчать.",
    "Контакты и инструкция доступны в Confluence: ",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_ACTIVITY_SECTION",
    "CONFLUENCE_INCIDENT_SUSPICIOUS_ACTIVITY_URL",
    "Подозрительная активность",
)

REPORT_INCIDENT_DATA_EXPOSED_TEXT = _confluence_block_after_body(
    "Если вы заметили, что доступ к файлу, папке или данным получили лишние сотрудники "
    "или внешние пользователи, сообщите об этом немедленно.",
    "Инструкция и контакты ответственных есть в Confluence: ",
    "CONFLUENCE_INCIDENT_DATA_EXPOSED_SECTION",
    "CONFLUENCE_INCIDENT_DATA_EXPOSED_URL",
    "Доступ к данным не тем людям",
)

REPORT_INCIDENT_POLICY_VIOLATION_TEXT = _confluence_block_after_body(
    "Если вы заметили нарушение требований ИБ, не игнорируйте ситуацию.\n\n"
    "Сообщение о таком случае помогает вовремя снизить риски для сотрудника и компании.",
    "Инструкция и контакты ответственных есть в Confluence: ",
    "CONFLUENCE_INCIDENT_POLICY_VIOLATION_SECTION",
    "CONFLUENCE_INCIDENT_POLICY_VIOLATION_URL",
    "Нарушение правил ИБ",
)

# Анонимная форма обратной связи (корпоративный портал)
IB_FEEDBACK_FORM_URL = os.getenv("IB_FEEDBACK_FORM_URL", "").strip()


def _report_feedback_text() -> str:
    p2 = (
        "Нам важно становиться лучше, поэтому мы внимательно относимся к обратной связи "
        "и гарантируем, что ваши персональные данные не будут переданы."
    )
    intro = (
        "Оставить комментарий о работе направления ИБ можно через анонимную форму на "
        "корпоративном портале: "
    )
    if IB_FEEDBACK_FORM_URL:
        return intro + f'<a href="{IB_FEEDBACK_FORM_URL}">ссылка</a>.\n\n' + p2
    return intro + "ссылка.\n\n" + p2


def _report_feedback_hr_text() -> str:
    p2 = "Все обращения рассматриваются бережно и конфиденциально."
    intro = (
        "Если вы хотите деликатно поднять вопрос или поделиться обратной связью, "
        "воспользуйтесь анонимной формой на корпоративном портале: "
    )
    if IB_FEEDBACK_FORM_URL:
        return intro + f'<a href="{IB_FEEDBACK_FORM_URL}">ссылка</a>.\n\n' + p2
    return intro + "ссылка.\n\n" + p2


REPORT_FEEDBACK_TEXT = _report_feedback_text()
REPORT_FEEDBACK_HR_TEXT = _report_feedback_hr_text()

FIND_CONTACT_MAIN_TEXT = (
    "Здесь можно найти, к кому обратиться по вашему вопросу.\n"
    "Например, уточнить информацию про инциденты, онбординг адаптация сотрудников, "
    "обучение, управление доступами, защиту информации, передачу файлов и многое другое.\n\n"
    "Какой у вас вопрос?\n\n"
    "<b>Инциденты ИБ</b> — если произошло подозрительное событие, утечка, потеря устройства, "
    "фишинг или иная нештатная ситуация\n\n"
    "<b>Онбординг Адаптация сотрудников</b> — если сотруднику или руководителю нужны вводные "
    "материалы и обязательные шаги\n\n"
    "<b>Обучение</b> — если есть вопросы по прохождению или назначению обучения\n\n"
    "<b>Управление доступами</b> — если нужно оформить, изменить или отозвать доступ\n\n"
    "<b>Защита информации</b> — если вопрос связан с передачей файлов, хранением данных и "
    "безопасной работой с информацией\n\n"
    "<b>Электронная подпись</b> — если вопрос связан с использованием ЭП"
)

FIND_CONTACT_TEAM_TEXT = _material_subpage_text(
    "В этом разделе собраны контакты команды ИБ и распределение зон ответственности.",
    "CONFLUENCE_FIND_CONTACT_TEAM_SECTION",
    "CONFLUENCE_FIND_CONTACT_TEAM_URL",
    "Контакты команды и зона ответственности",
)

# Поиск инструкции → Бизнес подразделения
FIND_INSTR_BIZ_TRAINING_TEXT = _material_subpage_text(
    "Здесь можно узнать, как пройти обязательное обучение по ИБ или назначить его "
    "сотруднику.",
    "CONFLUENCE_FIND_INSTR_BIZ_TRAINING_SECTION",
    "CONFLUENCE_FIND_INSTR_BIZ_TRAINING_URL",
    "Обучение (бизнес)",
)

FIND_INSTR_BIZ_ACCESS_TEXT = _material_subpage_text(
    "Здесь собраны инструкции по запросу, изменению и отзыву доступов.",
    "CONFLUENCE_FIND_INSTR_BIZ_ACCESS_SECTION",
    "CONFLUENCE_FIND_INSTR_BIZ_ACCESS_URL",
    "Управление доступами (бизнес)",
)

FIND_INSTR_BIZ_INFOPROT_TEXT = _material_subpage_text(
    "Здесь можно найти правила и инструкции по безопасной передаче файлов и защите "
    "информации.",
    "CONFLUENCE_FIND_INSTR_BIZ_INFOPROT_SECTION",
    "CONFLUENCE_FIND_INSTR_BIZ_INFOPROT_URL",
    "Защита информации (бизнес)",
)

FIND_INSTR_BIZ_ESIGN_TEXT = _material_subpage_text(
    "В этом разделе собраны материалы по использованию электронной подписи и связанным "
    "требованиям ИБ.",
    "CONFLUENCE_FIND_INSTR_BIZ_ESIGN_SECTION",
    "CONFLUENCE_FIND_INSTR_BIZ_ESIGN_URL",
    "Электронная подпись (бизнес)",
)

# Поиск инструкции → ИТ подразделения
FIND_INSTR_IT_NEW_SW_TEXT = _material_subpage_text(
    "Здесь можно узнать, как действовать при внедрении нового ПО, кого нужно поставить "
    "в известность и в каких случаях требуется согласование с ИБ.",
    "CONFLUENCE_FIND_INSTR_IT_NEW_SW_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_NEW_SW_URL",
    "Внедрение нового ПО",
)

FIND_INSTR_IT_DO_DONT_TEXT = _material_subpage_text(
    "Здесь собраны базовые критерии и правила, которые помогают понять, какие действия "
    "допустимы, а какие требуют согласования или запрещены.",
    "CONFLUENCE_FIND_INSTR_IT_DO_DONT_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_DO_DONT_URL",
    "Что можно и нельзя в ИТ (ИБ)",
)

FIND_INSTR_IT_ACCESS_PRIV_TEXT = _material_subpage_text(
    "Здесь можно найти инструкции по выдаче, изменению и отзыву доступов, а также по "
    "работе с привилегированными учетными записями.",
    "CONFLUENCE_FIND_INSTR_IT_ACCESS_PRIV_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_ACCESS_PRIV_URL",
    "Управление доступами и привилегиями",
)

FIND_INSTR_IT_INFRA_TEXT = _material_subpage_text(
    "В этом разделе собраны требования к изменениям в инфраструктуре: настройке "
    "сервисов, сетевых взаимодействий, хостов, серверов и других технических компонентов.",
    "CONFLUENCE_FIND_INSTR_IT_INFRA_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_INFRA_URL",
    "Изменения в инфраструктуре",
)

FIND_INSTR_IT_EXTERNAL_TEXT = _material_subpage_text(
    "Здесь можно узнать, в каких случаях допустимо использовать внешние сервисы, API, "
    "SaaS-решения и сторонние интеграции, а когда требуется отдельное согласование.",
    "CONFLUENCE_FIND_INSTR_IT_EXTERNAL_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_EXTERNAL_URL",
    "Внешние сервисы и интеграции",
)

FIND_INSTR_IT_DATA_ENV_TEXT = _material_subpage_text(
    "В этом разделе собраны правила работы с данными в разных средах, включая "
    "ограничения на использование продуктивных данных в тестировании и разработке.",
    "CONFLUENCE_FIND_INSTR_IT_DATA_ENV_SECTION",
    "CONFLUENCE_FIND_INSTR_IT_DATA_ENV_URL",
    "Данные в тестовых и продуктивных средах",
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

PENDING_ACCESS_TEXT = (
    "Ваша заявка на доступ к боту рассматривается.\n\n"
    "Когда доступ будет подтверждён, вы получите сообщение и сможете пользоваться "
    "всеми разделами. Обычно это занимает немного времени."
)


async def _notify_admins_new_request(user: types.User) -> None:
    safe_name = html.escape(user.full_name or "")
    line = (
        "Новая заявка на доступ к боту\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Имя: {safe_name}\n"
        f"Username: @{user.username or '—'}\n\n"
        f"Одобрить: <code>/approve {user.id}</code>"
    )
    for admin_id in access.admin_user_ids():
        try:
            await bot.send_message(admin_id, line, parse_mode="HTML")
        except Exception:
            logging.exception("Не удалось отправить уведомление админу %s", admin_id)


DIALOG = {
    # ========= ПРИВЕТСТВИЕ =========
    "root": {
        "text": (
            "Вас приветствует чат-бот направления ИБ ЦКР. Мы всегда готовы помочь "
            "с вопросами по информационной безопасности. Выберите, что вас интересует."
        ),
        "buttons": [
            ("Познакомиться с направлением ИБ", "about"),
            ("Сообщить о чём-то", "report"),
            ("Найти что-то", "find"),
            ("✈️ Телеграм канал", "news"),
        ],
        "parent": None,
    },

    # ========= РАЗДЕЛЫ (пока заглушки — наполним заново) =========
    "about": {
        "text": (
            "Здесь можно узнать, чем занимается направление ИБ в ЦКР, какие задачи "
            "решает команда и по каким вопросам можно обращаться.\n"
            "Что именно вас интересует?"
        ),
        "buttons": [
            ("Новости ИБ в компании", "about_news_ib"),
            ("ИБ в лицах", "about_faces"),
            ("Онбординг сотрудника", "about_onboarding"),
            ("Поиск учебного материала", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "root",
    },

    "about_news_ib": {
        "text": (
            "Здесь публикуются новости направления ИБ, обновления процессов и важные "
            "изменения.\n\n"
            "Чтобы ничего не пропустить, подпишитесь на канал: "
            '<a href="https://t.me/ib_ckr_bot">Просто об ИБ</a>'
        ),
        "buttons": [
            ("Назад", "about"),
            ("В начало", "root"),
        ],
        "parent": "about",
    },

    "about_faces": {
        "text": ABOUT_FACES_TEXT,
        "buttons": [
            ("Назад", "about"),
            ("В начало", "root"),
        ],
        "parent": "about",
    },

    "about_onboarding": {
        "text": (
            "Здесь собраны материалы, которые помогут быстро разобраться в основных "
            "требованиях ИБ.\n\n"
            "Выберите подходящий сценарий: для нового сотрудника или для руководителя."
        ),
        "buttons": [
            (
                "Я новый сотрудник, хочу сам ознакомиться с инструкциями",
                "about_onboarding_employee_self",
            ),
            (
                "Я руководитель, хочу онбордить своего сотрудника",
                "about_onboarding_manager",
            ),
            ("Назад", "about"),
            ("В начало", "root"),
        ],
        "parent": "about",
    },

    "about_onboarding_employee_self": {
        "text": ABOUT_ONBOARDING_EMPLOYEE_SELF_TEXT,
        "buttons": [
            ("Назад", "about_onboarding"),
            ("В начало", "root"),
        ],
        "parent": "about_onboarding",
    },

    "about_onboarding_manager": {
        "text": ABOUT_ONBOARDING_MANAGER_TEXT,
        "buttons": [
            ("Назад", "about_onboarding"),
            ("В начало", "root"),
        ],
        "parent": "about_onboarding",
    },

    "about_material_search": {
        "text": ABOUT_MATERIAL_SEARCH_TEXT,
        "buttons": [
            ("Глоссарий", "about_material_glossary"),
            ("Записи вебинаров", "about_material_webinars"),
            ("Памятки", "about_material_memos"),
            ("Кейсы", "about_material_cases"),
            ("Комиксы", "about_material_comics"),
            ("Квизы / викторины", "about_material_quizzes"),
            ("Инфографика", "about_material_infographics"),
            ("Назад", "about"),
            ("В начало", "root"),
        ],
        "parent": "about",
    },

    "about_material_glossary": {
        "text": ABOUT_MATERIAL_GLOSSARY_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_webinars": {
        "text": ABOUT_MATERIAL_WEBINARS_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_memos": {
        "text": ABOUT_MATERIAL_MEMOS_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_cases": {
        "text": ABOUT_MATERIAL_CASES_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_comics": {
        "text": ABOUT_MATERIAL_COMICS_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_quizzes": {
        "text": ABOUT_MATERIAL_QUIZZES_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "about_material_infographics": {
        "text": ABOUT_MATERIAL_INFOGRAPHICS_TEXT,
        "buttons": [
            ("Назад", "about_material_search"),
            ("В начало", "root"),
        ],
        "parent": "about_material_search",
    },

    "report": {
        "text": (
            "Если вы хотите сообщить о риске или инциденте, контакты ответственных лиц "
            "в направлении ИБ можно найти в этом разделе.\n\n"
            "Не бойтесь сообщать о ситуации: чем раньше мы узнаем, тем быстрее сможем "
            "помочь и снизить риски."
        ),
        "buttons": [
            ("Об инциденте", "report_incident"),
            ("Оставить комментарий о работе ИБ", "report_feedback"),
            ("В начало", "root"),
        ],
        "parent": "root",
    },

    "report_incident": {
        "text": (
            "Не бойтесь сообщать об инциденте: чем раньше мы узнаем о ситуации, тем "
            "быстрее сможем помочь и снизить риски.\n\n"
            "Хуже — не сообщить и потерять время."
        ),
        "buttons": [
            ("Хочу сообщить об инциденте", "report_incident_submit"),
            (
                "Хочу найти инструкцию, как действовать в случае инцидента",
                "report_incident_instruction",
            ),
            ("Хочу узнать о видах инцидентов", "report_incident_types"),
            (
                "Хочу узнать о возможных последствиях инцидента",
                "report_incident_consequences",
            ),
            ("Назад", "report"),
            ("В начало", "root"),
        ],
        "parent": "report",
    },

    "report_incident_submit": {
        "text": REPORT_INCIDENT_SUBMIT_TEXT,
        "buttons": [
            ("Назад", "report_incident"),
            ("В начало", "root"),
        ],
        "parent": "report_incident",
    },

    "report_incident_instruction": {
        "text": (
            "Здесь собраны инструкции для самых частых инцидентов ИБ.\n\n"
            "Выберите ситуацию, и я подскажу, где найти нужный порядок действий."
        ),
        "buttons": [
            ("Фишинговое письмо", "report_incident_phishing"),
            ("Потерял ноутбук", "report_incident_lost_laptop"),
            ("Случайно отправил данные не туда", "report_incident_misdelivery"),
            ("Перешел по подозрительной ссылке", "report_incident_suspicious_link"),
            ("Открыл подозрительное вложение", "report_incident_suspicious_attachment"),
            ("Подозрение на заражение устройства", "report_incident_infected_device"),
            ("Утеря телефона / токена / носителя", "report_incident_lost_media"),
            ("Подозрение на компрометацию учетной записи", "report_incident_compromised_account"),
            ("Сообщил пароль или код подтверждения", "report_incident_shared_password"),
            ("Обнаружил подозрительную активность", "report_incident_suspicious_activity"),
            ("Документ или данные стали доступны не тем людям", "report_incident_data_exposed"),
            ("Нарушение правил ИБ", "report_incident_policy_violation"),
            ("Назад", "report_incident"),
            ("В начало", "root"),
        ],
        "parent": "report_incident",
    },

    "report_incident_types": {
        "text": "Раздел «Виды инцидентов» пока в разработке.",
        "buttons": [
            ("Назад", "report_incident"),
            ("В начало", "root"),
        ],
        "parent": "report_incident",
    },

    "report_incident_consequences": {
        "text": "Раздел «Возможные последствия инцидента» пока в разработке.",
        "buttons": [
            ("Назад", "report_incident"),
            ("В начало", "root"),
        ],
        "parent": "report_incident",
    },

    "report_incident_phishing": {
        "text": REPORT_INCIDENT_PHISHING_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_lost_laptop": {
        "text": REPORT_INCIDENT_LOST_LAPTOP_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_misdelivery": {
        "text": REPORT_INCIDENT_MISDELIVERY_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_suspicious_link": {
        "text": REPORT_INCIDENT_SUSPICIOUS_LINK_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_suspicious_attachment": {
        "text": REPORT_INCIDENT_SUSPICIOUS_ATTACHMENT_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_infected_device": {
        "text": REPORT_INCIDENT_INFECTED_DEVICE_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_lost_media": {
        "text": REPORT_INCIDENT_LOST_MEDIA_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_compromised_account": {
        "text": REPORT_INCIDENT_COMPROMISED_ACCOUNT_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_shared_password": {
        "text": REPORT_INCIDENT_SHARED_PASSWORD_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_suspicious_activity": {
        "text": REPORT_INCIDENT_SUSPICIOUS_ACTIVITY_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_data_exposed": {
        "text": REPORT_INCIDENT_DATA_EXPOSED_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_incident_policy_violation": {
        "text": REPORT_INCIDENT_POLICY_VIOLATION_TEXT,
        "buttons": [
            ("Назад", "report_incident_instruction"),
            ("В начало", "root"),
        ],
        "parent": "report_incident_instruction",
    },

    "report_feedback": {
        "text": REPORT_FEEDBACK_TEXT,
        "buttons": [
            ("Анонимная форма - обсудить с HR", "report_feedback_hr"),
            ("Назад", "report"),
            ("В начало", "root"),
        ],
        "parent": "report",
    },

    "report_feedback_hr": {
        "text": REPORT_FEEDBACK_HR_TEXT,
        "buttons": [
            ("Назад", "report_feedback"),
            ("В начало", "root"),
        ],
        "parent": "report_feedback",
    },

    "find": {
        "text": (
            "Я помогу быстро найти нужный материал, инструкцию, контакт или обучающий "
            "контент по ИБ. Выберите тему, и я подскажу, где находится нужная "
            "информация."
        ),
        "buttons": [
            ("Поиск учебного материала", "about_material_search"),
            ("Поиск инструкции", "find_instruction"),
            ("Поиск контактного лица", "find_contact"),
            ("FAQ", "find_faq"),
            ("В начало", "root"),
        ],
        "parent": "root",
    },

    "find_instruction": {
        "text": (
            "Пожалуйста, выберите, к какому подразделению вы относитесь: Бизнес или ИТ.\n\n"
            "Это поможет показать инструкции, актуальные именно для вашей роли."
        ),
        "buttons": [
            ("Бизнес подразделения", "find_instruction_business"),
            ("ИТ подразделения", "find_instruction_it"),
            ("Работаете с другими организациями", "find_instruction_external_orgs"),
            ("Работаете с внутренними сотрудниками", "find_instruction_internal_staff"),
            ("Назад", "find"),
            ("В начало", "root"),
        ],
        "parent": "find",
    },

    "find_instruction_business": {
        "text": (
            "Выберите тему — мы подскажем, где найти инструкции для бизнес-подразделений."
        ),
        "buttons": [
            (
                "Обучение - как пройти, как назначить",
                "find_instruction_business_training",
            ),
            ("Управление доступами", "find_instruction_business_access"),
            ("Защита информации", "find_instruction_business_infoprotection"),
            ("Электронная подпись", "find_instruction_business_esign"),
            ("Инциденты", "report_incident"),
            ("Назад", "find_instruction"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction",
    },

    "find_instruction_business_training": {
        "text": FIND_INSTR_BIZ_TRAINING_TEXT,
        "buttons": [
            ("Назад", "find_instruction_business"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_business",
    },

    "find_instruction_business_access": {
        "text": FIND_INSTR_BIZ_ACCESS_TEXT,
        "buttons": [
            ("Назад", "find_instruction_business"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_business",
    },

    "find_instruction_business_infoprotection": {
        "text": FIND_INSTR_BIZ_INFOPROT_TEXT,
        "buttons": [
            ("Назад", "find_instruction_business"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_business",
    },

    "find_instruction_business_esign": {
        "text": FIND_INSTR_BIZ_ESIGN_TEXT,
        "buttons": [
            ("Назад", "find_instruction_business"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_business",
    },

    "find_instruction_it": {
        "text": (
            "Выберите тему — мы подскажем, где найти инструкции для ИТ-подразделений."
        ),
        "buttons": [
            ("Внедрение нового ПО", "find_instruction_it_new_software"),
            (
                "Что можно, а что нельзя делать в ИТ с точки зрения ИБ",
                "find_instruction_it_do_dont",
            ),
            (
                "Управление доступами и привилегиями",
                "find_instruction_it_access_privileges",
            ),
            ("Изменения в инфраструктуре", "find_instruction_it_infrastructure"),
            (
                "Использование внешних сервисов и интеграций",
                "find_instruction_it_external_services",
            ),
            (
                "Работа с данными в тестовых и продуктивных средах",
                "find_instruction_it_data_environments",
            ),
            ("Назад", "find_instruction"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction",
    },

    "find_instruction_it_new_software": {
        "text": FIND_INSTR_IT_NEW_SW_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_it_do_dont": {
        "text": FIND_INSTR_IT_DO_DONT_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_it_access_privileges": {
        "text": FIND_INSTR_IT_ACCESS_PRIV_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_it_infrastructure": {
        "text": FIND_INSTR_IT_INFRA_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_it_external_services": {
        "text": FIND_INSTR_IT_EXTERNAL_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_it_data_environments": {
        "text": FIND_INSTR_IT_DATA_ENV_TEXT,
        "buttons": [
            ("Назад", "find_instruction_it"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction_it",
    },

    "find_instruction_external_orgs": {
        "text": "Раздел «Работаете с другими организациями» пока в разработке.",
        "buttons": [
            ("Назад", "find_instruction"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction",
    },

    "find_instruction_internal_staff": {
        "text": "Раздел «Работаете с внутренними сотрудниками» пока в разработке.",
        "buttons": [
            ("Назад", "find_instruction"),
            ("В начало", "root"),
        ],
        "parent": "find_instruction",
    },

    "find_contact": {
        "text": FIND_CONTACT_MAIN_TEXT,
        "buttons": [
            ("Инциденты ИБ", "find_contact_incidents"),
            ("Онбординг Адаптация сотрудников", "find_contact_onboarding"),
            ("Обучение", "find_contact_training"),
            ("Управление доступами", "find_contact_access"),
            ("Защита информации", "find_contact_infoprotection"),
            ("Электронная подпись", "find_contact_esign"),
            ("📓 Контакты команды и зона ответственности", "find_contact_team"),
            ("Назад", "find"),
            ("В начало", "root"),
        ],
        "parent": "find",
    },

    "find_contact_incidents": {
        "text": "Раздел «Инциденты ИБ» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_onboarding": {
        "text": "Раздел «Онбординг Адаптация сотрудников» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_training": {
        "text": "Раздел «Обучение» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_access": {
        "text": "Раздел «Управление доступами» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_infoprotection": {
        "text": "Раздел «Защита информации» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_esign": {
        "text": "Раздел «Электронная подпись» пока в разработке.",
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_contact_team": {
        "text": FIND_CONTACT_TEAM_TEXT,
        "buttons": [
            ("Назад", "find_contact"),
            ("В начало", "root"),
        ],
        "parent": "find_contact",
    },

    "find_faq": {
        "text": "Раздел «FAQ» пока в разработке.",
        "buttons": [
            ("Назад", "find"),
            ("В начало", "root"),
        ],
        "parent": "find",
    },

    "news": {
        "text": (
            "Короткие публикации на актуальные темы по ИБ, анонсы предстоящих "
            "мероприятий, видео-фрагменты вебинаров и другой развлекательный контент "
            "вы можете найти в нашем "
            '<a href="https://t.me/ib_ckr_bot">телеграм-канале «Просто об ИБ»</a>'
        ),
        "buttons": [
            ("В начало", "root"),
        ],
        "parent": "root",
    },
}


def build_keyboard(node_key: str) -> InlineKeyboardMarkup:
    node = DIALOG[node_key]
    kb = InlineKeyboardMarkup(row_width=1)

    for text, target in node["buttons"]:
        btn = InlineKeyboardButton(text=text, callback_data=f"goto:{target}")
        kb.row(btn)

    return kb


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    if access.access_gate_enabled() and not access.user_has_access(uid):
        # Сначала ответ пользователю — чтобы заявка не «зависла», если уведомление админам упало
        await message.answer(PENDING_ACCESS_TEXT)
        try:
            if access.register_pending(uid):
                await _notify_admins_new_request(message.from_user)
        except Exception:
            logging.exception("Ошибка при регистрации заявки или уведомлении админов")
        return

    node_key = "root"
    await message.answer(
        DIALOG[node_key]["text"],
        reply_markup=build_keyboard(node_key),
    )


@dp.message_handler(commands=["approve"])
async def cmd_approve(message: types.Message):
    if not access.is_admin(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(
            "Использование: <code>/approve &lt;user_id&gt;</code>",
            parse_mode="HTML",
        )
        return
    uid = int(parts[1])
    if not access.approve_user(uid):
        await message.answer(
            f"Пользователь <code>{uid}</code> уже имеет доступ.",
            parse_mode="HTML",
        )
        return
    await message.answer(
        f"Доступ выдан пользователю <code>{uid}</code>.",
        parse_mode="HTML",
    )
    try:
        await bot.send_message(
            uid,
            "Вам открыт доступ к боту. Нажмите /start, чтобы открыть меню.",
        )
    except Exception:
        logging.exception("Не удалось уведомить пользователя %s", uid)


@dp.message_handler(commands=["pending"])
async def cmd_pending(message: types.Message):
    if not access.is_admin(message.from_user.id):
        return
    pending = access.list_pending()
    if not pending:
        await message.answer("Ожидающих заявок нет.")
        return
    lines = "\n".join(f"<code>{pid}</code> — /approve {pid}" for pid in pending)
    await message.answer("Ожидают доступа:\n" + lines, parse_mode="HTML")


@dp.message_handler(commands=["revoke"])
async def cmd_revoke(message: types.Message):
    if not access.is_admin(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(
            "Использование: <code>/revoke &lt;user_id&gt;</code>",
            parse_mode="HTML",
        )
        return
    uid = int(parts[1])
    if access.revoke_user(uid):
        await message.answer(
            f"Доступ у пользователя <code>{uid}</code> снят.",
            parse_mode="HTML",
        )
    else:
        await message.answer("Пользователь не был в списке одобренных или ожидающих.")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("goto:"))
async def process_goto(callback_query: types.CallbackQuery):
    if access.access_gate_enabled() and not access.user_has_access(callback_query.from_user.id):
        await callback_query.answer(
            "Разделы станут доступны после одобрения заявки администратором.",
            show_alert=True,
        )
        return

    target = callback_query.data.split(":", 1)[1]

    if target not in DIALOG:
        await callback_query.answer("Раздел ещё в разработке.", show_alert=True)
        return

    node = DIALOG[target]

    try:
        await bot.edit_message_text(
            node["text"],
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=build_keyboard(target),
        )
    except MessageNotModified:
        # Тот же экран нажали повторно — Telegram не меняет сообщение
        pass
    except TelegramAPIError as e:
        logging.exception("Telegram API при смене раздела: %s", e)
        await callback_query.answer(
            "Не удалось открыть раздел. Попробуйте /start.",
            show_alert=True,
        )
        return

    await callback_query.answer()


@dp.errors_handler()
async def global_error_handler(update, exception):
    """Логируем любую ошибку в обработчиках — иначе бот «молчит» без причины в консоли."""
    logging.exception("Ошибка при обработке update: %s", exception)
    return True


if __name__ == "__main__":
    warn = access.approval_config_warning()
    if warn:
        logging.warning(warn)
    executor.start_polling(dp, skip_updates=True)
