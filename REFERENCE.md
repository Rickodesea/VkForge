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
    VkCommandPool    cmdpool;
};
```

#### Key Functions:
- `VkForge_CreateCore()`: Initializes all core Vulkan objects
- `VkForge_DestroyCore()`: Cleans up all resources

### 2. Automatic Swapchain Management with VkForgeRender

The `VkForgeRender` system provides automatic swapchain management including:

- **Automatic recreation** when window is resized or minimized/maximized
- **Failure recovery** for swapchain recreation (up to `VKFORGE_MAX_SWAPCHAIN_RECREATION` attempts)
- **State management** of the rendering lifecycle

```c
struct VkForgeRender {
    // Core objects
    SDL_Window*           window;
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
    
    // Swapchain management
    VkSwapchainKHR        swapchain;
    VkImage*              swapchain_images;
    VkImageView*          swapchain_imgviews;
    uint32_t              swapchain_size;
    uint32_t              index;
    uint16_t              swapchainRecreationCount;
    
    // Sync objects
    VkFence               acquireImageFence;
    VkFence               submitQueueFence;
    VkSemaphore           copySemaphore;
    VkSemaphore           drawSemaphore;
    
    // State
    const char*           color;
    VkForgeRenderStatus   status;
    void*                 userData;
    bool                  acquireSuccessful;
    bool                  presentSuccessful;
};
```

#### Key Features:
- Automatically detects and handles swapchain invalidation (window resize, minimization)
- Maintains a recreation counter to prevent infinite recreation loops
- Provides clear error reporting when swapchain recreation fails
- Manages the complete rendering lifecycle state machine
- Provides a render loop and automatic synchronization design to render as fast as possible

#### Key Functions:
- `VkForge_CreateRender()`: Sets up the renderer and initial swapchain
- `VkForge_UpdateRender()`: Manages the render loop state machine
- `VkForge_DestroyRender()`: Cleans up render resources
- `VkForge_ReCreateRenderSwapchain()`: Internal function for swapchain recreation

### 3. Pipeline Layout System

VkForge's layout system stores optimized pipeline layout designs for all shader combinations:

- Layout designs are generated during build time and stored in `layout.c`
- Single layout design used for the entire application
- Automatically creates descriptor set layouts and pipeline layouts based on shader requirements

```c
// Example generated layout design
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

### 4. Pipeline Generation System

VkForge generates pipeline implementations based on your shaders:

- Generates pipeline implementation code from shaders
- Handles descriptor set layouts automatically
- Provides pipeline creation by name
- Maintains full visibility of the generated code

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

## Getting Started

### Basic Initialization

```c
// Initialize SDL and create window
SDL_Window* window = SDL_CreateWindow("VKFORGE", 400, 400, SDL_WINDOW_VULKAN);

// Initialize VkForge core
VkForgeCore* core = VkForge_CreateCore(
    window,
    NULL,  // No additional device extensions
    0
);

// Create renderer with automatic swapchain management
VkForgeRender* render = VkForge_CreateRender(
    window,
    core->physical_device,
    core->surface,
    core->device,
    core->queue,
    core->cmdpool,
    VK_FORMAT_B8G8R8A8_UNORM,  // Requested format
    2,                         // Double buffering
    VK_PRESENT_MODE_FIFO_KHR,  // VSync enabled
    CopyCallback,
    DrawCallback,
    "FFFFFF",  // White clear color
    NULL       // User data
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

    // Update and render - swapchain will be automatically managed
    VkForge_UpdateRender(render);
}
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

1. **Swapchain Management**: Let VkForgeRender handle swapchain recreation automatically
2. **Pipeline Creation**: Use the generated pipeline functions rather than creating pipelines manually
3. **Resource Management**: Take advantage of the `VkForgeBufferAlloc` and `VkForgeImageAlloc` helper structures
4. **Error Handling**: The system will exit on critical errors but provides clear error messages
5. **Layout Design**: Use the generated layout system for consistent pipeline layouts across your application

## Advanced Features

### Automatic Swapchain Recovery

VkForgeRender includes robust swapchain recovery:
- Automatically handles `VK_ERROR_OUT_OF_DATE_KHR` and `VK_SUBOPTIMAL_KHR`
- Limits recreation attempts to prevent infinite loops (`VKFORGE_MAX_SWAPCHAIN_RECREATION`)
- Verifies window is valid before attempting recreation
- Provides clear error messages when recovery fails

### State Management

The renderer maintains a clear state machine:
```c
enum VkForgeRenderStatus {
    VKFORGE_RENDER_READY,
    VKFORGE_RENDER_COPYING,
    VKFORGE_RENDER_ACQING_IMG,
    VKFORGE_RENDER_PENGING_ACQ_IMG,
    VKFORGE_RENDER_DRAWING,
    VKFORGE_RENDER_SUBMITTING,
    VKFORGE_RENDER_PENDING_SUBMIT,
    VKFORGE_RENDER_RECREATE
};
```

### Texture Loading

VkForge provides a complete texture loading utility:
```c
VkForgeTexture VkForge_CreateTexture(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkQueue queue,
    VkCommandBuffer commandBuffer,
    const char* filename
);
```

## Advantages Over Raw Vulkan

1. **Faster Setup**: Get a clear screen rendering in <30 minutes vs. a full day with raw Vulkan
2. **Automatic Management**: Swapchain and state management handled automatically
3. **Maintainable**: Generated code is visible and modifiable
4. **Consistent**: Enforces good practices across projects
5. **Flexible**: Mix VkForge convenience functions with raw Vulkan as needed
6. **Toolchain**: Can be used as part of a build system to generate base Vulkan code

## Limitations

1. Not a full framework - you still need to understand Vulkan concepts
2. Primarily focused on graphics pipelines (not compute) for now
3. Generated code may need customization for advanced use cases

## Conclusion

VkForge strikes a balance between convenience and control, making Vulkan more accessible while preserving its power and flexibility. By generating pipeline code, managing swapchains automatically, and providing utility functions for common tasks, it significantly reduces the boilerplate required for Vulkan applications while keeping all implementation details visible and modifiable.
