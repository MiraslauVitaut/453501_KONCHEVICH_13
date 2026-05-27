"""
Дополнительное задание ЛР5 — Многозадачность.
Вариант 13 — IoT Система (риэлтерское агентство).

Задача А (Threading):  5 потоков опрашивают датчики температуры в офисах (Lock).
Задача Б (Multiprocessing): Обработка кадра с камеры наблюдения (матрица яркости пикселей).
Задача В (Asyncio): Асинхронное управление 10 смарт-лампами в офисах агентства.
"""
import time
import asyncio
import threading
import random
import math
from concurrent.futures import ProcessPoolExecutor
from django.shortcuts import render


# ═══════════════════════════════════════════════════════════
# ЗАДАЧА А: Threading — опрос датчиков температуры (Lock)
# ═══════════════════════════════════════════════════════════

class TemperatureMonitor:
    """Система мониторинга температуры в офисах агентства."""

    def __init__(self):
        self.readings = []      # общий список показаний
        self.alerts = []        # список тревог
        self._lock = threading.Lock()
        self.log = []

    def poll_sensor(self, sensor_id, office_name):
        """Поток опрашивает датчик и записывает показание."""
        for i in range(3):  # 3 опроса на датчик
            time.sleep(random.uniform(0.05, 0.15))  # имитация задержки опроса

            temp = round(random.uniform(18.0, 32.0), 1)
            humidity = round(random.uniform(35.0, 75.0), 1)

            with self._lock:  # защита общего ресурса
                reading = {
                    'sensor': sensor_id,
                    'office': office_name,
                    'temp': temp,
                    'humidity': humidity,
                    'status': '🌡️ Норма' if 20 <= temp <= 26 else '⚠️ Отклонение',
                }
                self.readings.append(reading)

                if temp > 28:
                    self.alerts.append(
                        f'🔴 ТРЕВОГА: {office_name} — температура {temp}°C (норма 20-26°C)'
                    )
                elif temp < 20:
                    self.alerts.append(
                        f'🔵 ТРЕВОГА: {office_name} — температура {temp}°C (слишком холодно)'
                    )

                self.log.append(
                    f'[Датчик {sensor_id}] {office_name}: {temp}°C, влажность {humidity}%'
                )


def run_threading_demo():
    sensors = [
        (1, 'Главный офис (ул. Ленина, 5)'),
        (2, 'Офис продаж (пр. Независимости, 12)'),
        (3, 'Переговорная комната А'),
        (4, 'Архив документов'),
        (5, 'Серверная комната'),
    ]

    monitor = TemperatureMonitor()
    threads = []

    start = time.perf_counter()
    for sid, office in sensors:
        t = threading.Thread(target=monitor.poll_sensor, args=(sid, office))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = round(time.perf_counter() - start, 3)

    # Статистика
    temps = [r['temp'] for r in monitor.readings]
    avg_temp = round(sum(temps) / len(temps), 1) if temps else 0

    return {
        'log': monitor.log,
        'readings': monitor.readings,
        'alerts': monitor.alerts if monitor.alerts else ['✅ Все датчики в норме'],
        'avg_temp': avg_temp,
        'total_readings': len(monitor.readings),
        'elapsed': elapsed,
    }


# ═══════════════════════════════════════════════════════════
# ЗАДАЧА Б: Multiprocessing — обработка кадра камеры (яркость)
# ═══════════════════════════════════════════════════════════

def process_frame_segment(args):
    """
    Обрабатывает сегмент кадра с камеры наблюдения.
    Применяет коррекцию яркости и контраста к матрице пикселей.
    """
    segment_id, rows, cols, brightness_factor = args
    result_pixels = []

    for row in range(rows):
        for col in range(cols):
            # Имитация пикселя (градации серого 0-255)
            original = random.randint(0, 255)
            # Коррекция яркости: умножение + ограничение 0-255
            adjusted = min(255, max(0, int(original * brightness_factor)))
            # Гамма-коррекция (CPU-интенсивная операция)
            gamma = math.pow(adjusted / 255.0, 0.8) * 255 if adjusted > 0 else 0
            result_pixels.append(round(gamma))

    avg_brightness = sum(result_pixels) / len(result_pixels) if result_pixels else 0
    dark_pixels = sum(1 for p in result_pixels if p < 64)
    bright_pixels = sum(1 for p in result_pixels if p > 192)

    return {
        'segment': segment_id,
        'pixels_processed': len(result_pixels),
        'avg_brightness': round(avg_brightness, 1),
        'dark_pixels': dark_pixels,
        'bright_pixels': bright_pixels,
        'label': f'Сегмент {segment_id} ({rows}×{cols} пикс.)',
    }


def run_multiprocessing_demo():
    # Кадр 200×200 пикселей разбит на 4 сегмента по 50×200
    frame_segments = [
        (1, 50, 200, 1.2),   # верхняя часть, повышение яркости
        (2, 50, 200, 1.0),   # вторая четверть, без изменений
        (3, 50, 200, 0.8),   # третья четверть, снижение яркости
        (4, 50, 200, 1.1),   # нижняя часть, небольшое повышение
    ]

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(process_frame_segment, frame_segments))
    elapsed = round(time.perf_counter() - start, 3)

    total_pixels = sum(r['pixels_processed'] for r in results)
    overall_brightness = round(
        sum(r['avg_brightness'] for r in results) / len(results), 1
    )

    return {
        'results': results,
        'total_pixels': total_pixels,
        'overall_brightness': overall_brightness,
        'elapsed': elapsed,
        'frame_size': '200×200',
        'workers': 4,
    }


# ═══════════════════════════════════════════════════════════
# ЗАДАЧА В: Asyncio — управление смарт-лампами
# ═══════════════════════════════════════════════════════════

async def control_smart_lamp(lamp_id, room_name, action='on'):
    """
    Асинхронная команда смарт-лампе в офисе агентства.
    Имитирует сетевой запрос к IoT устройству.
    """
    delay = random.uniform(0.05, 0.2)  # разное время отклика у ламп
    await asyncio.sleep(delay)

    success = random.random() > 0.1  # 90% успешно, 10% ошибка связи

    return {
        'lamp_id': lamp_id,
        'room': room_name,
        'action': 'Включить' if action == 'on' else 'Выключить',
        'status': '✅ Выполнено' if success else '❌ Нет связи',
        'response_ms': round(delay * 1000),
        'brightness': random.randint(60, 100) if success else 0,
    }


async def control_all_lamps():
    lamps = [
        (1,  'Главный офис — зал приёма клиентов'),
        (2,  'Главный офис — кабинет директора'),
        (3,  'Главный офис — переговорная'),
        (4,  'Офис продаж — рабочая зона'),
        (5,  'Офис продаж — ресепшен'),
        (6,  'Архив — основной свет'),
        (7,  'Архив — дополнительная подсветка'),
        (8,  'Серверная — аварийное освещение'),
        (9,  'Коридор 1-й этаж'),
        (10, 'Коридор 2-й этаж'),
    ]
    tasks = [control_smart_lamp(lid, room) for lid, room in lamps]
    return await asyncio.gather(*tasks)


def run_asyncio_demo():
    start = time.perf_counter()
    results = asyncio.run(control_all_lamps())
    elapsed = round(time.perf_counter() - start, 3)

    success_count = sum(1 for r in results if '✅' in r['status'])
    avg_response = round(
        sum(r['response_ms'] for r in results) / len(results), 1
    )

    return {
        'results': list(results),
        'total': len(results),
        'success': success_count,
        'failed': len(results) - success_count,
        'avg_response_ms': avg_response,
        'elapsed': elapsed,
    }


# ═══════════════════════════════════════════════════════════
# View
# ═══════════════════════════════════════════════════════════

def multitasking_demo(request):
    run = request.GET.get('run', '')
    context = {'run': run}

    if run in ('a', 'all'):
        context['threading_result'] = run_threading_demo()
    if run in ('b', 'all'):
        context['mp_result'] = run_multiprocessing_demo()
    if run in ('c', 'all'):
        context['asyncio_result'] = run_asyncio_demo()

    return render(request, 'multitasking.html', context)
