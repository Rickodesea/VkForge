#include "VkForge/vkforge_typedecls.h"
#include "VkForge/vkforge_funcdecls.h"
#include "VkForge/vkforge_layout.h"
#include "entity.h"

// This version uses the VkForge Layout to generate
// the descriptorsets instead of manually generating it.

#define UPDATE_TICKS (1000 / 120)
#define DRAW_TICKS (1000 / 60)

static VisualRect entities[24] = {0};
static uint32_t entity_count = 0;

typedef struct UserCallbackData UserCallbackData;

struct UserCallbackData
{
    VkForgeLayout *layout;
    VkForgeLayoutQueue *layout_queue;
    VkForgePipelineLayout pipelineLayout;
    VkForgePipeline pipeline;
    float framerate;
    VkForgeBufferAlloc quadBuffer;
    VkForgeBufferAlloc entityBuffer;
    VkForgeBufferAlloc stagingBuffer;
    VkForgeTexture *texture;
};

static void CopyCallback(VkForgeRender render)
{
    UserCallbackData *userData = (UserCallbackData *)render.userData;

    entity_count = 0; // reset entity count

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

    if (entity_count)
    {
        void *data;
        vkMapMemory(
            render.device,
            userData->stagingBuffer.memory,
            0,
            sizeof(VisualRect) * entity_count,
            0,
            &data);
        SDL_memcpy(
            data,
            entities,
            sizeof(VisualRect) * entity_count);
        vkUnmapMemory(render.device, userData->stagingBuffer.memory);

        VkForge_CmdCopyBuffer(
            render.cmdbuf_copy,
            userData->stagingBuffer.buffer,
            userData->entityBuffer.buffer,
            0,
            0,
            sizeof(VisualRect) * entity_count);

        VkForge_CmdBufferBarrier(
            render.cmdbuf_copy,
            userData->entityBuffer.buffer,
            0,
            sizeof(VisualRect) * entity_count,
            VK_ACCESS_2_TRANSFER_WRITE_BIT,
            VK_ACCESS_2_VERTEX_ATTRIBUTE_READ_BIT,
            VK_PIPELINE_STAGE_2_TRANSFER_BIT,
            VK_PIPELINE_STAGE_2_VERTEX_INPUT_BIT);

        // Queue texture descriptor resource (only if texture exists and pipeline has descriptor sets)
        if (userData->texture && userData->pipelineLayout.descriptor_set_count > 0)
        {
            VkForgeDescriptorResource resource = {0};
            resource.image.imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
            resource.image.imageView = userData->texture->imageView;
            resource.image.sampler = userData->texture->sampler;

            VkForge_QueueDescriptorResourceForForgePipelineLayout(
                userData->layout_queue,
                &userData->pipelineLayout,
                0,
                0,
                resource);
        }
    }
}

static void DrawCallback(VkForgeRender render)
{
    UserCallbackData *userData = (UserCallbackData *)render.userData;

    VkViewport viewport = {0};
    viewport.width = (float)render.extent.width;
    viewport.height = (float)render.extent.height;
    viewport.maxDepth = 1.0f;

    VkRect2D scissor = {0};
    scissor.extent.width = render.extent.width;
    scissor.extent.height = render.extent.height;

    vkCmdSetViewport(render.cmdbuf_draw, 0, 1, &viewport);
    vkCmdSetScissor(render.cmdbuf_draw, 0, 1, &scissor);

    if (entity_count)
    {
        // Bind the pipeline
        vkCmdBindPipeline(
            render.cmdbuf_draw,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            userData->pipeline.pipeline);

        // Use the new binding function that handles descriptor writes and binding
        VkForge_BindForgePipelineLayoutPerWriteDescriptorResourceQueue(
            userData->layout,
            userData->layout_queue,
            &userData->pipelineLayout,
            render.cmdbuf_draw);

        VkBuffer buffers[] = {
            userData->quadBuffer.buffer,  // Buffer 0: match the Config and Shader
            userData->entityBuffer.buffer // Buffer 1: match the Config and Shader
        };
        VkDeviceSize offsets[] = {0, 0};

        vkCmdBindVertexBuffers(render.cmdbuf_draw, 0, 2, buffers, offsets);
        vkCmdDraw(render.cmdbuf_draw, 6, entity_count, 0, 0);
    }
}

int main()
{
    SDL_Log("Launching VkForge Quad Application");

    if (SDL_Init(SDL_INIT_VIDEO) == false)
    {
        SDL_LogError(0, "Failed to initialize: %s", SDL_GetError());
        exit(1);
    }

    SDL_Window *window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);
    if (!window)
    {
        SDL_LogError(0, "Failed to create window: %s", SDL_GetError());
        SDL_Quit();
        exit(1);
    }

    // Selects Physical Device and Create Core Vulkan Obects
    // Instance, Surface, Device, CommandPool
    VkForgeCore *core = VkForge_CreateCore(
        window,
        0,
        0);

    if (!core)
    {
        SDL_LogError(0, "Failed to create core");
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    // Create the layout manager using the new API
    VkForgeLayout *layout = VkForge_CreateForgeLayout(
        core->surface,
        core->physical_device,
        core->device);

    // Create layout queue for descriptor resources
    VkForgeLayoutQueue *layout_queue = VkForge_CreateForgeLayoutQueue();

    UserCallbackData userData = {0};
    userData.layout = layout;
    userData.layout_queue = layout_queue;

    // Create pipeline layout and pipeline using new API
    userData.pipelineLayout = VkForge_CreateForgePipelineLayout(layout, "Default");
    userData.pipeline = VkForge_CreateForgePipeline(layout, "Default", userData.pipelineLayout);

    if (!layout || !layout_queue ||
        userData.pipelineLayout.pipelineLayout == VK_NULL_HANDLE ||
        userData.pipeline.pipeline == VK_NULL_HANDLE)
    {
        SDL_LogError(0, "Failed to setup pipeline");

        // Clean up any created resources
        if (userData.pipeline.pipeline != VK_NULL_HANDLE)
            VkForge_DestroyForgePipeline(layout, &userData.pipeline);

        if (userData.pipelineLayout.pipelineLayout != VK_NULL_HANDLE)
            VkForge_DestroyForgePipelineLayout(layout, &userData.pipelineLayout);

        if (layout_queue)
            VkForge_DestroyForgeLayoutQueue(layout_queue);

        if (layout)
            VkForge_DestroyForgeLayout(layout);

        VkForge_DestroyCore(core);
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }

    // Temporary Command Buffer to use at initialization.
    VkCommandBuffer oneCopy = VkForge_AllocateCommandBuffer(core->device, core->cmdpool);

    // Quad with texture coordinates
    float quad[] = {
        // First triangle
        -1.0f, -1.0f, 0.0f, 0.0f, // bottom-left
        1.0f, -1.0f, 1.0f, 0.0f,  // bottom-right
        1.0f, 1.0f, 1.0f, 1.0f,   // top-right

        // Second triangle
        -1.0f, -1.0f, 0.0f, 0.0f, // bottom-left
        1.0f, 1.0f, 1.0f, 1.0f,   // top-right
        -1.0f, 1.0f, 0.0f, 1.0f   // top-left
    };

    userData.quadBuffer = VkForge_CreateBufferAlloc(
        core->physical_device,
        core->device,
        sizeof(quad),
        VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);

    VkForge_LoadBuffer(
        core->physical_device,
        core->device,
        core->queue,
        oneCopy,
        userData.quadBuffer.buffer,
        0,
        sizeof(quad),
        quad);

    // Load texture
    userData.texture = VkForge_CreateTexture(
        core->physical_device,
        core->device,
        core->queue,
        oneCopy,
        "statue.jpg",
        0);

    vkFreeCommandBuffers(core->device, core->cmdpool, 1, &oneCopy);

    // Queue initial texture descriptor resource (only once at startup for static texture)
    if (userData.texture && userData.pipelineLayout.descriptor_set_count > 0)
    {
        VkForgeDescriptorResource texture_resource = {0};
        texture_resource.image.imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
        texture_resource.image.imageView = userData.texture->imageView;
        texture_resource.image.sampler = userData.texture->sampler;

        VkForge_QueueDescriptorResourceForForgePipelineLayout(
            layout_queue,
            &userData.pipelineLayout,
            0, // set index
            0, // binding index
            texture_resource);

        // Write the initial descriptor set
        VkForge_WriteDescriptorResourceQueueForCurrentlyBoundForgePipelineLayout(
            layout,
            layout_queue,
            &userData.pipelineLayout);
    }

    // We create the buffers for entities
    userData.stagingBuffer = VkForge_CreateStagingBuffer(
        core->physical_device,
        core->device,
        sizeof(entities));

    userData.entityBuffer = VkForge_CreateBufferAlloc(
        core->physical_device,
        core->device,
        sizeof(entities),
        VK_BUFFER_USAGE_VERTEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);

    // Load VkForge Render Feature
    VkForgeRender *render = VkForge_CreateRender(
        window,
        core->surface,
        core->physical_device,
        core->device,
        core->queue,
        core->cmdpool,
        VK_FORMAT_B8G8R8A8_UNORM,
        4,
        VK_PRESENT_MODE_MAILBOX_KHR,
        CopyCallback,
        DrawCallback,
        "C5B0CD",
        &userData);

    if (!render)
    {
        SDL_LogError(0, "Failed to create renderer");

        // Clean up resources
        if (userData.texture)
            VkForge_DestroyTexture(core->device, userData.texture);
        VkForge_DestroyBufferAlloc(core->device, userData.quadBuffer);
        VkForge_DestroyBufferAlloc(core->device, userData.entityBuffer);
        VkForge_DestroyBufferAlloc(core->device, userData.stagingBuffer);
        VkForge_DestroyForgePipeline(layout, &userData.pipeline);
        VkForge_DestroyForgePipelineLayout(layout, &userData.pipelineLayout);
        VkForge_DestroyForgeLayoutQueue(layout_queue);
        VkForge_DestroyForgeLayout(layout);
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

    while (running)
    {
        SDL_Event event;
        while (SDL_PollEvent(&event))
        {
            if (event.type == SDL_EVENT_QUIT)
                running = false;
        }

        current_ticks = SDL_GetTicks();
        Sint64 u_elapsed_ticks = current_ticks - u_previous_ticks + u_accumulate_ticks;
        Sint64 d_elapsed_ticks = current_ticks - d_previous_ticks + d_accumulate_ticks;

        if (u_elapsed_ticks >= UPDATE_TICKS)
        {
            u_accumulate_ticks = u_elapsed_ticks - UPDATE_TICKS;
            u_previous_ticks = current_ticks;
        }

        if (d_elapsed_ticks >= DRAW_TICKS)
        {
            d_accumulate_ticks = d_elapsed_ticks - DRAW_TICKS;
            d_previous_ticks = current_ticks;
            userData.framerate = 1.0 / (float)d_elapsed_ticks;
            VkForge_UpdateRender(render);
        }
    }

    SDL_LogInfo(0, "Quitting Application");
    vkDeviceWaitIdle(core->device);

    if (userData.texture)
        VkForge_DestroyTexture(core->device, userData.texture);
    VkForge_DestroyBufferAlloc(core->device, userData.quadBuffer);
    VkForge_DestroyBufferAlloc(core->device, userData.entityBuffer);
    VkForge_DestroyBufferAlloc(core->device, userData.stagingBuffer);
    VkForge_DestroyRender(render);
    VkForge_DestroyForgePipeline(layout, &userData.pipeline);
    VkForge_DestroyForgePipelineLayout(layout, &userData.pipelineLayout);
    VkForge_DestroyForgeLayoutQueue(layout_queue);
    VkForge_DestroyForgeLayout(layout);
    VkForge_DestroyCore(core);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
