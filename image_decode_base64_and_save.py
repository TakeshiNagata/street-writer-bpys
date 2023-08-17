bl_info = {
    "name": "Base64 Image Importer",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import bpy
import base64
import os
import tempfile

def import_base64_image(base64_filepath):
    # Base64データのデコード
    with open(base64_filepath, 'r') as file:
        encoded_data = file.read()
        if "base64," in encoded_data:
            encoded_data = encoded_data.split(",")[1]
        decoded_data = base64.b64decode(encoded_data)
    
    # 一時的なPNGファイル名を生成
    image_name = bpy.path.basename(base64_filepath).replace('.base64', '.png')
    temp_file_path = os.path.join(tempfile.gettempdir(), image_name)

    # 保存
    with open(temp_file_path, 'wb') as file:
        file.write(decoded_data)

    # 画像をBlenderにインポート
    bpy.ops.image.open(filepath=temp_file_path)
    
    # 画像をBlenderの内部データとして保存
    if image_name in bpy.data.images:
        bpy.data.images[image_name].pack()

    # 一時ファイルを削除
    os.remove(temp_file_path)

    print(f"Image imported as {image_name} from {base64_filepath}!")

class IMPORT_OT_base64_image(bpy.types.Operator):
    bl_idname = "image.import_base64"
    bl_label = "Import Base64 Image"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(name="Base64 Filepath", subtype='FILE_PATH')

    def execute(self, context):
        import_base64_image(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(IMPORT_OT_base64_image.bl_idname, text="Base64 Image (.base64)")

def register():
    bpy.utils.register_class(IMPORT_OT_base64_image)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_class(IMPORT_OT_base64_image)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
