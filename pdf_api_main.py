# pdf_api_main.py
import fastapi
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
import uuid
import json
import logging
from typing import List, Dict, Any

# Импортируем адаптированную функцию из вашего скрипта
# Убедитесь, что Asinc_wirhout_Ocr_Norm.py находится в той же директории
# или доступен через PYTHONPATH, и что функция process_pdf_async была адаптирована.
try:
    from Asinc_wirhout_Ocr_Norm import process_pdf_async, GEMINI_API_KEYS, REFERENCE_ARTICLES_FILE_PATH
except ImportError:
    print("ОШИБКА: Не удалось импортировать 'process_pdf_async' из Asinc_wirhout_Ocr_Norm.py.")
    print("Убедитесь, что файл находится в правильной директории и не содержит синтаксических ошибок при импорте.")


    # Заглушка, чтобы сервер мог запуститься для демонстрации структуры
    async def process_pdf_async(pdf_path: str, output_folder: str) -> List[Dict[str, Any]]:
        print(f"ЗАГЛУШКА: process_pdf_async вызвана для {pdf_path} в {output_folder}")
        return [{"id": "mock1", "data": "Это тестовые данные, замените на реальную обработку"}]


    GEMINI_API_KEYS = []
    REFERENCE_ARTICLES_FILE_PATH = "Mrk2artikuls.txt"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
# В продакшене замените "*" на конкретный домен вашего Next.js приложения
# например, ["http://localhost:3000", "https://your-nextjs-app.com"]
origins = [
    "http://localhost:3000",  # Для локальной разработки Next.js
    "http://localhost:9002",  # Порт из вашего package.json
    # Добавьте сюда URL вашего развернутого Next.js приложения
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_UPLOAD_DIR = "temp_pdf_uploads"
TEMP_OUTPUT_DIR_BASE = "temp_pdf_outputs"  # Базовая папка для выходных данных скрипта

os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_OUTPUT_DIR_BASE, exist_ok=True)

# Проверка наличия ключей API Gemini
if not GEMINI_API_KEYS or any("Замените на ваш" in key for key in GEMINI_API_KEYS):
    logger.warning("ВНИМАНИЕ: Ключи GEMINI_API_KEYS не настроены или содержат заглушки в Asinc_wirhout_Ocr_Norm.py!")
    # Можно добавить логику для загрузки из переменных окружения здесь, если GEMINI_API_KEYS в скрипте пустые
    # Например:
    # gemini_keys_env = os.getenv("GEMINI_API_KEYS_JSON")
    # if gemini_keys_env:
    #     try:
    #         GEMINI_API_KEYS = json.loads(gemini_keys_env)
    #         logger.info("Ключи Gemini загружены из переменных окружения.")
    #     except json.JSONDecodeError:
    #         logger.error("Ошибка декодирования GEMINI_API_KEYS_JSON из переменных окружения.")

# Проверка файла справочника
if not os.path.exists(REFERENCE_ARTICLES_FILE_PATH):
    logger.warning(f"ВНИМАНИЕ: Файл справочника '{REFERENCE_ARTICLES_FILE_PATH}' не найден!")


@app.post("/api/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    """
    Принимает PDF файл, обрабатывает его с помощью Asinc_wirhout_Ocr_Norm.py
    и возвращает извлеченные структурированные данные в формате JSON.
    """
    unique_id = str(uuid.uuid4())
    temp_pdf_path = os.path.join(TEMP_UPLOAD_DIR, f"{unique_id}_{file.filename}")
    # Папка для временных выходных файлов конкретно этого запроса (если скрипт их создает)
    temp_output_dir_for_request = os.path.join(TEMP_OUTPUT_DIR_BASE, unique_id)
    os.makedirs(temp_output_dir_for_request, exist_ok=True)

    logger.info(f"Получен файл: {file.filename}, сохранен как: {temp_pdf_path}")

    try:
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Файл {temp_pdf_path} успешно сохранен.")

        # Вызов вашей адаптированной функции process_pdf_async
        # Она должна возвращать список словарей (JSON-совместимые данные)
        logger.info(f"Запуск process_pdf_async для {temp_pdf_path} с выходной папкой {temp_output_dir_for_request}")

        # Адаптированный вызов: process_pdf_async теперь должна возвращать данные
        extracted_data: List[Dict[str, Any]] = await process_pdf_async(temp_pdf_path, temp_output_dir_for_request)

        logger.info(f"Обработка файла {file.filename} завершена. Извлечено {len(extracted_data)} записей.")

        if not extracted_data:
            logger.warning(f"Для файла {file.filename} не было извлечено данных.")
            # Можно вернуть пустой список или ошибку, в зависимости от ожидаемого поведения
            # return []

        return extracted_data

    except HTTPException:
        raise  # Перебрасываем HTTP исключения FastAPI
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при обработке PDF: {str(e)}")
    finally:
        # Очистка временных файлов
        if os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
                logger.info(f"Временный PDF файл {temp_pdf_path} удален.")
            except OSError as e_remove:
                logger.error(f"Не удалось удалить временный PDF файл {temp_pdf_path}: {e_remove}")

        if os.path.exists(temp_output_dir_for_request):
            try:
                shutil.rmtree(temp_output_dir_for_request)
                logger.info(f"Временная выходная папка {temp_output_dir_for_request} удалена.")
            except OSError as e_rmtree:
                logger.error(f"Не удалось удалить временную выходную папку {temp_output_dir_for_request}: {e_rmtree}")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # Запуск uvicorn сервера. Для продакшена используйте более надежный способ запуска,
    # например, gunicorn с uvicorn воркерами.
    # uvicorn.run("pdf_api_main:app", host="0.0.0.0", port=8000, reload=True)
    # Для простоты, если запускаете напрямую:
    uvicorn.run(app, host="0.0.0.0", port=8000)
