#version 450

// Input from vertex shader
layout(location = 0) in vec4 fragColor;
layout(location = 1) in vec2 fragUV;

layout(set=0, binding=0) uniform sampler2D tex;

// Output color
layout(location = 0) out vec4 outColor;

void main() {
    // Simply output the color passed from vertex shader
    vec4 texColor = texture(tex, fragUV);
    outColor = vec4(fragColor.rgb * texColor.rgb, texColor.a);
}