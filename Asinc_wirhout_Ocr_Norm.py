# Asinc_wirhout_Ocr_Norm.py (Фрагменты для модификации)

# ... (все ваши импорты и определения констант/схем остаются как есть) ...
import os
import json
import logging  # Используем logging вместо print для лучшего контроля
from typing import List, Dict, Any  # Убедитесь, что типизация актуальна

# Настройка логирования (можно вынести в отдельный модуль или настроить глобально)
logger = logging.getLogger(__name__)


# logger.setLevel(logging.INFO) # Установите нужный уровень
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)


# --- Ключи API ---
# РЕКОМЕНДАЦИЯ: Загружайте ключи из переменных окружения, а не хардкодьте их.
# GEMINI_API_KEYS_STR = os.getenv("GEMINI_API_KEYS_JSON") # Например, '[ "key1", "key2" ]'
# if GEMINI_API_KEYS_STR:
#     try:
#         GEMINI_API_KEYS = json.loads(GEMINI_API_KEYS_STR)
#     except json.JSONDecodeError:
#         logger.error("Не удалось декодировать GEMINI_API_KEYS_JSON из переменных окружения.")
#         GEMINI_API_KEYS = ["dummy_fallback_key_if_not_set_in_env"]
# else:
#     logger.warning("Переменная окружения GEMINI_API_KEYS_JSON не установлена. Используются ключи из скрипта (если есть).")
#     # Оставьте ваши текущие GEMINI_API_KEYS как fallback, если переменная окружения не задана
#     # GEMINI_API_KEYS = [ "ваши_ключи_здесь..." ] # Как у вас сейчас
#
# # Проверка, что ключи не заглушки (если они все еще из скрипта)
# if not GEMINI_API_KEYS or GEMINI_API_KEYS == ["dummy_key_for_empty_list"] or any(
#         "Замените на ваш" in key for key in GEMINI_API_KEYS):
#     logger.error("ОШИБКА: Список ключей GEMINI_API_KEYS пуст или содержит заглушки. Добавьте реальные ключи или настройте переменные окружения.")
#     GEMINI_API_KEYS = ["dummy_fallback_key_if_not_set_critical"]


# --- Путь к файлу справочника ---
# Убедитесь, что этот путь корректен относительно места запуска API-сервера
# или используйте абсолютный путь / переменную окружения.
# REFERENCE_ARTICLES_FILE_PATH = os.getenv("REFERENCE_ARTICLES_FILE_PATH", r"Mrk2artikuls.txt")
# if not os.path.exists(REFERENCE_ARTICLES_FILE_PATH):
#    logger.error(f"Файл справочника не найден: {REFERENCE_ARTICLES_FILE_PATH}")


# ... (все ваши функции send_to_gemini_stage_X, process_stage_X_response, load_reference_articles и т.д. остаются) ...
# Важно: внутри этих функций замените print() на logger.info(), logger.warning(), logger.error()

# --- Адаптация основной функции process_pdf_async ---
async def process_pdf_async(pdf_path: str, output_folder_for_script_artifacts: str) -> List[Dict[str, Any]]:
    """
    Обрабатывает PDF-файл и возвращает список извлеченных элементов.
    Сохранение в файлы XLSX и промежуточные JSON теперь выполняется только если это необходимо
    для отладки или если API явно этого потребует (сейчас не требует).

    Args:
        pdf_path: Путь к PDF файлу для обработки.
        output_folder_for_script_artifacts: Папка, куда скрипт МОЖЕТ сохранять
                                            промежуточные артефакты, если это включено для отладки.
                                            API сервер будет управлять этой папкой.

    Returns:
        Список словарей, где каждый словарь представляет извлеченный элемент.
    """
    start_time_total = time.time()
    logger.info(f"Общая обработка начата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} для файла {pdf_path}")

    all_final_items_flat: List[Dict[str, Any]] = []  # Инициализация

    try:
        pdf_path = os.path.normpath(pdf_path.strip('"\''))
        if not os.path.exists(pdf_path):
            logger.error(f"Файл не найден: {pdf_path}")
            return []  # Возвращаем пустой список в случае ошибки

        # Имя PDF для логов и потенциальных артефактов (если они нужны)
        pdf_name = re.sub(r'[\\/*?:"<>|]', '', os.path.splitext(os.path.basename(pdf_path))[0]) or "Unknown"

        # output_folder создается API сервером и передается сюда.
        # os.makedirs(output_folder_for_script_artifacts, exist_ok=True) # Уже создана API сервером

        base64_full_pdf_for_stages = ""
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes_full_doc = f.read()
            base64_full_pdf_for_stages = base64.b64encode(pdf_bytes_full_doc).decode("utf-8")
        except Exception as e:
            logger.error(f"Критическая ошибка: Не удалось прочитать или закодировать PDF-файл {pdf_path}: {e}",
                         exc_info=True)
            return []

        # --- Этап 1 ---
        relevant_page_numbers_1_based = await identify_relevant_pages_stage_1_async(
            pdf_path, output_folder_for_script_artifacts, base64_full_pdf_for_stages
        )
        if not relevant_page_numbers_1_based:
            logger.info("Обработка остановлена: не найдено релевантных страниц на Этапе 1.")
            # save_data_to_xlsx([], output_folder_for_script_artifacts, f"{pdf_name}_final_data") # Опционально
            return []

        # ... (остальная часть вашей функции process_pdf_async без изменений до момента формирования all_final_items_flat) ...
        # Убедитесь, что все print() заменены на logger.info(), logger.warning() и т.д.

        # --- Сбор итоговых данных ---
        # Вместо сохранения в JSON и XLSX здесь, мы будем ВОЗВРАЩАТЬ all_final_items_flat
        # Логика сборки all_final_items_flat должна остаться такой же, как у вас была.
        # Пример (если у вас была такая логика в конце):
        # stage_7_enabled = False # или True, как у вас было
        # all_final_items_flat = []
        # results_to_flatten = stage_7_results_per_page if stage_7_enabled else stage_6_results_per_page
        #
        # for page_idx, page_items in results_to_flatten:
        #     for item_data in page_items:
        #         if item_data:
        #             item_copy_final = item_data.copy()
        #             if stage_7_enabled:
        #                  item_copy_final.setdefault('found_in_pdf_on_pages', []) # Уже должно быть из Этапа 7
        #             else: # Если Этап 7 отключен, добавляем пустой список
        #                  item_copy_final.setdefault('found_in_pdf_on_pages', [])
        #             all_final_items_flat.append(item_copy_final)

        # ВАЖНО: Убедитесь, что all_final_items_flat формируется корректно со всеми данными
        # до этой точки. Ниже приведен пример того, как это могло бы выглядеть, если вы
        # проходите все 6 этапов и собираете результаты.

        # --- Пример сборки all_final_items_flat, если у вас была такая логика ---
        # (этот блок нужно адаптировать под вашу реальную логику сборки `all_final_items_flat`
        #  после всех этапов обработки)

        # Предположим, что stage_6_results_per_page содержит финальные данные после всех этапов
        # (или stage_7_results_per_page, если этап 7 включен и используется)

        # ВАЖНО: Убедитесь, что переменная `stage_6_results_per_page` (или `stage_7_results_per_page`
        # если этап 7 используется) содержит данные в ожидаемом формате:
        # List[Tuple[int, List[Dict[str, str]]]]
        # И что `all_final_items_flat` корректно собирается из этих данных.

        # Пример сборки all_final_items_flat (если этап 7 не используется):
        for page_idx, page_items_s6 in stage_6_results_per_page:  # Замените на stage_7_results_per_page если этап 7 используется
            for item_s6 in page_items_s6:
                if item_s6:
                    item_copy_final = item_s6.copy()
                    # Убедитесь, что все необходимые поля присутствуют и имеют корректные типы для JSON
                    item_copy_final.setdefault('found_in_pdf_on_pages', [])  # Добавляем, если Этап 7 не был выполнен

                    # Преобразование потенциальных артикулов и страниц в строки, если они списки (для JSON)
                    if isinstance(item_copy_final.get("potential_artikuls"), list):
                        item_copy_final["potential_artikuls"] = ", ".join(
                            map(str, item_copy_final["potential_artikuls"]))
                    if isinstance(item_copy_final.get("found_in_pdf_on_pages"), list):
                        item_copy_final["found_in_pdf_on_pages"] = ", ".join(
                            map(str, item_copy_final["found_in_pdf_on_pages"]))

                    all_final_items_flat.append(item_copy_final)
        # --- Конец примера сборки ---

        if all_final_items_flat:
            logger.info(f"Финальные результаты (до возврата из функции): {len(all_final_items_flat)} строк.")
            # Опционально: сохранить JSON для отладки, если это нужно
            # debug_json_path = os.path.join(output_folder_for_script_artifacts, f"{pdf_name}_debug_api_return.json")
            # try:
            #     with open(debug_json_path, "w", encoding="utf-8") as f_debug:
            #         json.dump(all_final_items_flat, f_debug, ensure_ascii=False, indent=4)
            #     logger.info(f"Отладочный JSON сохранен: {debug_json_path}")
            # except Exception as e_json_save_debug:
            #     logger.error(f"Ошибка сохранения отладочного JSON: {e_json_save_debug}")
        else:
            logger.warning("Нет финальных данных для возврата.")

        return all_final_items_flat  # Возвращаем результат

    except FileNotFoundError:
        logger.error(f"Ошибка: Файл не найден при обработке: {pdf_path}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Общая ошибка в process_pdf_async для файла {pdf_path}: {str(e)}", exc_info=True)
        return []  # Возвращаем пустой список или можно выбросить исключение, которое поймает API
    finally:
        duration_total = time.time() - start_time_total
        logger.info(
            f"Общая обработка файла {pdf_path} завершена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Длительность: {duration_total:.2f} сек.)"
        )

# --- Удаление или комментирование блока if __name__ == "__main__": ---
# Этот блок не нужен, когда скрипт используется как модуль API.
# Если вы хотите оставить возможность запускать скрипт отдельно для отладки,
# вы можете оставить его, но убедитесь, что он не мешает импорту.
#
# if __name__ == "__main__":
#    # ... ваш текущий код для запуска из командной строки ...
#    # Например:
#    # pdf_file_path_input = input("Введите путь к PDF-файлу: ")
#    # asyncio.run(process_pdf_async(pdf_file_path_input, "local_output_folder")) # Пример с указанием папки
#    pass
