#include <SDL3/SDL.h>
#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"

#define UPDATE_TICKS (1000 / 120)
#define DRAW_TICKS   (1000 / 60)

// Simple render callbacks
static void CopyCallback(VkForgeRender render) {
    // Copy operations (like uploading textures) would go here
}

static void DrawCallback(VkForgeRender render) {
    // Get the layout from user data
    //VkForgeLayout* layout = (VkForgeLayout*)render.userData;
    
    // Bind pipeline
    //VkForge_BindPipeline(layout, "MyPipeline", render.drawCmdBuf);
    
    // Actual drawing commands would go here
    // (This is where you'd draw your objects)
}

int main()
{
    if(!SDL_Init(SDL_INIT_VIDEO))
    {
        SDL_Log("[SDL] Failed to initialize: %s", SDL_GetError());
        exit(1);
    }

    SDL_Window* window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);
    if(!window)
    {
        SDL_Log("[SDL] Failed to create window: %s", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    // Initialize Vulkan core
    //const char* deviceExtensions[] = {VK_KHR_SWAPCHAIN_EXTENSION_NAME};
    VkForgeCore* core = VkForge_CreateCore(
        window,
        VK_FORMAT_B8G8R8A8_UNORM,
        2,                         // Double buffering
        VK_PRESENT_MODE_FIFO_KHR,  // VSync enabled
        0,//deviceExtensions,
        0//1
    );

    if(!core)
    {
        SDL_Log("[Vulkan] Failed to create core");
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    // Create layout and pipeline
    VkForgeLayout* layout = VkForge_CreateLayout(core);
    if(!layout || VkForge_CreatePipeline(layout, "MyPipeline") != VK_SUCCESS)
    {
        SDL_Log("[Vulkan] Failed to setup pipeline");
        if(layout) VkForge_DestroyLayout(layout);
        VkForge_DestroyCore(core);
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    // Create renderer
    VkForgeRender* render = VkForge_CreateRender(
        core->physical_device,
        core->surface,
        core->device,
        core->queue,
        core->cmdpool,
        core->swapchain,
        core->swapchain_images,
        core->swapchain_imgviews,
        CopyCallback,
        DrawCallback,
        "F9CB99",
        layout  // Pass layout as user data
    );

    if(!render)
    {
        SDL_Log("[Vulkan] Failed to create renderer");
        VkForge_DestroyLayout(layout);
        VkForge_DestroyCore(core);
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    bool running = true;
    Uint64 current_ticks;
    Uint64 u_previous_ticks = SDL_GetTicks();
    Uint64 d_previous_ticks = u_previous_ticks;
    Uint64 u_accumulate_ticks = 0;
    Uint64 d_accumulate_ticks = 0;

    while(running)
    {
        SDL_Event event;
        while(SDL_PollEvent(&event))
        {
            if(event.type == SDL_EVENT_QUIT)
                running = false;
        }

        current_ticks = SDL_GetTicks();
        Sint64 u_elapsed_ticks = current_ticks - u_previous_ticks + u_accumulate_ticks;
        Sint64 d_elapsed_ticks = current_ticks - d_previous_ticks + d_accumulate_ticks;

        // Update loop (120Hz)
        if(u_elapsed_ticks >= UPDATE_TICKS)
        {
            u_accumulate_ticks = u_elapsed_ticks - UPDATE_TICKS;
            u_previous_ticks = current_ticks;
            
            // Game state updates would go here
        }

        // Render loop (60Hz)
        if(d_elapsed_ticks >= DRAW_TICKS)
        {
            d_accumulate_ticks = d_elapsed_ticks - DRAW_TICKS;
            d_previous_ticks = current_ticks;

            // Let VkForge handle all rendering operations
            VkForge_UpdateRender(render);
        }
    }

    // Cleanup
    vkDeviceWaitIdle(core->device);
    VkForge_DestroyRender(render);
    VkForge_DestroyLayout(layout);
    VkForge_DestroyCore(core);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}