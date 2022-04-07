# Модуль для просмотра ВАХ

PyQt-виджет для отображения ВАХ. Предназначен в первую очередь для встраивания в разные продукты линейки EyePoint. Виджет должен уметь выводить несколько ВАХ на график и при необходимости обновлять их.

## Запуск в Windows

1. Установите зависимости:

   ```bash
   python -m venv venv
   venv\Scripts\python -m pip install --upgrade pip
   venv\Scripts\python -m pip install -r requirements.txt
   ```

2. Запустите пример:

   ```bash
   venv\Scripts\python -m ivviewer
   ```

3. Запустите тест:

   ```bash
   testall.bat
   ```

## Запуск в Linux

1. Установите зависимости:

   ```bash
   python3 -m venv venv
   venv/bin/python3 -m pip install --upgrade pip
   venv/bin/python3 -m pip install -r requirements.txt
   ```

2. Запустите пример:

   ```bash
   venv/bin/python3 -m ivviewer
   ```

3. Запустите тест:

   ```bash
   bash testall.sh
   ```

## Примечания

- Модуль тестировался на Python версии 3.6.
- В системе должны быть установлены Qt5, Qwt.
