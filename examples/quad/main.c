#include "VkForge/vkforge_typedecls.h"
#include "VkForge/vkforge_funcdecls.h"
#include "entity.h"

#define UPDATE_TICKS (1000 / 120)
#define DRAW_TICKS   (1000 / 60)

static VisualRect   entities[24] = {0};
static uint32_t entity_count = 0;

typedef struct UserCallbackData UserCallbackData;

struct UserCallbackData //This is just an example. Another approach would to make these fields global.
{
    VkForgeLayout* layout;
    float framerate;
    VkForgeBufferAlloc quadBuffer;
    VkForgeBufferAlloc entityBuffer; 
    VkForgeBufferAlloc stagingBuffer;
};

static void CopyCallback(VkForgeRender render) {
    UserCallbackData* userData = (UserCallbackData*)render.userData;

    entity_count = 0; //reset entity count

    /////////////////////////////////////////////////
    // Updated By External User Defined Draw Commands
    // vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


    VisualRect entity = {0};
    entity.color[0] = 1;
    entity.color[1] = 1;
    entity.color[2] = 1;
    entity.color[3] = 1;
    entity.size[0] = 0.75f;
    entity.size[1] = 0.75f;

    entities[entity_count++] = entity;

    // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    /////////////////////////////////////////////////
    
    if(entity_count)
    {
        void* data;
        vkMapMemory(
            render.device, 
            userData->stagingBuffer.memory, 
            0, 
            sizeof(VisualRect) * entity_count, 
            0, 
            &data
        );
        SDL_memcpy(
            data, 
            entities, 
            sizeof(VisualRect) * entity_count
        );
        vkUnmapMemory(render.device, userData->stagingBuffer.memory);

        VkForge_CmdCopyBuffer(
            render.cmdbuf_copy,
            userData->stagingBuffer.buffer,
            userData->entityBuffer.buffer,
            0,
            0,
            sizeof(VisualRect) * entity_count
        );

        VkForge_CmdBufferBarrier(
            render.cmdbuf_copy,
            userData->entityBuffer.buffer,
            0,
            sizeof(VisualRect) * entity_count,
            VK_ACCESS_2_TRANSFER_WRITE_BIT,
            VK_ACCESS_2_VERTEX_ATTRIBUTE_READ_BIT,
            VK_PIPELINE_STAGE_2_TRANSFER_BIT,
            VK_PIPELINE_STAGE_2_VERTEX_INPUT_BIT
        );
    }
}

static void DrawCallback(VkForgeRender render) {
    UserCallbackData* userData = (UserCallbackData*)render.userData;

    VkViewport viewport = {0};
    viewport.width = (float)render.extent.width;
    viewport.height = (float)render.extent.height;
    viewport.maxDepth = 1.0f;

    VkRect2D scissor = {0};
    scissor.extent.width = render.extent.width;
    scissor.extent.height = render.extent.height;

    vkCmdSetViewport(render.cmdbuf_draw, 0, 1, &viewport);
    vkCmdSetScissor(render.cmdbuf_draw, 0, 1, &scissor);

    if(entity_count)
    {
        // if any descriptset, you need to bind them manually using Vk functions
        VkForge_BindPipeline(userData->layout, "Default", render.cmdbuf_draw);

        
        VkBuffer buffers[] = {
            userData->quadBuffer.buffer,   // Buffer 0: match the Config and Shader
            userData->entityBuffer.buffer  // Buffer 1: match the Config and Shader
        };
        VkDeviceSize offsets[] = {0, 0}; //Could be the same buffer bound multiple times at different offsets

        vkCmdBindVertexBuffers(render.cmdbuf_draw, 0, 2, buffers, offsets);
        vkCmdDraw(render.cmdbuf_draw, 6, entity_count, 0, 0);
    }
}

int main() {
    SDL_Log("Launching VkForge Quad Application");

    if( SDL_Init(SDL_INIT_VIDEO) == false ) {
        SDL_LogError(0, "Failed to initialize: %s", SDL_GetError());
        exit(1);
    }

    SDL_Window* window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);
    if(!window) {
        SDL_LogError(0, "Failed to create window: %s", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    // Selects Physical Device and Create Core Vulkan Obects
    // Instance, Surface, Device, CommandPool 
    VkForgeCore* core = VkForge_CreateCore(
        window,
        0,
        0
    );

    if(!core) {
        SDL_LogError(0, "Failed to create core");
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    // Load VkForge Layout Feature
    // It designs pipeline layouts based on all the pipelines in your Config
    // It loads them as needed when you create your pipelines
    VkForgeLayout* layout = VkForge_CreateLayout(
        core->surface, 
        core->physical_device, 
        core->device
    );

    if(!layout || VkForge_CreatePipeline(layout, "Default") != VK_SUCCESS)  //Pipeline name is the same name defined in the Config
    {
        SDL_LogError(0, "Failed to setup pipeline");
        if(layout) VkForge_DestroyLayout(layout);
        VkForge_DestroyCore(core);
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    UserCallbackData userData = {0};
    userData.layout = layout;

    // Temporary Command Buffer to use at initialization.
    // We will free after use since Render creates it own command buffers and pass those to the callbacks
    // I could have created the render object first and use one of its command buffers
    VkCommandBuffer oneCopy = VkForge_AllocateCommandBuffer(core->device, core->cmdpool);

    // Quad
    // Each vertex: x, y
    float quad[] = {
        // First triangle
        -1.0f, -1.0f,
        1.0f, -1.0f,
        1.0f,  1.0f,

        // Second triangle
        -1.0f, -1.0f,
        1.0f,  1.0f,
        -1.0f,  1.0f
    };

    userData.quadBuffer = VkForge_CreateBufferAlloc(
        core->physical_device,
        core->device,
        sizeof(quad),
        VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
    );

    VkForge_LoadBuffer( //Since we will only ever need to load quad once, we can use LoadBuffer convenience function
        core->physical_device,
        core->device,
        core->queue,
        oneCopy,
        userData.quadBuffer.buffer, // VkBuffer receiving the data
        0, // offset in VkBuffer
        sizeof(quad), // sizeof data being copied
        quad // actual raw data
    ); 

    vkFreeCommandBuffers(core->device, core->cmdpool, 1, &oneCopy);

    // We create the buffers for entities
    // There are updated in the callback for copy
    userData.stagingBuffer = VkForge_CreateStagingBuffer(
        core->physical_device,
        core->device,
        sizeof(entities)
    );

    userData.entityBuffer = VkForge_CreateBufferAlloc(
        core->physical_device,
        core->device,
        sizeof(entities),
        VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
    );

    // Load VkForge Render Feature
    // Handles Swapchain management, Synchronize Management, Image Layout Management and Clearing the Screen with just one function call.
    // You job is to handle the transfering the data, binding of descriptors and pipelines and making draw calls 
    VkForgeRender* render = VkForge_CreateRender(
        window,
        core->surface,
        core->physical_device,        
        core->device,
        core->queue,
        core->cmdpool,
        VK_FORMAT_B8G8R8A8_UNORM, // Requested Format
        4, // Requested Swapchain Size
        VK_PRESENT_MODE_MAILBOX_KHR, // Requested Present Mode
        CopyCallback, // Your Callback with your transfer commands
        DrawCallback, // Your Callback with your draw commands
        "C5B0CD", // Clear Screen Color in Hex RGB. Alpha is always 1 for clear screen.
        &userData // Your Data to Pass to your callbacks
    );

    if(!render) {
        SDL_LogError(0, "Failed to create renderer");
        VkForge_DestroyLayout(layout); // Destroys all created pipelines, pipeline layouts and descriptorset layouts
        VkForge_DestroyCore(core); // Destroys all core objects.
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
            userData.framerate = 1.0 / (float)d_elapsed_ticks;
            VkForge_UpdateRender(render);
        }
    }

    SDL_LogInfo(0, "Quitting Application");
    vkDeviceWaitIdle(core->device);
    VkForge_DestroyBufferAlloc(core->device, userData.quadBuffer);
    VkForge_DestroyBufferAlloc(core->device, userData.entityBuffer);
    VkForge_DestroyBufferAlloc(core->device, userData.stagingBuffer);
    VkForge_DestroyRender(render);
    VkForge_DestroyLayout(layout);
    VkForge_DestroyCore(core);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}