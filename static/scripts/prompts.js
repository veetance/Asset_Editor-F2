/**
 * ASSET EDITOR - Prompt Patterns Bank
 * 20 suggestions per input, randomized on load
 */

const PromptBank = {
    // Generate mode prompts
    generate: [
        "A cyberpunk cityscape at night with neon signs and flying cars",
        "Portrait of a mysterious figure in renaissance oil painting style",
        "Futuristic sports car on an empty highway at sunset",
        "Ancient temple ruins overgrown with bioluminescent plants",
        "Astronaut floating in space with Earth reflection in helmet",
        "Steampunk mechanical dragon with brass gears and steam vents",
        "Cozy mountain cabin interior with fireplace and snow outside",
        "Abstract fluid art with metallic gold and deep purple swirls",
        "Hyperrealistic diamond ring on velvet with dramatic lighting",
        "Japanese garden in autumn with red maple leaves and koi pond",
        "Retro-futuristic space station interior with 1970s aesthetics",
        "Fashion model in avant-garde geometric clothing, editorial shot",
        "Underwater coral reef with exotic fish and light rays",
        "Dark fantasy castle on a cliff during lightning storm",
        "Minimalist product shot of premium headphones on marble",
        "Surreal desert landscape with floating geometric shapes",
        "Photorealistic wolf portrait with piercing blue eyes",
        "Art deco poster design for a luxury hotel in gold and black",
        "Mystical forest with glowing mushrooms and fairy lights",
        "High-end wristwatch macro shot with water droplets"
    ],

    // Edit/Inpaint mode prompts
    edit: [
        "Replace background with sunset beach",
        "Add dramatic storm clouds to the sky",
        "Change clothing color to deep burgundy",
        "Add reflections on the wet floor",
        "Replace with marble texture",
        "Add neon glow effect to edges",
        "Change time of day to golden hour",
        "Add snow falling in the scene",
        "Replace with chrome metallic finish",
        "Add lens flare from light source",
        "Change season to autumn colors",
        "Add bokeh lights in background",
        "Replace with wood grain texture",
        "Add motion blur to suggest speed",
        "Change material to frosted glass",
        "Add fog and atmospheric haze",
        "Replace with galaxy pattern",
        "Add water ripple reflections",
        "Change surface to brushed aluminum",
        "Add fire and ember particles"
    ],

    // Decompose doesn't need prompts, but we can add layer naming suggestions
    decompose: [
        "Background",
        "Subject",
        "Foreground Elements",
        "Shadow Layer",
        "Highlight Layer",
        "Color Grading",
        "Texture Overlay",
        "Ambient Light",
        "Detail Enhancement",
        "Edge Definition"
    ],

    // Stylize mode prompts
    stylize: [
        "Apply the color palette and mood from the style image",
        "Transfer the artistic brushwork keeping the layout",
        "Blend the lighting atmosphere from reference",
        "Apply vintage film grain and tones from style",
        "Match the material textures from reference",
        "Transfer the contrast and shadow style",
        "Apply the neon aesthetic from style image",
        "Blend watercolor painting style from reference",
        "Transfer the cinematic color grading",
        "Apply minimalist design language from style",
        "Match the retro poster aesthetic",
        "Transfer cyberpunk neon glow effects",
        "Apply the oil painting texture and strokes",
        "Blend anime illustration style from reference",
        "Transfer the golden hour lighting mood",
        "Apply the dark moody atmosphere",
        "Match the glossy magazine aesthetic",
        "Transfer grunge texture overlay",
        "Apply the clean product photography style",
        "Blend impressionist color treatment"
    ],

    init() {
        this.setPlaceholder('genPrompt', this.generate);
        this.setPlaceholder('editPrompt', this.edit);
        this.setPlaceholder('stylizePrompt', this.stylize);
    },

    setPlaceholder(elementId, prompts) {
        const element = document.getElementById(elementId);
        if (element && prompts.length > 0) {
            const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
            element.placeholder = randomPrompt;
        }
    },

    // Get a random prompt from a bank
    getRandom(bank) {
        const prompts = this[bank];
        if (prompts && prompts.length > 0) {
            return prompts[Math.floor(Math.random() * prompts.length)];
        }
        return '';
    },

    // Shuffle and return all prompts from a bank
    getAll(bank) {
        const prompts = this[bank];
        if (prompts) {
            return [...prompts].sort(() => Math.random() - 0.5);
        }
        return [];
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    PromptBank.init();
});
