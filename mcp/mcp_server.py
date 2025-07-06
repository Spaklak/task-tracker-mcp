import logging
import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Annotated
from pydantic import Field
from schemas import StatusType 

load_dotenv()

mcp = FastMCP(name="MCP Server to work with tasks")
NOTES_SERVICE_NAME=os.getenv("API_SERVICE_NAME")
URL=f"http://{NOTES_SERVICE_NAME}:5252/api/v1/notes"

def setup_logging() -> None:
    """Задает конфиг для логирования"""
    logger = logging.getLogger("server")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    current_file_path = os.path.abspath(__file__)
    current_file_dir = os.path.dirname(current_file_path)
    parent_dir = os.path.dirname(current_file_dir)
    log_dir = os.path.join(parent_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "server_logs.log")
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


@mcp.tool(name="Получение количества задач")
async def get_notes_count() -> str:
    """Получает общее количество задач, доступных на сервере

    ## Примеры практического использования
    - Может быть использовано для осведомленности пользователя о его общем количестве задач
    - Для понимания того, какие параметры паггинации нужны для вызова функции get_notes
    """
    response = requests.get(f"{URL}/stats/count")
    if response.status_code == 200:
        logger.info(f"Получение количества задач. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при получеии количества задач. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при получеии количества задач. Код ошибки: {response.status_code}, текст ошибки: {response.text}"

@mcp.tool(name="Получение задач с учетом паггинации")
async def get_notes(
    skip: Annotated[int, Field(ge=0, default=0, description="Количество записей, котрые нужно пропустить")],
    limit: Annotated[int, Field(ge=1, le=1000, default=10, description="Количество записей, котрые нужно получить")],
    status_filter: Annotated[StatusType, Field(default=None, description="Статус задачи, который может быть одним из трех типов: done, in_progress, not_activate. Если не передать значение, то выберутся все задачи")]
) -> str:
    """Получает задачи с учетом пагинации

    ## Правила работы
    - Перед использованием нужно узнать общее количество задач и подобрать оптимальные параметры пагинации
    - Нужно учесть получение всех задач. Возможно, за несколько вызовов функции, если за 1 невозможно
    - Тип статуса может быть только один либо не быть вообще. Соответственно для 2х статусов нужно 2 раза вызвать функцию с разным фильтром. Но для получения всех статусов нужен лишь 1 вызов
    
    ## Тело ответа
    - **id**: уникальный id задачи
    - **name**: название задачи
    - **description**: описание задачи
    - **comment**: комментарий к задаче
    - **status**: статус задачи

    Comment и description могут быть незаполнены т.к. не являются обязательными
    """
    params = {
        "skip": skip,
        "limit": limit
    }
    if status_filter:
        params["status_filter"] = status_filter
    response = requests.get(f"{URL}", params=params)
    if response.status_code == 200:
        logger.info(f"Получение задач с учетом паггинации. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при получеии задач. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при получеии задач. Код ошибки: {response.status_code}, текст ошибки: {response.text}"

@mcp.tool(name="Получение задачи по ID")
async def get_note(
    note_id: Annotated[int, Field(..., description="ID задачи, которую нужно получить. ID можно посмотреть в выводе get_notes")]
) -> str:
    """Получение конкреткой задачи
    
    ## Пример использования
    - Пользователь просит задачу по конкретному id
    - Ты не помнишь детали задачи, но ты помнишь её id

    ## Тело ответа
    - **id**: уникальный id задачи
    - **name**: название задачи
    - **description**: описание задачи
    - **comment**: комментарий к задаче
    - **status**: статус задачи

    Comment и description могут быть незаполнены т.к. не являются обязательными
    """
    response = requests.get(f"{URL}/{note_id}")
    if response.status_code == 200:
        logger.info(f"Получение задачи по ID. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при получеии задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при получеии задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}"

@mcp.tool(name="Создание задачи")
async def create_note(
    name: Annotated[str, Field(..., description="Название задачи")],
    description: Annotated[str, Field(default=None, description="Описание задаче")],
    comment: Annotated[str, Field(default=None, description="Комментарий к задаче")],
    status: Annotated[StatusType, Field(default=StatusType.IN_PROGRESS, description="Статус задачи")],
) -> str:
    """Создание задачи

    ## Важная информация при создании
    - Создавать задачу нужно только по просьбе пользователя
    - Нужно разграничивать комментарии и описания, если они переданы
    - Если тебе непонятно, как нужно разграничить комментарий и описание, то попроси пользователя уточнить

    ## Тело ответа
    - **id**: уникальный id задачи
    - **name**: название задачи
    - **description**: описание задачи
    - **comment**: комментарий к задаче
    - **status**: статус задачи

    Comment и description могут быть незаполнены т.к. не являются обязательными
    """
    data = {"name": name}

    if description:
        data["description"] = description
    if comment:
        data["comment"] = comment
    if status:
        data["status"] = status

    response = requests.post(f"{URL}", json=data)
    if response.status_code == 201:
        logger.info(f"Создание задачи. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при создании задачи. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при создании задачи. Код ошибки: {response.status_code}, текст ошибки: {response.text}"
    
@mcp.tool(name="Удаление задачи")
async def delete_note(
    note_id: Annotated[int, Field(..., description="ID задачи, которую нужно удалить. ID можно посмотреть в выводе get_notes")]
) -> str:
    """Удаление конкреткой задачи по её id
    
    ## Пример использования
    - Пользователь просит удалить задачу

    ## Важно
    - Перед удалением ОБЯЗАТЕЛЬНО нужно переспросить ту ли задачу нужно удалить
    """
    response = requests.delete(f"{URL}/{note_id}")
    if response.status_code == 204:
        logger.info(f"Удаление задачи. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при удалении задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при удалении задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}"

@mcp.tool(name="Обновление информации по задаче")
async def update_note(
    note_id: Annotated[int, Field(..., description="ID задачи, которую нужно обновить. ID можно посмотреть в выводе get_notes")],
    name: Annotated[str, Field(default=None, description="Название задачи")],
    description: Annotated[str, Field(default=None, description="Описание задаче")],
    comment: Annotated[str, Field(default=None, description="Комментарий к задаче")],
    status: Annotated[StatusType, Field(default=None, description="Статус задачи")]
) -> str:
    """Обновление информации задачи по её id

    ## Важные инструкции
    - Любое поле может быть None, поэтому НУЖНО передавать только то, что указал пользователь

    ## Тело ответа
    - **id**: уникальный id задачи
    - **name**: название задачи
    - **description**: описание задачи
    - **comment**: комментарий к задаче
    - **status**: статус задачи

    Comment и description могут быть незаполнены т.к. не являются обязательными
    """
    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    if comment:
        data["comment"] = comment
    if status:
        data["status"] = status
    if len(data.keys()) == 0:
        return "Ошибка при использовании обновления задачи. Не передан ни один аргумент"
    response = requests.put(f"{URL}/{note_id}", json=data)
    if response.status_code == 200:
        logger.info(f"Обновление задачи. Ответ: {response.text}")
        return response.text
    else:
        logger.error(f"Ошибка при обновлении задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}")
        return f"Ошибка при обновлении задачи по ID. Код ошибки: {response.status_code}, текст ошибки: {response.text}"


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Start new server")
    mcp.run(transport='streamable-http')