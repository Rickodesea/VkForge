from vkforge.context import VkForgeContext
from vkforge.mappings import *

def CreateSurface(ctx: VkForgeContext) -> str:
    content = """\
void {name}
(
    VkAllocationCallbacks* allocator,
    void*                  next,
    VkInstance             instance,
    SDL_Window*            window,

    VkSurfaceKHR*          retSurface
)
{{
    assert(retSurface);

    (void)next;

    VkSurfaceKHR surface = VK_NULL_HANDLE;

    if( !SDL_Vulkan_CreateSurface(window, instance, allocator, &surface) )
    {{
        SDL_Log("Failed to Create Vulkan/SDL3 Surface: %%s", SDL_GetError());
        exit(1);
    }}

    *retSurface = surface;
}}


"""
    output = content.format(name=FUNC_NAME.SURFACE)

    return output

def GetPipelineStrings(ctx: VkForgeContext):
    return [
        
    ]