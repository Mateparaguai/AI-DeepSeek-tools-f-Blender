import bpy

# Получаем список выделенных объектов
selected_objects = bpy.context.selected_objects

# Проверяем, что выбрано больше одного объекта
if len(selected_objects) < 2:
    print("Выберите хотя бы два объекта!")
else:
    # Определяем начальную позицию и шаг для распределения
    start_position = selected_objects[0].location.x
    step = 2.0  # Расстояние между объектами (можно изменить)

    # Расставляем объекты на равном расстоянии вдоль оси X
    for i, obj in enumerate(selected_objects):
        obj.location.x = start_position + i * step

    print("Объекты успешно расставлены!")