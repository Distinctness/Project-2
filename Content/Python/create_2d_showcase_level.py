"""Build the 2D showcase level for Echoes of Four Realms in Unreal Engine 5.7.4.

Run from the UE Python console or command line:
    py "Content/Python/create_2d_showcase_level.py"

The script creates /Game/Levels/L_2D_Showcase_Gauntlet using existing project
content: 2D character/game mode, environment blueprints, pickups, enemies, and
earth sprites. The layout is deliberately long-form (roughly 3-5 minutes for a
first-time playthrough) and divided into readable gameplay beats for iteration.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

import unreal

LEVEL_PACKAGE = "/Game/Levels/L_2D_Showcase_Gauntlet"
LEVEL_TITLE = "L_2D_Showcase_Gauntlet"
LANE_Y = 0.0
SPRITE_Y = -80.0
WALL_DEPTH = 80.0
PLATFORM_Z_THICKNESS = 35.0

ASSET_PATHS = {
    "game_mode": "/Game/ThirdPerson/Blueprints/BP_GM_2D_Plat.BP_GM_2D_Plat_C",
    "player": "/Game/ThirdPerson/Blueprints/BP_Third_2D_Character.BP_Third_2D_Character_C",
    "hud": "/Game/ThirdPerson/Blueprints/UI/InGame/BP_myHUD.BP_myHUD_C",
    "moving_platform": "/Game/ThirdPerson/Blueprints/Environment/BP_MovingPlatform.BP_MovingPlatform_C",
    "damaged_platform": "/Game/ThirdPerson/Blueprints/Environment/BP_DamagedPlatform.BP_DamagedPlatform_C",
    "delete_platform": "/Game/ThirdPerson/Blueprints/Environment/BP_DeletePlatform.BP_DeletePlatform_C",
    "falling_rumble": "/Game/ThirdPerson/Blueprints/Environment/BP_FallingRumble.BP_FallingRumble_C",
    "hot_surface": "/Game/ThirdPerson/Blueprints/Environment/BP_HotSurface.BP_HotSurface_C",
    "slippery_surface": "/Game/ThirdPerson/Blueprints/Environment/BP_SlipperySurface.BP_SlipperySurface_C",
    "spikes": "/Game/ThirdPerson/Blueprints/Environment/BP_Spikes.BP_Spikes_C",
    "trampoline": "/Game/ThirdPerson/Blueprints/Environment/BP_Trampoline.BP_Trampoline_C",
    "wind": "/Game/ThirdPerson/Blueprints/Environment/BP_Wind.BP_Wind_C",
    "swimming": "/Game/ThirdPerson/Blueprints/Environment/BP_Swimming.BP_Swimming_C",
    "jd_platform": "/Game/ThirdPerson/Blueprints/Environment/BP_JDPlatform.BP_JDPlatform_C",
    "destructible_wall": "/Game/ThirdPerson/Blueprints/Environment/BP_DestructibleWall.BP_DestructibleWall_C",
    "door": "/Game/ThirdPerson/Blueprints/Environment/BP_Door.BP_Door_C",
    "respawn": "/Game/ThirdPerson/Blueprints/Environment/BP_Respawn.BP_Respawn_C",
    "double_jump": "/Game/ThirdPerson/Blueprints/PickUps/BP_DoubleJumpPickUp.BP_DoubleJumpPickUp_C",
    "additional_jump": "/Game/ThirdPerson/Blueprints/PickUps/BP_AdditionalJump.BP_AdditionalJump_C",
    "ability": "/Game/ThirdPerson/Blueprints/PickUps/BP_AbilityPickUp.BP_AbilityPickUp_C",
    "damage": "/Game/ThirdPerson/Blueprints/PickUps/BP_DamagePickUp.BP_DamagePickUp_C",
    "health": "/Game/ThirdPerson/Blueprints/PickUps/BP_HealthPickUp.BP_HealthPickUp_C",
    "exp": "/Game/ThirdPerson/Blueprints/PickUps/BP_EXPPickUp.BP_EXPPickUp_C",
    "idle_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/IdleEnemy/BP_IdleEnemy.BP_IdleEnemy_C",
    "focus_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/FocusEnemy/BP_FocusEnemy.BP_FocusEnemy_C",
    "flying_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/FlyingEnemy/BP_FlyingEnemy.BP_FlyingEnemy_C",
    "random_projectile_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/RandomProjectileEnemy/BP_RandomProjectileEnemy.BP_RandomProjectileEnemy_C",
    "focus_projectile_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/FocusProjectileEnemy/BP_FocusProjectileEnemy.BP_FocusProjectileEnemy_C",
    "burrowing_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/BurrowingEnemy/BP_BurrowingEnemy.BP_BurrowingEnemy_C",
    "explosive_enemy": "/Game/ThirdPerson/Blueprints/AI/BasicEnemies/ExplosiveEnemy/BP_ExplosiveEnemy.BP_ExplosiveEnemy_C",
    "boss_badger": "/Game/ThirdPerson/Blueprints/AI/Bosses/Badger/BP_Badger.BP_Badger_C",
    "grass_sprite": "/Game/Environement_assets/Earth/Grass_Sprite.Grass_Sprite",
    "grass_details": "/Game/Environement_assets/Earth/Grass_Details_Sprite.Grass_Details_Sprite",
    "earth_1": "/Game/Environement_assets/Earth/1.1",
    "earth_2": "/Game/Environement_assets/Earth/2.2",
    "earth_3": "/Game/Environement_assets/Earth/3.3",
    "earth_4": "/Game/Environement_assets/Earth/4.4",
}


@dataclass(frozen=True)
class Beat:
    name: str
    x_start: float
    x_end: float
    coaching: str


BEATS = [
    Beat("00_Onboarding_Meadow", 0, 2600, "Run, jump, collect EXP, and confirm the 2D camera framing."),
    Beat("01_DoubleJump_Grove", 2600, 5200, "Earn double jump and climb safe vertical lanes."),
    Beat("02_Hazard_Causeway", 5200, 7900, "Read spikes, hot surfaces, falling platforms, and respawn pacing."),
    Beat("03_Wind_Water_Cavern", 7900, 10800, "Use wind boosts, trampolines, and swimming volume traversal."),
    Beat("04_Combat_Ridge", 10800, 14000, "Layer grounded, flying, projectile, burrowing, and explosive enemies."),
    Beat("05_Gauntlet_Ascent", 14000, 17600, "Chain all movement verbs under pressure with recovery pickups."),
    Beat("06_Badger_Arena_Finale", 17600, 20500, "Close with a miniboss arena and locked exit door."),
]


def load_asset(path: str):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        unreal.log_warning(f"Could not load asset: {path}")
    return asset


def load_class(path: str):
    cls = unreal.EditorAssetLibrary.load_blueprint_class(path)
    if not cls:
        cls = unreal.load_class(None, path)
    if not cls:
        unreal.log_warning(f"Could not load class: {path}")
    return cls


def set_label(actor: unreal.Actor, label: str) -> None:
    try:
        actor.set_actor_label(label)
    except Exception:
        pass


def spawn_actor(actor_class, label: str, x: float, z: float, *, y: float = LANE_Y, yaw: float = 0.0, scale=(1.0, 1.0, 1.0)):
    if actor_class is None:
        return None
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(x, y, z),
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if actor:
        actor.set_actor_scale3d(unreal.Vector(*scale))
        set_label(actor, label)
    return actor


def spawn_blueprint(key: str, label: str, x: float, z: float, *, y: float = LANE_Y, yaw: float = 0.0, scale=(1.0, 1.0, 1.0)):
    return spawn_actor(load_class(ASSET_PATHS[key]), label, x, z, y=y, yaw=yaw, scale=scale)


def spawn_text(label: str, text: str, x: float, z: float, size: float = 44.0) -> None:
    actor = spawn_actor(unreal.TextRenderActor, label, x, z, y=-115.0)
    if not actor:
        return
    component = actor.get_component_by_class(unreal.TextRenderComponent)
    if component:
        component.set_text(text)
        alignment = getattr(unreal, "HorizontalTextAligment", None)
        if alignment:
            component.set_horizontal_alignment(alignment.EHTA_CENTER)
        component.set_world_size(size)
        component.set_text_render_color(unreal.Color(229, 245, 255, 255))


def spawn_blocking_box(label: str, x: float, z: float, width: float, height: float, *, depth: float = WALL_DEPTH) -> None:
    actor = spawn_actor(unreal.BlockingVolume, label, x, z)
    if actor:
        # BlockingVolume brushes default to a 200uu cube; scale to requested 2D slab.
        actor.set_actor_scale3d(unreal.Vector(width / 200.0, depth / 200.0, height / 200.0))


def spawn_platform(label: str, x: float, z: float, width: float, *, height: float = PLATFORM_Z_THICKNESS) -> None:
    spawn_blocking_box(label, x, z, width, height)
    add_ground_sprite_strip(f"Decor_{label}", x, z + height * 0.65, width)


def spawn_checkpoint(index: int, x: float, z: float) -> None:
    spawn_blueprint("respawn", f"Checkpoint_{index:02d}", x, z + 90.0)
    spawn_text(f"CheckpointLabel_{index:02d}", f"CHECKPOINT {index}", x, z + 240.0, 34.0)


def add_ground_sprite_strip(label_prefix: str, center_x: float, z: float, width: float) -> None:
    sprite_class = getattr(unreal, "PaperSpriteActor", None)
    if sprite_class is None:
        return
    sprite = load_asset(ASSET_PATHS["grass_sprite"])
    details = load_asset(ASSET_PATHS["grass_details"])
    count = max(1, int(math.ceil(width / 320.0)))
    start_x = center_x - (count - 1) * 160.0
    for idx in range(count):
        actor = spawn_actor(sprite_class, f"{label_prefix}_Grass_{idx:02d}", start_x + idx * 320.0, z, y=SPRITE_Y)
        if actor:
            comp = actor.get_component_by_class(unreal.PaperSpriteComponent)
            if comp and sprite:
                comp.set_editor_property("source_sprite", sprite)
            actor.set_actor_scale3d(unreal.Vector(2.1, 2.1, 2.1))
    if details:
        for idx in range(0, count, 2):
            actor = spawn_actor(sprite_class, f"{label_prefix}_GrassDetails_{idx:02d}", start_x + idx * 320.0 + 80.0, z + 30.0, y=SPRITE_Y - 5.0)
            if actor:
                comp = actor.get_component_by_class(unreal.PaperSpriteComponent)
                if comp:
                    comp.set_editor_property("source_sprite", details)
                actor.set_actor_scale3d(unreal.Vector(1.8, 1.8, 1.8))


def add_background_tiles() -> None:
    sprite_class = getattr(unreal, "PaperSpriteActor", None)
    if sprite_class is None:
        unreal.log_warning("PaperSpriteActor unavailable; skipping decorative Earth sprite backdrop.")
        return
    earth_keys = ["earth_1", "earth_2", "earth_3", "earth_4"]
    for lane, z in enumerate([-160, 420, 960]):
        for i, x in enumerate(range(-600, 21100, 650)):
            sprite = load_asset(ASSET_PATHS[earth_keys[(i + lane) % len(earth_keys)]])
            actor = spawn_actor(sprite_class, f"Backdrop_Earth_{lane}_{i:02d}", float(x), float(z), y=-360.0 - lane * 20.0)
            if actor:
                comp = actor.get_component_by_class(unreal.PaperSpriteComponent)
                if comp and sprite:
                    comp.set_editor_property("source_sprite", sprite)
                actor.set_actor_scale3d(unreal.Vector(3.5, 3.5, 3.5))


def add_core_world_settings() -> None:
    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings()
    game_mode = load_class(ASSET_PATHS["game_mode"])
    if game_mode:
        settings.set_editor_property("default_game_mode", game_mode)
    settings.set_editor_property("world_to_meters", 100.0)

    player_cls = load_class(ASSET_PATHS["player"])
    spawn_actor(player_cls, "Player_Start_2D_Controller", 80.0, 160.0)
    spawn_actor(unreal.PlayerStart, "PlayerStart", 80.0, 160.0)

    camera = spawn_actor(unreal.CameraActor, "CineCamera_2D_SideView", 9000.0, 900.0, y=-3300.0)
    if camera:
        camera.set_actor_rotation(unreal.Rotator(0.0, 90.0, 0.0))
        camera_component = camera.get_component_by_class(unreal.CameraComponent)
        if camera_component:
            camera_component.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
            camera_component.set_editor_property("ortho_width", 1800.0)

    light = spawn_actor(unreal.DirectionalLight, "KeyLight_Warm2D", 3500.0, 1600.0, y=-900.0, yaw=-40.0)
    if light:
        light.set_actor_rotation(unreal.Rotator(-42.0, -35.0, 0.0))
    spawn_actor(unreal.SkyLight, "SkyLight_SoftFill", 4000.0, 1200.0, y=-900.0)


def add_onboarding() -> None:
    spawn_platform("StartMeadow_MainGround", 650, 0, 1650)
    spawn_text("TitleSign", "2D SHOWCASE GAUNTLET - Movement, Hazards, Combat", 760, 280, 48)
    for i, x in enumerate([360, 700, 1040, 1380, 1820]):
        spawn_blueprint("exp", f"Onboarding_EXP_{i:02d}", x, 170)
    spawn_platform("Onboarding_Step_01", 1850, 150, 420)
    spawn_platform("Onboarding_Step_02", 2300, 310, 360)
    spawn_blueprint("health", "EarlyHealthPickup", 2350, 470)
    spawn_checkpoint(1, 2550, 310)


def add_double_jump_grove() -> None:
    spawn_platform("DoubleJump_SafeLedge", 2920, 310, 420)
    spawn_blueprint("double_jump", "Ability_DoubleJump_CoreReward", 2920, 510)
    heights = [500, 720, 960, 1210, 1460]
    xs = [3380, 3840, 4320, 4760, 5180]
    for i, (x, z) in enumerate(zip(xs, heights)):
        spawn_platform(f"DoubleJump_Climb_{i:02d}", x, z, 310)
        spawn_blueprint("exp", f"DoubleJump_EXP_{i:02d}", x, z + 170)
    spawn_blueprint("additional_jump", "Optional_AdditionalJump_HighRisk", 4860, 1670)
    spawn_checkpoint(2, 5260, 1460)


def add_hazard_causeway() -> None:
    spawn_platform("Hazard_Entry", 5550, 1180, 380)
    for i, x in enumerate([6020, 6500, 6990]):
        spawn_platform(f"Hazard_SpikeIsland_{i:02d}", x, 1040 - i * 70, 300)
        spawn_blueprint("spikes", f"SpikeSet_{i:02d}", x + 55, 1110 - i * 70)
    spawn_blueprint("hot_surface", "HotSurface_TimingLane", 7420, 880, scale=(1.3, 1.0, 1.0))
    spawn_platform("Hazard_PostHotSafe", 7800, 860, 360)
    for i, x in enumerate([8170, 8500, 8830]):
        spawn_blueprint("falling_rumble", f"FallingRumble_{i:02d}", x, 850 - i * 40)
    spawn_blueprint("slippery_surface", "SlipperySurface_BrakeTest", 9300, 720, scale=(1.6, 1.0, 1.0))
    spawn_blueprint("health", "HazardRecoveryHealth", 9630, 900)
    spawn_checkpoint(3, 9840, 720)


def add_wind_water_cavern() -> None:
    spawn_platform("Cavern_Entry", 10150, 720, 380)
    spawn_blueprint("trampoline", "Trampoline_FirstLaunch", 10560, 760)
    spawn_platform("Cavern_HighCatch", 10960, 1250, 360)
    spawn_blueprint("wind", "WindColumn_VerticalLift", 11360, 950, scale=(1.0, 1.0, 2.4))
    spawn_platform("Cavern_WindExit", 11840, 1510, 420)
    spawn_blueprint("swimming", "SwimmingVolume_CooldownPool", 12360, 1010, scale=(2.0, 1.0, 1.0))
    spawn_platform("Cavern_PoolFloor", 12360, 650, 1120)
    spawn_blueprint("ability", "OptionalAbility_PoolReward", 12560, 1320)
    spawn_blueprint("jd_platform", "JumpDownPlatform_Tutorial", 13200, 1120, scale=(1.3, 1.0, 1.0))
    spawn_checkpoint(4, 13620, 940)


def add_combat_ridge() -> None:
    spawn_platform("Combat_EntryFloor", 14000, 940, 620)
    spawn_blueprint("idle_enemy", "Combat_IdleEnemy_Warmup", 14200, 1050)
    spawn_platform("Combat_Ridge_Lower", 14800, 760, 650)
    spawn_blueprint("focus_enemy", "Combat_FocusEnemy_Chaser", 14800, 890)
    spawn_platform("Combat_Ridge_Mid", 15550, 1020, 520)
    spawn_blueprint("flying_enemy", "Combat_FlyingEnemy_Airspace", 15550, 1320)
    spawn_blueprint("random_projectile_enemy", "Combat_RandomProjectileEnemy", 16180, 1120)
    spawn_platform("Combat_Ridge_Upper", 16480, 1240, 640)
    spawn_blueprint("focus_projectile_enemy", "Combat_FocusProjectileEnemy", 16680, 1390)
    spawn_blueprint("damage", "Combat_DamagePickup", 17000, 1450)
    spawn_checkpoint(5, 17260, 1240)


def add_gauntlet_ascent() -> None:
    for i, (x, z, width) in enumerate([
        (17680, 1120, 300), (18080, 1350, 280), (18480, 1580, 260),
        (18880, 1390, 260), (19280, 1640, 260), (19680, 1900, 280),
    ]):
        spawn_platform(f"Ascent_ManualPlatform_{i:02d}", x, z, width)
        if i % 2 == 0:
            spawn_blueprint("moving_platform", f"Ascent_MovingPlatform_Assist_{i:02d}", x + 180, z + 120)
        else:
            spawn_blueprint("damaged_platform", f"Ascent_DamagedPlatform_{i:02d}", x + 120, z + 70)
    spawn_blueprint("burrowing_enemy", "Ascent_BurrowingEnemy_Ambush", 18740, 1510)
    spawn_blueprint("explosive_enemy", "Ascent_ExplosiveEnemy_Pressure", 19380, 1780)
    spawn_blueprint("health", "Ascent_FinalHealth", 19880, 2080)
    spawn_checkpoint(6, 20100, 1900)


def add_finale() -> None:
    spawn_platform("Arena_Floor", 21300, 1660, 1800)
    spawn_blocking_box("Arena_LeftWall", 20450, 1910, 90, 500)
    spawn_blocking_box("Arena_RightWall", 22150, 1910, 90, 500)
    spawn_text("ArenaIntroSign", "FINALE: survive the Badger arena, then exit.", 21300, 2170, 42)
    spawn_blueprint("boss_badger", "Finale_Badger_MiniBoss", 21320, 1840, scale=(0.85, 0.85, 0.85))
    for i, x in enumerate([20780, 21120, 21500, 21860]):
        spawn_blueprint("exp", f"Arena_EXP_{i:02d}", x, 1840)
    spawn_blueprint("destructible_wall", "Arena_ExitBreakableWall", 22280, 1840)
    spawn_blueprint("door", "Arena_ExitDoor", 22640, 1840)
    spawn_text("EndSign", "END OF SHOWCASE - target playtime: 3-5 minutes", 22880, 2050, 38)


def add_beat_markers(beats: Iterable[Beat]) -> None:
    for i, beat in enumerate(beats):
        x = (beat.x_start + beat.x_end) * 0.5
        spawn_text(f"BeatMarker_{i:02d}_{beat.name}", f"{i}. {beat.name}\n{beat.coaching}", x, 520 + (i % 3) * 380, 30.0)


def main() -> None:
    unreal.log(f"Creating {LEVEL_PACKAGE}...")
    unreal.EditorLevelLibrary.new_level(LEVEL_PACKAGE)
    add_core_world_settings()
    add_background_tiles()
    add_beat_markers(BEATS)
    add_onboarding()
    add_double_jump_grove()
    add_hazard_causeway()
    add_wind_water_cavern()
    add_combat_ridge()
    add_gauntlet_ascent()
    add_finale()
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(f"Saved {LEVEL_PACKAGE}. Open {LEVEL_TITLE} from Content/Levels to iterate or playtest.")


if __name__ == "__main__":
    main()
