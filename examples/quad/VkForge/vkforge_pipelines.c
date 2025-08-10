#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>

#include "vkforge_typedecls.h"
#include "vkforge_funcdecls.h"

#include "../entity.h"

/** NO USER DECLARATIONS **/

VkPipeline VkForge_CreatePipelineForDefault
(
    VkAllocationCallbacks* allocator,
    void* next,
    VkDevice device,
    VkPipelineLayout pipeline_layout
)
{

	VkResult result;
	VkPipeline pipeline = VK_NULL_HANDLE;

	VkShaderModule shader_vert = VkForge_CreateShaderModule(device, "build/shader.vert.spv");
	if( VK_NULL_HANDLE == shader_vert )
	{
		SDL_LogError(0, "Failed to create vert shader for Default pipeline\n");
		exit(1);
	}

	VkShaderModule shader_frag = VkForge_CreateShaderModule(device, "build/shader.frag.spv");
	if( VK_NULL_HANDLE == shader_frag )
	{
		SDL_LogError(0, "Failed to create frag shader for Default pipeline\n");
		exit(1);
	}

	VkPipelineShaderStageCreateInfo stageInfo[] =
	{
		{
			.sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
			.stage  = VK_SHADER_STAGE_VERTEX_BIT,
			.module = shader_vert,
			.pName  = "main",
		},
		{
			.sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
			.stage  = VK_SHADER_STAGE_FRAGMENT_BIT,
			.module = shader_frag,
			.pName  = "main",
		},
	};
	uint32_t stageInfoCount = 2;

	VkVertexInputBindingDescription bindingDesc[] =
	{
		{
			.binding = 0,
			.stride = sizeof(float) * 2,
			.inputRate = VK_VERTEX_INPUT_RATE_VERTEX,
		},
		{
			.binding = 1,
			.stride = sizeof(Entity),
			.inputRate = VK_VERTEX_INPUT_RATE_INSTANCE,
		},
	};
	uint32_t bindingDescCount = 2;

	VkVertexInputAttributeDescription attributeDesc[] =
	{
		{
			.binding = 0,
			.location = 0,
			.format = VK_FORMAT_R32G32_SFLOAT,
			.offset = 0,
		},
		{
			.binding = 1,
			.location = 1,
			.format = VK_FORMAT_R32G32B32A32_SFLOAT,
			.offset = offsetof(Entity, color),
		},
		{
			.binding = 1,
			.location = 2,
			.format = VK_FORMAT_R32G32_SFLOAT,
			.offset = offsetof(Entity, pos),
		},
		{
			.binding = 1,
			.location = 3,
			.format = VK_FORMAT_R32G32_SFLOAT,
			.offset = offsetof(Entity, size),
		},
	};
	uint32_t attributeDescCount = 4;

	VkPipelineVertexInputStateCreateInfo inputStateInfo = {0};
	inputStateInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;
	inputStateInfo.vertexBindingDescriptionCount = bindingDescCount;
	inputStateInfo.pVertexBindingDescriptions = bindingDescCount ? bindingDesc : 0;
	inputStateInfo.vertexAttributeDescriptionCount = attributeDescCount;
	inputStateInfo.pVertexAttributeDescriptions = attributeDescCount ? attributeDesc : 0;

	VkPipelineInputAssemblyStateCreateInfo inputAssemblyInfo = {0};
	inputAssemblyInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;
	inputAssemblyInfo.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;

	VkPipelineViewportStateCreateInfo viewportState = {0};
	viewportState.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;
	viewportState.viewportCount = 1;
	viewportState.scissorCount = 1;

	VkPipelineRasterizationStateCreateInfo rasterizerInfo = {0};
	rasterizerInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;
	rasterizerInfo.depthClampEnable = VK_FALSE;
	rasterizerInfo.rasterizerDiscardEnable = VK_FALSE;
	rasterizerInfo.polygonMode = VK_POLYGON_MODE_FILL;
	rasterizerInfo.cullMode = VK_CULL_MODE_NONE;
	rasterizerInfo.frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE;
	rasterizerInfo.depthBiasEnable = VK_FALSE;
	rasterizerInfo.depthBiasConstantFactor = 0;
	rasterizerInfo.depthBiasClamp = 0;
	rasterizerInfo.depthBiasSlopeFactor = 0;
	rasterizerInfo.lineWidth = 1.0;

	VkPipelineMultisampleStateCreateInfo multisampleState = {0};
	multisampleState.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;
	multisampleState.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;

	VkPipelineDepthStencilStateCreateInfo depthStencil = {0};
	depthStencil.sType = VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO;
	depthStencil.depthTestEnable = VK_FALSE;
	depthStencil.depthWriteEnable = VK_FALSE;
	depthStencil.depthCompareOp = VK_COMPARE_OP_LESS;
	depthStencil.depthBoundsTestEnable = VK_FALSE;
	depthStencil.stencilTestEnable = VK_FALSE;

	VkPipelineColorBlendAttachmentState colorBlendAttachment = {0};
	colorBlendAttachment.blendEnable = VK_TRUE;
	colorBlendAttachment.srcColorBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA;
	colorBlendAttachment.dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA;
	colorBlendAttachment.colorBlendOp = VK_BLEND_OP_ADD;
	colorBlendAttachment.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;

	VkPipelineColorBlendStateCreateInfo colorBlending = {0};
	colorBlending.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;
	colorBlending.logicOpEnable = VK_FALSE;
	colorBlending.attachmentCount = 1;
	colorBlending.pAttachments = &colorBlendAttachment;

	VkDynamicState dynamicStates[] =
	{
		VK_DYNAMIC_STATE_VIEWPORT,
		VK_DYNAMIC_STATE_SCISSOR,
	};

	VkPipelineDynamicStateCreateInfo dynamicInfo = {0};
	dynamicInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO;
	dynamicInfo.dynamicStateCount = sizeof(dynamicStates) / sizeof(VkDynamicState);
	dynamicInfo.pDynamicStates = dynamicStates;

	VkGraphicsPipelineCreateInfo pipelineInfo = {0};
	pipelineInfo.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;
	pipelineInfo.stageCount = sizeof(stageInfo)/sizeof(VkPipelineShaderStageCreateInfo);
	pipelineInfo.pStages = stageInfo;
	pipelineInfo.pVertexInputState = &inputStateInfo;
	pipelineInfo.pInputAssemblyState = &inputAssemblyInfo;
	pipelineInfo.pRasterizationState = &rasterizerInfo;
	pipelineInfo.pColorBlendState = &colorBlending;
	pipelineInfo.pDepthStencilState = &depthStencil;
	pipelineInfo.pDynamicState = &dynamicInfo;
	pipelineInfo.pViewportState = &viewportState;
	pipelineInfo.pMultisampleState = &multisampleState;
	pipelineInfo.layout = pipeline_layout;

	/// Ensure VkRenderingInfo is passed to pNext for Successful Dynamic Rendering ///
	pipelineInfo.pNext = next;
	///********************///
	result = vkCreateGraphicsPipelines(device, VK_NULL_HANDLE, 1, &pipelineInfo, allocator, &pipeline);
	if (result != VK_SUCCESS) {
		SDL_LogError(0, "Failed to create pipeline Default");
		return VK_NULL_HANDLE;
	}

	vkDestroyShaderModule(device, shader_vert, allocator);
	vkDestroyShaderModule(device, shader_frag, allocator);

	return pipeline;
}



