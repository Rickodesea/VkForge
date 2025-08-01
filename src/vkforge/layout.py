from .schema import VkForgeConfig, VkShaderModule
from .shader import VkForgeShaderConfig, ShaderDetail
from .mappings import S
from dataclasses import dataclass, field
from typing import List, Tuple, Dict


@dataclass
class VkDescriptorSetLayoutBinding:
    binding: int = None
    descriptorType: str = None
    descriptorCount: int = None
    stageFlags: List[str] = None


@dataclass
class VkForgeLayout:
    layout_bindings: List[VkDescriptorSetLayoutBinding] = None


def print_warnings(id: str, R: dict):
    unsupported = [S.SUBPASS]
    for r in R.keys():
        if r in unsupported:
            print(f"WARNING: VkForge does not support {r} in shader {id}.")


def raise_errors(id: str, R: dict):
    recognized = [
        S.IMG,
        S.SSBO,
        S.SUBPASS,
        S.TEX_IMG,
        S.TEX_SAM,
        S.ENTRY,
        S.IN,
        S.OUT,
        S.UBO,
    ]

    unrecognized = []
    for r in R.keys():
        if not r in recognized:
            unrecognized.append(r)
    if len(unrecognized) > 0:
        raise ValueError(
            f"ERROR: VkForge does not recognize the {unrecognized} in your shader {id}"
        )


def get_array_size(member: dict) -> int:
    if "array_size_is_literal" in member and "array" in member:
        if member["array_size_is_literal"] == [True]:
            return sum(member["array"])
    return 1


def generate_descriptorsets(sd: ShaderDetail):
    descriptorset_types = [S.IMG, S.UBO, S.SSBO, S.TEX, S.TEX_IMG, S.TEX_SAM]

    R = sd.r  # reflect
    mode = sd.sm

    descriptorsets = []

    for descriptorset_type in descriptorset_types:
        if descriptorset_type in R.keys():
            members = R[descriptorset_type]
            for member in members:
                dtype = member["type"]
                set = member["set"]
                binding = member["binding"]
                count = get_array_size(member)
                descriptorsets.append((mode, set, binding, dtype, count))

    return descriptorsets


def check_for_errors_single_descriptorsets(
    id: str, descriptorsets: List[Tuple[str, int, int, str, int]]
):
    for i, d in enumerate(descriptorsets):
        if i == len(descriptorsets) - 1:
            break
        mode1, set1, binding1, dtype1, count1 = d
        for e in descriptorsets[i + 1 :]:
            mode2, set2, binding2, dtype2, count2 = e
            if set1 == set2 and binding1 == binding2:
                raise ValueError(
                    f"set {set1} and binding {binding1} overlapped for shader {id}"
                )


def check_for_errors_group_descriptorsets(
    descriptorsets_group: Dict[str, List[Tuple[str, int, int, str, int]]],
):
    for i, id, descriptorsets in enumerate(descriptorsets_group):
        if i == len(descriptorsets_group) - 1:
            break
        for mode1, set1, binding1, dtype1, count1 in descriptorsets:
            for id2, descriptorsets2 in descriptorsets_group[i + 1 :]:
                for mode2, set2, binding2, dtype2, count2 in descriptorsets2:
                    if set1 == set2 and binding1 == binding2:
                        raise ValueError(
                            f"set {set1} and binding {binding1} overlapped for shaders {id} and {id2}. "
                            f"This is not allowed since bother shaders are grouped together in a single pipeline."
                        )


def condense_group(
    descriptorset_group: Dict[str, List[Tuple[str, int, int, str, int]]],
) -> List[Tuple[str, int, int, str, int]]:
    sets = set()
    for id, descriptorsets in descriptorset_group:
        for d in descriptorsets:
            sets.add(d)
    return list(sets)


def build_descriptorset_layout(
    descriptorset_group: Dict[str, List[Tuple[str, int, int, str, int]]],
) -> List[VkDescriptorSetLayoutBinding]:
    bindings: Dict[Tuple, VkDescriptorSetLayoutBinding] = {}

    condensed_descriptorsets = condense_group(descriptorset_group)

    for d in condensed_descriptorsets:
        mode, dset, binding, dtype, count = d
        key = (dset, binding, dtype, count)
        if key in bindings:
            current = bindings[key]
            if not mode in current.stageFlags:
                current.stageFlags.append(mode)
        else:
            binding = VkDescriptorSetLayoutBinding(binding, dtype, count, [mode])
            bindings[key] = binding

    return [value for key, value in bindings]


def create_layout(fc: VkForgeConfig, sc: VkForgeShaderConfig) -> VkForgeLayout:
    bindings: List[VkDescriptorSetLayoutBinding] = []

    for shader_group in sc.combinations:
        descriptorsets_group = {}
        for id in shader_group:
            sd: ShaderDetail = sc.details.get(id)
            R = sd.r  # reflect
            print_warnings(id, R)
            raise_errors(id, R)

            descriptorsets = generate_descriptorsets(sd)
            check_for_errors_single_descriptorsets(id, descriptorsets)

            descriptorsets_group[id] = descriptorsets
        check_for_errors_group_descriptorsets(descriptorsets_group)

        bindings.extend(build_descriptorset_layout(descriptorsets_group))

    return list(set(bindings))
