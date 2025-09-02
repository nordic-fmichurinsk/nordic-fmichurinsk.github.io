import requests
import json
import os



def correct_ocr_with_yandexgpt(ocr_text) -> tuple: 


    
    # Формируем промпт для YandexGPT
    api_key = "YOUR_API_KEY_HERE"    # ключ апи
    folder_id = "b1gkjdb418i68vkhi8ok" # айди папки
    ERROR_TEXT = "Не удалось распознать"

    prompt = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "100"
        },
        "messages": [
            {
                "role": "system",
                "text": (
                    "Ты помогаешь корректировать результаты OCR табличек с образцами. "
                    "Табличка содержит: 1) Место сбора (город, станица и т.д.), "
                    "2) Дату в формате число.римская_цифра.число (например, 12.IV.2023), "
                    "3) Номер образца (начинается на z, содержит цифры и '-'). "
                    "Исправь возможные ошибки OCR и извлеки только место сбора и дату. "
                    "Ответ должен содержать ТОЛЬКО JSON в формате: [{\"date\": \"исправленная дата\", \"location\": \"исправленное место\"}]. "
                    "Если какой-то элемент не распознан, укажи null."
                )
            },
            {
                "role": "user",
                "text": ocr_text
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id,
        "x-data-logging-enabled": "true"
    }
    
    try:
        # Отправляем запрос к YandexGPT API
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers=headers,
            json=prompt
        )

        corrected_data_list = {}
        if response.status_code == 200:
        
            # Парсим ответ
            result = response.json()
            gpt_response = result['result']['alternatives'][0]['message']['text']
            # Удаляем возможные лишние символы вокруг JSON
            gpt_response = gpt_response.strip()
            if gpt_response.startswith("```"):
                gpt_response = gpt_response[3:]
            if gpt_response.endswith("```"):
                gpt_response = gpt_response[:-3]

            # Извлекаем данные из JSON-ответа (ожидаем список)
            corrected_data_list = json.loads(gpt_response)
        
        # Берем первый элемент списка
        if isinstance(corrected_data_list, list) and len(corrected_data_list) > 0:
            corrected_data = corrected_data_list[0]
        else:
            corrected_data = {}
        
        date = corrected_data.get('date')
        location = corrected_data.get('location')
        
        if not date or date == 'null':
        	date = ERROR_TEXT
        if not location or location == 'null':
        	location = ERROR_TEXT

        return date, location
    
    except Exception as e:
#        print(f"Ошибка при работе с YandexGPT API: {e}")
        return ERROR_TEXT, ERROR_TEXT 