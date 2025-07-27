# VkForge Config Schema
# (c) Alrick Grandison, Algodal

# This schema defines the default configuration layout for a graphics renderer.
# While VkForge can support Compute GPU functionalities, its primary focus is
# graphics rendering.

# Note that VkForge does not allow customization of the following:
# - Command buffers and synchronization are managed internally by VkForge.
#   If you require full control over command buffer handling and rendering
#   synchronization, VkForge may not be the right tool for your needs.
#
#   VkForge allocates two command buffers: one for copying and one for drawing.
#   Both command buffers remain active for the entire lifetime of the application.
#
#   Rendering synchronization is handled using semaphores for command ordering,
#   fence status checks via VkGetFenceStatus, and a custom internal VkForge
#   state system. Together, these mechanisms ensure your renderer runs as fast
#   as possible without blocking.
#
#   Importantly, VkForge never calls any wait functions during rendering.
#   Wait functions are only called during application shutdown.
#
# - Only one queue is supported by VkForge even if the physical device can support
#   multiple queues. That queue must support both graphics and transfer operations.
#
# Contributions are welcomed from the community to make VkForge more versatile
# and support other types of implementation of Vulkan.

from pydantic import BaseModel, Field, field_validator, model_validator, PrivateAttr
from typing import List, Optional, Literal, Union
import re

class VkInstanceCreateInfo(BaseModel):
    ppEnabledLayerNames: Optional[List[Literal[
        "VK_LAYER_KHRONOS_validation",
        "VK_VALIDATION_FEATURE_ENABLE_BEST_PRACTICES_EXT"
    ]]] = Field(
        default=["VK_LAYER_KHRONOS_validation"],
        description=(
            "List of Vulkan validation layers to enable. For example, "
            "'VK_LAYER_KHRONOS_validation' enables standard validation, "
            "and 'VK_VALIDATION_FEATURE_ENABLE_BEST_PRACTICES_EXT' enables best practices validation."
        )
    )


class VkApplicationInfo(BaseModel):
    apiVersion: Optional[Literal[
        "VK_API_VERSION_1_0",
        "VK_API_VERSION_1_1",
        "VK_API_VERSION_1_2",
        "VK_API_VERSION_1_3",
        "1.0", "1.1", "1.2", "1.3",
    ]] = Field(
        default="VK_API_VERSION_1_3",
        description="Vulkan API version to target."
    )
    pEngineName: Optional[str] = Field(
        default="VkForge",
        description="Name of the engine."
    )
    pApplicationName: Optional[str] = Field(
        default="VkForge Renderer",
        description="Name of the application."
    )
    applicationVersion: Optional[int] = 0
    engineVersion: Optional[int] = 0


class VkDebugUtilsMessengerCreateInfoEXT(BaseModel):
    messageSeverity: Optional[List[Literal[
        "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
        "VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT",
        "VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT",
        "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT",
        "warning", "info", "verbose", "error"
    ]]] = Field(
        default=[
            "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT"
        ],
        description="List of message severities to enable for debug messenger."
    )
    messageType: Optional[List[Literal[
        "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
        "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
        "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT",
        "general", "validation", "performance"
    ]]] = Field(
        default=[
            "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT"
        ],
        description="List of message types to enable for debug messenger."
    )


class VkPhysicalDeviceVulkan13Features(BaseModel):
    dynamicRendering: Optional[bool] = Field(
        default=False,
        description="Enable dynamic rendering feature. Requires Vulkan >= 1.3."
    )
    synchronization2: Optional[bool] = Field(
        default=False,
        description="Enable synchronization2 feature. Requires Vulkan >= 1.3."
    )
    # only the above features are supported for the time being

class VkPhysicalDeviceFeatures(BaseModel):
    robustBufferAccess: Optional[bool] = False
    fullDrawIndexUint32: Optional[bool] = False
    imageCubeArray: Optional[bool] = False
    independentBlend: Optional[bool] = False
    geometryShader: Optional[bool] = False
    tessellationShader: Optional[bool] = False
    sampleRateShading: Optional[bool] = False
    dualSrcBlend: Optional[bool] = False
    logicOp: Optional[bool] = False
    multiDrawIndirect: Optional[bool] = False
    drawIndirectFirstInstance: Optional[bool] = False
    depthClamp: Optional[bool] = False
    depthBiasClamp: Optional[bool] = False
    fillModeNonSolid: Optional[bool] = False
    depthBounds: Optional[bool] = False
    wideLines: Optional[bool] = False
    largePoints: Optional[bool] = False
    alphaToOne: Optional[bool] = False
    multiViewport: Optional[bool] = False
    samplerAnisotropy: Optional[bool] = False
    textureCompressionETC2: Optional[bool] = False
    textureCompressionASTC_LDR: Optional[bool] = False
    textureCompressionBC: Optional[bool] = False
    occlusionQueryPrecise: Optional[bool] = False
    pipelineStatisticsQuery: Optional[bool] = False
    vertexPipelineStoresAndAtomics: Optional[bool] = False
    fragmentStoresAndAtomics: Optional[bool] = False
    shaderTessellationAndGeometryPointSize: Optional[bool] = False
    shaderImageGatherExtended: Optional[bool] = False
    shaderStorageImageExtendedFormats: Optional[bool] = False
    shaderStorageImageMultisample: Optional[bool] = False
    shaderStorageImageReadWithoutFormat: Optional[bool] = False
    shaderStorageImageWriteWithoutFormat: Optional[bool] = False
    shaderUniformBufferArrayDynamicIndexing: Optional[bool] = False
    shaderSampledImageArrayDynamicIndexing: Optional[bool] = False
    shaderStorageBufferArrayDynamicIndexing: Optional[bool] = False
    shaderStorageImageArrayDynamicIndexing: Optional[bool] = False
    shaderClipDistance: Optional[bool] = False
    shaderCullDistance: Optional[bool] = False
    shaderFloat64: Optional[bool] = False
    shaderInt64: Optional[bool] = False
    shaderInt16: Optional[bool] = False
    shaderResourceResidency: Optional[bool] = False
    shaderResourceMinLod: Optional[bool] = False
    sparseBinding: Optional[bool] = False
    sparseResidencyBuffer: Optional[bool] = False
    sparseResidencyImage2D: Optional[bool] = False
    sparseResidencyImage3D: Optional[bool] = False
    sparseResidency2Samples: Optional[bool] = False
    sparseResidency4Samples: Optional[bool] = False
    sparseResidency8Samples: Optional[bool] = False
    sparseResidency16Samples: Optional[bool] = False
    sparseResidencyAliased: Optional[bool] = False
    variableMultisampleRate: Optional[bool] = False
    inheritedQueries: Optional[bool] = False


class VkDeviceCreateInfo(BaseModel):
    ppEnabledExtensionNames: Optional[List[str]] = Field(
        default_factory=lambda: ["VK_KHR_swapchain"],
        description='List device entensions. "VK_KHR_swapchain" extension is always required.'
    )

    PhysicalDeviceFeatures: Optional[VkPhysicalDeviceFeatures] = Field(
        default=None,
        description="Boolean indicators of all the features to be enabled"
    )

    @field_validator('ppEnabledExtensionNames')
    def ensure_swapchain_extension(cls, v):
        if v is None or len(v) == 0:
            raise ValueError("VK_KHR_swapchain is required in ppEnabledExtensionNames!")
        elif "VK_KHR_swapchain" not in v:
            raise ValueError("VK_KHR_swapchain is required in ppEnabledExtensionNames!")
        return v


class VkSwapchainCreateInfoKHR(BaseModel):
    minImageCount: Optional[int] = Field(
        default=4,
        description="Number of images in the swapchain."
    )
    imageFormat: Optional[str] = Field(
        default="VK_FORMAT_R8G8B8_UNORM",
        description="Format of the swapchain images."
    )
    presentMode: Optional[str] = Field(
        default="VK_PRESENT_MODE_MAILBOX_KHR",
        description="Present mode of the swapchain."
    )


class VkShaderModule(BaseModel):
    path: str = Field(..., description="Path to the shader binary or shader GLSL source. If it is a source then the shader will be complied first before being processed.")
    mode: Optional[Literal[
        "vert", "frag", "comp", "geom", "tesc", "tese",
        "mesh", "task", "rgen", "rint", "rahit", "rchit",
        "rmiss", "rcall", "mesh_nv", "task_nv"
    ]] = Field(
        default=None,
        description="Shader stage mode, e.g. 'vert' or 'frag'. If it is not specified, it is determined from the extension."
    )
    pName: Optional[str] = Field(
        default=None,
        description="Entry point name of the shader for this stage."
    )
    # VkSpecializationInfo is not supported. We can add support for this in the future with help from the community.

class VkVertexInputBindingDescription(BaseModel):
    stride: Union[str, int] = Field(
        ...,
        description="User defined type name, `sizeof(...)` string, or literal integer stride size."
    )
    _stride_kind: Optional[Literal["TYPE", "SIZEOF", "INT"]] = PrivateAttr(default=None)

    stride_members: Optional[List[str]] = Field(
        default=None,
        description="List of all members of the type in declaration order. If you omit this, then VkForge will attempt to calculate the offset. Otherwise, VkForge will use the listed members and the type to get the offset. The name must match the type used in the stride"
    )
    inputRate: Optional[Literal["vertex", "instance"]] = Field(
        default="vertex",
        description="Input rate for the binding."
    )
    first_location: int = Field(..., description="First location index in the shader input.")

    @property
    def stride_kind(self):
        return self._stride_kind
    
    @model_validator(mode="after")
    def validate_stride_kind(self):
        if isinstance(self.stride, int):
            self._stride_kind = "INT"
        elif isinstance(self.stride, str):
            s = self.stride.strip()
            if re.fullmatch(r"sizeof\s*\(?\s*\w+\s*\)?", s):
                self._stride_kind = "SIZEOF"
            elif re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", s):
                self._stride_kind = "TYPE"
            else:
                raise ValueError(
                    f"Invalid stride string: '{self.stride}'. Must be sizeof(Type) or valid C type name."
                )
        else:
            raise ValueError(f"Invalid stride type: {type(self.stride)}")
        return self
    
    @model_validator(mode="after")
    def validate_stride_members(self):
        if self.stride_members is not None and self._stride_kind != "TYPE":
            raise ValueError(
                "If stride_members is provided, stride must be a typenot a literal int or sizeof(...)."
            )
        return self


class VkPipelineInputAssemblyStateCreateInfo(BaseModel):
    topology: Optional[Literal[
        "VK_PRIMITIVE_TOPOLOGY_POINT_LIST",
        "VK_PRIMITIVE_TOPOLOGY_LINE_LIST",
        "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP",
        "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
        "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP",
        "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN",
        "VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY",
        "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP_WITH_ADJACENCY",
        "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST_WITH_ADJACENCY",
        "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY",
        "VK_PRIMITIVE_TOPOLOGY_PATCH_LIST",
        "point_list",
        "line_list",
        "line_strip",
        "triangle_list",
        "triangle_strip",
        "triangle_fan",
        "line_list_with_adjacency",
        "line_strip_with_adjacency",
        "triangle_list_with_adjacency",
        "triangle_strip_with_adjacency",
        "patch_list",
    ]] = Field(
        default="VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
        description="Primitive topology for input assembly."
    )


class VkPipelineRasterizationStateCreateInfo(BaseModel):
    polygonMode: Optional[str] = Field(
        default="VK_POLYGON_MODE_FILL",
        description="Polygon mode for rasterization."
    )
    cullMode: Optional[str] = Field(
        default="VK_CULL_MODE_NONE",
        description="Face culling mode."
    )
    frontFace: Optional[str] = Field(
        default="VK_FRONT_FACE_COUNTER_CLOCKWISE",
        description="Front face winding order."
    )
    lineWidth: Optional[float] = Field(
        default=1.0,
        description="Width of rasterized line."
    )
    depthClampEnable: Optional[bool] = Field(
        default=False,
        description="Enables depth clamping."
    )
    rasterizerDiscardEnable: Optional[bool] = Field(
        default=False,
        description="Discard primitives before rasterization."
    )
    depthBiasEnable: Optional[bool] = Field(
        default=False,
        description="Enable depth bias during rasterization."
    )
    depthBiasConstantFactor: Optional[float] = Field(
        default=0,
        description="Constant depth bias factor."
    )
    depthBiasClamp: Optional[float] = Field(
        default=0,
        description="Maximum depth bias of a fragment."
    )
    depthBiasSlopeFactor: Optional[float] = Field(
        default=0,
        description="Slope factor applied to depth bias."
    )


class VkPipeline(BaseModel):
    name: Optional[str] = Field(None, description="User defined pipeline name.")
    extern_import: Optional[List[str]] = Field(
        default=[],
        description="List of user-defined header imports (includes)."
    )

    ShaderModule: List[VkShaderModule] = Field(..., description="List of shader modules.")
    VertexInputBindingDescription: List[VkVertexInputBindingDescription] = Field(
        ..., description="List of vertex input binding descriptions."
    )
    PipelineInputAssemblyStateCreateInfo: Optional[VkPipelineInputAssemblyStateCreateInfo] = Field(
        default_factory=VkPipelineInputAssemblyStateCreateInfo,
        description="Input assembly state description."
    )
    DynamicState: Optional[List[Literal[
        "VK_DYNAMIC_STATE_VIEWPORT",
        "VK_DYNAMIC_STATE_SCISSOR",
        "VK_DYNAMIC_STATE_LINE_WIDTH",
        "VK_DYNAMIC_STATE_DEPTH_BIAS",
        "VK_DYNAMIC_STATE_BLEND_CONSTANTS",
        "VK_DYNAMIC_STATE_DEPTH_BOUNDS",
        "VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK",
        "VK_DYNAMIC_STATE_STENCIL_WRITE_MASK",
        "VK_DYNAMIC_STATE_STENCIL_REFERENCE",
        "VK_DYNAMIC_STATE_CULL_MODE",
        "VK_DYNAMIC_STATE_FRONT_FACE",
        "VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY",
        "VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT",
        "VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT",
        "VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE",
        "VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE",
        "VK_DYNAMIC_STATE_DEPTH_WRITE_ENABLE",
        "VK_DYNAMIC_STATE_DEPTH_COMPARE_OP",
        "VK_DYNAMIC_STATE_DEPTH_BOUNDS_TEST_ENABLE",
        "VK_DYNAMIC_STATE_STENCIL_TEST_ENABLE",
        "VK_DYNAMIC_STATE_STENCIL_OP",
        "VK_DYNAMIC_STATE_RASTERIZER_DISCARD_ENABLE",
        "VK_DYNAMIC_STATE_DEPTH_BIAS_ENABLE",
        "VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE",
        "viewport",
        "scissor",
        "line_width",
        "depth_bias",
        "blend_constants",
        "depth_bounds",
        "stencil_compare_mask",
        "stencil_write_mask",
        "stencil_reference",
        "cull_mode",
        "front_face",
        "primitive_topology",
        "viewport_with_count",
        "scissor_with_count",
        "vertex_input_binding_stride",
        "depth_test_enable",
        "depth_write_enable",
        "depth_compare_op",
        "depth_bounds_test_enable",
        "stencil_test_enable",
        "stencil_op",
        "rasterizer_discard_enable",
        "depth_bias_enable",
        "primitive_restart_enable",
    ]]] = Field(
        default_factory=lambda: ["VK_DYNAMIC_STATE_VIEWPORT", "VK_DYNAMIC_STATE_SCISSOR"],
        description="List of dynamic state enables (viewport and scissor always required)."
    )
    PipelineRasterizationStateCreateInfo: Optional[VkPipelineRasterizationStateCreateInfo] = Field(
        default_factory=VkPipelineRasterizationStateCreateInfo,
        description="Rasterization state description."
    )

    @field_validator("DynamicState")
    def must_include_viewport_and_scissor(cls, v):
        required = {"VK_DYNAMIC_STATE_VIEWPORT", "VK_DYNAMIC_STATE_SCISSOR"}
        if v is None:
            raise ValueError(f"DynamicState must include: {required}!")
        missing = required - set(v)
        if missing:
            raise ValueError(f"DynamicState must include: {required}!")
        return v


class VkForgeConfig(BaseModel):
    namespace: Optional[str] = Field(
        default="vkforge_",
        description="Namespace prefix for generated symbols."
    )
    namestyle: Optional[Literal["snake_case", "camel_case", "pascal_case"]] = Field(
        default="snake_case",
        description="Naming style for generated identifiers."
    )
    
    InstanceCreateInfo: Optional[VkInstanceCreateInfo] = Field(
        default_factory=VkInstanceCreateInfo,
        description="Instance creation info."
    )
    ApplicationInfo: Optional[VkApplicationInfo] = Field(
        default_factory=VkApplicationInfo,
        description="Application info."
    )
    DebugUtilsMessengerCreateInfoEXT: Optional[VkDebugUtilsMessengerCreateInfoEXT] = Field(
        default_factory=VkDebugUtilsMessengerCreateInfoEXT,
        description="Debug messenger creation info."
    )
    PhysicalDeviceVulkan13Features: Optional[VkPhysicalDeviceVulkan13Features] = Field(
        default_factory=VkPhysicalDeviceVulkan13Features,
        description="Physical device Vulkan 1.3 features."
    )
    DeviceCreateInfo: Optional[VkDeviceCreateInfo] = Field(
        default_factory=VkDeviceCreateInfo,
        description="Device creation info."
    )
    SwapchainCreateInfoKHR: Optional[VkSwapchainCreateInfoKHR] = Field(
        default_factory=VkSwapchainCreateInfoKHR,
        description="Swapchain creation info."
    )

    Pipeline: List[VkPipeline] = Field(..., description="List of graphics pipelines.")
