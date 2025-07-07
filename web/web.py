import os
import asyncio
from dotenv import find_dotenv, load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from nicegui import ui, app



# Загружаем переменные окружения
load_dotenv(find_dotenv())



model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_KEY"),
)



checkpointer = InMemorySaver()
template = "Ты - личный помощник, который умеет управлять задачами через MCP"
config = {"configurable": {"thread_id": "1"}}



# Глобальные переменные для агента
agent = None
client = None
session = None
input_field = None
chat_container = None



# Добавляем кастомные стили
def add_custom_styles():
    """Добавление кастомных стилей в духе книги 'Глубокое обучение'"""
    ui.add_head_html('''
    <style>
        /* Основные цвета в духе обложки "Глубокое обучение" */
        :root {
            --deep-blue: #1a237e;
            --neural-orange: #ff6f00;
            --dark-bg: #0d1117;
            --card-bg: #161b22;
            --text-primary: #e6edf3;
            --text-secondary: #7d8590;
            --accent-blue: #2196f3;
            --success-green: #238636;
            --error-red: #da3633;
            --warning-yellow: #d29922;
        }
        
        /* Общий фон */
        body {
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--deep-blue) 100%);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        /* Заголовки */
        .neural-title {
            background: linear-gradient(45deg, var(--neural-orange), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            text-shadow: 0 0 20px rgba(255, 111, 0, 0.3);
        }
        
        /* Карточки сообщений */
        .user-message {
            background: linear-gradient(135deg, var(--accent-blue), var(--neural-orange));
            border: none;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
            border-radius: 18px;
        }
        
        .assistant-message {
            background: var(--card-bg);
            border: 1px solid rgba(255, 111, 0, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border-radius: 18px;
        }
        
        .system-message {
            background: linear-gradient(90deg, var(--warning-yellow), var(--neural-orange));
            border: none;
            box-shadow: 0 2px 10px rgba(210, 153, 34, 0.3);
            border-radius: 12px;
        }
        
        /* Контейнер чата */
        .chat-container {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(255, 111, 0, 0.3);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        /* Поле ввода */
        .neural-input {
            background: var(--card-bg);
            border: 2px solid rgba(255, 111, 0, 0.3);
            border-radius: 12px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }


        .neural-input:focus {
            border-color: var(--neural-orange);
            box-shadow: 0 0 20px rgba(255, 111, 0, 0.4);
        }
        
        /* Кнопка отправки */
        .send-button {
            background: linear-gradient(135deg, var(--neural-orange), var(--accent-blue));
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 111, 0, 0.3);
        }
        
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 111, 0, 0.4);
        }
        
        /* Статус индикаторы */
        .status-ready {
            color: var(--success-green);
            text-shadow: 0 0 10px rgba(35, 134, 54, 0.5);
        }
        
        .status-error {
            color: var(--error-red);
            text-shadow: 0 0 10px rgba(218, 54, 51, 0.5);
        }
        
        .status-warning {
            color: var(--warning-yellow);
            text-shadow: 0 0 10px rgba(210, 153, 34, 0.5);
        }
        
        /* Анимации */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .loading-indicator {
            animation: pulse 1.5s infinite;
        }
        
        /* Скроллбар */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--dark-bg);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, var(--neural-orange), var(--accent-blue));
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(45deg, var(--accent-blue), var(--neural-orange));
        }
        
        /* Markdown стили */
        .markdown-content code {
            background: rgba(255, 111, 0, 0.1);
            border: 1px solid rgba(255, 111, 0, 0.3);
            border-radius: 4px;
            color: var(--neural-orange);
        }
        
        .markdown-content pre {
            background: var(--dark-bg);
            border: 1px solid rgba(255, 111, 0, 0.3);
            border-radius: 8px;
        }
        
        .markdown-content blockquote {
            border-left: 4px solid var(--neural-orange);
            background: rgba(255, 111, 0, 0.05);
        }
    </style>
    ''')



async def initialize_agent():
    """Инициализация MCP клиента и агента"""
    global agent, client, session
    
    try:
        client = MultiServerMCPClient(
            {
                "temp": {
                    "url": f"http://{os.getenv('MCP_SERVICE_NAME')}:8000/mcp",
                    "transport": "streamable_http",
                }
            }
        )
        
        session = client.session("temp")
        session_obj = await session.__aenter__()
        tools = await load_mcp_tools(session_obj)
        
        agent = create_react_agent(
            model,
            tools,
            prompt=template,
            checkpointer=checkpointer,
        )
        
        print("Агент успешно инициализирован")
        return True
        
    except Exception as e:
        print(f"Ошибка инициализации агента: {e}")
        return False



async def cleanup_agent():
    """Очистка ресурсов"""
    global session, client
    
    try:
        if session:
            await session.__aexit__(None, None, None)
        if client:
            await client.close()
    except Exception as e:
        print(f"Ошибка при очистке: {e}")



def add_user_message(message_text):
    """Добавление сообщения пользователя в чат"""
    with chat_container:
        with ui.row().classes('w-full mb-3 justify-end'):
            with ui.card().classes('user-message text-white p-4 max-w-xs shadow-lg'):
                ui.label(message_text).classes('text-sm font-medium')
                ui.label('Пользователь').classes('text-xs opacity-90 mt-2 font-light')



def add_assistant_message(message_text):
    """Добавление сообщения ассистента с поддержкой Markdown"""
    with chat_container:
        with ui.row().classes('w-full mb-3 justify-start'):
            with ui.card().classes('assistant-message p-4 max-w-md shadow-lg'):
                ui.markdown(message_text).classes('text-sm markdown-content text-gray-100')
                ui.label('🤖 Нейро-Ассистент').classes('text-xs mt-2 font-light').style('color: var(--neural-orange)')



def add_system_message(message_text):
    """Добавление системного сообщения"""
    with chat_container:
        with ui.row().classes('w-full mb-3 justify-center'):
            with ui.card().classes('system-message p-3 loading-indicator'):
                ui.label(message_text).classes('text-xs font-medium text-gray-900')



async def send_message(message_text):
    """Обработка отправки сообщения"""
    global chat_container
    
    print(f"send_message вызвана с текстом: '{message_text}'")
    
    if not chat_container:
        print("chat_container не инициализирован")
        return
    
    if not message_text or not message_text.strip():
        print("Пустое сообщение")
        return
    
    print(f"Отправляем сообщение: {message_text}")
    
    # Добавляем сообщение пользователя
    add_user_message(message_text)
    
    # Показываем индикатор загрузки
    add_system_message("🧠 Обрабатываю нейронные связи...")
    
    try:
        # Получаем ответ от агента
        if agent:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": message_text}]}, 
                config
            )
            
            # Удаляем последнее системное сообщение (индикатор загрузки)
            if chat_container.default_slot.children:
                chat_container.default_slot.children[-1].delete()
            
            # Извлекаем текст ответа
            assistant_message = response['messages'][-1].content
            
            # Добавляем ответ ассистента с поддержкой Markdown
            add_assistant_message(assistant_message)
            
        else:
            # Удаляем индикатор загрузки
            if chat_container.default_slot.children:
                chat_container.default_slot.children[-1].delete()
            add_system_message("⚠️ Ошибка: нейронная сеть не активна")
                
    except Exception as e:
        # Удаляем индикатор загрузки
        if chat_container.default_slot.children:
            chat_container.default_slot.children[-1].delete()
        add_system_message(f"❌ Ошибка нейронной обработки: {str(e)}")



# Инициализация при старте приложения
@app.on_startup
async def startup():
    await initialize_agent()



# Очистка при завершении
@app.on_shutdown
async def shutdown():
    await cleanup_agent()



@ui.page('/')
def main():
    """Главная страница приложения"""
    global input_field, chat_container
    
    # Добавляем кастомные стили
    add_custom_styles()
    
    ui.page_title('🧠 Deep Learning Assistant')
    
    with ui.column().classes('w-full max-w-5xl mx-auto p-6'):
        # Заголовок в стиле нейронных сетей
        with ui.row().classes('w-full justify-center mb-6'):
            ui.label('🧠 Deep Learning Assistant').classes('text-4xl font-bold neural-title')
        
        with ui.row().classes('w-full justify-center mb-8'):
            ui.label('Персональный помощник на основе нейронных сетей').classes('text-lg text-gray-400 font-light')
        
        # Статус подключения с улучшенным дизайном
        with ui.row().classes('w-full justify-center mb-6'):
            status_container = ui.row().classes('items-center gap-3')
            
            with status_container:
                status_icon = ui.label('🔄').classes('text-xl')
                status_label = ui.label('Инициализация нейронной сети...').classes('text-sm status-warning font-medium')
        
        def update_status():
            if agent:
                status_icon.text = '🟢'
                status_label.text = '✨ Нейронная сеть активна и готова к работе'
                status_label.classes('text-sm status-ready font-medium')
            else:
                status_icon.text = '🔴'
                status_label.text = '❌ Нейронная сеть не инициализирована'
                status_label.classes('text-sm status-error font-medium')
        
        ui.timer(1.0, update_status)
        
        # Контейнер для чата с улучшенным дизайном
        with ui.scroll_area().classes('w-full h-[600px] chat-container p-6 mb-6'):
            chat_container = ui.column().classes('w-full gap-2')
            
            # Приветственное сообщение в стиле Deep Learning
            add_assistant_message(
                "🚀 **Добро пожаловать в Deep Learning Assistant!**\n\n"
                "Я - **нейронный помощник**, обученный на принципах глубокого обучения.\n\n"
                "**Мои возможности:**\n"
                "- 🧠 Обработка сложных запросов через *нейронные связи*\n"
                "- 📊 Анализ данных с помощью **машинного обучения**\n"
                "- 🔗 Интеграция с MCP для расширенного функционала\n"
                "- 💡 Поддержка `Markdown` разметки\n\n"
                "> *\"Глубокое обучение - это не просто алгоритм, это способ мышления\"*\n\n"
                "**Готов помочь вам в исследовании мира ИИ! 🤖**"
            )
            
        # Поле ввода и кнопка отправки с улучшенным дизайном
        def handle_send():
            """Обработчик для кнопки отправки"""
            message_text = input_field.value.strip()
            print(f"handle_send: получен текст '{message_text}'")
            
            if message_text:
                # Очищаем поле сразу
                input_field.value = ''
                # Отправляем сообщение
                asyncio.create_task(send_message(message_text))
            else:
                print("Пустое сообщение в handle_send")
        
        with ui.row().classes('w-full gap-4'):
            input_field = ui.input(
                placeholder='🧠 Введите ваше сообщение'
            ).classes('flex-grow neural-input text-lg p-4').props('input-style="color: var(--text-primary)"')
            
            input_field.on('keydown.enter', lambda: handle_send())
            
            send_button = ui.button(
                '🚀 Отправить', 
                on_click=handle_send
            ).classes('send-button px-6 py-4 text-lg font-semibold')
        
        # Футер с информацией
        with ui.row().classes('w-full justify-center mt-8'):
            ui.label('Powered by Deep Learning & Neural Networks').classes('text-xs text-gray-500 font-light')



# Запуск приложения
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0', port=8080, reload=False)
