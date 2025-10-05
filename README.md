# Escape the Lava!

Escape the Lava is a fast-paced 2D platformer built using **Pygame**, where you jump your way up through dangerous levels filled with rising lava, spinning saws, and cannon projectiles. The goal is simple: reach the green door at the top before the lava catches you. The game includes multiple levels, a lives system, and smooth camera movement for an immersive vertical challenge.

---

## How It's Made:
**Tech used:** Python, Pygame

This project was built from the ground up in one long day by a freshman college student learning Pygame for the first time. The goal was to create a full, playable game with menus, levels, hazards, and victory/death screens. The game loop follows standard Pygame structure with consistent frame updates, collision detection, and rendering cycles.

The player is represented by a simple rectangle that can move horizontally and jump using physics-based velocity updates. A coyote time and jump buffer system were implemented to make platforming smoother and more forgiving. Multiple levels are generated with randomized platform positions, moving saws, and cannons that shoot timed projectiles. The lava constantly rises, adding pressure as the player climbs.

The camera system tracks the player with interpolation, ensuring smooth scrolling while maintaining visibility of nearby platforms and hazards. Game states include a main menu, active gameplay, death screen, and win screen.

The game architecture is divided into key classes:
- **Player** handles movement, jumping, and rendering.
- **Platform, Saw, MovingSaw, Cannon, Projectile, Door** are modular game entities.
- **Level** manages procedural platform placement, hazard spawning, and environment updates.
- **Game** controls all states, updates, rendering, and event handling.

---

## Optimizations
A significant focus was on keeping the frame rate consistent at 60 FPS even with many active hazards. Optimizations include:
- Caching font rendering for static text elements.
- Clamping and reusing platform and projectile updates.
- Reducing unnecessary collision checks by limiting range for active projectiles.
- Reusing random seeds for predictable level building while maintaining variation.

If further optimization were done, one area of improvement would be spatial partitioning for collision detection, which would reduce computation when there are many entities on screen.

---

## Lessons Learned
Building **Escape the Lava** taught me how a full game loop operates and how to balance multiple systems like physics, rendering, and input handling. Before this, I had no experience with Pygame, so learning how to handle sprites, surfaces, and delta time was a big step.

I also learned how important it is to break large problems into smaller, testable parts. Getting basic movement right made later stages like collision and camera control much easier to implement. Lastly, this project showed me that finishing something—even if not perfect—is a big achievement in learning game development.

---
