# How to Contribute

Thank you for your interest in improving **VkForge**.  
This project exists to help the community make Vulkan development faster, clearer, and more flexible.

---

## What is VkForge?

VkForge is a **Vulkan API Implementation** Generator.  
It generates clean Vulkan C source from your shaders and config files — no runtime wrapper layer, full control.  
The current core focus is **C99** with **SDL3**, but more frameworks are welcome through contributions.

---

## Ways to Contribute

- Improve documentation (README, examples, tutorials)
- Report bugs or issues
- Suggest new features or improvements
- Add support for new frameworks (GLFW, Raylib, etc.)
- Improve the code generator (optimizations, clearer output)
- Write tests or sample configs
- Review pull requests

---

## Getting Started

1. **Fork** the repository on GitHub.  
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/VkForge.git
````

3. **Create a branch**:

   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Make your changes**, then commit:

   ```bash
   git commit -m "Describe your changes here"
   ```
5. **Push** to your fork:

   ```bash
   git push origin feature/my-new-feature
   ```
6. **Open a Pull Request** on GitHub.

---

## Coding Guidelines

* Keep C generator **C99 compliant** — no compiler-specific extensions.
* Keep code clear, modular, and well-commented.
* Follow the existing file and folder structure.
* Add a test or example if your change affects generated output.
* Keep commits focused and descriptive.

---

## Testing

* Run existing samples to confirm your changes work.
* Add new examples to `/examples/`.
* Place new tests in `/tests/` with clear names.

---

## License

By contributing, you agree your code will be released under the **MIT License**, the same as VkForge.

---

Thank you for helping improve VkForge!

(c) 2025 Alrick Grandison, Algodal
