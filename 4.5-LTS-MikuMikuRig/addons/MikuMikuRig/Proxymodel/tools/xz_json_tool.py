import bpy
import json


def get_selected_bbone_dict(context, only_bbone=True):
    if context.mode != 'POSE':
        raise RuntimeError("请在 POSE 模式下运行")

    selected_bones = context.selected_pose_bones
    if not selected_bones:
        return {}

    result = {}
    for pb in selected_bones:
        if only_bbone and pb.bone.bbone_segments <= 1:
            continue
        result[pb.name] = [pb.bone.bbone_x, pb.bone.bbone_z]

    return result


def apply_bbone_dict(context, data):
    arm = context.active_object
    if arm is None or arm.type != 'ARMATURE':
        raise RuntimeError("请先选中一个 Armature 对象")

    missing = []
    for name, values in data.items():
        pb = arm.pose.bones.get(name)
        if pb is None or not (isinstance(values, (list, tuple)) and len(values) == 2):
            missing.append(name)
            continue
        pb.bone.bbone_x, pb.bone.bbone_z = values[0], values[1]

    if missing:
        print(f"[WARN] 未找到或数据错误：{missing}")

    context.view_layer.update()


def main():
    context = bpy.context

    bbone_dict = get_selected_bbone_dict(context, only_bbone=False)
    print("==== Selected B-Bone Dict ====")
    print(json.dumps(bbone_dict, indent=4, ensure_ascii=False))

    context.scene["selected_bbone_dict"] = bbone_dict

    # 测试写回：
    # apply_bbone_dict(context, {k: [0.1, 0.1] for k in bbone_dict})


if __name__ == "__main__":
    main()