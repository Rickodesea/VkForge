from vkforge.context import VkForgeContext
from vkforge.mappings import F, FT


def CreateDebugMsgCallback(ctx: VkForgeContext) -> str:
    content = """\
VKAPI_ATTR VkBool32 VKAPI_CALL {name}
(
    VkDebugUtilsMessageSeverityFlagBitsEXT severity,
    VkDebugUtilsMessageTypeFlagsEXT type,
    const VkDebugUtilsMessengerCallbackDataEXT* callback,
    void* user
)
{{
    (void)user;

    const char* typeStr = "";
    if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT)
    {{
        typeStr = "[VALIDATION]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT)
    {{
        typeStr = "[PERFORMANCE]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT)
    {{
        typeStr = "[GENERAL]";
    }}

    if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT)
    {{
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "%%s %%s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT)
    {{
        SDL_LogWarn(SDL_LOG_CATEGORY_APPLICATION, "%%s %%s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT ||
               severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT)
    {{
        SDL_Log("%%s %%s", typeStr, callback->pMessage);
    }}

    return VK_FALSE;
}}
"""
    output = content.format(name=F.DEBUG_MSG_CALLBACK)

    return output


def CreateDebugMsgInfo(ctx: VkForgeContext) -> str:
    content = """\
VkDebugUtilsMessengerCreateInfoEXT {name}()
{{
    VkDebugUtilsMessengerCreateInfoEXT createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
    createInfo.messageSeverity =
        VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
        //VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT |
        //VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
        VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
    createInfo.messageType =
        VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
        VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
        VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
    createInfo.pfnUserCallback = {callback};
    return createInfo;
}}
"""
    output = content.format(name=F.DEBUG_MSG_INFO, callback=F.DEBUG_MSG_CALLBACK)

    return output


def CreateScorePhysicalDevice(ctx: VkForgeContext) -> str:
    content = """\
uint32_t {name}(VkPhysicalDeviceLimits limits)
{{
    uint32_t score = 0;
    score += limits.maxImageDimension1D;
    score += limits.maxImageDimension2D;
    score += limits.maxImageDimension3D;
    score += limits.maxImageDimensionCube;
    score += limits.maxImageArrayLayers;
    score += limits.maxTexelBufferElements;
    score += limits.maxUniformBufferRange;
    score += limits.maxStorageBufferRange;
    score += limits.maxPushConstantsSize;
    score += limits.maxMemoryAllocationCount;
    score += limits.maxSamplerAllocationCount;
    score += limits.maxBoundDescriptorSets;
    score += limits.maxPerStageDescriptorSamplers;
    score += limits.maxPerStageDescriptorUniformBuffers;
    score += limits.maxPerStageDescriptorStorageBuffers;
    score += limits.maxPerStageDescriptorSampledImages;
    score += limits.maxPerStageDescriptorStorageImages;
    score += limits.maxPerStageDescriptorInputAttachments;
    score += limits.maxPerStageResources;
    score += limits.maxDescriptorSetSamplers;
    score += limits.maxDescriptorSetUniformBuffers;
    score += limits.maxDescriptorSetUniformBuffersDynamic;
    score += limits.maxDescriptorSetStorageBuffers;
    score += limits.maxDescriptorSetStorageBuffersDynamic;
    score += limits.maxDescriptorSetSampledImages;
    score += limits.maxDescriptorSetStorageImages;
    score += limits.maxDescriptorSetInputAttachments;
    score += limits.maxVertexInputAttributes;
    score += limits.maxVertexInputBindings;
    score += limits.maxVertexInputAttributeOffset;
    score += limits.maxVertexInputBindingStride;
    score += limits.maxVertexOutputComponents;
    score += limits.maxTessellationGenerationLevel;
    score += limits.maxTessellationPatchSize;
    score += limits.maxTessellationControlPerVertexInputComponents;
    score += limits.maxTessellationControlPerVertexOutputComponents;
    score += limits.maxTessellationControlPerPatchOutputComponents;
    score += limits.maxTessellationControlTotalOutputComponents;
    score += limits.maxTessellationEvaluationInputComponents;
    score += limits.maxTessellationEvaluationOutputComponents;
    score += limits.maxGeometryShaderInvocations;
    score += limits.maxGeometryInputComponents;
    score += limits.maxGeometryOutputComponents;
    score += limits.maxGeometryOutputVertices;
    score += limits.maxGeometryTotalOutputComponents;
    score += limits.maxFragmentInputComponents;
    score += limits.maxFragmentOutputAttachments;
    score += limits.maxFragmentDualSrcAttachments;
    score += limits.maxFragmentCombinedOutputResources;
    score += limits.maxComputeSharedMemorySize;
    score += limits.maxComputeWorkGroupInvocations;
    score += limits.maxDrawIndexedIndexValue;
    score += limits.maxDrawIndirectCount;
    score += limits.maxSamplerLodBias;
    score += limits.maxSamplerAnisotropy;
    score += limits.maxViewports;
    score += limits.maxTexelOffset;
    score += limits.maxTexelGatherOffset;
    score += limits.maxInterpolationOffset;
    score += limits.maxFramebufferWidth;
    score += limits.maxFramebufferHeight;
    score += limits.maxFramebufferLayers;
    score += limits.framebufferColorSampleCounts;
    score += limits.framebufferDepthSampleCounts;
    score += limits.framebufferStencilSampleCounts;
    score += limits.framebufferNoAttachmentsSampleCounts;
    score += limits.maxColorAttachments;
    score += limits.sampledImageColorSampleCounts;
    score += limits.sampledImageIntegerSampleCounts;
    score += limits.sampledImageDepthSampleCounts;
    score += limits.sampledImageStencilSampleCounts;
    score += limits.storageImageSampleCounts;
    score += limits.maxSampleMaskWords;
    score += limits.maxClipDistances;
    score += limits.maxCullDistances;
    score += limits.maxCombinedClipAndCullDistances;

    return score;
}}
"""
    output = content.format(name=F.SCORE_PHYSICAL_DEVICE)

    return output


def CreateFence(ctx: VkForgeContext) -> str:
    content = """\
VkFence {name}(VkDevice device, VkAllocationCallbacks* allocator)
{{
    VkFenceCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkFence fence = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &createInfo, allocator, &fence);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkFence.");
        exit(1);
    }}

    return fence;
}}
"""
    output = content.format(F.FENCE)

    return output


def CreateSemaphore(ctx: VkForgeContext) -> str:
    content = """\
VkSemaphore {name}(VkDevice device, VkAllocationCallbacks* allocator)
{{
    VkSemaphoreCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkSemaphore semaphore = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &createInfo, allocator, &semaphore);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkSemaphore.");
        exit(1);
    }}

    return semaphore;
}}
"""
    output = content.format(F.SEMAPHORE)

    return output


def CreateGetCache(ctx: VkForgeContext) -> str:
    content = """\
void {name}
(
    VkAllocationCallbacks* allocator,
    void*                  next,
    VkInstance             instance,
    VkSurfaceKHR           surface,
    VkPhysicalDevice       physical_device,

    {cacheType}*          retCache
)
{{
    assert(retCache);

    (void)allocator;
    (void)next;

    VkResult result;
    {cacheType} cache = {{0}};

    {enum}(
        formats,
        VkSurfaceFormatKHR,
        vkGetPhysicalDeviceSurfaceFormatsKHR,
        64,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < formats_count; i++)
    {{
        cache.surface_fmt = formats_buffer[i].format;
        if ({reqFormat} == formats_buffer[i].format)
            break;
    }}

    result = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physical_device, surface, &cache.surface_cap);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to get Vulkan physical device surface capabilities");
        exit(1);
    }}

    *retCache = cache;
}}

"""
    output = content.format(
        name=F.CACHE, cacheType=FT.CACHE, enum=FT.ENUM, reqFormat="UNION"
    )

    return output


def CreateCmdImageBarrier(ctx: VkForgeContext) -> str:
    content = """\
void CmdImageBarrier
(
    VkCommandBuffer cmdbuf,

    VkImage image,
    VkImageLayout oldLayout,
    VkImageLayout newLayout,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkImageMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barrier.oldLayout = oldLayout;
    barrier.newLayout = newLayout;
    barrier.image = image;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        0,0,
        1, &barrier
    );
}}


"""
    output = content.format()

    return output


def CreateCmdBufferBarrier(ctx: VkForgeContext) -> str:
    content = """\
void CmdBufferBarrier
(
    VkCommandBuffer cmdbuf,

    VkBuffer buffer,
    VkDeviceSize offset,
    VkDeviceSize size,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkBufferMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barrier.buffer = buffer;
    barrier.offset = offset;
    barrier.size = size;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        1, &barrier,
        0,0
    );
}}

"""
    output = content.format()

    return output


def CreateGetSurfaceFormat(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceFormatKHR GetSurfaceFormat
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface,
    VkFormat         req_format
)
{{
    VULKAN_ENUM(
        formats,
        VkSurfaceFormatKHR,
        vkGetPhysicalDeviceSurfaceFormatsKHR,
        64,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < formats_count; i++)
    {{
        if (req_format == formats_buffer[i].format)
            return formats_buffer[i];
    }}

    return formats_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetSwapchainSize(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceCapabilitiesKHR GetSurfaceCapabilities
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface
)
{{
    VkSurfaceCapabilitiesKHR surface_cap = {{0}};
    VkResult result = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physical_device, surface, &surface_cap);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to get physical device surface capabilities");
        exit(1);
    }}

    return surface_cap;
}}

"""
    output = content.format()

    return output


def CreateGetPresentMode(ctx: VkForgeContext) -> str:
    content = """\
VkPresentModeKHR GetPresentMode
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface,
    VkPresentModeKHR req_mode
)
{{
    VULKAN_ENUM(
        modes,
        VkPresentModeKHR,
        vkGetPhysicalDeviceSurfacePresentModesKHR,
        4,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < modes_count; i++)
    {{
        if (req_mode == modes_buffer[i]) return req_mode;
    }}

    return modes_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetMemoryTypeIndex(ctx: VkForgeContext) -> str:
    content = """\
uint32_t GetMemoryTypeIndex
(
    VkPhysicalDevice      physical_device,
    uint32_t              typeFilter,
    VkMemoryPropertyFlags properties
)
{{
    VkPhysicalDeviceMemoryProperties memProperties = {{0}};
    vkGetPhysicalDeviceMemoryProperties(physical_device, &memProperties);

    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++)
    {{
        if ((typeFilter & (1 << i)) &&
            (memProperties.memoryTypes[i].propertyFlags & properties) == properties)
        {{
            return i;
        }}
    }}

    SDL_LogError(0, "Failed to find suitable Vulkan memory type");
    exit(1);
    return 0;
}}

"""
    output = content.format()

    return output
