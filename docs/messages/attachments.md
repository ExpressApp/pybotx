# Вложения

В этом разделе описаны способы работы с файловыми вложениями в pybotx.

## Введение

pybotx позволяет отправлять и получать файлы в сообщениях. Для работы с файлами используются классы:

- `OutgoingAttachment` — для отправки файлов
- `IncomingFileAttachment` — для получения файлов из входящих сообщений

Файлы могут быть отправлены вместе с текстовым сообщением или как самостоятельное сообщение (в этом случае текст сообщения может быть пустым).

## OutgoingAttachment

Класс `OutgoingAttachment` используется для создания файловых вложений, которые можно отправить в сообщении. Существует несколько способов создания экземпляра `OutgoingAttachment`:

### Создание из асинхронного буфера

```python
from aiofiles.tempfile import NamedTemporaryFile
from pybotx import OutgoingAttachment

async def create_attachment_from_buffer():
    # Создаем временный файл с асинхронным интерфейсом
    async with NamedTemporaryFile("wb+") as async_buffer:
        # Записываем данные в буфер
        await async_buffer.write(b"Hello, world!\n")
        # Перемещаем указатель в начало файла
        await async_buffer.seek(0)
        
        # Создаем вложение из буфера
        attachment = await OutgoingAttachment.from_async_buffer(
            async_buffer, 
            filename="hello.txt"
        )
        
        return attachment
```

### Создание из синхронного буфера

```python
from io import BytesIO
from pybotx import OutgoingAttachment

async def create_attachment_from_sync_buffer():
    # Создаем буфер в памяти
    buffer = BytesIO(b"Hello, world!\n")
    
    # Создаем вложение из буфера
    attachment = await OutgoingAttachment.from_sync_buffer(
        buffer, 
        filename="hello.txt"
    )
    
    return attachment
```

### Создание из файла на диске

```python
from pybotx import OutgoingAttachment

async def create_attachment_from_file():
    # Создаем вложение из файла на диске
    attachment = await OutgoingAttachment.from_file(
        "/path/to/file.txt", 
        filename="renamed_file.txt"  # Опционально: переименовать файл
    )
    
    return attachment
```

### Создание из байтов

```python
from pybotx import OutgoingAttachment

async def create_attachment_from_bytes():
    # Создаем вложение из байтов
    data = b"Hello, world!\n"
    attachment = await OutgoingAttachment.from_bytes(
        data, 
        filename="hello.txt"
    )
    
    return attachment
```

## Отправка файлов

Для отправки файла в сообщении используется параметр `file` в методах `bot.answer_message()` или `bot.send_message()`:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/send_file", description="Отправить файл")
async def send_file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем вложение из байтов
    data = b"Hello, world!\n"
    attachment = await OutgoingAttachment.from_bytes(
        data, 
        filename="hello.txt"
    )
    
    # Отправляем сообщение с вложением
    await bot.answer_message(
        "Вот запрошенный файл:",
        file=attachment
    )
```

Также можно отправить файл без текста сообщения:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/send_file_only", description="Отправить только файл")
async def send_file_only_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем вложение из байтов
    data = b"Hello, world!\n"
    attachment = await OutgoingAttachment.from_bytes(
        data, 
        filename="hello.txt"
    )
    
    # Отправляем сообщение только с вложением
    await bot.answer_message("", file=attachment)
```

> **Note**
> 
> Даже если текст сообщения пустой, параметр `body` все равно должен быть передан в метод `bot.answer_message()` или `bot.send_message()`.

## Получение файлов

Когда пользователь отправляет сообщение с файлом, файл доступен через атрибут `message.file` типа `IncomingFileAttachment`:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/process_file", description="Обработать полученный файл")
async def process_file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли файл в сообщении
    if not message.file:
        await bot.answer_message("Пожалуйста, отправьте файл")
        return
    
    # Получаем информацию о файле
    file_info = (
        f"Имя файла: {message.file.filename}\n"
        f"Размер: {message.file.size} байт\n"
        f"Тип: {message.file.content_type}\n"
    )
    
    # Читаем содержимое файла (для текстовых файлов)
    if message.file.content_type.startswith("text/"):
        file_content = await message.file.read()
        file_text = file_content.decode("utf-8")
        
        # Ограничиваем вывод первыми 100 символами
        preview = file_text[:100] + ("..." if len(file_text) > 100 else "")
        file_info += f"\nПредпросмотр содержимого:\n```\n{preview}\n```"
    
    await bot.answer_message(file_info)
```

Класс `IncomingFileAttachment` предоставляет следующие атрибуты и методы:

- `filename` — имя файла
- `size` — размер файла в байтах
- `content_type` — MIME-тип файла
- `async def read() -> bytes` — асинхронно читает содержимое файла и возвращает его в виде байтов

## Эхо-файл

Один из распространенных сценариев использования — эхо-файл, когда бот отправляет обратно тот же файл, который получил от пользователя:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/echo_file", description="Отправить файл обратно")
async def echo_file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли файл в сообщении
    if not message.file:
        await bot.answer_message("Пожалуйста, отправьте файл")
        return
    
    # Отправляем тот же файл обратно
    await bot.answer_message(
        f"Вы отправили файл: {message.file.filename}",
        file=message.file
    )
```

Обратите внимание, что `IncomingFileAttachment` можно напрямую использовать в качестве параметра `file` при отправке сообщения, без необходимости создавать `OutgoingAttachment`.

## Примеры использования

### Генерация текстового файла

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/generate_text", description="Сгенерировать текстовый файл")
async def generate_text_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем текст из аргумента команды или используем текст по умолчанию
    text = message.argument or "Это сгенерированный текстовый файл."
    
    # Создаем содержимое файла
    content = text.encode("utf-8")
    
    # Создаем вложение
    attachment = await OutgoingAttachment.from_bytes(
        content,
        filename="generated.txt"
    )
    
    # Отправляем файл
    await bot.answer_message("Сгенерированный файл:", file=attachment)
```

### Создание CSV-файла

```python
import csv
from io import StringIO
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/generate_csv", description="Сгенерировать CSV-файл")
async def generate_csv_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем буфер для CSV-данных
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    
    # Записываем заголовки
    writer.writerow(["Имя", "Возраст", "Город"])
    
    # Записываем данные
    writer.writerow(["Иван", 25, "Москва"])
    writer.writerow(["Мария", 30, "Санкт-Петербург"])
    writer.writerow(["Алексей", 22, "Казань"])
    
    # Получаем строку с CSV-данными
    csv_string = csv_buffer.getvalue()
    
    # Создаем вложение
    attachment = await OutgoingAttachment.from_bytes(
        csv_string.encode("utf-8"),
        filename="users.csv"
    )
    
    # Отправляем файл
    await bot.answer_message("CSV-файл с данными:", file=attachment)
```

### Обработка изображений

```python
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/watermark", description="Добавить водяной знак на изображение")
async def watermark_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли файл в сообщении
    if not message.file:
        await bot.answer_message("Пожалуйста, отправьте изображение")
        return
    
    # Проверяем, является ли файл изображением
    if not message.file.content_type.startswith("image/"):
        await bot.answer_message("Пожалуйста, отправьте файл изображения")
        return
    
    try:
        # Читаем содержимое файла
        image_data = await message.file.read()
        
        # Открываем изображение с помощью PIL
        image = Image.open(BytesIO(image_data))
        
        # Создаем объект для рисования
        draw = ImageDraw.Draw(image)
        
        # Добавляем водяной знак
        watermark_text = message.argument or "© pybotx"
        
        # Определяем размер и положение текста
        width, height = image.size
        x = width - 10  # правый край с отступом
        y = height - 10  # нижний край с отступом
        
        # Рисуем текст
        draw.text(
            (x, y),
            watermark_text,
            fill=(255, 255, 255, 128),  # белый цвет с прозрачностью
            anchor="rb",  # правый нижний угол текста
        )
        
        # Сохраняем изображение в буфер
        output = BytesIO()
        image.save(output, format=image.format)
        output.seek(0)
        
        # Создаем вложение
        attachment = await OutgoingAttachment.from_sync_buffer(
            output,
            filename=f"watermarked_{message.file.filename}"
        )
        
        # Отправляем файл
        await bot.answer_message("Изображение с водяным знаком:", file=attachment)
    
    except Exception as e:
        await bot.answer_message(f"Ошибка при обработке изображения: {e}")
```

### Конвертация файлов

```python
from io import BytesIO
import json
import csv
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/csv_to_json", description="Конвертировать CSV в JSON")
async def csv_to_json_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли файл в сообщении
    if not message.file:
        await bot.answer_message("Пожалуйста, отправьте CSV-файл")
        return
    
    # Проверяем расширение файла
    if not message.file.filename.lower().endswith(".csv"):
        await bot.answer_message("Пожалуйста, отправьте файл с расширением .csv")
        return
    
    try:
        # Читаем содержимое файла
        file_content = await message.file.read()
        csv_text = file_content.decode("utf-8")
        
        # Парсим CSV
        csv_reader = csv.DictReader(csv_text.splitlines())
        data = list(csv_reader)
        
        # Конвертируем в JSON
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Создаем имя для JSON-файла
        json_filename = message.file.filename.rsplit(".", 1)[0] + ".json"
        
        # Создаем вложение
        attachment = await OutgoingAttachment.from_bytes(
            json_data.encode("utf-8"),
            filename=json_filename
        )
        
        # Отправляем файл
        await bot.answer_message("Конвертированный JSON-файл:", file=attachment)
    
    except Exception as e:
        await bot.answer_message(f"Ошибка при конвертации файла: {e}")
```

### Загрузка файла из интернета

```python
import aiohttp
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/download", description="Загрузить файл по URL")
async def download_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем URL из аргумента команды
    url = message.argument
    
    if not url:
        await bot.answer_message("Пожалуйста, укажите URL файла")
        return
    
    try:
        # Создаем HTTP-сессию
        async with aiohttp.ClientSession() as session:
            # Отправляем GET-запрос
            async with session.get(url) as response:
                # Проверяем статус ответа
                if response.status != 200:
                    await bot.answer_message(f"Ошибка при загрузке файла: HTTP {response.status}")
                    return
                
                # Получаем имя файла из URL
                filename = url.split("/")[-1]
                
                # Читаем содержимое файла
                file_content = await response.read()
                
                # Создаем вложение
                attachment = await OutgoingAttachment.from_bytes(
                    file_content,
                    filename=filename
                )
                
                # Отправляем файл
                await bot.answer_message(f"Загруженный файл ({len(file_content)} байт):", file=attachment)
    
    except Exception as e:
        await bot.answer_message(f"Ошибка при загрузке файла: {e}")
```

## См. также

- [Отправка сообщений](sending.md)
- [Редактирование сообщений](editing.md)
- [Удаление сообщений](deleting.md)
- [Кнопки и разметка](bubbles.md)
- [Упоминания](mentions.md)