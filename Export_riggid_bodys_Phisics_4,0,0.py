import bpy
from mathutils import Vector

# Оператор для создания костей, которые следуют за объектами
class OBJECT_OT_create_follow_bones(bpy.types.Operator):
    bl_idname = "object.create_follow_bones"
    bl_label = "Create Follow Bones"
    bl_description = "Create bones that follow the selected objects' animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        # Создаём новую armature (риг)
        armature = bpy.data.armatures.new("Follow_Armature")
        armature_obj = bpy.data.objects.new("Follow_Armature", armature)
        bpy.context.collection.objects.link(armature_obj)

        # Переходим в режим редактирования armature
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        for obj in selected_objects:
            # Создаём кость в месте расположения объекта
            bone = armature.edit_bones.new(f"{obj.name}_Bone")
            
            # Начало кости в месте объекта
            bone.head = obj.location
            
            # Конец кости направлен вверх относительно ориентации объекта
            tail_offset = Vector((0, 0, 1))  # Вектор, направленный вверх
            tail_offset.rotate(obj.matrix_world.to_quaternion())  # Поворачиваем вектор согласно ориентации объекта
            bone.tail = obj.location + tail_offset

            # Применяем поворот объекта к кости
            bone.matrix = obj.matrix_world

        # Выходим из режима редактирования armature
        bpy.ops.object.mode_set(mode='OBJECT')

        # Добавляем constraints для каждой кости
        for obj in selected_objects:
            # Находим кость по имени
            bone_name = f"{obj.name}_Bone"
            bone_obj = armature_obj.pose.bones.get(bone_name)
            if not bone_obj:
                self.report({'WARNING'}, f"Bone {bone_name} not found!")
                continue

            # Копируем положение объекта
            copy_location = bone_obj.constraints.new(type='COPY_LOCATION')
            copy_location.target = obj

            # Копируем поворот объекта
            copy_rotation = bone_obj.constraints.new(type='COPY_ROTATION')
            copy_rotation.target = obj

            print(f"Bone created for object: {obj.name}")

        self.report({'INFO'}, "Follow bones created!")
        return {'FINISHED'}

# Оператор для запекания анимации костей
class OBJECT_OT_bake_bone_animation(bpy.types.Operator):
    bl_idname = "object.bake_bone_animation"
    bl_label = "Bake Bone Animation"
    bl_description = "Bake the animation of the bones and remove constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Находим armature в сцене
        armature_obj = None
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.name == "Follow_Armature":
                armature_obj = obj
                break

        if not armature_obj:
            self.report({'WARNING'}, "No armature found!")
            return {'CANCELLED'}

        # Переходим в режим поз
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')

        # Выбираем все кости
        bpy.ops.pose.select_all(action='SELECT')

        # Запекаем анимацию для всех костей
        bpy.ops.nla.bake(
            frame_start=bpy.context.scene.frame_start,
            frame_end=bpy.context.scene.frame_end,
            only_selected=True,  # Запекаем только выделенные кости
            visual_keying=True,
            clear_constraints=True,  # Удаляем constraints после запекания
            use_current_action=True,
            bake_types={'POSE'}
        )

        # Возвращаемся в объектный режим
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Bone animation baked!")
        return {'FINISHED'}

# Оператор для привязки объектов к костям
class OBJECT_OT_bind_objects_to_bones(bpy.types.Operator):
    bl_idname = "object.bind_objects_to_bones"
    bl_label = "Bind Objects to Bones"
    bl_description = "Bind the objects to their corresponding bones, remove Rigidbody, and parent to armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        # Находим armature в сцене
        armature_obj = None
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.name == "Follow_Armature":
                armature_obj = obj
                break

        if not armature_obj:
            self.report({'WARNING'}, "No armature found!")
            return {'CANCELLED'}

        for obj in selected_objects:
            # Удаляем Rigidbody с объекта
            if obj.rigid_body:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_remove()

            # Находим кость по имени
            bone_name = f"{obj.name}_Bone"
            bone = armature_obj.pose.bones.get(bone_name)
            if not bone:
                self.report({'WARNING'}, f"Bone {bone_name} not found!")
                continue

            # Сохраняем текущее мировое положение и поворот объекта
            world_matrix = obj.matrix_world.copy()

            # Добавляем модификатор Armature и привязываем к кости
            armature_modifier = obj.modifiers.new(name="Armature", type='ARMATURE')
            armature_modifier.object = armature_obj

            # Создаём группу вершин и привязываем её к кости
            vertex_group = obj.vertex_groups.new(name=bone_name)
            vertex_group.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')

            # Делаем объект дочерним для арматуры
            obj.parent = armature_obj
            obj.parent_type = 'BONE'  # Родитель — кость
            obj.parent_bone = bone_name

            # Восстанавливаем мировое положение и поворот объекта
            obj.matrix_world = world_matrix

            # Принудительно обновляем трансформации
            bpy.context.view_layer.update()

            # Отвязываем объект от родителя после привязки к кости
            obj.parent = None  # Отвязываем от арматуры
            obj.matrix_world = world_matrix  # Восстанавливаем мировую матрицу

            print(f"Object {obj.name} bound to bone {bone_name} and unparented")

        self.report({'INFO'}, "Objects bound to bones and unparented!")
        return {'FINISHED'}

# Панель для вызова операторов
class VIEW3D_PT_follow_bone_panel(bpy.types.Panel):
    bl_label = "Follow Bone Tools"
    bl_idname = "VIEW3D_PT_follow_bone_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        # Кнопка 1: Создание костей
        layout.operator("object.create_follow_bones", text="1. Create Follow Bones", icon='BONE_DATA')
        # Кнопка 2: Запекание анимации
        layout.operator("object.bake_bone_animation", text="2. Bake Bone Animation", icon='ACTION')
        # Кнопка 3: Привязка объектов к костям
        layout.operator("object.bind_objects_to_bones", text="3. Bind Objects to Bones", icon='CONSTRAINT_BONE')

# Регистрация классов
def register():
    bpy.utils.register_class(OBJECT_OT_create_follow_bones)
    bpy.utils.register_class(OBJECT_OT_bake_bone_animation)
    bpy.utils.register_class(OBJECT_OT_bind_objects_to_bones)
    bpy.utils.register_class(VIEW3D_PT_follow_bone_panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_create_follow_bones)
    bpy.utils.unregister_class(OBJECT_OT_bake_bone_animation)
    bpy.utils.unregister_class(OBJECT_OT_bind_objects_to_bones)
    bpy.utils.unregister_class(VIEW3D_PT_follow_bone_panel)

if __name__ == "__main__":
    register()