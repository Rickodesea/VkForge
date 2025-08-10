#pragma once

#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>

#include "vkforge_typedecls.h"

#ifdef __cplusplus
extern "C" {
#endif

#define VKFORGE_ENUM(Var, Type, Func, Sizelimit, ...) \
    Type Var##_buffer[Sizelimit] = {0}; uint32_t Var##_count = 0; do { \
    Func(__VA_ARGS__, &Var##_count, 0); \
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \
} while(0)

#define VKFORGE_VOID_ENUM(Var, Type, Func, Sizelimit, ...) \
    Type Var##_buffer[Sizelimit] = {0}; uint32_t Var##_count = 0; do { \
    Func(__VA_ARGS__, &Var##_count, 0); \
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \
} while(0)

// Function Declarations

void VkForge_CreateInstance(VkInstance*            retInstance);

void VkForge_CreateSurface(VkInstance             instance,
    SDL_Window*            window,

    VkSurfaceKHR*          retSurface);

void VkForge_SelectPhysicalDevice(VkInstance instance, 
    VkSurfaceKHR surface, 
    VkPhysicalDevice* inPhysicalDevice, 
    uint32_t* inQueueFamilyIndex);

void VkForge_CreateDevice(VkPhysicalDevice       physical_device,
    uint32_t               queue_family_index,
    const char**           requested_extensions_buffer,
    uint32_t               requested_extensions_count,

    VkDevice*              retDevice,
    VkQueue*               retQueue);

void VkForge_CreateSwapchain(VkSurfaceKHR           surface,
    VkPhysicalDevice       physical_device,
    VkDevice               device,
    VkSwapchainKHR         old_swapchain,
    VkFormat               req_format,
    uint32_t               req_swapchain_size,
    VkPresentModeKHR       req_present_mode,

    VkSwapchainKHR*        retSwapchain,
    uint32_t*              retSwapchainSize,
    VkImage**              retSwapchainImages,
    VkImageView**          retSwapchainImageViews);

void VkForge_CreateCommandPoolAndBuffers(uint32_t               queue_family_index,
    VkDevice               device,
    uint32_t               bufferCount,

    VkCommandPool*         retCommandPool,
    VkCommandBuffer*       retCommandBuffers);

VkForgeCore* VkForge_CreateCore(SDL_Window*            window,
    const char**           requested_device_extensions_buffer,
    uint32_t               requested_device_extensions_count);

void VkForge_DestroyCore(VkForgeCore* core);

void VkForge_Destroy(VkDevice device, uint32_t count, VkForgeDestroyCallback* destroyers);

VkForgeRender* VkForge_CreateRender(SDL_Window*           window,
    VkPhysicalDevice      physical_device,
    VkSurfaceKHR          surface,
    VkDevice              device,
    VkQueue               queue,
    VkCommandPool         cmdPool,
    VkFormat              req_format,
    uint32_t              req_swapchain_size,
    VkPresentModeKHR      req_present_mode,
    VkForgeRenderCallback copyCallback,
    VkForgeRenderCallback drawCallback,
    const char*           clearColorHex,
    void*                 userData);

void VkForge_UpdateRender(VkForgeRender* render);

void VkForge_RefreshRenderData(VkForgeRender* r);

void VkForge_DestroyRender(VkForgeRender* r);

void VkForge_ReCreateRenderSwapchain(VkForgeRender* r);

VkDebugUtilsMessengerCreateInfoEXT VkForge_GetDebugUtilsMessengerCreateInfo();

VKAPI_ATTR VkBool32 VKAPI_CALL VkForge_DebugMsgCallback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,
    VkDebugUtilsMessageTypeFlagsEXT type,
    const VkDebugUtilsMessengerCallbackDataEXT* callback,
    void* user);

uint32_t VkForge_ScorePhysicalDeviceLimits(VkPhysicalDeviceLimits limits);

uint32_t VkForge_GetMemoryTypeIndex(VkPhysicalDevice      physical_device,
    uint32_t              typeFilter,
    VkMemoryPropertyFlags properties);

uint32_t VkForge_GetSwapchainSize(VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    uint32_t         req_size);

VkSurfaceFormatKHR VkForge_GetSurfaceFormat(VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    VkFormat         req_format);

VkSurfaceCapabilitiesKHR VkForge_GetSurfaceCapabilities(VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device);

VkPresentModeKHR VkForge_GetPresentMode(VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    VkPresentModeKHR req_mode);

void VkForge_CmdBufferBarrier(VkCommandBuffer cmdbuf,

    VkBuffer buffer,
    VkDeviceSize offset,
    VkDeviceSize size,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags);

void VkForge_CmdImageBarrier(VkCommandBuffer cmdbuf,

    VkImage image,
    VkImageLayout oldLayout,
    VkImageLayout newLayout,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags);

VkFence VkForge_CreateFence(VkDevice device);

VkSemaphore VkForge_CreateSemaphore(VkDevice device);

void VkForge_BeginCommandBuffer(VkCommandBuffer cmdBuf);

void VkForge_EndCommandBuffer(VkCommandBuffer cmdBuf);

void VkForge_CmdCopyBufferToImage(VkCommandBuffer cmdBuf,
    VkBuffer buffer,
    VkImage image,
    float x, float y,
    float w, float h,
    VkImageLayout layout);

void VkForge_QueueSubmit(VkQueue queue,
    VkCommandBuffer cmdBuf,
    VkPipelineStageFlags waitStage,
    VkSemaphore waitSemaphore,
    VkSemaphore signalSemaphore,
    VkFence fence);

VkBuffer VkForge_CreateBuffer(VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,

    VkMemoryRequirements      *inMemReqs);

VkForgeBufferAlloc VkForge_CreateBufferAlloc(VkPhysicalDevice           physical_device,
    VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,
    VkMemoryPropertyFlags      properties);

VkBuffer VkForge_CreateOffsetBuffer(VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage);

VkImage VkForge_CreateImage(VkDevice               device,
    uint32_t               width,
    uint32_t               height,
    VkFormat               format,
    VkImageUsageFlags      usage,

    VkMemoryRequirements  *inMemReqs);

VkForgeImageAlloc VkForge_CreateImageAlloc(VkPhysicalDevice           physical_device,
    VkDevice                   device,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage,
    VkMemoryPropertyFlags      properties);

VkImage VkForge_CreateOffsetImage(VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage);

VkForgeBufferAlloc VkForge_CreateStagingBuffer(VkPhysicalDevice physical_device,
    VkDevice device,
    VkDeviceSize size);

VkImageView VkForge_CreateImageView(VkDevice device,
    VkImage image,
    VkFormat format);

VkSampler VkForge_CreateSampler(VkDevice device,
    VkFilter filter,
    VkSamplerAddressMode addressMode);

VkForgeTexture VkForge_CreateTexture(VkPhysicalDevice physical_device,
    VkDevice device,
    VkQueue queue,
    VkCommandBuffer commandBuffer,
    const char* filename);

VkDeviceMemory VkForge_AllocDeviceMemory(VkPhysicalDevice physical_device,
    VkDevice device,
    VkMemoryRequirements memRequirements,
    VkMemoryPropertyFlags properties);

void VkForge_BindBufferMemory(VkDevice device, VkBuffer buffer, VkDeviceMemory memory, VkDeviceSize offset);

void VkForge_BindImageMemory(VkDevice device, VkImage image, VkDeviceMemory memory, VkDeviceSize offset);

void VkForge_DestroyBufferAlloc(VkDevice device, VkForgeBufferAlloc bufferAlloc);

void VkForge_DestroyImageAlloc(VkDevice device, VkForgeImageAlloc imageAlloc);

void VkForge_SetColor(const char* hex, float alpha, float color[4]);

void VkForge_CmdBeginRendering(VkCommandBuffer  cmdbuf,
    VkForgeImagePair imgPair,
    const char*      clearColorHex,
    VkForgeQuad      quad);

void VkForge_CmdEndRendering(VkCommandBuffer cmdbuf, VkForgeImagePair imgPair);

VkResult VkForge_QueuePresent(VkQueue queue,
    VkSwapchainKHR swapchain,
    uint32_t index,
    VkSemaphore waitSemaphore);

void* VkForge_ReadFile(const char* filePath, Sint64* inSize);

VkShaderModule VkForge_CreateShaderModule(VkDevice device, const char* filePath);

const char* VkForge_StringifyResult(VkResult result);

void VkForge_LoadBuffer(VkPhysicalDevice physical_device,
    VkDevice         device,
    VkQueue          queue,
    VkCommandBuffer  cmdBuffer,
    VkBuffer         dstBuffer,
    VkDeviceSize     dstOffset,
    VkDeviceSize     size,
    const void*      srcData);

void VkForge_CmdCopyBuffer(VkCommandBuffer cmdBuf,
    VkBuffer        srcBuffer,
    VkBuffer        dstBuffer,
    VkDeviceSize    srcOffset,
    VkDeviceSize    dstOffset,
    VkDeviceSize    size);

VkCommandBuffer VkForge_AllocateCommandBuffer(VkDevice      device,
    VkCommandPool pool);

VkForgeLayout* VkForge_CreateLayout(VkSurfaceKHR surface, VkPhysicalDevice physical_device, VkDevice device);

void VkForge_DestroyLayout(VkForgeLayout* layout);

VkResult VkForge_CreatePipeline(VkForgeLayout* layout, const char* pipeline_name);

void VkForge_BindPipeline(VkForgeLayout* layout, const char* pipeline_name, VkCommandBuffer cmdbuf);



#ifdef __cplusplus
}
#endif
