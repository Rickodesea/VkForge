#version 450

layout(location=0) in vec2 inPos;

layout(location=0) out vec4 outColor;
layout(location=1) out vec4 outOther;

void main()
{
    gl_Position = vec4(inPos, 0, 1);
}