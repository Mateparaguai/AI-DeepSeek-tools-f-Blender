bl_info = {
    "name": "Add Animation",
    "blender": (4, 0, 0),
    "category": "Animation",
    "author": "Your Name",
    "version": (1, 0),
    "description": "Adds animations to the NLA Editor based on a search text.",
}

import bpy

# Определение панели
class AddAnimationPanel(bpy.types.Panel):
    bl_label = "Add Animation"
    bl_idname = "OBJECT_PT_add_animation_panel"
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        # Получаем значение текста из настроек
        text = context.scene.animation_search_text

        # Отображаем текстовое поле
        layout.prop(context.scene, "animation_search_text", text="Search Text")

        # Кнопка для добавления анимаций на трек
        layout.operator("object.add_animation_to_nla", text="Add Animations")


# Определение оператора
class OBJECT_OT_AddAnimationToNLA(bpy.types.Operator):
    bl_label = "Add Animations to NLA"
    bl_idname = "object.add_animation_to_nla"

    def execute(self, context):
        text = context.scene.animation_search_text

        # Получаем активный объект
        obj = bpy.context.active_object

        if obj and obj.animation_data:
            for action in bpy.data.actions:
                # Проверяем, содержит ли имя анимации указанный текст
                if text.lower() in action.name.lower():
                    # Создаем новый трек в NLA Editor
                    track = obj.animation_data.nla_tracks.new()

                    # Создаем новый strip в треке для найденной анимации
                    strip = track.strips.new(action.name, start=0, action=action)

        return {'FINISHED'}


# Регистрация классов и свойств
classes = (
    AddAnimationPanel,
    OBJECT_OT_AddAnimationToNLA,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.animation_search_text = bpy.props.StringProperty(
        name="Search Text",
        description="Text to search for in animation names",
        default=""
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.animation_search_text


if __name__ == "__main__":
    register()