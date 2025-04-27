bl_info = {
    "name": "Random Keyframe Offset",
    "blender": (4, 0, 0),
    "category": "Animation",
    "version": (1, 0),
    "author": "Your Name",
    "description": "Randomly offsets selected keyframes for objects and bones, with direction options.",
}

import bpy
import random

class RandomKeyframeOffsetPanel(bpy.types.Panel):
    bl_label = "Random Keyframe Offset"
    bl_idname = "ACTION_PT_random_keyframe_offset"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Диапазон сдвига
        row = layout.row()
        row.prop(scene, "random_offset_range", text="Offset Range")

        # Кнопки выбора направления
        row = layout.row()
        row.prop(scene, "offset_direction", expand=True)

        # Кнопка применения сдвига
        row = layout.row()
        row.operator("action.random_keyframe_offset", text="Apply Random Offset")

class RandomKeyframeOffsetOperator(bpy.types.Operator):
    bl_idname = "action.random_keyframe_offset"
    bl_label = "Random Keyframe Offset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        offset_range = scene.random_offset_range
        offset_direction = scene.offset_direction

        # Получаем все выделенные объекты и кости
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.animation_data]
        selected_bones = self.get_selected_bones(context)

        # Обрабатываем объекты
        for obj in selected_objects:
            action = obj.animation_data.action
            if not action:
                continue

            # Генерируем случайное значение сдвига для каждого объекта
            random_offset = self.get_random_offset(offset_range, offset_direction)

            # Сдвигаем ключи для всех F-Curves объекта
            for fcurve in action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    if keyframe.select_control_point:
                        keyframe.co.x += random_offset

        # Обрабатываем кости
        for bone in selected_bones:
            action = bone.id_data.animation_data.action
            if not action:
                continue

            # Генерируем случайное значение сдвига для каждой кости
            random_offset = self.get_random_offset(offset_range, offset_direction)

            # Сдвигаем ключи для всех F-Curves кости
            for fcurve in action.fcurves:
                if fcurve.data_path.startswith(f'pose.bones["{bone.name}"]'):
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.select_control_point:
                            keyframe.co.x += random_offset

        return {'FINISHED'}

    def get_selected_bones(self, context):
        # Получаем выделенные кости в Pose Mode
        selected_bones = []
        if context.mode == 'POSE':
            for bone in context.selected_pose_bones:
                selected_bones.append(bone)
        return selected_bones

    def get_random_offset(self, offset_range, direction):
        # Генерируем случайное значение сдвига в зависимости от выбранного направления
        if direction == 'POSITIVE':
            return random.randint(1, offset_range)
        elif direction == 'NEGATIVE':
            return random.randint(-offset_range, -1)
        else:  # 'BOTH'
            return random.randint(-offset_range, offset_range)

# Свойства сцены
def register_properties():
    bpy.types.Scene.random_offset_range = bpy.props.IntProperty(
        name="Offset Range",
        description="Range for random keyframe offset",
        default=30,
        min=0
    )
    bpy.types.Scene.offset_direction = bpy.props.EnumProperty(
        name="Direction",
        description="Direction of the offset",
        items=[
            ('POSITIVE', "Positive", "Only positive offset"),
            ('NEGATIVE', "Negative", "Only negative offset"),
            ('BOTH', "Both", "Both positive and negative offset"),
        ],
        default='BOTH'
    )

def unregister_properties():
    del bpy.types.Scene.random_offset_range
    del bpy.types.Scene.offset_direction

# Регистрация аддона
def register():
    bpy.utils.register_class(RandomKeyframeOffsetPanel)
    bpy.utils.register_class(RandomKeyframeOffsetOperator)
    register_properties()

def unregister():
    bpy.utils.unregister_class(RandomKeyframeOffsetPanel)
    bpy.utils.unregister_class(RandomKeyframeOffsetOperator)
    unregister_properties()

if __name__ == "__main__":
    register()