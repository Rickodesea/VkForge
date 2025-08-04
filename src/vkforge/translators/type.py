from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateForgeType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkInstance       instance;
    VkSurfaceKHR     surface;
    VkPhysicalDevice physical_device;
    uint32_t         queue_family_index;
    VkDevice         device;
    VkQueue          queue;
    VkSwapchainKHR   swapchain;
    uint32_t         swapchain_size;
    VkImage*         swapchain_images;
    VkImageView*     swapchain_imgviews;
    VkCommandPool    cmdpool;
    VkCommandBuffer  cmdbuf_copy;
    VkCommandBuffer  cmdbuf_draw;
}};
"""
    output = content.format(name=TYPE_NAME.FORGE)

    return output


def CreateCacheType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkSurfaceCapabilitiesKHR surface_cap;
    VkSurfaceFormatKHR       surface_fmt;
}};
"""
    output = content.format(name=TYPE_NAME.CACHE)

    return output


def CreateBufferAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkBuffer       buffer;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format(name=TYPE_NAME.BUFFERALLOC)

    return output

def CreateForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};
"""
    output = content.format(name=TYPE_NAME.FORGE_LAYOUT)

    return output

