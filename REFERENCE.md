# VkForge Documentation

## Overview

VkForge is a Vulkan utility library designed to simplify Vulkan initialization and pipeline creation while maintaining full visibility and control over the Vulkan API. It provides convenience functions for common tasks but doesn't abstract away the underlying Vulkan concepts.

## Core Components

### 1. VkForgeCore

The central convenience structure that holds all essential Vulkan objects:

```c
struct VkForgeCore {
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
};
```

#### Key Functions:
- `VkForge_CreateCore()`: Initializes all core Vulkan objects
- `VkForge_DestroyCore()`: Cleans up all resources

### 2. Pipeline Generation System

VkForge's standout feature is its pipeline generator that automatically creates pipeline implementations based on your shaders and configuration.

#### Key Benefits:
- Generates pipeline implementation code from shaders
- Handles descriptor set layouts automatically
- Provides pipeline creation by name
- Maintains full visibility of the generated code

### 3. Rendering System

The `VkForgeRender` structure and related functions manage the rendering loop:

```c
struct VkForgeRender {
    // Core objects
    VkPhysicalDevice      physical_device;
    VkSurfaceKHR          surface;
    VkDevice              device;
    VkQueue               queue;
    VkCommandPool         cmdPool;
    
    // Rendering state
    VkExtent2D            extent;
    VkCommandBuffer       copyCmdBuf;
    VkCommandBuffer       drawCmdBuf;
    VkForgeRenderCallback copyCallback;
    VkForgeRenderCallback drawCallback;
    
    // Swapchain
    VkSwapchainKHR        swapchain;
    VkImage*              images;
    VkImageView*          imgviews;
    uint32_t              index;
    
    // Sync objects
    VkFence               acquireImageFence;
    VkFence               submitQueueFence;
    VkSemaphore           copySemaphore;
    VkSemaphore           drawSemaphore;
    
    // State
    const char*           color;
    VkForgeRenderStatus   status;
    void*                 userData;
};
```

#### Key Functions:
- `VkForge_CreateRender()`: Sets up the renderer
- `VkForge_UpdateRender()`: Manages the render loop state machine
- `VkForge_DestroyRender()`: Cleans up render resources

## Getting Started

### Basic Initialization

```c
// Initialize SDL and create window
SDL_Window* window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);

// Initialize VkForge core
VkForgeCore* core = VkForge_CreateCore(
    window,
    VK_FORMAT_B8G8R8A8_UNORM,  // Requested format
    2,                         // Double buffering
    VK_PRESENT_MODE_FIFO_KHR,  // VSync enabled
    NULL,                      // No additional device extensions
    0
);

// Create pipeline layout
VkForgeLayout* layout = VkForge_CreateLayout(core);

// Create pipeline by name
VkForge_CreatePipeline(layout, "MyPipeline");

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
    "FFFFFF",  // White clear color
    layout     // User data
);
```

### Main Loop

```c
while (running) {
    // Handle events
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_EVENT_QUIT)
            running = false;
    }

    // Update and render
    VkForge_UpdateRender(render);
}
```

## Pipeline System

### Pipeline Creation

VkForge generates pipeline implementations based on your shaders. The generated code includes:

1. Vertex input descriptions
2. Pipeline state configurations
3. Shader module creation
4. Pipeline creation

Example generated pipeline:

```c
VkPipeline VkForge_CreatePipelineForMyPipeline(
    VkAllocationCallbacks* allocator,
    void* next,
    VkDevice device,
    VkPipelineLayout pipeline_layout
) {
    // Shader module creation
    VkShaderModule shader_vert = VkForge_CreateShaderModule(device, "build/vert.vert.spv");
    VkShaderModule shader_frag = VkForge_CreateShaderModule(device, "build/frag.frag.spv");
    
    // Pipeline state setup
    VkPipelineShaderStageCreateInfo stageInfo[2] = {...};
    VkVertexInputBindingDescription bindingDesc[1] = {...};
    VkVertexInputAttributeDescription attributeDesc[1] = {...};
    
    // Pipeline creation
    VkGraphicsPipelineCreateInfo pipelineInfo = {...};
    vkCreateGraphicsPipelines(device, VK_NULL_HANDLE, 1, &pipelineInfo, allocator, &pipeline);
    
    return pipeline;
}
```

### Pipeline Layouts

VkForge automatically creates descriptor set layouts and pipeline layouts based on your shader's requirements:

```c
static VkForgeLayoutBindDesign BIND_0_0_0 = {
    VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, 1, STAGE_0_0_0
};

static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_0_0 = {
    14, BIND_DESIGNS_0_0  // 14 bindings
};

static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_0 = {
    1, DESCRIPTOR_SET_LAYOUTS_0  // 1 descriptor set layout
};
```

## Utility Functions

VkForge provides numerous utility functions for common Vulkan operations:

### Memory Management
- `VkForge_CreateBufferAlloc()`
- `VkForge_CreateImageAlloc()`
- `VkForge_AllocDeviceMemory()`

### Command Buffer Operations
- `VkForge_BeginCommandBuffer()`
- `VkForge_EndCommandBuffer()`
- `VkForge_CmdImageBarrier()`
- `VkForge_CmdBufferBarrier()`

### Synchronization
- `VkForge_CreateFence()`
- `VkForge_CreateSemaphore()`
- `VkForge_QueueSubmit()`
- `VkForge_QueuePresent()`

### Shader Loading
- `VkForge_CreateShaderModule()`
- `VkForge_ReadFile()`

## Best Practices

1. **Pipeline Creation**: Use the generated pipeline functions rather than creating pipelines manually
2. **Resource Management**: Take advantage of the `VkForgeBufferAlloc` and `VkForgeImageAlloc` helper structures
3. **Rendering**: Use the `VkForgeRender` system for managing the render loop
4. **Error Handling**: Check all VkForge functions for failure (many will exit on error)

## Example Shader Setup

VkForge works with your existing SPIR-V shaders. Just place them in the expected location (e.g., `build/vert.vert.spv` and `build/frag.frag.spv`) and the pipeline generator will create appropriate pipeline code.

## Advantages Over Raw Vulkan

1. **Faster Setup**: Get a clear screen rendering in <30 minutes vs. a full day with raw Vulkan
2. **Maintainable**: Generated code is visible and modifiable
3. **Consistent**: Enforces good practices across projects
4. **Flexible**: Mix VkForge convenience functions with raw Vulkan as needed
5. **Foundation**: You can build on top of the initial generated code
6. **Toolchain**: You can use VkForge as part of a tool chain to generate your base Vulkan code

## Limitations

1. Not a full framework - you still need to understand Vulkan concepts and take the components and build what you want.
2. Generated code may need customization for advanced use cases
3. Primarily focused on graphics pipelines (not compute) for now. See [CONTRIBUTION](CONTRIBUTION.md) to help improve VkForge. We will love to have helper functions for compute logic.

## Conclusion

VkForge strikes a balance between convenience and control, making Vulkan more accessible while preserving its power and flexibility. By generating pipeline code and providing utility functions for common tasks, it significantly reduces the boilerplate required for Vulkan applications while keeping all implementation details visible and modifiable.