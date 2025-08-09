#include <SDL3/SDL.h>
#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"

#define UPDATE_TICKS (1000 / 120)
#define DRAW_TICKS   (1000 / 60)

static void CopyCallback(VkForgeRender render) {
}

static void DrawCallback(VkForgeRender render) {
}

int main() {
    if(!SDL_Init(SDL_INIT_VIDEO)) {
        SDL_Log("[SDL] Failed to initialize: %s", SDL_GetError());
        exit(1);
    }

    SDL_Window* window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);
    if(!window) {
        SDL_Log("[SDL] Failed to create window: %s", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    VkForgeCore* core = VkForge_CreateCore(
        window,
        0,
        0
    );

    if(!core) {
        SDL_Log("[Vulkan] Failed to create core");
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    VkForgeLayout* layout = VkForge_CreateLayout(core->device);
    if(!layout || VkForge_CreatePipeline(layout, "MyPipeline") != VK_SUCCESS) {
        SDL_Log("[Vulkan] Failed to setup pipeline");
        if(layout) VkForge_DestroyLayout(layout);
        VkForge_DestroyCore(core);
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    VkForgeRender* render = VkForge_CreateRender(
        window,
        core->physical_device,
        core->surface,
        core->device,
        core->queue,
        core->cmdpool,
        VK_FORMAT_B8G8R8A8_UNORM,
        2,
        VK_PRESENT_MODE_FIFO_KHR,
        CopyCallback,
        DrawCallback,
        "F9CB99",
        layout
    );

    if(!render) {
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

    while(running) {
        SDL_Event event;
        while(SDL_PollEvent(&event)) {
            if(event.type == SDL_EVENT_QUIT)
                running = false;
        }

        current_ticks = SDL_GetTicks();
        Sint64 u_elapsed_ticks = current_ticks - u_previous_ticks + u_accumulate_ticks;
        Sint64 d_elapsed_ticks = current_ticks - d_previous_ticks + d_accumulate_ticks;

        if(u_elapsed_ticks >= UPDATE_TICKS) {
            u_accumulate_ticks = u_elapsed_ticks - UPDATE_TICKS;
            u_previous_ticks = current_ticks;
        }

        if(d_elapsed_ticks >= DRAW_TICKS) {
            d_accumulate_ticks = d_elapsed_ticks - DRAW_TICKS;
            d_previous_ticks = current_ticks;
            VkForge_UpdateRender(render);
        }
    }

    vkDeviceWaitIdle(core->device);
    VkForge_DestroyRender(render);
    VkForge_DestroyLayout(layout);
    VkForge_DestroyCore(core);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}