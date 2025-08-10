#version 450

layout(location = 0) in vec2 fragUV;
layout(location = 1) in vec4 fragColor;

layout(location = 0) out vec4 outColor;

// Combined image sampler (binding 2)
layout(set = 0, binding = 8) uniform sampler2D texSampler;
layout(set = 0, binding = 7) uniform sampler2D texSampler2[2];

// Sampled image (binding 3) + separate sampler (binding 4)
layout(set = 0, binding = 3) uniform texture2D texImage;
layout(set = 0, binding = 4) uniform sampler texSamplerSeparate;

// Storage image (binding 5)
layout(set = 1, binding = 5, rgba32f) uniform image2D storageImage;

// Input attachment (binding 6) — used with subpass input (for deferred shading)
layout(set = 2, binding = 6,input_attachment_index =0) uniform subpassInput inputAttachment;

void main() {
    // Sample from combined sampler
    vec4 texColor = texture(texSampler, fragUV);

    // Sample from separate image + sampler
    vec4 separateColor = texture(sampler2D(texImage, texSamplerSeparate), fragUV);

    // Read from input attachment (subpass input)
    vec4 inputAttachColor = subpassLoad(inputAttachment);

    // Read from storage image (can read or write)
    vec4 storageColor = imageLoad(storageImage, ivec2(gl_FragCoord.xy));

    outColor = texColor * separateColor * fragColor + inputAttachColor + storageColor;
}
