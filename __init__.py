bl_info = {
    "name": "Lsystem Modifier",
    "blender": (2, 93, 0),
    "category": "Object",
}

import bpy
from .LSM import (
    LSystemRule,
    LSystemModifierProperties,
    OBJECT_OT_AddLSystemRule,
    OBJECT_OT_ApplyLSystemModifier,
)

def register():
    bpy.utils.register_class(LSystemRule)
    bpy.utils.register_class(LSystemModifierProperties)
    bpy.utils.register_class(OBJECT_OT_AddLSystemRule)
    bpy.utils.register_class(OBJECT_OT_ApplyLSystemModifier)
    bpy.types.Object.lsystem_modifier = bpy.props.PointerProperty(type=LSystemModifierProperties)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(LSystemRule)
    bpy.utils.unregister_class(LSystemModifierProperties)
    bpy.utils.unregister_class(OBJECT_OT_AddLSystemRule)
    bpy.utils.unregister_class(OBJECT_OT_ApplyLSystemModifier)
    del bpy.types.Object.lsystem_modifier
    bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_ApplyLSystemModifier.bl_idname)

if __name__ == "__main__":
    register()

