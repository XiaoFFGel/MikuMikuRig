import bpy
import json
import os

class ProxyModelOperator(bpy.types.Operator):
    '''ProxyModelOperator'''
    bl_idname = "object.proxy_model_ops"
    bl_label = "Open Proxy Model"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == 'ARMATURE'

    def execute(self, context: bpy.types.Context):
        arm = context.view_layer.objects.active

        def new_align_bone_to_parent(armature, bone):
            edit_bone = armature.data.edit_bones.get(bone.name)
            new_bone = armature.data.edit_bones.new(name=bone.name + "_proxy")
            new_bone.head = edit_bone.head
            new_bone.tail = edit_bone.tail
            new_bone.roll = edit_bone.roll
            new_bone.parent = edit_bone
            return new_bone.name

        new_bone_collections = {
    "spine_proxy": [
        "ORG-spine",
    ],
    "thigh_proxy": [
        "ORG-thigh",
    ],
    "shin_proxy": [
        "ORG-shin",
    ],
    "foot_proxy": [
        "ORG-foot",
    ],
    "toe_proxy": [
        "ORG-toe",
    ],
    "eye_proxy": [
        "ORG-eye",
    ],
    "shoulder_proxy": [
        "ORG-shoulder",
    ],
    "upper_arm_proxy": [
        "ORG-upper_arm",
    ],
    "forearm_proxy": [
        "ORG-forearm",
    ],
    "hand_proxy": [
        "ORG-hand",
    ],
    "手捩_proxy": [
        "ORG-手捩",
    ],
    "腕捩_proxy": [
        "ORG-腕捩",
    ],
    "Finger_proxy": [
        "ORG-thumb",
        "ORG-f_index",
        "ORG-f_middle",
        "ORG-f_ring",
        "ORG-f_pinky",
    ],
}
        new_bone_names = []
        for collection in arm.data.collections:
            if collection.name == "_parent":

                for bone in collection.bones:

                    # 进入编辑模式
                    bpy.ops.object.mode_set(mode='EDIT')

                    new_bone_name = new_align_bone_to_parent(arm, bone)
                    new_bone_names.append(new_bone_name)

        # 退出编辑模式
        bpy.ops.object.mode_set(mode='POSE')

        # 设置显示类型
        for bone_name in new_bone_names:
            data_bone = arm.data.bones.get(bone_name)
            if data_bone:
                data_bone.display_type = 'BBONE'
                data_bone.bbone_x = data_bone.bbone_z = 0.015

        # 将新骨骼分配到对应的集合中
        for collection_name, bone_names in new_bone_collections.items():
            if collection_name not in arm.data.collections:
                new_bone_collection = arm.data.collections.new(name=collection_name)
            else:
                new_bone_collection = arm.data.collections[collection_name]

            # 分配新骨骼到集合
            for bone_name in bone_names:
                for bone1_name in new_bone_names:
                    if bone_name in bone1_name:
                        print(bone_name+":"+bone1_name)
                        if arm.pose.bones.get(bone1_name):
                            arm.data.collections[new_bone_collection.name].assign(arm.pose.bones[bone1_name])
                            arm.pose.bones[bone1_name].mmr_bone.proxy_bool = True # 标记为代理骨骼

        # 加载sokj.json
        with open(os.path.join(os.path.dirname(__file__), "sokj.json"), "r") as f:
            bbone_dict = json.load(f)

        # 应用bbone_dict
        for bone_name, values in bbone_dict.items():
            pb = arm.pose.bones.get(bone_name)
            if pb is None or not (isinstance(values, (list, tuple)) and len(values) == 2):
                print(f"[WARN] 未找到或数据错误：{bone_name}")
                continue
            pb.bone.bbone_x, pb.bone.bbone_z = values[0], values[1]

        arm.mmr.openproxy = True

        return {'FINISHED'}

# 切换可选代理
class SwitchProxyOperator(bpy.types.Operator):
    '''SwitchProxyOperator'''
    bl_idname = "mmr.switch_proxy_ops"
    bl_label = "Switch Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == 'ARMATURE' and obj.mode == 'POSE'

    def execute(self, context):

        arm = context.view_layer.objects.active

        arm.mmr.switch_proxy_bool = not arm.mmr.switch_proxy_bool # 切换状态

        for bone in arm.pose.bones:
            if bone.mmr_bone.proxy_bool:

                if arm.mmr.switch_proxy_bool:
                    bone.hide_select = True
                else:
                    bone.hide_select = False

        return {'FINISHED'}
