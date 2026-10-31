# Binary profile

Edit `profile.json`, then run `python scripts/render_profile.py`. The renderer uses only the Python standard library. It produces light/dark desktop/mobile SVGs. Their CSS changes the bits in place and dissolves the face into a binary-built 27 every 12 seconds. Reduced-motion mode holds the face still. SVGs contain no scripts, embedded raster art, external fonts, or tracking services.

The palette follows the user's NVIDIA-inspired direction: black, white, neutral grays, and NVIDIA Green `#76B900`, verified in [NVIDIA's published guidelines](https://www.nvidia.com/content/dam/en-zz/Solutions/about-us/documents/NVIDIA-Trademark-and-Logo-Usage-Guidelines.pdf). Light-theme text uses a darker green for contrast on white. No NVIDIA logo or affiliation is implied.

## GitHub workflow

`.github/workflows/profile.yml` runs on relevant pushes to main, manually from Actions, and at minute 17 every six hours (UTC). It fetches public GitHub repository/star counts, renders the artwork, validates it, and commits generated changes. It uses GitHub's built-in token; no personal access token or extra secret is required. API failures fail the job without overwriting the last successful cache. Scheduled runs require the workflow on the default branch and Actions enabled; repository rules must permit the bot to push generated commits. The workflow has been prepared locally; it has not run on GitHub yet.

The counters are public repository count and the sum of stars across all owned public repositories, including forks. There is no private repository enumeration, location, employer, email address, age, or birthdate. The cache retains only the two counts and UTC check date. HTB and Root-Me are direct profile links; their changing scores/ranks are intentionally not copied into the artwork.

Public refresh: `python scripts/update_public_stats.py`  
Build: `python scripts/render_profile.py`  
Validate: `python scripts/check_profile.py`

## Content evidence

The hobbies are editorial descriptions based on Lahsen's own published writeups and CV, not invented hardware interests:

- [Handshake](https://github.com/LahsenAitOiahmane/0xWriteups/blob/main/REV/HandShake/README.md): XOR and PRNG derivation.
- [dark_portal](https://github.com/LahsenAitOiahmane/0xWriteups/blob/main/PWN/darkportal/dark_portal.md): heap use-after-free and GOT overwrite analysis.
- [JWT public-key challenge](https://github.com/LahsenAitOiahmane/0xWriteups/blob/main/WEB/RootMe/rootme-jwt-public-key-ch60.md): JWT algorithm confusion.
- [Hexplain](https://github.com/LahsenAitOiahmane/Hexplain): LLM-assisted binary analysis. The CV also describes local Ollama/RAG work.

The terminal portrait plus aligned dot leaders take structural inspiration from [Andrew6rant's profile](https://github.com/Andrew6rant/Andrew6rant). His source portrait and code were not copied. His workflow uses a daily scheduled Python job to update its SVGs from GitHub statistics; this implementation uses public-only REST counts and self-contained animated artwork.

## Source art and generation prompt

The user supplied a portrait and explicitly requested a close-up of his face with glasses. The built-in image generation tool made an identity-preserving monochrome close-up. `assets/source/face-luminance.json` is its 64 by 80 luminance grid used by the renderer. Neither the original photograph nor the edited raster close-up is stored in this repository or embedded in the SVGs. The earlier fictional placeholder was removed.

Exact prompt:

> Edit the supplied photograph of the user as a high-fidelity identity-preserving SOURCE IMAGE for a binary/ASCII portrait. This is the same person, NOT a fictional face. Crop/zoom tightly to his full head from just above hair to chin and a short neck. Remove the torso, shirt, and room/background. Preserve exactly his face shape, distinctive dark thick roundish eyeglasses including bridge and frame outline, visible eyes behind clear lenses, thin moustache, side-parted wavy hairstyle with the loose forehead curl, eyebrows, ears, pose and calm expression. Do NOT add facial hair, change age, change identity, remove glasses, add sunglasses, smooth into a generic model, or change hairstyle. Convert to clean high-contrast monochrome on a SOLID PURE BLACK background. Keep balanced bright gray facial planes on BOTH sides, not an extreme half-face shadow. Black hair must have enough silver edge lighting and texture to outline the hairstyle on black. Glasses frames and moustache should stay dark against bright face, eyes clearly readable. Head should fill 82% width and 90% height of a 2:3 portrait. A little black negative space surrounding the hair. This will be downsampled to roughly 64x80 luminance cells, so preserve strong readable glasses/eyes/nose/lip outlines and large facial forms. Photographic likeness is more important than cinematic style. No text, no numbers, no code, no logos, no decorative effects. Do not draw binary yourself; software will do it.
