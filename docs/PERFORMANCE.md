# Profile animation performance

The live SVG implementation was the cause of the reported transition lag. It reproduced locally, independently of GitHub hosting. Each image contained 10,204 SVG elements, including 2,028 motion animations and 2,028 color animations. This caused repeated browser style calculations during the morph.

## Local comparison

Measured in the same headless Chromium build on this workstation, at a 1120 by 620 viewport, across a 4.5-second interval covering the transition. Frame counts below measure the page's `requestAnimationFrame` cadence, not the encoded animation frame rate. Results vary with device and browser.

| Measurement | Original SVG, paused | Original SVG, running | Pre-rendered WebP, running |
| --- | ---: | ---: | ---: |
| Page frames in 4.5 seconds | 270 | 34 | 268 |
| Approximate page cadence | 60 fps | 7.6 fps | 59.6 fps |
| 95th-percentile frame interval | 16.9 ms | 1,183.3 ms | 16.9 ms |
| Main-thread task time | 0.104 s | 4.728 s | 0.107 s |
| Style calculation time | 0 s | 3.518 s | 0 s |

The delivered WebP animation is encoded at **30 fps during motion**, with long frames during stationary poses. It loops for 16 seconds and preserves the same curved trajectories, facial abstraction, palette, and shaded numeral. All particle computation now happens during the build. Visitors decode a normal animated image. Reduced-motion visitors receive a completely static SVG.

The previous side-by-side chat GIF was only 6 fps; it should not be used to assess the replacement's smoothness. GitHub's status API reported all systems operational when the issue was investigated, but status alone would not rule out a browser rendering issue. The local reproduction establishes the file's rendering workload as the issue here.

## Regression guards

`scripts/check_profile.py` rejects animated SVG elements, checks every WebP's duration and motion frame timing, validates image dimensions, and enforces an 8 MiB download limit per image. Desktop images are approximately 6–6.6 MB and mobile images 3.6–3.9 MB. Only the matching theme/layout image is requested by the README picture element.

The GitHub workflow installs the pinned encoder, builds WebPs and static SVG fallbacks, validates them, and commits generated changes. No GitHub-side workflow run or hosted-profile performance measurement has been performed from this local task.
