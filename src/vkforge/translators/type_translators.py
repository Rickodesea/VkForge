from vkforge.designer import DesignInfo, design_name

def create_core(di: DesignInfo) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkInstance       instance;
    VkSurfaceKHR     surface;
    VkPhysicalDevice physical_device;
    VkDevice         device;
    VkQueue          queue;
    uint32_t         queue_family_index;
    VkCommandPool    commandpool;
    VkCommandBuffer  cmdbuf_cpy;
    VkCommandBuffer  cmdbuf_drw;
    VkSwapchainKHR   swapchain;
    uint32_t         swapchain_size;
    VkImage*         swapchain_images;
    VkImageView*     swapchain_imgviews;
}};
"""
    output = content.format(
        name=design_name(di, "VkCore")
    )

    return output

def create_cache(di: DesignInfo) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkSurfaceCapabilitiesKHR surface_cap;
    VkSurfaceFormatKHR       surface_fmt;
}};
"""
    output = content.format(
        name=design_name(di, "VkCache")
    )

    return output

def create_bufferalloc(di: DesignInfo) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkBuffer       buffer;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format(
        name=design_name(di, "VkBufferAlloc")
    )

    return output

def create_enum(di: DesignInfo) -> str:
    content = """\
#define {name}(Var, Type, Func, Sizelimit, ...) \
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \
    Func(__VA_ARGS__, &Var##_count, 0); \
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \
}} while(0)
"""
    output = content.format(
        name=design_name(di, "VULKAN_ENUM")
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