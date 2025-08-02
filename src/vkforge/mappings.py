from typing import Any

############################################
# Map Function
############################################


def map_value(mapping: dict, key: str) -> Any:
    if key.lower() in mapping:
        return mapping[key]
    return key


############################################
# Maps
############################################

API_VERSION_MAP = {
    "1.0": "VK_API_VERSION_1_0",
    "1.1": "VK_API_VERSION_1_1",
    "1.2": "VK_API_VERSION_1_2",
    "1.3": "VK_API_VERSION_1_3",
}

MSG_SEVERITY_MAP = {
    "warning": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
    "info": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT",
    "verbose": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT",
    "error": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT",
}

MSG_TYPE_MAP = {
    "general": "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
    "validation": "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
    "performance": "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT",
}

SHADER_STAGE_MAP = {
    "vert": "VK_SHADER_STAGE_VERTEX_BIT",
    "frag": "VK_SHADER_STAGE_FRAGMENT_BIT",
    "comp": "VK_SHADER_STAGE_COMPUTE_BIT",
    "geom": "VK_SHADER_STAGE_GEOMETRY_BIT",
    "tesc": "VK_SHADER_STAGE_TESSELLATION_CONTROL_BIT",
    "tese": "VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT",
    "mesh": "VK_SHADER_STAGE_MESH_BIT_EXT",
    "task": "VK_SHADER_STAGE_TASK_BIT_EXT",
    "rgen": "VK_SHADER_STAGE_RAYGEN_BIT_KHR",
    "rint": "VK_SHADER_STAGE_INTERSECTION_BIT_KHR",
    "rahit": "VK_SHADER_STAGE_ANY_HIT_BIT_KHR",
    "rchit": "VK_SHADER_STAGE_CLOSEST_HIT_BIT_KHR",
    "rmiss": "VK_SHADER_STAGE_MISS_BIT_KHR",
    "rcall": "VK_SHADER_STAGE_CALLABLE_BIT_KHR",
    "mesh_nv": "VK_SHADER_STAGE_MESH_BIT_NV",
    "task_nv": "VK_SHADER_STAGE_TASK_BIT_NV",
}

INPUT_RATE_MAP = {
    "vertex": "VK_VERTEX_INPUT_RATE_VERTEX",
    "instance": "VK_VERTEX_INPUT_RATE_INSTANCE",
}

TOPOLOGY_MAP = {
    "point_list": "VK_PRIMITIVE_TOPOLOGY_POINT_LIST",
    "line_list": "VK_PRIMITIVE_TOPOLOGY_LINE_LIST",
    "line_strip": "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP",
    "triangle_list": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
    "triangle_strip": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP",
    "triangle_fan": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN",
    "line_list_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY",
    "line_strip_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP_WITH_ADJACENCY",
    "triangle_list_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST_WITH_ADJACENCY",
    "triangle_strip_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY",
    "patch_list": "VK_PRIMITIVE_TOPOLOGY_PATCH_LIST",
}

DYNAMIC_STATE_MAP = {
    "viewport": "VK_DYNAMIC_STATE_VIEWPORT",
    "scissor": "VK_DYNAMIC_STATE_SCISSOR",
    "line_width": "VK_DYNAMIC_STATE_LINE_WIDTH",
    "depth_bias": "VK_DYNAMIC_STATE_DEPTH_BIAS",
    "blend_constants": "VK_DYNAMIC_STATE_BLEND_CONSTANTS",
    "depth_bounds": "VK_DYNAMIC_STATE_DEPTH_BOUNDS",
    "stencil_compare_mask": "VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK",
    "stencil_write_mask": "VK_DYNAMIC_STATE_STENCIL_WRITE_MASK",
    "stencil_reference": "VK_DYNAMIC_STATE_STENCIL_REFERENCE",
    "cull_mode": "VK_DYNAMIC_STATE_CULL_MODE",
    "front_face": "VK_DYNAMIC_STATE_FRONT_FACE",
    "primitive_topology": "VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY",
    "viewport_with_count": "VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT",
    "scissor_with_count": "VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT",
    "vertex_input_binding_stride": "VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE",
    "depth_test_enable": "VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE",
    "depth_write_enable": "VK_DYNAMIC_STATE_DEPTH_WRITE_ENABLE",
    "depth_compare_op": "VK_DYNAMIC_STATE_DEPTH_COMPARE_OP",
    "depth_bounds_test_enable": "VK_DYNAMIC_STATE_DEPTH_BOUNDS_TEST_ENABLE",
    "stencil_test_enable": "VK_DYNAMIC_STATE_STENCIL_TEST_ENABLE",
    "stencil_op": "VK_DYNAMIC_STATE_STENCIL_OP",
    "rasterizer_discard_enable": "VK_DYNAMIC_STATE_RASTERIZER_DISCARD_ENABLE",
    "depth_bias_enable": "VK_DYNAMIC_STATE_DEPTH_BIAS_ENABLE",
    "primitive_restart_enable": "VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE",
}

############################################
# Keys
############################################

from enum import Enum

class StringEnum(str, Enum):
    def __format__(self, format_spec):
        return format(self.value, format_spec)

class F(StringEnum):
    
    DEBUG_MSG_CALLBACK = "VkForge_DebugMsgCallback"
    DEBUG_MSG_INFO = "VkForge_GetDebugUtilsMessengerCreateInfo"
    SCORE_PHYSICAL_DEVICE = "VkForge_ScorePhysicalDeviceLimits"
    SELECT_PHYSICAL_DEVICE = "VkForge_SelectPhysicalDevice"
    SEMAPHORE = "VkForge_CreateVkSemaphore"
    FENCE = "VkForge_CreateVkFence"
    DEVICE = "VkForge_CreateDevice"
    COMMAND_BUFFERS = "VkForge_CreateCommandBuffers"
    CACHE = "VkForge_GetCache"


class FT(str, Enum):
    def __format__(self, format_spec):
        return format(self.value, format_spec)
    
    FORGE = "VkForge"
    CACHE = "VkForgeCache"
    BUFFERALLOC = "VkForgeBufferAlloc"
    ENUM = "VKFORGE_ENUM"
    RESULT_ENUM = "VKFORGE_RESULT_ENUM"


class SHADER(StringEnum):
    MODE      = "mode"
    ENTRYNAME = "entryname"
    BINPATH   = "binary_path"
    SRCPATH   = "source_path"
    REFLECT   = "reflect"
    LIST      = "shader_list"
    COMBO     = "shader_combinations"

class LAYOUT(StringEnum):
    STAGES      = "stages"
    SET         = "set"
    BIND        = "binding"
    TYPE        = "type"
    COUNT       = "count"
    DSET_LAYOUT = "descriptorset_layouts"
    DSET_REF    = "descriptorset_layout_references"

class REFLECT(StringEnum):
    TEXTURE       = "textures"
    SAMPLER_IMAGE = "separate_images"
    SAMPLER       = "separate_samplers"
    IMAGE         = "images"
    SSBO          = "ssbos"
    UBO           = "ubos"
    SUBPASS       = "subpass_inputs"
    INPUT         = "inputs"
    OUTPUT        = "outputs"
    ENTRYPOINT    = "entryPoints"
    TYPE          = "types"

class MEMBER(StringEnum):
    TYPE = "type"
    NAME = "name"
    ARRAY = "array"
    ARRAY_LITERAL = "array_size_is_literal"
    SET = "set"
    BIND = "binding"

class FILE(StringEnum):
    CORE       = "vkforge_core.c"
    UTIL       = "vkforge_utils.c"
    TYPE       = "vkforge_typedecls.h"
    FUNC       = "vkforge_funcdecls.h"
    PIPELINE_C = "vkforge_pipelines.c"
    PIPELINE_H = "vkforge_pipelines.h"
    CMAKE      = "CMakeLists.txt"

