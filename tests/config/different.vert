#version 450

// Input vertex attributes
layout(location = 0) in vec2 inPosition;
layout(location = 1) in vec2 inUV;
layout(location = 2) in vec4 inColor;

// Output to fragment shader
layout(location = 0) out vec2 fragUV;
layout(location = 1) out vec4 fragColor;

// Uniform buffer (binding 0)
layout(set = 0, binding = 0) uniform UBO {
    mat4 model;
    mat4 view;
    mat4 proj;
} ubo;

layout(set = 0, binding = 2) uniform AnyNameUBO {
    mat4 model;
    mat4 view;
    mat4 proj;
} anubo[4];

// Storage buffer (binding 1)
layout(set = 0, binding = 1) buffer SSBO {
    vec4 extraData[256];
} ssbo;

layout(set = 1, binding = 1) buffer AnyName2 {
    vec4 extraData[256];
} anyname2;

void main() {
    fragUV = inUV;
    fragColor = inColor;

    vec4 pos = vec4(inPosition, 0.0, 1.0);

    // Example: add a value from SSBO for fun
    pos.xy += ssbo.extraData[0].xy;

    gl_Position = ubo.proj * ubo.view * ubo.model * pos;
}
