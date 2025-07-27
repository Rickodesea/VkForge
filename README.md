# VkForge

**VkForge** (Vulkan Forge) is a **Vulkan API Implementation Generator** written in **Python**. It's purpose is to quickly generate the code needed for Graphics Renderer development.

VkForge is the opposite of using a wrapper layer (like SDL_GPU or shVulkan).  
Instead of abstracting Vulkan, you use the **Vulkan API directly** — but VkForge saves you from writing all the repetitive boilerplate by generating it for you, based on your **shaders** and a simple **config**.

VkForge does not force any design pattern — you have the same freedom as hand-written Vulkan.  
By design, VkForge does not generate an entire renderer (though you can do so) — it generates **components** for you to connect as you wish.

---

## VkForge Source

The input for VkForge is:
- **Shaders:** Provide type, location, descriptor sets, and bindings.
- **Config:** Defines pipeline details and other setup.

---

## VkForge Output

VkForge generates **C99 source code** for your Vulkan implementation.  
Platform integration is done via **SDL3**.
Other frameworks and languages will be supported in the future — see [CONTRIBUTING.md](CONTRIBUTING.md).

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
