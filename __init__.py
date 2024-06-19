bl_info = {
    "name": "Lsystem Modifier",
    "blender": (2, 93, 0),
    "category": "Object",
}

import bpy
from .Lsystemmodifer import (
    LSystemRule,
    LSystemModifier,
    OBJECT_OT_AddLSystemRule,
)

def register():
    bpy.utils.register_class(LSystemRule)
    bpy.utils.register_class(LSystemModifier)
    bpy.utils.register_class(OBJECT_OT_AddLSystemRule)

def unregister():
    bpy.utils.unregister_class(LSystemRule)
    bpy.utils.unregister_class(LSystemModifier)
    bpy.utils.unregister_class(OBJECT_OT_AddLSystemRule)

if __name__ == "__main__":
    register()
