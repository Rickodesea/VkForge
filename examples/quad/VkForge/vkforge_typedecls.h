#pragma once

#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>



#ifdef __cplusplus
extern "C" {
#endif

#define VKFORGE_DEFAULT_FORMAT VK_FORMAT_B8G8R8A8_UNORM

#define VKFORGE_MAX_PIPELINES 1
#define VKFORGE_MAX_PIPELINE_LAYOUTS 1
#define VKFORGE_MAX_DESCRIPTORSET_LAYOUTS 1
#define VKFORGE_MAX_DESCRIPTOR_BINDINGS 1

typedef struct VkForgeCore VkForgeCore;

struct VkForgeCore
{
    VkInstance       instance;
    VkSurfaceKHR     surface;
    VkPhysicalDevice physical_device;
    uint32_t         queue_family_index;
    VkDevice         device;
    VkQueue          queue;
    VkCommandPool    cmdpool;
};

typedef struct VkForgeBufferAlloc VkForgeBufferAlloc;

struct VkForgeBufferAlloc
{
    VkBuffer       buffer;
    VkDeviceSize   size;
    VkDeviceMemory memory;
};

typedef struct VkForgeImageAlloc VkForgeImageAlloc;

struct VkForgeImageAlloc
{
    VkImage        image;
    VkDeviceSize   size;
    VkDeviceMemory memory;
};

typedef struct VkForgeLayout VkForgeLayout;

typedef struct VkForgeTexture VkForgeTexture;

struct VkForgeTexture
{
    VkImage image;                      // The actual GPU image
    VkDeviceMemory memory;              // Memory bound to the VkImage
    VkImageView imageView;              // Optional: for sampling/viewing the image
    VkSampler sampler;                  // Sampler used to read from the texture
    uint32_t width;                     // Texture width in pixels
    uint32_t height;                    // Texture height in pixels
    VkSampleCountFlagBits samples;      // Multisample count (e.g., VK_SAMPLE_COUNT_1_BIT)
    VkFormat format;                    // Image format (e.g., VK_FORMAT_R8G8B8A8_UNORM)
};

#define VKFORGE_MAX_SWAPCHAIN_RECREATION 128

typedef enum VkForgeRenderStatus VkForgeRenderStatus;

enum VkForgeRenderStatus
{
    VKFORGE_RENDER_READY,
    VKFORGE_RENDER_COPYING,
    VKFORGE_RENDER_ACQING_IMG,
    VKFORGE_RENDER_PENGING_ACQ_IMG,
    VKFORGE_RENDER_DRAWING,
    VKFORGE_RENDER_SUBMITTING,
    VKFORGE_RENDER_PENDING_SUBMIT,
    VKFORGE_RENDER_RECREATE
};

typedef struct VkForgeRender VkForgeRender;
typedef void (*VkForgeRenderCallback)(VkForgeRender render);

struct VkForgeRender
{
    SDL_Window*           window;
    VkPhysicalDevice      physical_device;
    VkSurfaceKHR          surface;
    VkDevice              device;
    VkQueue               queue;
    VkCommandPool         cmdPool;
    VkExtent2D            extent;
    VkCommandBuffer       copyCmdBuf;
    VkCommandBuffer       drawCmdBuf;
    VkForgeRenderCallback copyCallback;
    VkForgeRenderCallback drawCallback;
    VkFormat              req_format;
    uint32_t              req_swapchain_size;
    VkPresentModeKHR      req_present_mode;
    VkSwapchainKHR        swapchain;
    uint32_t              swapchain_size;
    VkImage*              swapchain_images;
    VkImageView*          swapchain_imgviews;
    uint32_t              index;
    VkFence               acquireImageFence;
    VkFence               submitQueueFence;
    VkSemaphore           copySemaphore;
    VkSemaphore           drawSemaphore;
    const char*           color;
    VkForgeRenderStatus   status;
    void*                 userData;
    bool                  acquireSuccessful;
    bool                  presentSuccessful;
    uint16_t              swapchainRecreationCount; //prevents a loop of recreating the swapchain
};

typedef void (*VkForgeDestroyCallback)(void);

typedef union VkForgeQuad VkForgeQuad;

union VkForgeQuad
{
    struct {float x, y, w, h;};
    struct {float s, t, u, v;};
    float p[4];
};

typedef struct VkForgeImagePair VkForgeImagePair;

struct VkForgeImagePair
{
    VkImage     image;
    VkImageView imgview;
};


#ifdef __cplusplus
}
#endif
