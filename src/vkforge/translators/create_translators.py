from vkforge.designer import DesignInfo, design_name

def create_vk_instance(di: DesignInfo) -> str:
    content = """\
VkInstance {name}(
    VkAllocationCallbacks* allocator,
    VkInstanceCreateInfo   createInfo
)
{{
    VkInstance instance = VK_NULL_HANDLE;
    VkResult   result;

    result = vkCreateInstance(&createInfo, allocator, &instance);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkInstance");
        exit(1);
    }}

    return instance;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "instance"])
    )

    return output

def create_vk_surface(di: DesignInfo) -> str:
    content = """\
VkSurface {name}(
    VkInstance             instance,
    VkAllocationCallbacks* allocator,
    SDL_Window*            window
)
{{
    VkSurface  surface = VK_NULL_HANDLE;
    bool       success;

    success = SDL_Vulkan_CreateSurface(window, instance, allocator, &surface);

    if( true != success )
    {{
        SDL_Log("Failed to create VkSurface");
        exit(1);
    }}

    return surface;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "surface"])
    )

    return output

def create_vk_device(di: DesignInfo) -> str:
    content = """\
VkSurface {name}(
    VkPhysicalDevice       physical_device,
    VkAllocationCallbacks* allocator,
    VkDeviceCreateInfo     createInfo
)
{{
    VkDevice   device = VK_NULL_HANDLE;
    VkResult   result;

    result = vkCreateDevice(physical_device, &createInfo, allocator, &device);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkDevice");
        exit(1);
    }}

    return device;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "instance"])
    )

    return output

def create_vk_fence(di: DesignInfo) -> str:
    content = """\
VkFence {name}(VkDevice device, VkAllocationCallbacks* allocator)
{{
    VkFenceCreateInfo info = {{0}};
    info.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkFence fence = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &info, allocator, &fence);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkFence.");
        exit(1);
    }}

    return fence;
}}
"""
    output = content.format(
        name=design_name(di, ["create", "vk", "fence"])
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