#version 450

layout(location=0) in vec2 inPos;

layout(location=0) out vec4 outColor;
layout(location=1) out vec4 outOther;

layout(set = 0, binding = 0) uniform UBO {
    mat4 model;
    mat4 view;
    mat4 proj;
} ubo;
layout(set = 0, binding = 2) uniform sampler2D texSampler;

void main()
{
    gl_Position = vec4(inPos, 0, 1);
}