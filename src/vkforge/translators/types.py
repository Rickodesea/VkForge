from vkforge.context import VkForgeContext
from vkforge.mappings import FT


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
    output = content.format(name=FT.FORGE)

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
    output = content.format(name=FT.CACHE)

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
    output = content.format(name=FT.BUFFERALLOC)

    return output


def CreateVoidEnum(ctx: VkForgeContext) -> str:
    content = """\
#define {name}(Var, Type, Func, Sizelimit, ...) \
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \
    Func(__VA_ARGS__, &Var##_count, 0); \
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \
}} while(0)
"""
    output = content.format(name=FT.ENUM)

    return output

def CreateResultEnum(ctx: VkForgeContext) -> str:
    content = """\
#define {name}(Var, Type, Func, Sizelimit, ...) \
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \
    Func(__VA_ARGS__, &Var##_count, 0); \
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \
}} while(0)
"""
    output = content.format(name=FT.ENUM)

    return output
