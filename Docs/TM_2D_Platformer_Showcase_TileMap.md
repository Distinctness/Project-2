# TM_2D_Platformer_Showcase Tile Map

`Content/Python/create_2d_platformer_tile_map.py` creates a Paper2D tile map asset for Unreal Engine 5.7.4 at `/Game/Environement_assets/TM_2D_Platformer_Showcase`. The tile map uses the project's existing Earth tile sets and includes a preview level at `/Game/Levels/L_2D_Platformer_TileMap_Preview`.

## How to build the tile map in UE 5.7.4

1. Open `EchoesOfFourRealms.uproject` in Unreal Engine 5.7.4.
2. Confirm the `Paper2D`, `PythonScriptPlugin`, and `EditorScriptingUtilities` plugins are enabled.
3. Open the Output Log command line or run an editor command line.
4. Execute one of the supported commands below.

   **Output Log command**

   Paste this as a single line in the Unreal Output Log command box:

   ```python
   py import runpy, unreal; runpy.run_path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "Python/create_2d_platformer_tile_map.py", run_name="__main__")
   ```

   **Editor command line**

   Replace the placeholder with the absolute path to your local checkout:

   ```powershell
   "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe" "<absolute path>\EchoesOfFourRealms.uproject" -ExecutePythonScript="<absolute path>\Content\Python\create_2d_platformer_tile_map.py"
   ```

5. Open `/Game/Environement_assets/TM_2D_Platformer_Showcase` to edit tile-level details, or open `/Game/Levels/L_2D_Platformer_TileMap_Preview` to inspect the generated map in a level.

## Tile map specs

| Setting | Value |
| --- | ---: |
| Map size | 128 x 28 tiles |
| Tile size | 128 x 128 px |
| Pixels per Unreal Unit | 1.0 |
| Collision thickness | 80 uu |
| Primary asset path | `/Game/Environement_assets/TM_2D_Platformer_Showcase` |
| Preview level path | `/Game/Levels/L_2D_Platformer_TileMap_Preview` |

## Layers

| Layer | Purpose |
| --- | --- |
| `Terrain_Collision` | Solid grass-topped earth platforms for core side-scrolling traversal. |
| `Grass_Details` | Non-blocking decorative grass detail tiles. |
| `Hazard_Placement_Guide` | Non-blocking visual markers for where spike or hot-surface Blueprint hazards should be placed. |

## Gameplay layout

The tile map is designed as a compact first-pass 2D platformer route:

- An onboarding meadow with long, flat grass terrain.
- A rising double-jump climb that can host the existing double-jump pickup.
- Offset hazard islands with visual hazard guide tiles.
- A mid-route traversal section for trampoline, wind, or swimming Blueprint experiments.
- Uneven combat ridges for basic enemy placement.
- A finale arena floor with room for the existing boss, destructible wall, and door Blueprints.

## Tile sets used

- `/Game/Environement_assets/Earth/Grass_Sprite_TileSet`
- `/Game/Environement_assets/Earth/Grass_Details_Sprite_TileSet`
- `/Game/Environement_assets/Earth/1_TileSet`
- `/Game/Environement_assets/Earth/2_TileSet`
- `/Game/Environement_assets/Earth/3_TileSet`
- `/Game/Environement_assets/Earth/4_TileSet`

## Designer notes

- The generator deletes and recreates `/Game/Environement_assets/TM_2D_Platformer_Showcase`, so duplicate the asset before hand-editing if you want to preserve a custom pass.
- Gameplay hazards remain Blueprint actors in this project. Use the `Hazard_Placement_Guide` layer as placement reference, then add `BP_Spikes`, `BP_HotSurface`, or other hazard Blueprints in the preview level.
- The preview level is intentionally lightweight: it contains the tile map, a side-view orthographic camera, lighting, and a text note only.
