"""Create a Paper2D tile map for the 2D platformer in Unreal Engine 5.7.4.

Run from the UE Output Log with a project-root-safe path resolver:
    py import runpy, unreal; runpy.run_path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "Python/create_2d_platformer_tile_map.py", run_name="__main__")

Or run from the editor command line with an absolute script path:
    UnrealEditor.exe "<absolute path>/EchoesOfFourRealms.uproject" -ExecutePythonScript="<absolute path>/Content/Python/create_2d_platformer_tile_map.py"

The script builds /Game/Environement_assets/TM_2D_Platformer_Showcase from the
project's existing Earth Paper2D tile sets. It also creates a lightweight preview
level at /Game/Levels/L_2D_Platformer_TileMap_Preview so designers can open and
inspect the map immediately.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import unreal

TILE_MAP_PACKAGE = "/Game/Environement_assets"
TILE_MAP_NAME = "TM_2D_Platformer_Showcase"
TILE_MAP_PATH = f"{TILE_MAP_PACKAGE}/{TILE_MAP_NAME}"
PREVIEW_LEVEL = "/Game/Levels/L_2D_Platformer_TileMap_Preview"

MAP_WIDTH = 128
MAP_HEIGHT = 28
TILE_SIZE = 128
PIXELS_PER_UNREAL_UNIT = 1.0
COLLISION_THICKNESS = 80.0

TILE_SETS = {
    "grass": "/Game/Environement_assets/Earth/Grass_Sprite_TileSet.Grass_Sprite_TileSet",
    "grass_detail": "/Game/Environement_assets/Earth/Grass_Details_Sprite_TileSet.Grass_Details_Sprite_TileSet",
    "earth_1": "/Game/Environement_assets/Earth/1_TileSet.1_TileSet",
    "earth_2": "/Game/Environement_assets/Earth/2_TileSet.2_TileSet",
    "earth_3": "/Game/Environement_assets/Earth/3_TileSet.3_TileSet",
    "earth_4": "/Game/Environement_assets/Earth/4_TileSet.4_TileSet",
}

TERRAIN_LAYER = 0
DETAIL_LAYER = 1
HAZARD_GUIDE_LAYER = 2


@dataclass(frozen=True)
class PlatformRun:
    """A horizontal run of solid tiles using tile-map coordinates."""

    x_start: int
    x_end: int
    top_y: int
    fill_depth: int = 3


@dataclass(frozen=True)
class HazardRun:
    x_start: int
    x_end: int
    y: int


PLATFORMS: tuple[PlatformRun, ...] = (
    PlatformRun(0, 18, 21, 7),      # onboarding meadow
    PlatformRun(20, 25, 19, 4),
    PlatformRun(28, 31, 17, 3),
    PlatformRun(34, 37, 15, 3),
    PlatformRun(40, 46, 13, 4),     # double-jump reward ledge
    PlatformRun(49, 52, 11, 3),
    PlatformRun(55, 58, 9, 3),
    PlatformRun(61, 65, 12, 4),
    PlatformRun(68, 72, 15, 4),     # hazard recovery island
    PlatformRun(75, 82, 18, 6),
    PlatformRun(85, 88, 14, 3),
    PlatformRun(91, 94, 11, 3),
    PlatformRun(97, 101, 15, 4),    # combat ridge
    PlatformRun(104, 109, 18, 5),
    PlatformRun(112, 116, 14, 4),
    PlatformRun(119, 127, 20, 8),   # finale arena floor
)

HAZARDS: tuple[HazardRun, ...] = (
    HazardRun(59, 60, 8),
    HazardRun(66, 67, 11),
    HazardRun(73, 74, 14),
    HazardRun(110, 111, 17),
)

DECORATION_TILES: tuple[tuple[int, int], ...] = (
    (4, 20), (7, 20), (12, 20), (23, 18), (30, 16), (43, 12),
    (51, 10), (57, 8), (70, 14), (78, 17), (87, 13), (93, 10),
    (100, 14), (106, 17), (114, 13), (123, 19),
)


def load_asset(path: str):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        raise RuntimeError(f"Required asset is missing: {path}")
    return asset


def make_tile_info(tile_set, tile_index: int = 0):
    info = unreal.PaperTileInfo()
    info.set_editor_property("tile_set", tile_set)
    info.set_editor_property("packed_tile_index", tile_index)
    return info


def call_first(target, method_names: Iterable[str], *args):
    for method_name in method_names:
        method = getattr(target, method_name, None)
        if callable(method):
            return method(*args)
    raise RuntimeError(
        f"{target.get_name() if hasattr(target, 'get_name') else target} does not expose any of: "
        + ", ".join(method_names)
    )


def create_component_with_tile_map():
    actor_class = getattr(unreal, "PaperTileMapActor", None)
    if actor_class is None:
        raise RuntimeError("Paper2D is not available. Enable the Paper2D plugin and restart Unreal Engine.")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, unreal.Vector(0.0, 0.0, 0.0))
    actor.set_actor_label(TILE_MAP_NAME)
    component = actor.get_component_by_class(unreal.PaperTileMapComponent)
    if component is None:
        raise RuntimeError("Spawned PaperTileMapActor does not have a PaperTileMapComponent.")

    call_first(
        component,
        ("create_new_tile_map", "CreateNewTileMap"),
        MAP_WIDTH,
        MAP_HEIGHT,
        TILE_SIZE,
        TILE_SIZE,
        PIXELS_PER_UNREAL_UNIT,
        True,
    )

    # The initial layer is terrain. Add separate visual/detail layers so gameplay
    # collision can stay limited to the terrain layer.
    call_first(component, ("add_new_layer", "AddNewLayer"))
    call_first(component, ("add_new_layer", "AddNewLayer"))
    tile_map = component.get_editor_property("tile_map")
    return actor, component, tile_map


def set_layer_name(tile_map, layer_index: int, name: str) -> None:
    layers = tile_map.get_editor_property("tile_layers")
    if layer_index < len(layers):
        layers[layer_index].set_editor_property("layer_name", name)


def set_tile(component, x: int, y: int, layer: int, tile_info) -> None:
    call_first(component, ("set_tile", "SetTile"), x, y, layer, tile_info)


def clear_tile(component, x: int, y: int, layer: int) -> None:
    set_tile(component, x, y, layer, unreal.PaperTileInfo())


def paint_platforms(component, tiles) -> None:
    earth_cycle = [tiles["earth_1"], tiles["earth_2"], tiles["earth_3"], tiles["earth_4"]]
    grass_info = make_tile_info(tiles["grass"])
    for platform in PLATFORMS:
        for x in range(platform.x_start, platform.x_end + 1):
            set_tile(component, x, platform.top_y, TERRAIN_LAYER, grass_info)
            for depth in range(1, platform.fill_depth + 1):
                y = platform.top_y + depth
                if y < MAP_HEIGHT:
                    earth_info = make_tile_info(earth_cycle[(x + depth) % len(earth_cycle)])
                    set_tile(component, x, y, TERRAIN_LAYER, earth_info)


def paint_details(component, tiles) -> None:
    detail_info = make_tile_info(tiles["grass_detail"])
    for x, y in DECORATION_TILES:
        set_tile(component, x, y, DETAIL_LAYER, detail_info)


def paint_hazard_guides(component, tiles) -> None:
    # The project hazards are Blueprint actors, not tiles. This visual guide uses
    # a contrasting earth tile on a non-colliding layer to mark where designers
    # should place spike/hot-surface Blueprint hazards in the tile-map level.
    hazard_info = make_tile_info(tiles["earth_4"])
    for hazard in HAZARDS:
        for x in range(hazard.x_start, hazard.x_end + 1):
            set_tile(component, x, hazard.y, HAZARD_GUIDE_LAYER, hazard_info)


def configure_tile_map_asset(tile_map) -> None:
    tile_map.set_editor_property("map_width", MAP_WIDTH)
    tile_map.set_editor_property("map_height", MAP_HEIGHT)
    tile_map.set_editor_property("tile_width", TILE_SIZE)
    tile_map.set_editor_property("tile_height", TILE_SIZE)
    tile_map.set_editor_property("pixels_per_unreal_unit", PIXELS_PER_UNREAL_UNIT)
    tile_map.set_editor_property("separation_per_layer", 8.0)
    tile_map.set_editor_property("background_color", unreal.LinearColor(0.06, 0.09, 0.13, 1.0))

    if hasattr(tile_map, "set_collision_thickness"):
        tile_map.set_collision_thickness(COLLISION_THICKNESS)
    elif tile_map.has_editor_property("collision_thickness"):
        tile_map.set_editor_property("collision_thickness", COLLISION_THICKNESS)


def save_tile_map_asset(component, tile_map) -> None:
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    unreal.EditorAssetLibrary.make_directory(TILE_MAP_PACKAGE)
    unreal.EditorAssetLibrary.delete_asset(TILE_MAP_PATH)

    duplicated = asset_tools.duplicate_asset(TILE_MAP_NAME, TILE_MAP_PACKAGE, tile_map)
    if not duplicated:
        raise RuntimeError(f"Unable to save generated tile map asset at {TILE_MAP_PATH}.")

    component.set_editor_property("tile_map", duplicated)
    unreal.EditorAssetLibrary.save_asset(TILE_MAP_PATH, only_if_is_dirty=False)


def add_preview_helpers() -> None:
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(7900.0, -3500.0, 1450.0))
    camera.set_actor_label("Camera_TileMap_SideView")
    camera.set_actor_rotation(unreal.Rotator(0.0, 90.0, 0.0))
    camera_component = camera.get_component_by_class(unreal.CameraComponent)
    if camera_component:
        camera_component.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        camera_component.set_editor_property("ortho_width", 3600.0)

    light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(3200.0, -800.0, 2600.0))
    light.set_actor_label("KeyLight_TileMap")
    light.set_actor_rotation(unreal.Rotator(-35.0, -35.0, 0.0))

    text = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(650.0, -120.0, 2500.0))
    text.set_actor_label("TileMap_DesignerNotes")
    component = text.get_component_by_class(unreal.TextRenderComponent)
    if component:
        component.set_text("TM_2D_Platformer_Showcase\n128x28 tiles @ 128px\nTerrain layer collides; details and hazard guides are visual.")
        component.set_world_size(92.0)
        component.set_text_render_color(unreal.Color(229, 245, 255, 255))


def main() -> None:
    unreal.log(f"Creating {TILE_MAP_PATH} and preview level {PREVIEW_LEVEL}...")
    unreal.EditorLevelLibrary.new_level(PREVIEW_LEVEL)

    tiles = {name: load_asset(path) for name, path in TILE_SETS.items()}
    _actor, component, tile_map = create_component_with_tile_map()
    configure_tile_map_asset(tile_map)
    set_layer_name(tile_map, TERRAIN_LAYER, "Terrain_Collision")
    set_layer_name(tile_map, DETAIL_LAYER, "Grass_Details")
    set_layer_name(tile_map, HAZARD_GUIDE_LAYER, "Hazard_Placement_Guide")

    for layer in (TERRAIN_LAYER, DETAIL_LAYER, HAZARD_GUIDE_LAYER):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                clear_tile(component, x, y, layer)

    paint_platforms(component, tiles)
    paint_details(component, tiles)
    paint_hazard_guides(component, tiles)
    save_tile_map_asset(component, tile_map)
    add_preview_helpers()

    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(f"Saved tile map asset: {TILE_MAP_PATH}")
    unreal.log(f"Saved preview level: {PREVIEW_LEVEL}")


if __name__ == "__main__":
    main()
