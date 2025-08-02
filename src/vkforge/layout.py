from .schema import VkForgeModel
from .mappings import *
from typing import List, Tuple, Dict


def print_unsupported_warning(id: str, reflect: dict):
    unsupported = [SHADER.SUBPASS]
    for r in reflect.keys():
        if r in unsupported:
            print(f"WARNING: VkForge does not support {r} in shader {id}.")


def raise_unrecognized_error(id: str, reflect: dict):
    recognized = [
        REFLECT.IMAGE, 
        REFLECT.UBO, 
        REFLECT.SSBO, 
        REFLECT.TEXTURE, 
        REFLECT.SAMPLER_IMAGE, 
        REFLECT.SAMPLER,
        REFLECT.SUBPASS,
        REFLECT.ENTRYPOINT,
        REFLECT.INPUT,
        REFLECT.OUTPUT,
        REFLECT.TYPE,
    ]

    unrecognized = []
    for r in reflect.keys():
        if not r in recognized:
            unrecognized.append(r)
    if len(unrecognized) > 0:
        raise ValueError(
            f"ERROR: VkForge does not recognize the {unrecognized} in your shader {id}"
        )


def get_reflect_member_size(member: dict) -> int:
    if MEMBER.ARRAY_LITERAL in member and MEMBER.ARRAY in member:
        if member[MEMBER.ARRAY_LITERAL] == [True]:
            return sum(member[MEMBER.ARRAY])
    return 1


def create_descriptorsets(shader: dict):
    dset_types = [
        REFLECT.IMAGE, 
        REFLECT.UBO, 
        REFLECT.SSBO, 
        REFLECT.TEXTURE, 
        REFLECT.SAMPLER_IMAGE, 
        REFLECT.SAMPLER
    ]

    reflect = shader[SHADER.REFLECT]
    mode    = shader[SHADER.MODE]

    dsets = []

    for dset_type in dset_types:
        if dset_type in reflect.keys():
            members = reflect[dset_type]
            for member in members:
                type = member[MEMBER.TYPE]
                if REFLECT.TYPE in reflect and type in reflect[REFLECT.TYPE]:
                    type = dset_type
                set = member[MEMBER.SET]
                binding = member[MEMBER.BIND]
                count = get_reflect_member_size(member)
                dsets.append((mode, set, binding, type, count))

    return dsets


def check_for_errors_single_descriptorsets(
    id: str, dsets: List[Tuple[str, int, int, str, int]]
):
    for i, dset in enumerate(dsets):
        if i == len(dsets) - 1:
            break
        mode1, set1, binding1, dtype1, count1 = dset
        for e in dsets[i + 1 :]:
            mode2, set2, binding2, dtype2, count2 = e
            if set1 == set2 and binding1 == binding2 and mode1 == mode2:
                raise ValueError(
                    f"set {set1} and binding {binding1} overlapped for shader {id}"
                )


def check_for_errors_group_descriptorsets(shader_combo_dsets: Dict[str, List[Tuple]],):
    for i, (id, dsets) in enumerate(shader_combo_dsets.items()):
        if i == len(shader_combo_dsets) - 1:
            break
        for mode1, set1, binding1, dtype1, count1 in dsets:
            for j, (id2, descriptorsets2) in enumerate(shader_combo_dsets.items()):
                if j < i + 1:
                    continue
                for mode2, set2, binding2, dtype2, count2 in descriptorsets2:
                    if set1 == set2 and binding1 == binding2 and mode1 == mode2:
                        raise ValueError(
                            f"set {set1} and binding {binding1} overlapped for shaders {id} and {id2}. "
                            f"This is not allowed since bother shaders are grouped together in a single pipeline."
                        )
                    elif set1 == set2 and binding1 == binding2 and dtype1 != dtype2:
                        raise ValueError(
                            f"set {set1} and binding {binding1} have "
                            f"different types {dtype1}, {dtype2} in {id}, {id2} shaders"
                        )

def descriptorset_dict_to_list(dset_group: dict,):
    sets = set()
    for _, dsets in dset_group.items():
        for dset in dsets:
            sets.add(dset)
    return list(sets)


def create_descriptorset_layout_per_dset_group(dset_group: dict,) -> List[dict]:
    layouts: Dict[Tuple, dict] = {}

    dset_list = descriptorset_dict_to_list(dset_group)

    for dset in dset_list:
        d_mode, d_set, d_binding, d_type, d_count = dset
        key = (d_set, d_binding, d_type, d_count)
        if key in layouts:
            current = layouts[key]
            if not d_mode in current[LAYOUT.STAGES]:
                current[LAYOUT.STAGES].append(d_mode)
        else:
            binding = {
                LAYOUT.SET    :  d_set,
                LAYOUT.BIND   :  d_binding,
                LAYOUT.TYPE   :  d_type,
                LAYOUT.COUNT  :  d_count,
                LAYOUT.STAGES : [d_mode]
            }
            layouts[key] = binding

    return [value for key, value in layouts.items()]

def combine_descriptorset_layouts(layouts: Dict[Tuple, dict]):
    new_layouts = {}
    for key in layouts:
        if not key in new_layouts:
            new_layouts[key] = layouts[key]
        else:
            new_layouts[key][LAYOUT.STAGES].extend(layouts[key][LAYOUT.STAGES])
            new_layouts[key][LAYOUT.STAGES] = list(set([key][LAYOUT.STAGES]))

def create_descriptorset_layouts_from_list_of_shader_dsets(shader_dset_list: List[dict]):
    layouts = []
    for shader_dset in shader_dset_list:
        layouts.append(create_descriptorset_layout_per_dset_group(shader_dset))

def create_descriptorset_layouts(fm: VkForgeModel, sd: dict):
    shader_dset_list = []

    for shader_combo in sd[SHADER.COMBO]:
        shader_combo_dsets = {}

        for id in shader_combo:
            shader = sd[SHADER.LIST].get(id)
            reflect = shader[SHADER.REFLECT]

            print_unsupported_warning(id, reflect)
            raise_unrecognized_error(id, reflect)

            dsets = create_descriptorsets(shader)
            check_for_errors_single_descriptorsets(id, dsets)

            shader_combo_dsets[id] = dsets
        check_for_errors_group_descriptorsets(shader_combo_dsets)
        shader_dset_list.append(shader_combo_dsets)

    return create_descriptorset_layouts_from_list_of_shader_dsets(shader_dset_list)
