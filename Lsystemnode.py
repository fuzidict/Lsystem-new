bl_info = {
    "name": "Lsystem Node",
    "blender": (2, 93, 0),
    "category": "Node",
}

import bpy
import math
import mathutils
import re
import random
from bpy.types import Node, NodeSocket, NodeCustomGroup
from bpy.props import IntProperty, FloatProperty, StringProperty, CollectionProperty

class LSystem:
    def __init__(self, numIters, startStr, rules, step_length, default_angle, mesh_dict):
        self.numIters = numIters
        self.startStr = startStr
        self.rules = rules
        self.step_length = step_length
        self.default_angle = default_angle
        self.resultStrs = [self.startStr]
        self.vertices = []
        self.edges = []
        self.faces = []
        self.vertex_index = 0
        self.mesh_objects = []
        self.mesh_dict = mesh_dict  # Dictionary to store mesh objects
        self.generate()

    def generate(self):
        oldStr = self.startStr
        for i in range(self.numIters):
            newStr = self.replaceProcess(oldStr)
            oldStr = newStr
            self.resultStrs.append(newStr)

    def replaceProcess(self, oldStr):
        return ''.join(self.replace(char) for char in oldStr)

    def replace(self, char):
        return self.rules.get(char, char)

    def extract_value(self, instruction):
        match = re.match(r'([A-Za-z\+\-&^\\\/|])\((\d+)\)', instruction)
        if match:
            return match.group(1), float(match.group(2))
        return instruction, None

    def draw(self):
        direction = mathutils.Vector([0, 0, 1])
        location = mathutils.Vector((0, 0, 0))
        stack = []

        for rule in self.resultStrs:
            index = 0
            while index < len(rule):
                instruction = rule[index]
                if index + 2 < len(rule) and rule[index + 1] == '(':
                    end_index = rule.find(')', index)
                    instruction = rule[index:end_index + 1]
                    index = end_index
                symbol, value = self.extract_value(instruction)

                if symbol in self.mesh_dict:
                    self.add_mesh_instance(symbol, location, direction)
                elif symbol == "F":
                    step = value if value is not None else self.step_length
                    new_location = location + direction * step
                    self.add_line(location, new_location)
                    location = new_location
                elif symbol == "f":
                    step = value if value is not None else self.step_length
                    location += direction * step
                elif symbol == "[":
                    stack.append((location.copy(), direction.copy()))
                elif symbol == "]":
                    location, direction = stack.pop()
                else:
                    self.rotate_direction(symbol, direction, value)
                index += 1
        
        self.create_mesh()

    def rotate_direction(self, symbol, direction, value):
        angle = math.radians(value if value is not None else self.default_angle)
        rotations = {
            "+": (0, 0, angle),
            "-": (0, 0, -angle),
            "&": (angle, 0, 0),
            "^": (-angle, 0, 0),
            "<": (0, angle, 0),
            ">": (0, -angle, 0),
            "|": (0, 0, math.pi)
        }
        if symbol in rotations:
            direction.rotate(mathutils.Euler(rotations[symbol], 'XYZ'))

    def add_line(self, start, end):
        if self.vertex_index == 0 or (start.x, start.y, start.z) != self.vertices[-1]:
            self.vertices.append((start.x, start.y, start.z))
            self.vertex_index += 1
        self.vertices.append((end.x, end.y, end.z))
        self.edges.append((self.vertex_index - 1, self.vertex_index))
        self.vertex_index += 1

    def add_mesh_instance(self, symbol, location, direction):
        mesh = self.mesh_dict[symbol]
        mesh_instance = mesh.copy()
        bpy.context.collection.objects.link(mesh_instance)
        mesh_instance.location = location

        # Generate random rotation
        random_rotation = mathutils.Euler((random.uniform(0, 2 * math.pi),
                                           random.uniform(0, 2 * math.pi),
                                           random.uniform(0, 2 * math.pi)), 'XYZ')
        mesh_instance.rotation_euler = random_rotation

    def create_mesh(self):
        mesh_data = bpy.data.meshes.new("LSystemMesh")
        mesh_data.from_pydata(self.vertices, self.edges, self.faces)  # Include faces
        mesh_data.update()

        mesh_object = bpy.data.objects.new("LSystemObject", mesh_data)
        bpy.context.collection.objects.link(mesh_object)

        # Ensure the mesh object is active and selected
        bpy.context.view_layer.objects.active = mesh_object
        mesh_object.select_set(True)
        
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].levels = 3

        
        # Merge vertices by distance
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply skin modifier
        bpy.ops.object.modifier_add(type='SKIN')
        
        # Adjust skin modifier thickness
        for vertex in mesh_object.data.vertices:
            skin_vertex = mesh_object.data.skin_vertices[0].data[vertex.index]
            skin_vertex.radius = [0.02, 0.02]  # Adjust the radius to the desired thickness

# Define input and output socket types
class LSystemNodeSocket(NodeSocket):
    bl_idname = 'LSystemNodeSocket'
    bl_label = 'LSystem Node Socket'
    
    default_value: StringProperty()

    def draw(self, context, layout, node, text):
        layout.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.6, 0.6, 0.2, 1.0)

# Define the custom node
class LSystemNode(NodeCustomGroup):
    bl_idname = 'LSystemNode'
    bl_label = 'Lsystem Node'
    bl_icon = 'NODE'
    
    numIters: IntProperty(name='Iterations', default=20)
    step_length: FloatProperty(name='Step Length', default=1.0)
    default_angle: FloatProperty(name='Default Angle', default=80.0)
    startStr: StringProperty(name='Start String', default='&SYS')
    rules: CollectionProperty(name='Rules', type=bpy.types.PropertyGroup)
    
    def init(self, context):
        self.inputs.new('NodeSocketInt', 'Iterations')
        self.inputs.new('NodeSocketFloat', 'Step Length')
        self.inputs.new('NodeSocketFloat', 'Default Angle')
        self.inputs.new('LSystemNodeSocket', 'Start String')
        self.inputs.new('LSystemNodeSocket', 'Rules')
        self.outputs.new('NodeSocketGeometry', 'Geometry')
    
    def update(self):
        for output in self.outputs:
            output.default_value = None  # Dummy value to trigger update
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'numIters')
        layout.prop(self, 'step_length')
        layout.prop(self, 'default_angle')
        layout.prop(self, 'startStr')
        
        row = layout.row()
        row.label(text='Rules:')
        row.operator('node.add_lsystem_rule', text='Add Rule')

class NODE_OT_AddLSystemRule(bpy.types.Operator):
    bl_idname = 'node.add_lsystem_rule'
    bl_label = 'Add Lsystem Rule'
    bl_description = 'Add a new rule to the Lsystem node'
    
    def execute(self, context):
        node = context.node
        node.rules.add()
        return {'FINISHED'}

def node_category_func(self, context):
    self.layout.operator("node.add_node", text="Lsystem Node", icon="NODE")
    
def register():
    bpy.utils.register_class(LSystemNodeSocket)
    bpy.utils.register_class(LSystemNode)
    bpy.utils.register_class(NODE_OT_AddLSystemRule)
    bpy.types.NODE_MT_add.append(node_category_func)

def unregister():
    bpy.utils.unregister_class(LSystemNodeSocket)
    bpy.utils.unregister_class(LSystemNode)
    bpy.utils.unregister_class(NODE_OT_AddLSystemRule)
    bpy.types.NODE_MT_add.remove(node_category_func)

if __name__ == '__main__':
    register()