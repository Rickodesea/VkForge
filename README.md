# VkForge

**VkForge** (Vulkan Forge) is a **Vulkan User-End API Implementation Generator** written in **Python**. It's purpose is to quickly generate the code needed for Graphics Renderer development.

VkForge is the opposite of using a wrapper layer (like SDL_GPU or shVulkan).  
Instead of abstracting Vulkan, you use the **Vulkan API directly** — but VkForge saves you from writing all the repetitive boilerplate by generating it for you, based on your **shaders** and a simple **config**.

VkForge does not force any design pattern — you have the same freedom as hand-written Vulkan.  
By design, VkForge does not generate an entire renderer — it generates **components** for you to connect as you wish.

VkForge also provides a list of utility code that makes it quicker to code in Vulkan. If the utility function
abstracts away something you want to control, just use the direct Vulkan function.

---

## VkForge Source

The input for VkForge is:
- **Shaders:** Provide type, location, descriptor sets, and bindings.
- **Config:** Defines pipeline details and other setup.

---

## VkForge Output

VkForge generates **C99 source code** for your Vulkan implementation.  
Platform integration is done via **SDL3**.
We are hoping to improve VkForge — see [CONTRIBUTING.md](CONTRIBUTING.md).
Feel free to contribute by using it, reporting issues, making pull requests and via othe produtive ways!

---

## Generated Code

The generated C code is split into:
- core : the core vulkan objects
- utils: the utility vulkan functions
- pipelines: the generated pipelines based on your shaders
- layout: the generated layouts based on your shaders
- header files with type and function declarations

Example Implementation:
```c
#include <SDL3/SDL.h>
#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"

#define UPDATE_TICKS (1000 / 120)
#define DRAW_TICKS   (1000 / 60)

static void CopyCallback(VkForgeRender render) {
}

static void DrawCallback(VkForgeRender render) {
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

    VkForgeCore* core = VkForge_CreateCore(
        window,
        VK_FORMAT_B8G8R8A8_UNORM,
        2,                         // Double buffering
        VK_PRESENT_MODE_FIFO_KHR,  // VSync enabled
        0, // Extensions requested - VkForge already request the basic required ones
        0
    );

    if(!core)
    {
        SDL_Log("[Vulkan] Failed to create core");
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    /// VkForge Special Layout Feature
    /// It design your layout automatically based on all combination of your shaders.
    /// You can also create your pipelines from it.
    /// You name your pipeline in your config file.
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

    /// VkForge Special Render Feature
    /// Manages sync for you in the fastest possible way!
    /// Manages the swapchain and dynamic rendering and clear screen.
    /// You insert your custom logic via the callbacks.
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
        "F9CB99", //Clear screen color. Just copy and past from sites like https://colorhunt.co/
        layout    // Pass any data here and your callbacks will have access. In this case we pass
                  // VkForge special layout as user data.
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

        if(u_elapsed_ticks >= UPDATE_TICKS)
        {
            u_accumulate_ticks = u_elapsed_ticks - UPDATE_TICKS;
            u_previous_ticks = current_ticks;            
            //You game logic here
            //Ex: Move player left by 200 pixels, etc
        }

        if(d_elapsed_ticks >= DRAW_TICKS)
        {
            d_accumulate_ticks = d_elapsed_ticks - DRAW_TICKS;
            d_previous_ticks = current_ticks;

            // You update any buffer that will be copied in the copyCallback here.

            VkForge_UpdateRender(render); //This function handles everything including rendering.
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
```

See [REFERENCE](REFERENCE.md) for more details.

---

## Todo

- [ ] Add support for Renderpass and earlier versions: Currently only support Vulkan >= 1.3 and Dynamic Rendering. 
- [ ] Platform abstraction: Allow users to pass a flag `vkforge --platform SDL3` with options like `Raylib`, `GLFW`, etc. VkForge will generate the code specific for the platform you want.
- [ ] Sub-Platform abstraction: I can combined SDL3 as my main platform and then use SDL3_image, stb_image, etc to load images and so on. `vkforge --platform-image SDL3_image`.
- [ ] 3D utility functions: Utility functions specific for 3D rendering
- [ ] Extended version utility functions: Extended utility functions provide additional parameters that allow the user to pass pNext and pAllocationCallbacks.

---

## Connections

* [VkForge Python Package](https://pypi.org/project/vkforge/) - Check out for stable release
* [VkForge Github](https://github.com/Rickodesea/VkForge) - Check out for latest release and updates

---

## Purpose

Vulkan is extremely detailed — this is a good thing!  
But it can mean tedious and repetitive coding.  
VkForge solves this by letting you describe your Vulkan setup in a simple Config file.  
A config is short, easy to write, and saves hours of manual work.

---

## Closing

VkForge is free and MIT licensed — contributions are welcome!  
I hope you find it useful for your projects.

VkForge is led and maintained by its benevolent leader, Alrick Grandison.

(c) 2025 Alrick Grandison, Algodal
