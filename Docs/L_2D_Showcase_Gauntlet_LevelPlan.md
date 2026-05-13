# L_2D_Showcase_Gauntlet Level Plan

`Content/Python/create_2d_showcase_level.py` generates a new Unreal Engine 5.7.4 level at `/Game/Levels/L_2D_Showcase_Gauntlet`. It is a side-view 2D controller showcase that uses the project's existing content assets instead of introducing new art or gameplay dependencies.

## How to build the level in UE 5.7.4

1. Open `EchoesOfFourRealms.uproject` in Unreal Engine 5.7.4.
2. Open the Output Log command line or run an editor command line.
3. Execute one of the supported commands below.

   **Output Log command**

   Paste this as a single line in the Unreal Output Log command box:

   ```python
   py import runpy, unreal; runpy.run_path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "Python/create_2d_showcase_level.py", run_name="__main__")
   ```

   **Editor command line**

   Replace the placeholder with the absolute path to your local checkout:

   ```powershell
   "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe" "<absolute path>\EchoesOfFourRealms.uproject" -ExecutePythonScript="<absolute path>\Content\Python\create_2d_showcase_level.py"
   ```

   Do **not** run `py "Content/Python/create_2d_showcase_level.py"` from the Output Log. Unreal resolves that relative path from the engine binary directory, which produces paths like `C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/Content/Python/create_2d_showcase_level.py` instead of this project's `Content/Python` directory.

4. Open `/Game/Levels/L_2D_Showcase_Gauntlet` and press Play.

## Intended playtime

The level is tuned as a 3-5 minute first-pass route for a 2D character controller. It uses long horizontal traversal, vertical routes, checkpoint spacing, hazard recovery pickups, and a compact arena finale so testers can exercise movement, pickups, hazards, enemies, and UI without leaving the level.

## Gameplay beats

| Beat | Approx. X range | Purpose | Key content used |
| --- | ---: | --- | --- |
| 00 Onboarding Meadow | 0-2600 | Start area, basic movement, EXP trail, first checkpoint. | `BP_Third_2D_Character`, `BP_GM_2D_Plat`, `BP_EXPPickUp`, `BP_Respawn`, earth/grass sprites |
| 01 Double-Jump Grove | 2600-5200 | Awards double jump and introduces safe vertical platforming. | `BP_DoubleJumpPickUp`, `BP_AdditionalJump`, blocking platforms, grass sprites |
| 02 Hazard Causeway | 5200-7900 | Tests reading and recovering from spikes, heat, falling platforms, and slippery surfaces. | `BP_Spikes`, `BP_HotSurface`, `BP_FallingRumble`, `BP_SlipperySurface`, `BP_HealthPickUp` |
| 03 Wind/Water Cavern | 7900-10800 | Demonstrates traversal modifiers and environmental verbs. | `BP_Trampoline`, `BP_Wind`, `BP_Swimming`, `BP_JDPlatform`, `BP_AbilityPickUp` |
| 04 Combat Ridge | 10800-14000 | Layers enemy archetypes over uneven terrain. | `BP_IdleEnemy`, `BP_FocusEnemy`, `BP_FlyingEnemy`, `BP_RandomProjectileEnemy`, `BP_FocusProjectileEnemy`, `BP_DamagePickUp` |
| 05 Gauntlet Ascent | 14000-17600 | Chains platforming, moving platforms, damaged platforms, and enemy pressure. | `BP_MovingPlatform`, `BP_DamagedPlatform`, `BP_BurrowingEnemy`, `BP_ExplosiveEnemy`, `BP_HealthPickUp` |
| 06 Badger Arena Finale | 17600-20500+ | Ends with a miniboss-style combat arena and gated exit. | `BP_Badger`, `BP_DestructibleWall`, `BP_Door`, `BP_EXPPickUp` |

## Level implementation notes

- The generator sets the world override to `BP_GM_2D_Plat` and places both `BP_Third_2D_Character` and a `PlayerStart` near the first meadow platform.
- Blocking volumes define dependable 2D collision slabs while grass and earth Paper2D sprites provide visual dressing from the existing `Content/Environement_assets/Earth` folder.
- Text render markers are intentionally placed in the editor build to make each beat easy to find during review; they can be hidden or deleted after approval.
- Checkpoints are placed after every major skill test to support several minutes of gameplay without forcing complete restarts.
- The finale uses arena walls plus `BP_Badger`, `BP_DestructibleWall`, and `BP_Door` as a clear end-of-level objective.
