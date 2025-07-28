from vkforge.designer import DesignInfo, design_name

def create_callback(di: DesignInfo) -> str:
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
    output = content.format(
        name=design_name(di, "debug_msg_callback")
    )

    return output

def create_debug(di: DesignInfo) -> str:
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
    output = content.format(
        name=design_name(di, "GetDebugUtilsMessengerCreateInfo"),
        callback=design_name(di, "debug_msg_callback")
    )

    return output

def create_score(di: DesignInfo) -> str:
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
    output = content.format(
        name=design_name(di, "ScoreGPU")
    )

    return output

def create_vk_fence(di: DesignInfo) -> str:
    content = """\
void {name}(VkInstance instance, VkSurfaceKHR surface, VkPhysicalDevice* inPhysicalDevice, uint32_t* inQueueFamilyIndex)
{{
    static_assert(inPhysicalDevice, "inPhysicalDevice can not be null.");
    static_assert(inQueueFamilyIndex, "inQueueFamilyIndex can not be null.");

    VULKAN_ENUM(physical_dev, VkPhysicalDevice, vkEnumeratePhysicalDevices, 32, instance);

        uint32_t best_score = 0;
    VkPhysicalDevice best_physical_dev = VK_NULL_HANDLE;
    uint32_t best_queue_fam_ind;

        for (uint32_t i = 0; i < physical_dev_count; i++)
    {{
                VkPhysicalDeviceProperties physical_dev_prop = {{0}};
                vkGetPhysicalDeviceProperties(physical_dev_buffer[i], &physical_dev_prop);
        VULKAN_ENUM(queue_fam_prop, VkQueueFamilyProperties, vkGetPhysicalDeviceQueueFamilyProperties, 32, physical_dev_buffer[i]);
                uint32_t score = {score}(physical_dev_prop.limits);

                for (uint32_t j = 0; j < queue_fam_prop_count; j++) {{
            uint32_t requested_flags = VK_QUEUE_GRAPHICS_BIT;
                        if (requested_flags == (queue_fam_prop_buffer[j].queueFlags & requested_flags))
            {{
                                VkBool32 supported = VK_FALSE;
                                vkGetPhysicalDeviceSurfaceSupportKHR(physical_dev_buffer[i], j, surface, &supported);

                                if (supported && (score > best_score)) {{
                    best_score = score;

                                        best_physical_dev = physical_dev_buffer[i];
                                        best_queue_fam_ind = j;
                                }}
                        }}
                }}
        }}

        if(best_physical_dev == VK_NULL_HANDLE )
    {{
        SDL_LogError(0, "No physical device found!");
        exit(1);
    }}

    *inPhysicalDevice   = best_physical_dev;
    *inQueueFamilyIndex = best_queue_fam_ind;
}}
"""
    output = content.format(
        name=design_name(di, "VulkanSelectGPU"),
        score=design_name(di, "ScoreGPU")
    )

    return output

def create_vk_semaphore(di: DesignInfo) -> str:
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
    output = content.format(
        name=design_name(di, ["create", "vk", "semaphore"])
    )

    return output

def create_vk_swapchain(di: DesignInfo) -> str:
    content = """\
VkSwapchainKHR {name}(
    VkDevice device,
    VkAllocationCallbacks* allocator,
    VkSwapchainCreateInfoKHR createInfo
)
{{
    VkSwapchainKHR swapchain = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateSwapchainKHR(device, &createInfo, allocator, &swapchain);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkSwapchain.");
        exit(1);
    }}

    return swapchain;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "swapchain"])
    )

    return output

def create_vk_commandpool(di: DesignInfo) -> str:
    content = """\
VkCommandPool {name}(
    VkDevice device,
    VkAllocationCallbacks* allocator,
    VkCommandPoolCreateInfo createInfo
)
{{
    VkCommandPool commandpool = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateCommandPool(device, &createInfo, allocator, &commandpool);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkCommandPool.");
        exit(1);
    }}

    return commandpool;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "commandpool"])
    )

    return output