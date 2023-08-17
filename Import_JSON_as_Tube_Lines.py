bl_info = {
    "name": "Import JSON as Tube Lines",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import json

class IMPORT_OT_json_tube(bpy.types.Operator):
    bl_idname = "object.import_json_tube"
    bl_label = "Import JSON as Tube Lines"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        file_path = self.filepath
        clear_data = context.scene.json_tube_clear_data
        line_width_multiplier = context.scene.json_tube_line_width_multiplier
        
        if not file_path:
            self.report({'ERROR'}, "File path is not specified!")
            return {'CANCELLED'}

        # 1. Optionally clear all existing materials and objects
        if clear_data:
            bpy.ops.object.select_all(action='DESELECT')
            for material in bpy.data.materials:
                bpy.data.materials.remove(material)
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
        
        # Load the JSON data
        with open(file_path, 'r') as f:
            data = json.load(f)

        frame_num = 1
        
        # Create a single material
        mat = bpy.data.materials.new(name="Tube_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        emission = nodes.new('ShaderNodeEmission')
        output = nodes.get("Material Output")
        links.new(emission.outputs["Emission"], output.inputs["Surface"])
        
        # Attribute node to get color from object's custom properties
        attr_node = nodes.new('ShaderNodeAttribute')
        attr_node.attribute_name = "color"
        attr_node.attribute_type = 'OBJECT'  # <-- この行を追加
        links.new(attr_node.outputs["Color"], emission.inputs["Color"])


        for key, entry in data.items():
            if entry['points']:
                curve = bpy.data.curves.new(name=key, type='CURVE')
                curve.dimensions = '3D'
                curve.resolution_u = 2
                curve.bevel_depth = float(entry['lineWidth']) * line_width_multiplier
                curve.use_fill_caps = True
                
                polyline = curve.splines.new('POLY')
                polyline.points.add(len(entry['points'])-1)
                
                for i, point in enumerate(entry['points']):
                    x, y, z = point['x'], -point['z'], point['y']
                    polyline.points[i].co = (x, y, z, 1)
                    if i == 0 or i == len(entry['points']) - 1:
                        polyline.points[i].radius = 0
                
                obj = bpy.data.objects.new(key, curve)
                bpy.context.collection.objects.link(obj)
                
                color_tuple = (entry['color']['r'], entry['color']['g'], entry['color']['b'])
                obj["color"] = color_tuple
                
                obj.data.materials.append(mat)
                
                obj.hide_render = True
                obj.keyframe_insert(data_path="hide_render", frame=frame_num - 1)
                obj.hide_render = False
                obj.keyframe_insert(data_path="hide_render", frame=frame_num)

                obj.hide_viewport = True
                obj.keyframe_insert(data_path="hide_viewport", frame=frame_num - 1)
                obj.hide_viewport = False
                obj.keyframe_insert(data_path="hide_viewport", frame=frame_num)
                
                frame_num += 1
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OBJECT_PT_json_tube_importer(bpy.types.Panel):
    bl_label = "Import JSON as Tube Lines"
    bl_idname = "OBJECT_PT_json_tube_importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(context.scene, "json_tube_clear_data", text="Clear Existing Data")
        col.prop(context.scene, "json_tube_line_width_multiplier", text="Line Width Multiplier")
        col.operator("object.import_json_tube", text="Import JSON")


def register():
    bpy.utils.register_class(IMPORT_OT_json_tube)
    bpy.utils.register_class(OBJECT_PT_json_tube_importer)
    
    bpy.types.Scene.json_tube_clear_data = bpy.props.BoolProperty(
        name="Clear Existing Data",
        default=True,
    )
    bpy.types.Scene.json_tube_line_width_multiplier = bpy.props.FloatProperty(
        name="Line Width Multiplier",
        default=1.0,
        min=0.1,
        max=10.0,
    )


def unregister():
    bpy.utils.unregister_class(IMPORT_OT_json_tube)
    bpy.utils.unregister_class(OBJECT_PT_json_tube_importer)
    
    del bpy.types.Scene.json_tube_clear_data
    del bpy.types.Scene.json_tube_line_width_multiplier


if __name__ == "__main__":
    register()
