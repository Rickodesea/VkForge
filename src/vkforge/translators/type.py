from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateCore(ctx: VkForgeContext) -> str:
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
    output = content.format(name=TYPE_NAME.CORE)

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

def CreateImageAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};

struct {name}
{{
    VkImage        image;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format(name=TYPE_NAME.IMAGEALLOC)

    return output

def CreateLayout(ctx: VkForgeContext) -> str:
    content = """\
typedef struct {name} {name};
"""
    output = content.format(name=TYPE_NAME.LAYOUT)

    return output

def GetMaxPipelines(ctx: VkForgeContext):
    references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
    return max(len(references), 1)

def GetMaxPipelineLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    return max(len(layouts), 1)

def GetMaxDescriptorSetLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptorset_layout = 0
    for layout in layouts:
        if len(layout) > max_descriptorset_layout:
            max_descriptorset_layout = len(layout)
    return max(max_descriptorset_layout, 1)

def GetMaxDescriptorBindings(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptor_binding = 0
    for layout in layouts:
        for set1 in layout:
            if len(set1) > max_descriptor_binding:
                max_descriptor_binding = len(set1)
    return max(max_descriptor_binding, 1)

def CreateMaxes(ctx: VkForgeContext) -> str:
    content = """\
#define {max_pipelines} {max_pipelines_value}
#define {max_pipeline_layouts} {max_pipeline_layouts_value}
#define {max_descriptorset_layouts} {max_descriptorset_layouts_value}
#define {max_descriptor_bindings} {max_descriptor_bindings_value}
"""
    output = content.format(
        max_pipelines=TYPE_NAME.MAX_PIPELINES,
        max_pipelines_value=GetMaxPipelines(ctx),
        max_pipeline_layouts=TYPE_NAME.MAX_PIPELINE_LAYOUTS,
        max_pipeline_layouts_value=GetMaxPipelineLayouts(ctx),
        max_descriptorset_layouts=TYPE_NAME.MAX_DESCRIPTORSET_LAYOUTS,
        max_descriptorset_layouts_value=GetMaxDescriptorSetLayouts(ctx),
        max_descriptor_bindings=TYPE_NAME.MAX_DESCRIPTOR_BINDINGS,
        max_descriptor_bindings_value=GetMaxDescriptorBindings(ctx)
    )

    return output

def GetTypeStrings(ctx: VkForgeContext):
    return [
        CreateMaxes(ctx),
        CreateCore(ctx),
        CreateBufferAllocType(ctx),
        CreateImageAllocType(ctx),
        CreateLayout(ctx),
        
    ]