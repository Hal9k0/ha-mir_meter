# MIR meter

Интеграция для Home Assistant.  
Предназначена для считывания данных со счётчиков электрической энергии МИР по Bluetooth LE.

В вашем Home Assistant должна быть установлена и настроена интеграция Bluetooth, которая работает с адаптером Bluetooth LE.  
Или интеграция ESPHome Builder, в которой требуется зарегистрировать плату ESP32, работающую в режиме Bluetooth Proxy.

Ваш счётчик должен быть оборудован модулем Bluetooth. Об этом говорит буква **B** в маркировке счётчика.  
Например: МИР С-05.10-230-5(80)-PZ1**B**-KNQ-S-D

Имя счётчика состоит из модели и серийного номера. Например, C05-12345678901234.  
ПИН-код можно найти в формуляре счётчика.  
Проверялось на счётчиках МИР С-05 и С-04. Должно работать и с С-07.

## Установка
**Способ 1:** [HACS](https://hacs.xyz/)

* Установите и настройте [HACS](https://hacs.xyz/docs/use/#getting-started-with-hacs)
* Откройте HACS -> Три точки в верхнем правом углу -> Пользовательские репозитории
* Добавьте репозиторий `https://github.com/Hal9k0/ha-mir_meter.git` (тип `Интеграция`)
* В поиске найдите и откройте `MIR meter` -> Скачать
* Перезагрузите Home Assistant

**Способ 2:** вручную, не рекомендуется

* Скачайте архив `mir_meter.zip` из [последнего релиза](https://github.com/Hal9k0/ha-mir_meter/releases/latest)
* Создайте подкаталог `custom_components/mir_meter` в каталоге где расположен файл `configuration.yaml`
* Распакуйте содержимое архива в `custom_components/mir_meter`
* Перезагрузите Home Assistant

Если ваш счётчик будет находится в зоне обнаружения Bluetooth, Home Assistant сообщит вам об этом.
