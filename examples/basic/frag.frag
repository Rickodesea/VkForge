#version 450

layout(location=0) in vec4 inColor;

layout(location=0) out vec4 fragColor;

layout(set = 0, binding = 2) uniform sampler2D texSampler;
layout(set = 0, binding = 1) uniform sampler2D texSampler2;


void main()
{
    fragColor = inColor;
}