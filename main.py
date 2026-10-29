import json
import math
import os
import random
import sys
from array import array
from pathlib import Path

import pygame


GAME_WIDTH, GAME_HEIGHT, FPS = 800, 1200, 60
ROAD_LEFT, ROAD_RIGHT = 90, 710
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
PLAYER_MIN_Y = 650

WHITE = (242, 242, 238)
BLACK = (18, 19, 22)
ASPHALT = (63, 65, 68)
ASPHALT_DARK = (51, 53, 56)
GRASS = (35, 105, 50)
GRASS_DARK = (28, 86, 41)
YELLOW = (250, 210, 48)
ORANGE = (244, 132, 35)
CYAN = (70, 215, 235)
RED = (210, 48, 48)

PLAYER_MODELS = [
    {"name": "KLASİK", "size": (88, 148), "speed": 455, "unlock": 0, "sprite": "classic.png"},
    {"name": "SPOR", "size": (82, 145), "speed": 520, "unlock": 9, "sprite": "sport.png"},
    {"name": "SUV", "size": (98, 160), "speed": 430, "unlock": 28, "sprite": "suv.png"},
    {"name": "KAMYON", "size": (108, 190), "speed": 385, "unlock": 53, "sprite": "truck.png"},
    {"name": "TANK", "size": (112, 168), "speed": 350, "unlock": 67, "sprite": "tank.png"},
]

ENEMY_MODELS = {
    "compact": {"size": (70, 120), "color": (220, 55, 55)},
    "sedan": {"size": (84, 145), "color": (190, 42, 48)},
    "truck": {"size": (104, 185), "color": (165, 35, 38)},
}

ENVIRONMENTS = ["İLKBAHAR", "YAZ", "SONBAHAR", "KIŞ", "ÇÖL", "ŞEHİR", "GECE"]

CAR_COLORS = [
    (38, 125, 230),
    (240, 170, 28),
    (165, 62, 225),
    (40, 185, 115),
    (235, 235, 235),
    (225, 60, 75),
]

PATTERN_DEFS = [
    {"name": "DÜZ", "level": 1},
    {"name": "TEK ŞERİT", "level": 2},
    {"name": "ÇİFT ŞERİT", "level": 3},
    {"name": "DAMA", "level": 5},
    {"name": "ALEV", "level": 7},
    {"name": "KAMUFLAJ", "level": 10},
    {"name": "ŞİMŞEK", "level": 15},
    {"name": "NEON", "level": 20},
]
PATTERNS = [pattern["name"] for pattern in PATTERN_DEFS]
PLAYER_SPRITES = {}
ENEMY_SPRITES = {}
TRAFFIC_COLORS = [(205, 48, 52), (48, 105, 190), (225, 165, 42), (205, 210, 215),
                  (45, 145, 92), (125, 72, 175)]

# Fare ile kullanılan arayüz alanları (sanal 800x1200 koordinatları).
GARAGE_COLOR_RECTS = [pygame.Rect(120 + i * 94, 560, 66, 58) for i in range(len(CAR_COLORS))]
GARAGE_PATTERN_RECTS = [pygame.Rect(82 + (i % 4) * 160, 650 + (i // 4) * 58, 150, 48)
                        for i in range(len(PATTERNS))]
GARAGE_MODEL_RECTS = [pygame.Rect(125, 780 + i * 48, 550, 40) for i in range(len(PLAYER_MODELS))]
GARAGE_START_RECT = pygame.Rect(390, 1040, 350, 70)
GARAGE_BACK_RECT = pygame.Rect(60, 1040, 270, 70)
HUD_GARAGE_RECT = pygame.Rect(635, 88, 130, 38)
RESTART_RECT = pygame.Rect(220, 650, 360, 76)
HUD_PAUSE_RECT = pygame.Rect(350, 20, 100, 42)
PAUSE_CONTINUE_RECT = pygame.Rect(190, 490, 420, 72)
PAUSE_GARAGE_RECT = pygame.Rect(190, 585, 420, 72)
PAUSE_EXIT_RECT = pygame.Rect(190, 680, 420, 72)

MENU_PLAY_RECT = pygame.Rect(180, 445, 440, 72)
MENU_GARAGE_RECT = pygame.Rect(180, 535, 440, 72)
MENU_MISSIONS_RECT = pygame.Rect(180, 625, 440, 72)
MENU_SETTINGS_RECT = pygame.Rect(180, 715, 440, 72)
MENU_EXIT_RECT = pygame.Rect(180, 805, 440, 72)
BACK_RECT = pygame.Rect(40, 1080, 190, 66)
BRIEFING_START_RECT = pygame.Rect(220, 850, 360, 76)
BRIEFING_BACK_RECT = pygame.Rect(220, 950, 360, 66)
CHAPTER_CONTINUE_RECT = pygame.Rect(210, 720, 380, 76)

SETTINGS_MUSIC_MINUS = pygame.Rect(170, 400, 70, 60)
SETTINGS_MUSIC_PLUS = pygame.Rect(560, 400, 70, 60)
SETTINGS_SFX_MINUS = pygame.Rect(170, 500, 70, 60)
SETTINGS_SFX_PLUS = pygame.Rect(560, 500, 70, 60)
SETTINGS_MUSIC_TOGGLE = pygame.Rect(220, 600, 360, 62)
SETTINGS_SFX_TOGGLE = pygame.Rect(220, 680, 360, 62)
SETTINGS_FULLSCREEN = pygame.Rect(220, 760, 360, 62)
RESOLUTION_RECTS = [pygame.Rect(100 + i * 205, 880, 190, 62) for i in range(3)]
WINDOW_SIZES = [(600, 900), (800, 1000), (900, 1200)]

MISSION_DEFS = [
    {"chapter": "BÖLÜM 1", "name": "İLK KONTAK", "biome": "İLKBAHAR", "effect": "Sakin trafik • öğretici rota",
     "speaker": "ADA — Tamirci", "dialogue": "Önce araca alış. Garajın çevresindeki kısa rotayı tamamla; risk almana gerek yok.",
     "description": "0.50 km ilerle", "key": "distance", "target": 0.5, "reward": 1, "special": "TEK ŞERİT DESENİ", "jokers": 1},
    {"chapter": "BÖLÜM 2", "name": "İLK KAZANÇ", "biome": "İLKBAHAR", "effect": "Az trafik • bol ödül",
     "speaker": "ADA", "dialogue": "Yol kenarındaki sponsor altınları ilk tamir masrafımızı karşılayacak.",
     "description": "3 ödül topla", "key": "collected", "target": 3, "reward": 1, "special": "ÇİFT ŞERİT DESENİ"},
    {"chapter": "BÖLÜM 3", "name": "KÖY YOLU", "biome": "İLKBAHAR", "effect": "Yola çıkan koyunlar",
     "speaker": "ADA", "dialogue": "Köy yolu açık. Koyunlara dikkat et ve trafiği temiz biçimde geç.",
     "description": "6 aracı geride bırak", "key": "passed", "target": 6, "reward": 2, "special": "DAMA DESENİ"},
    {"chapter": "BÖLÜM 4", "name": "BAHAR FIRTINASI", "biome": "İLKBAHAR", "effect": "Yağmur • düşük yol tutuşu",
     "speaker": "ADA", "dialogue": "İlk ciddi sınavın yağmur altında. Ritmini koru ve kırsal etabı bitir.",
     "description": "1.20 km ilerle", "key": "distance", "target": 1.2, "reward": 2, "special": "ALEV DESENİ", "jokers": 1},
    {"chapter": "BÖLÜM 5", "name": "SICAK ASFALT", "biome": "YAZ", "effect": "Yakıt tüketimi artar",
     "speaker": "ADA", "dialogue": "Yaz sıcağı motoru yoracak. Benzini izle ve kısa test rotasını tamamla.",
     "description": "1.00 km ilerle", "key": "distance", "target": 1.0, "reward": 3, "special": "SPOR ARABA AÇILDI"},
    {"chapter": "BÖLÜM 6", "name": "SPONSOR ROTASI", "biome": "YAZ", "effect": "Ödül hattı • sıcak hava",
     "speaker": "ADA", "dialogue": "Yeni sponsor seni izliyor. Altınları toplarsan garaja gerçek bir bütçe ayıracak.",
     "description": "7 ödül topla", "key": "collected", "target": 7, "reward": 3, "special": "3 ALTIN BONUS"},
    {"chapter": "BÖLÜM 7", "name": "KURU DEPO", "biome": "YAZ", "effect": "Hızlı yakıt tüketimi",
     "speaker": "ADA", "dialogue": "Depo küçük, rota uzun. Yoldaki bidonları kullanmayı öğrenmeden çöle giremeyiz.",
     "description": "2 benzin bidonu topla", "key": "fuel_pickups", "target": 2, "reward": 3, "special": "KAMUFLAJ + ŞİMŞEK DESENİ"},
    {"chapter": "BÖLÜM 8", "name": "ÇÖL EŞİĞİ", "biome": "ÇÖL", "effect": "Kum sıcağı • konvoy trafiği",
     "speaker": "KUZGUN — Rakip", "dialogue": "Kuzgun çölde dayanamayacağını söylüyor. Konvoyun önüne geç ve ona cevap ver.",
     "description": "15 aracı geride bırak", "key": "passed", "target": 15, "reward": 4, "special": "1 JOKER HAKKI", "jokers": 1},
    {"chapter": "BÖLÜM 9", "name": "KUM SAATİ", "biome": "ÇÖL", "effect": "Yoğun trafik olayları",
     "speaker": "ADA", "dialogue": "Motor ısınıyor. Hızlı ama temiz sürerek etap puanını tamamla.",
     "description": "500 skor yap", "key": "score", "target": 500, "reward": 4, "special": "NEON DESENİ"},
    {"chapter": "BÖLÜM 10", "name": "ÇÖL KONVOYU", "biome": "ÇÖL", "effect": "Uzun konvoy • az yakıt",
     "speaker": "ADA", "dialogue": "Ağır araç parçaları konvoyun sonunda. Oraya ulaşırsan garaj yeni sınıfa geçecek.",
     "description": "25 aracı geride bırak", "key": "passed", "target": 25, "reward": 5, "special": "SUV SINIFI"},
    {"chapter": "BÖLÜM 11", "name": "SİS PERDESİ", "biome": "SONBAHAR", "effect": "Hafif sis • kısa rota",
     "speaker": "ADA", "dialogue": "Sonbahar vadisinde görüş azalıyor. Önce sis içinde kısa bir keşif yap.",
     "description": "0.80 km ilerle", "key": "distance", "target": 0.8, "reward": 4, "special": "4 ALTIN BONUS"},
    {"chapter": "BÖLÜM 12", "name": "DÜŞEN YAPRAKLAR", "biome": "SONBAHAR", "effect": "Sis • yoğun trafik",
     "speaker": "KUZGUN", "dialogue": "Kuzgun sisin arkasına saklandı. Trafikte onu yakalayacak kadar hızlı ol.",
     "description": "20 aracı geride bırak", "key": "passed", "target": 20, "reward": 5, "special": "NEON DESENİ"},
    {"chapter": "BÖLÜM 13", "name": "KAYIP ROTA", "biome": "SONBAHAR", "effect": "Yoğun sis • düşük görüş",
     "speaker": "ADA", "dialogue": "Navigasyon kesildi. İşaretleri takip et ve vadi çıkışına ulaş.",
     "description": "1.80 km ilerle", "key": "distance", "target": 1.8, "reward": 5, "special": "1 JOKER HAKKI", "jokers": 1},
    {"chapter": "BÖLÜM 14", "name": "İLK BUZ", "biome": "KIŞ", "effect": "Hafif kayma • kar yağışı",
     "speaker": "ADA", "dialogue": "Direksiyonu yumuşak kullan. Kış rotasının ilk kısmı yalnızca denge sınavı.",
     "description": "0.80 km ilerle", "key": "distance", "target": 0.8, "reward": 5, "special": "KIŞ PAKETİ"},
    {"chapter": "BÖLÜM 15", "name": "BEYAZ GEÇİT", "biome": "KIŞ", "effect": "Kaygan yol • sert trafik",
     "speaker": "ADA", "dialogue": "Kar kalınlaşıyor. Savrulmadan rakiplerini geç ve dağ yolunu aç.",
     "description": "20 aracı geride bırak", "key": "passed", "target": 20, "reward": 6, "special": "KAMYON SINIFI"},
    {"chapter": "BÖLÜM 16", "name": "ZİRVE HATTI", "biome": "KIŞ", "effect": "Maksimum buzlanma",
     "speaker": "KUZGUN", "dialogue": "Zirveye çıkabilirsen Kuzgun seni artık gerçek rakibi olarak kabul edecek.",
     "description": "2.50 km ilerle", "key": "distance", "target": 2.5, "reward": 7, "special": "1 JOKER + 7 ALTIN", "jokers": 1},
    {"chapter": "BÖLÜM 17", "name": "ŞEHİR IŞIKLARI", "biome": "ŞEHİR", "effect": "Dar geçitler • yol çalışmaları",
     "speaker": "ADA", "dialogue": "Kupa şehre döndü. Kalabalığın önünde güçlü bir puanla giriş yap.",
     "description": "750 skor yap", "key": "score", "target": 750, "reward": 7, "special": "TANK SINIFI"},
    {"chapter": "BÖLÜM 18", "name": "GECE PAZARI", "biome": "GECE", "effect": "Karanlık • ödül hatları",
     "speaker": "ADA", "dialogue": "Final parçaları gece pazarında. Farlarını açık tut ve sponsor kasalarını topla.",
     "description": "10 ödül topla", "key": "collected", "target": 10, "reward": 8, "special": "8 ALTIN BONUS"},
    {"chapter": "BÖLÜM 19", "name": "SON SABOTAJ", "biome": "GECE", "effect": "Yağ lekeleri • barikatlar",
     "speaker": "KUZGUN", "dialogue": "Kuzgun son kez yolunu kesiyor. Hatasız bir skorla final kapısını aç.",
     "description": "1200 skor yap", "key": "score", "target": 1200, "reward": 10, "special": "2 JOKER HAKKI", "jokers": 2},
    {"chapter": "BÖLÜM 20 • FİNAL", "name": "DÖRT MEVSİM KUPASI", "biome": "FİNAL", "effect": "Her kilometrede değişen biyom",
     "speaker": "KUZGUN", "dialogue": "Yirmi etaplık yolun sonu. Dört mevsimi aş, garajı kurtar ve kupayı eve getir.",
     "description": "4.00 km tamamla", "key": "distance", "target": 4.0, "reward": 20, "special": "ŞAMPİYONLUK + 3 JOKER", "jokers": 3},
]

# Windows'ta kayıt, oyunun kurulu olduğu klasör yerine kullanıcıya ait AppData'da tutulur.
# Böylece oyun Program Files altına kurulduğunda da kayıt yazılabilir.
SAVE_DIRECTORY = Path(os.environ.get("LOCALAPPDATA", Path(__file__).parent)) / "CarRalling"
SAVE_FILE = SAVE_DIRECTORY / "savegame.json"
DEFAULT_SAVE = {
    "version": 6,
    "high_score": 0,
    "rewards": 0,
    "model_index": 0,
    "color_index": 0,
    "pattern_index": 0,
    "mission_mask": 0,
    "story_stage": 0,
    "jokers": 1,
    "music_volume": 55,
    "sfx_volume": 70,
    "music_enabled": 0,
    "sfx_enabled": 1,
    "resolution_index": 1,
    "fullscreen": 1,
}


def resource_path(*parts):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def player_level(rewards):
    return max(1, 1 + int(rewards))


def pattern_is_unlocked(pattern_index, rewards):
    return PATTERN_DEFS[pattern_index]["level"] <= player_level(rewards)


def load_player_sprites():
    """Yüksek çözünürlüklü araçları bir kez ölçekler ve renk varyantlarını önbelleğe alır."""
    PLAYER_SPRITES.clear()
    ENEMY_SPRITES.clear()
    for model_index, model in enumerate(PLAYER_MODELS):
        try:
            image = pygame.image.load(str(resource_path("assets", "vehicles", model["sprite"]))).convert_alpha()
            bounds = image.get_bounding_rect(min_alpha=8)
            if bounds.width and bounds.height:
                image = image.subsurface(bounds).copy()
            image = pygame.transform.smoothscale(image, model["size"])
            grayscale = pygame.transform.grayscale(image)
            for color_index, color in enumerate(CAR_COLORS):
                tinted = grayscale.copy()
                tint = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                tint.fill((*color, 255))
                tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # Parlaklık kaybolmasın diye orijinal vurguları hafifçe geri ekle.
                highlight = image.copy()
                highlight.set_alpha(42)
                tinted.blit(highlight, (0, 0))
                PLAYER_SPRITES[(model_index, color_index)] = tinted
        except (pygame.error, OSError):
            # Asset bulunamazsa eski vektör çizim otomatik yedek olarak kalır.
            continue

    enemy_sources = {"compact": "classic.png", "sedan": "sport.png", "truck": "truck.png"}
    for enemy_type, filename in enemy_sources.items():
        try:
            image = pygame.image.load(str(resource_path("assets", "vehicles", filename))).convert_alpha()
            bounds = image.get_bounding_rect(min_alpha=8)
            if bounds.width and bounds.height:
                image = image.subsurface(bounds).copy()
            image = pygame.transform.smoothscale(image, ENEMY_MODELS[enemy_type]["size"])
            grayscale = pygame.transform.grayscale(image)
            for color_index, color in enumerate(TRAFFIC_COLORS):
                tinted = grayscale.copy()
                tint = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                tint.fill((*color, 255))
                tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                highlight = image.copy()
                highlight.set_alpha(35)
                tinted.blit(highlight, (0, 0))
                ENEMY_SPRITES[(enemy_type, color_index)] = tinted
        except (pygame.error, OSError):
            continue


class SoundManager:
    """Harici dosya olmadan kısa efektler ve döngü müziği üretir."""
    def __init__(self, profile):
        self.profile = profile
        self.available = pygame.mixer.get_init() is not None
        self.effects = {}
        self.music = None
        if not self.available:
            return
        try:
            effect_names = ("click", "reward", "fuel", "shield", "turbo", "crash", "mission", "event")
            for name in effect_names:
                path = resource_path("assets", "audio", f"{name}.ogg")
                if path.exists():
                    self.effects[name] = pygame.mixer.Sound(str(path))
            self.music = self._melody()
            self.apply_settings(restart_music=True)
        except pygame.error:
            self.available = False

    @staticmethod
    def _tone(frequency, duration, volume, wave="sine"):
        sample_rate = 44100
        frames = array("h")
        count = int(sample_rate * duration)
        for i in range(count):
            phase = 2 * math.pi * frequency * i / sample_rate
            envelope = min(1.0, i / 500) * max(0.0, 1.0 - i / count)
            if wave == "square":
                value = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave == "noise":
                value = random.uniform(-1.0, 1.0) * (1.0 - i / count)
            else:
                value = math.sin(phase)
            sample = int(32767 * volume * envelope * value)
            frames.extend((sample, sample))
        return pygame.mixer.Sound(buffer=frames.tobytes())

    @staticmethod
    def _melody():
        sample_rate = 44100
        notes = [220, 277, 330, 415, 330, 277, 247, 330, 370, 440, 370, 294, 247, 294, 330, 277]
        note_duration = 0.24
        frames = array("h")
        per_note = int(sample_rate * note_duration)
        for note in notes:
            for i in range(per_note):
                t = i / sample_rate
                envelope = min(1.0, i / 700) * min(1.0, (per_note - i) / 900)
                value = math.sin(2 * math.pi * note * t) * 0.55
                value += math.sin(2 * math.pi * note * 0.5 * t) * 0.22
                sample = int(32767 * 0.16 * envelope * value)
                frames.extend((sample, sample))
        return pygame.mixer.Sound(buffer=frames.tobytes())

    def apply_settings(self, restart_music=False):
        if not self.available:
            return
        sfx_volume = self.profile["sfx_volume"] / 100 if self.profile["sfx_enabled"] else 0
        for effect in self.effects.values():
            effect.set_volume(sfx_volume)
        if self.music:
            self.music.set_volume(self.profile["music_volume"] / 100 if self.profile["music_enabled"] else 0)
            if restart_music:
                self.music.play(loops=-1, fade_ms=500)

    def play(self, name):
        if self.available and self.profile["sfx_enabled"] and name in self.effects:
            self.effects[name].play()


class Car:
    def __init__(self, x, y, enemy_type=None, model_index=0, color_index=0, pattern_index=0):
        self.enemy_type = enemy_type
        self.model_index = model_index
        self.color_index = color_index
        self.pattern_index = pattern_index
        self.traffic_color_index = random.randrange(len(TRAFFIC_COLORS))
        self.x, self.y = float(x), float(y)
        self._set_size()

    @property
    def enemy(self):
        return self.enemy_type is not None

    def _set_size(self):
        size = ENEMY_MODELS[self.enemy_type]["size"] if self.enemy else PLAYER_MODELS[self.model_index]["size"]
        self.width, self.height = size
        self.rect = pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def change_model(self, model_index):
        center = self.rect.center
        self.model_index = model_index
        self._set_size()
        self.rect.center = center
        self.x, self.y = map(float, self.rect.topleft)

    def update_rect(self):
        self.rect.topleft = (round(self.x), round(self.y))

    def draw_pattern(self, surface):
        r = self.rect
        index = self.pattern_index
        if index == 1:
            pygame.draw.rect(surface, WHITE, (r.centerx - 6, r.y + 8, 12, r.h - 16), border_radius=5)
        elif index == 2:
            pygame.draw.rect(surface, WHITE, (r.centerx - 16, r.y + 8, 8, r.h - 16), border_radius=4)
            pygame.draw.rect(surface, WHITE, (r.centerx + 8, r.y + 8, 8, r.h - 16), border_radius=4)
        elif index == 3:
            cell = max(9, r.w // 7)
            for row in range(4):
                for col in range(4):
                    if (row + col) % 2 == 0:
                        pygame.draw.rect(surface, BLACK,
                                         (r.centerx - cell * 2 + col * cell, r.centery - cell * 2 + row * cell,
                                          cell, cell), border_radius=2)
        elif index == 4:
            flames = [(r.centerx, r.y + 12), (r.centerx - 20, r.y + 60), (r.centerx - 5, r.y + 50),
                      (r.centerx - 12, r.y + 100), (r.centerx + 18, r.y + 55), (r.centerx + 7, r.y + 62)]
            pygame.draw.polygon(surface, (245, 72, 28), flames)
            pygame.draw.lines(surface, YELLOW, True, flames, 4)
        elif index == 5:
            for ox, oy, rw, rh, color in ((-22, -40, 31, 24, (37, 72, 40)),
                                           (8, -12, 35, 28, (96, 105, 55)),
                                           (-25, 28, 40, 25, (48, 56, 42)),
                                           (5, 50, 28, 20, (123, 119, 69))):
                pygame.draw.ellipse(surface, color, (r.centerx + ox, r.centery + oy, rw, rh))
        elif index == 6:
            bolt = [(r.centerx + 8, r.y + 15), (r.centerx - 18, r.centery - 3),
                    (r.centerx - 2, r.centery - 3), (r.centerx - 14, r.bottom - 16),
                    (r.centerx + 25, r.centery - 18), (r.centerx + 7, r.centery - 18)]
            pygame.draw.lines(surface, (185, 32, 30), True, bolt, 9)
            pygame.draw.polygon(surface, YELLOW, bolt)
            pygame.draw.lines(surface, (255, 245, 170), True, bolt, 3)
        elif index == 7:
            pygame.draw.line(surface, (255, 35, 215), (r.left + 10, r.top + 22),
                             (r.left + 10, r.bottom - 18), 6)
            pygame.draw.line(surface, CYAN, (r.right - 10, r.top + 22),
                             (r.right - 10, r.bottom - 18), 6)
            pygame.draw.circle(surface, WHITE, r.center, max(8, r.w // 9), 3)

    def draw(self, surface, shield=False):
        r = self.rect
        color = ENEMY_MODELS[self.enemy_type]["color"] if self.enemy else CAR_COLORS[self.color_index]
        accent = tuple(max(0, c - 75) for c in color)

        if self.enemy:
            sprite = ENEMY_SPRITES.get((self.enemy_type, self.traffic_color_index))
        else:
            sprite = PLAYER_SPRITES.get((self.model_index, self.color_index))
        if sprite is not None:
            surface.blit(sprite, r.topleft)
            if not self.enemy:
                self.draw_pattern(surface)
            if shield:
                aura = pygame.Surface((r.w + 60, r.h + 60), pygame.SRCALPHA)
                pygame.draw.ellipse(aura, (70, 215, 235, 42), aura.get_rect(), 14)
                pygame.draw.ellipse(aura, (150, 245, 255, 205), aura.get_rect().inflate(-8, -8), 5)
                surface.blit(aura, (r.x - 30, r.y - 30))
            return

        # Yumuşak gölge arabayı asfalttan ayırır.
        shadow = pygame.Surface((r.w + 32, r.h + 32), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 75), shadow.get_rect().inflate(-8, -2))
        surface.blit(shadow, (r.x - 9, r.y + 12))

        # Kamyonun dingilleri daha büyük, spor arabanın tekerlekleri daha incedir.
        wheel_w = 15 if self.enemy_type == "truck" else 12
        wheel_h = 38 if self.enemy_type == "truck" else 30
        for wx, wy in ((r.left - wheel_w // 2, r.top + 25), (r.right - wheel_w // 2, r.top + 25),
                       (r.left - wheel_w // 2, r.bottom - 55), (r.right - wheel_w // 2, r.bottom - 55)):
            pygame.draw.rect(surface, BLACK, (wx, wy, wheel_w, wheel_h), border_radius=5)

        corner = 10 if self.enemy_type == "truck" else 20
        pygame.draw.rect(surface, color, r, border_radius=corner)
        pygame.draw.rect(surface, tuple(min(255, c + 35) for c in color), r, 3, border_radius=corner)

        if self.enemy_type == "truck":
            pygame.draw.rect(surface, accent, (r.x + 9, r.y + 62, r.w - 18, r.h - 72), border_radius=5)
            pygame.draw.rect(surface, (150, 205, 225), (r.x + 17, r.y + 18, r.w - 34, 32), border_radius=5)
            pygame.draw.line(surface, WHITE, (r.centerx, r.y + 70), (r.centerx, r.bottom - 14), 4)
        else:
            cabin_top = r.y + (28 if self.enemy_type == "compact" else 35)
            pygame.draw.rect(surface, accent, (r.x + 13, cabin_top, r.w - 26, r.h // 2), border_radius=11)
            pygame.draw.rect(surface, (145, 207, 228), (r.x + 18, r.y + 15, r.w - 36, 25), border_radius=6)
            pygame.draw.rect(surface, (95, 160, 190), (r.x + 18, r.bottom - 42, r.w - 36, 25), border_radius=6)
            pygame.draw.line(surface, (210, 240, 250), (r.x + 24, r.y + 20), (r.right - 28, r.y + 20), 3)

        if not self.enemy:
            self.draw_pattern(surface)

        light = YELLOW if not self.enemy else (255, 175, 110)
        pygame.draw.circle(surface, light, (r.left + 17, r.top + 10), 7)
        pygame.draw.circle(surface, light, (r.right - 17, r.top + 10), 7)
        pygame.draw.rect(surface, (145, 20, 25), (r.left + 11, r.bottom - 10, 15, 7), border_radius=3)
        pygame.draw.rect(surface, (145, 20, 25), (r.right - 26, r.bottom - 10, 15, 7), border_radius=3)
        pygame.draw.rect(surface, (205, 210, 215), (r.x + 9, r.y + 2, r.w - 18, 4), border_radius=2)
        if shield:
            aura = pygame.Surface((r.w + 60, r.h + 60), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (70, 215, 235, 42), aura.get_rect(), 14)
            pygame.draw.ellipse(aura, (150, 245, 255, 205), aura.get_rect().inflate(-8, -8), 5)
            surface.blit(aura, (r.x - 30, r.y - 30))


class Pickup:
    COLORS = {"reward": YELLOW, "shield": CYAN, "turbo": ORANGE, "fuel": (225, 58, 48)}

    def __init__(self, kind):
        self.kind = kind
        self.radius = 27
        self.x = random.randint(ROAD_LEFT + 48, ROAD_RIGHT - 48)
        self.y = -60.0
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.update_rect()

    def update_rect(self):
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, surface, font):
        color = self.COLORS[self.kind]
        cx, cy = self.rect.center
        glow = pygame.Surface((90, 90), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, 32), (45, 45), 43)
        pygame.draw.circle(glow, (*color, 55), (45, 45), 34)
        surface.blit(glow, (cx - 45, cy - 45))

        if self.kind == "reward":
            # Altın para ve ortasında kabartmalı yıldız.
            pygame.draw.circle(surface, (105, 72, 8), (cx, cy), 30)
            pygame.draw.circle(surface, color, (cx, cy), 26)
            pygame.draw.circle(surface, (255, 239, 112), (cx, cy), 20, 3)
            points = []
            for i in range(10):
                angle = -math.pi / 2 + i * math.pi / 5
                radius = 13 if i % 2 == 0 else 6
                points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
            pygame.draw.polygon(surface, (155, 103, 12), points)
        elif self.kind == "shield":
            # Kalkan rozeti.
            points = [(cx, cy - 29), (cx + 24, cy - 19), (cx + 20, cy + 10),
                      (cx, cy + 29), (cx - 20, cy + 10), (cx - 24, cy - 19)]
            pygame.draw.polygon(surface, (10, 70, 88), points)
            pygame.draw.polygon(surface, color, points, 5)
            pygame.draw.line(surface, WHITE, (cx, cy - 18), (cx, cy + 16), 4)
            pygame.draw.line(surface, WHITE, (cx - 11, cy - 2), (cx + 11, cy - 2), 4)
        elif self.kind == "turbo":
            # Turbo için şimşek simgesi.
            points = [(cx + 5, cy - 31), (cx - 19, cy + 2), (cx - 4, cy + 2),
                      (cx - 12, cy + 31), (cx + 22, cy - 9), (cx + 6, cy - 9)]
            pygame.draw.polygon(surface, BLACK, [(x + 3, y + 3) for x, y in points])
            pygame.draw.polygon(surface, color, points)
            pygame.draw.lines(surface, (255, 220, 110), True, points, 3)
        else:
            # Harf yerine sapı ve ağzı olan kırmızı benzin bidonu.
            body = pygame.Rect(cx - 20, cy - 23, 39, 48)
            pygame.draw.rect(surface, BLACK, body.inflate(7, 7), border_radius=7)
            pygame.draw.rect(surface, color, body, border_radius=6)
            pygame.draw.rect(surface, (255, 125, 105), (cx - 11, cy - 15, 18, 12), 4, border_radius=3)
            pygame.draw.polygon(surface, BLACK, [(cx + 12, cy - 24), (cx + 25, cy - 19),
                                                 (cx + 25, cy - 12), (cx + 16, cy - 14)])
            pygame.draw.line(surface, (120, 20, 18), (cx - 11, cy + 13), (cx + 11, cy - 7), 5)
            pygame.draw.line(surface, (120, 20, 18), (cx - 9, cy - 7), (cx + 11, cy + 13), 5)


class RoadHazard:
    def __init__(self, kind):
        self.kind = kind
        self.vx = 0.0
        if kind == "pothole":
            self.width, self.height = 100, 55
        elif kind == "oil":
            self.width, self.height = 125, 68
        elif kind == "sheep":
            self.width, self.height = 78, 58
        else:
            self.width, self.height = 135, 48
        if kind == "sheep":
            from_left = random.choice((True, False))
            self.x = float(ROAD_LEFT - self.width if from_left else ROAD_RIGHT)
            self.vx = random.uniform(115.0, 165.0) * (1 if from_left else -1)
        else:
            self.x = float(random.randint(ROAD_LEFT + 35, ROAD_RIGHT - self.width - 35))
        self.y = -100.0
        self.rect = pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update_rect(self):
        self.rect.topleft = (round(self.x), round(self.y))

    def draw(self, surface):
        r = self.rect
        if self.kind == "pothole":
            pygame.draw.ellipse(surface, (31, 32, 34), r)
            pygame.draw.ellipse(surface, (86, 78, 66), r, 5)
            pygame.draw.ellipse(surface, BLACK, r.inflate(-28, -20))
        elif self.kind == "oil":
            pygame.draw.ellipse(surface, (12, 13, 16), r)
            pygame.draw.ellipse(surface, (70, 75, 88), r.inflate(-15, -13), 4)
            pygame.draw.arc(surface, (125, 140, 165), r.inflate(-32, -26), 3.5, 5.8, 3)
        elif self.kind == "sheep":
            direction = 1 if self.vx >= 0 else -1
            pygame.draw.ellipse(surface, (232, 231, 214), (r.x + 8, r.y + 8, 54, 38))
            for wool_x, wool_y in ((18, 18), (31, 12), (44, 18), (27, 28), (43, 29)):
                pygame.draw.circle(surface, (250, 249, 235), (r.x + wool_x, r.y + wool_y), 13)
            head_x = r.right - 12 if direction > 0 else r.left + 12
            pygame.draw.ellipse(surface, (70, 63, 56), (head_x - 12, r.y + 15, 24, 26))
            pygame.draw.circle(surface, WHITE, (head_x + direction * 5, r.y + 23), 3)
            for leg_x in (r.x + 24, r.x + 50):
                pygame.draw.line(surface, (58, 52, 47), (leg_x, r.y + 39),
                                 (leg_x + direction * 4, r.bottom - 2), 5)
        else:
            pygame.draw.rect(surface, (230, 225, 205), r, border_radius=5)
            stripe_w = 25
            for x in range(r.left, r.right, stripe_w * 2):
                pygame.draw.polygon(surface, ORANGE, [(x, r.bottom), (x + stripe_w, r.bottom),
                                                       (x + stripe_w * 2, r.top), (x + stripe_w, r.top)])
            pygame.draw.rect(surface, BLACK, r, 4, border_radius=5)
            pygame.draw.line(surface, BLACK, (r.left + 18, r.bottom), (r.left + 4, r.bottom + 28), 8)
            pygame.draw.line(surface, BLACK, (r.right - 18, r.bottom), (r.right - 4, r.bottom + 28), 8)


def create_enemy():
    enemy_type = random.choices(["compact", "sedan", "truck"], weights=[40, 42, 18])[0]
    width = ENEMY_MODELS[enemy_type]["size"][0]
    x = random.randint(ROAD_LEFT + 28, ROAD_RIGHT - width - 28)
    return Car(x, -220, enemy_type=enemy_type)


def new_road_specks():
    return [[random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20), random.randint(0, GAME_HEIGHT),
             random.randint(2, 5)] for _ in range(48)]


def new_rain_drops():
    return [[random.randint(0, GAME_WIDTH), random.randint(-GAME_HEIGHT, GAME_HEIGHT),
             random.randint(650, 1050), random.randint(14, 28)] for _ in range(105)]


def draw_background(surface, stripe_offset, specks, environment="ORMAN", raining=False):
    if environment in ("YAZ", "ÇÖL"):
        surface.fill((184, 145, 78))
        for x in range(0, GAME_WIDTH, 44):
            pygame.draw.line(surface, (163, 123, 66), (x, 0), (x + 16, GAME_HEIGHT), 2)
    elif environment in ("ŞEHİR", "GECE", "FİNAL"):
        surface.fill((72, 76, 83))
        for x in range(0, GAME_WIDTH, 52):
            pygame.draw.line(surface, (102, 106, 112), (x, 0), (x, GAME_HEIGHT), 3)
    elif environment == "KIŞ":
        surface.fill((202, 218, 225))
        for x in range(0, GAME_WIDTH, 46):
            pygame.draw.line(surface, (178, 199, 211), (x, 0), (x + 8, GAME_HEIGHT), 2)
    elif environment == "SONBAHAR":
        surface.fill((116, 91, 49))
        for x in range(0, GAME_WIDTH, 42):
            pygame.draw.line(surface, (91, 70, 40), (x, 0), (x, GAME_HEIGHT), 2)
    else:
        surface.fill(GRASS)
        for x in range(0, GAME_WIDTH, 42):
            pygame.draw.line(surface, GRASS_DARK, (x, 0), (x, GAME_HEIGHT), 2)

    decoration_offset = int(stripe_offset * 0.38) % 210
    for y in range(-210 + decoration_offset, GAME_HEIGHT + 210, 210):
        if environment == "İLKBAHAR":
            for x in (38, 758):
                pygame.draw.rect(surface, (80, 57, 34), (x - 5, y + 30, 10, 34), border_radius=3)
                pygame.draw.circle(surface, (18, 73, 37), (x, y + 24), 30)
                pygame.draw.circle(surface, (32, 112, 53), (x - 10, y + 15), 19)
                pygame.draw.circle(surface, (244, 150, 190), (x + 12, y + 9), 7)
        elif environment in ("YAZ", "ÇÖL"):
            for x in (42, 755):
                pygame.draw.circle(surface, (116, 89, 62), (x, y + 44), 13)
                pygame.draw.line(surface, (47, 112, 57), (x, y + 38), (x, y - 8), 9)
                pygame.draw.line(surface, (47, 112, 57), (x, y + 10), (x - 15, y), 7)
        elif environment == "KIŞ":
            for x in (38, 758):
                pygame.draw.rect(surface, (75, 70, 66), (x - 5, y + 30, 10, 36), border_radius=3)
                pygame.draw.polygon(surface, (235, 244, 247),
                                    [(x, y - 18), (x - 28, y + 35), (x + 28, y + 35)])
        elif environment == "SONBAHAR":
            for x in (38, 758):
                pygame.draw.rect(surface, (76, 50, 30), (x - 5, y + 30, 10, 36), border_radius=3)
                pygame.draw.circle(surface, (166, 76, 29), (x, y + 18), 30)
                pygame.draw.circle(surface, (221, 142, 35), (x - 12, y + 9), 17)
        else:
            for x in (5, 730):
                pygame.draw.rect(surface, (47, 51, 60), (x, y - 15, 65, 130), border_radius=5)
                for wy in range(y, y + 90, 28):
                    for wx in range(x + 10, x + 55, 22):
                        pygame.draw.rect(surface, (238, 205, 96), (wx, wy, 10, 13), border_radius=2)

    # Yol gölgesi ve yol kenarı derinliği.
    pygame.draw.rect(surface, (20, 23, 25), (ROAD_LEFT - 18, 0, ROAD_WIDTH + 36, GAME_HEIGHT))
    pygame.draw.rect(surface, ASPHALT, (ROAD_LEFT, 0, ROAD_WIDTH, GAME_HEIGHT))

    # Asfalta hafif merkez aydınlığı vererek düz renk görünümünü azalt.
    # Doğrudan çizmek, her karede büyük saydam yüzey üretmekten daha hızlıdır.
    for band in range(10):
        inset = band * 22
        shade = 57 + band
        pygame.draw.rect(surface, (shade, shade + 2, shade + 4),
                         (ROAD_LEFT + inset, 0, ROAD_WIDTH - inset * 2, GAME_HEIGHT))

    # Asfalttaki sabit dokular yol ile birlikte yavaşça akar.
    for x, y, radius in specks:
        speck_color = (43, 47, 52) if raining else ASPHALT_DARK
        pygame.draw.circle(surface, speck_color, (x, int(y)), radius)
        if radius >= 4:
            pygame.draw.line(surface, (47, 48, 50), (x, int(y)), (x + 14, int(y) + 9), 2)

    # Sade otoyol omuz çizgileri; eski kırmızı-beyaz oyuncak pist görünümü kaldırıldı.
    pygame.draw.rect(surface, (218, 220, 216), (ROAD_LEFT, 0, 7, GAME_HEIGHT))
    pygame.draw.rect(surface, (218, 220, 216), (ROAD_RIGHT - 7, 0, 7, GAME_HEIGHT))
    edge_offset = int(stripe_offset * 0.55) % 150
    for y in range(-150 + edge_offset, GAME_HEIGHT + 150, 150):
        pygame.draw.rect(surface, (245, 188, 52), (ROAD_LEFT + 8, y, 5, 22), border_radius=2)
        pygame.draw.rect(surface, (245, 188, 52), (ROAD_RIGHT - 13, y, 5, 22), border_radius=2)

    # Daha seyrek ve daha yumuşak şerit animasyonu göz yorgunluğunu azaltır.
    period = 230
    lane_lines = (ROAD_LEFT + ROAD_WIDTH // 3, ROAD_LEFT + ROAD_WIDTH * 2 // 3)
    for y in range(int(stripe_offset) - period, GAME_HEIGHT + period, period):
        for lane_x in lane_lines:
            pygame.draw.rect(surface, (35, 36, 38), (lane_x - 8, y + 5, 16, 105), border_radius=5)
            pygame.draw.rect(surface, (215, 215, 205), (lane_x - 6, y, 12, 105), border_radius=5)

    # Yol kenarı reflektörleri.
    reflector_offset = int(stripe_offset * 0.42) % 180
    for y in range(-180 + reflector_offset, GAME_HEIGHT + 180, 180):
        for x in (ROAD_LEFT - 28, ROAD_RIGHT + 18):
            pygame.draw.rect(surface, (42, 45, 47), (x, y, 10, 34), border_radius=3)
            pygame.draw.rect(surface, (255, 210, 60), (x + 2, y + 5, 6, 10), border_radius=2)


def draw_panel(surface, rect, alpha=180):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (8, 10, 13, alpha), panel.get_rect(), border_radius=15)
    pygame.draw.rect(panel, (105, 122, 138, min(190, alpha + 10)), panel.get_rect(), 2, border_radius=12)
    surface.blit(panel, rect.topleft)


def draw_button(surface, rect, text, font, mouse_pos, selected=False, disabled=False, color=None):
    """Modern, fare üzerine gelince parlayan bir arayüz düğmesi çizer."""
    hovered = mouse_pos is not None and rect.collidepoint(mouse_pos) and not disabled
    if disabled:
        fill, border, text_color = (45, 47, 52), (85, 87, 92), (125, 128, 134)
    elif selected:
        fill, border, text_color = (25, 90, 112), CYAN, WHITE
    elif hovered:
        fill, border, text_color = (48, 74, 93), (125, 225, 245), WHITE
    else:
        fill, border, text_color = (28, 32, 39), (105, 112, 122), WHITE
    if color is not None:
        fill = color
        text_color = BLACK if sum(color) > 460 else WHITE
    if hovered:
        glow = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        pygame.draw.rect(glow, (80, 220, 245, 45), glow.get_rect(), border_radius=18)
        surface.blit(glow, (rect.x - 8, rect.y - 8))
    pygame.draw.rect(surface, fill, rect, border_radius=12)
    pygame.draw.rect(surface, border, rect, 3 if selected or hovered else 2, border_radius=12)
    label = font.render(text, True, text_color)
    surface.blit(label, label.get_rect(center=rect.center))


def draw_wrapped_text(surface, text, font, color, rect, line_spacing=8, center=False):
    words = text.split()
    lines, current = [], []
    for word in words:
        candidate = " ".join(current + [word])
        if current and font.size(candidate)[0] > rect.width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    y = rect.y
    for line in lines:
        rendered = font.render(line, True, color)
        x = rect.centerx - rendered.get_width() // 2 if center else rect.x
        surface.blit(rendered, (x, y))
        y += rendered.get_height() + line_spacing
    return y


def mouse_to_canvas(window, position):
    """Gerçek pencere koordinatını 800x1200 oyun koordinatına çevirir."""
    ww, wh = window.get_size()
    scale = min(ww / GAME_WIDTH, wh / GAME_HEIGHT)
    draw_w, draw_h = GAME_WIDTH * scale, GAME_HEIGHT * scale
    offset_x, offset_y = (ww - draw_w) / 2, (wh - draw_h) / 2
    x, y = position
    if not (offset_x <= x < offset_x + draw_w and offset_y <= y < offset_y + draw_h):
        return None
    return int((x - offset_x) / scale), int((y - offset_y) / scale)


def load_progress():
    """Kayıt yoksa veya bozuksa güvenli varsayılanlarla oyunu açar."""
    data = DEFAULT_SAVE.copy()
    loaded_version = 0
    try:
        loaded = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            loaded_version = int(loaded.get("version", 0))
            for key in data:
                if key in loaded and isinstance(loaded[key], int):
                    data[key] = loaded[key]
    except (OSError, ValueError, TypeError):
        pass

    if loaded_version < 3:
        # Eski prosedürel müzik yeni sürümde varsayılan olarak kapatılır.
        data["music_enabled"] = 0
        data["music_volume"] = min(data["music_volume"], 30)
    if loaded_version < 4:
        data["story_stage"] = min(data["mission_mask"].bit_count(), len(MISSION_DEFS))
    if loaded_version < 5:
        # Mevsim tabanlı yeni kariyer eski görevlerle eşleşmediği için hikâye baştan başlar.
        # Rekor, ödüller, araçlar ve bütün kullanıcı ayarları aynen korunur.
        data["story_stage"] = 0
        data["mission_mask"] = 0
    if loaded_version < 6:
        # 20 bölümlük yeni kariyer eski bölüm sırasıyla eşleşmez.
        data["story_stage"] = 0
        data["mission_mask"] = 0
    data["version"] = 6
    data["high_score"] = max(0, data["high_score"])
    data["rewards"] = max(0, data["rewards"])
    data["color_index"] = max(0, min(data["color_index"], len(CAR_COLORS) - 1))
    data["pattern_index"] = max(0, min(data["pattern_index"], len(PATTERNS) - 1))
    data["model_index"] = max(0, min(data["model_index"], len(PLAYER_MODELS) - 1))
    data["mission_mask"] = max(0, data["mission_mask"])
    data["story_stage"] = max(0, min(data["story_stage"], len(MISSION_DEFS)))
    data["jokers"] = max(0, data["jokers"])
    data["music_volume"] = max(0, min(data["music_volume"], 100))
    data["sfx_volume"] = max(0, min(data["sfx_volume"], 100))
    data["music_enabled"] = int(bool(data["music_enabled"]))
    data["sfx_enabled"] = int(bool(data["sfx_enabled"]))
    data["resolution_index"] = max(0, min(data["resolution_index"], len(WINDOW_SIZES) - 1))
    data["fullscreen"] = int(bool(data["fullscreen"]))
    if data["rewards"] < PLAYER_MODELS[data["model_index"]]["unlock"]:
        data["model_index"] = 0
    if not pattern_is_unlocked(data["pattern_index"], data["rewards"]):
        data["pattern_index"] = 0
    return data


def save_progress(profile):
    """Önce geçici dosyaya yazar; yarım kayıt oluşmasını önler."""
    temporary = SAVE_FILE.with_suffix(".tmp")
    try:
        SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        payload = {key: int(profile.get(key, value)) for key, value in DEFAULT_SAVE.items()}
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(SAVE_FILE)
        return True
    except (OSError, TypeError, ValueError) as error:
        print(f"Kayıt dosyası yazılamadı: {error}", file=sys.stderr)
        return False


def sync_profile(profile, state):
    player = state["player"]
    profile["rewards"] = state["rewards"]
    profile["model_index"] = player.model_index
    profile["color_index"] = player.color_index
    profile["pattern_index"] = player.pattern_index
    profile["high_score"] = max(profile["high_score"], state["score"])


def reset_game(total_rewards, model_index, color_index, pattern_index, start_in_garage=False):
    model_w = PLAYER_MODELS[model_index]["size"][0]
    return {
        "player": Car(GAME_WIDTH // 2 - model_w // 2, GAME_HEIGHT - 205,
                      model_index=model_index, color_index=color_index, pattern_index=pattern_index),
        "enemies": [], "pickups": [], "hazards": [], "specks": new_road_specks(),
        "rain_drops": new_rain_drops(), "raining": False, "weather_timer": random.uniform(12.0, 20.0),
        "environment": "İLKBAHAR", "night": False, "ice_drift": 0.0,
        "event_timer": 0.0, "next_event": random.uniform(16.0, 25.0),
        "event_banner": "", "event_banner_time": 0.0,
        "score": 0, "rewards": total_rewards, "fuel": 100.0, "distance": 0.0,
        "passed": 0, "collected": 0, "fuel_pickups": 0,
        "enemy_timer": 0.0, "pickup_timer": 0.0, "hazard_timer": 0.0, "animal_timer": 0.0,
        "next_pickup": random.uniform(3.2, 4.8), "next_hazard": random.uniform(5.0, 8.0),
        "next_animal": random.uniform(5.0, 8.0),
        "stripe_offset": 0.0, "shield_time": 0.0, "turbo_time": 0.0, "slow_time": 0.0,
        "game_over": False, "game_over_reason": "OYUN BİTTİ!", "garage": start_in_garage,
        "paused": False, "result_saved": False,
        "mission_completed_this_run": False, "chapter_complete": False,
        "message": "", "message_time": 0.0,
    }


def unlocked_models(rewards):
    return [i for i, model in enumerate(PLAYER_MODELS) if rewards >= model["unlock"]]


def select_model(state, index):
    if index in unlocked_models(state["rewards"]):
        state["player"].change_model(index)
        player = state["player"]
        player.x = max(ROAD_LEFT + 22, min(player.x, ROAD_RIGHT - player.width - 22))
        player.y = max(PLAYER_MIN_Y, min(player.y, GAME_HEIGHT - player.height))
        player.update_rect()
        state["message"] = f"ARAÇ: {PLAYER_MODELS[index]['name']}"
        changed = True
    else:
        state["message"] = f"KİLİTLİ: {PLAYER_MODELS[index]['unlock']} ÖDÜL GEREKİYOR"
        changed = False
    state["message_time"] = 1.6
    return changed


def select_pattern(state, index):
    if pattern_is_unlocked(index, state["rewards"]):
        state["player"].pattern_index = index
        state["message"] = f"DESEN: {PATTERNS[index]}"
        changed = True
    else:
        level = PATTERN_DEFS[index]["level"]
        state["message"] = f"KİLİTLİ: SEVİYE {level} GEREKİYOR"
        changed = False
    state["message_time"] = 1.8
    return changed


def cycle_pattern(state, direction):
    unlocked = [i for i in range(len(PATTERNS)) if pattern_is_unlocked(i, state["rewards"])]
    current = state["player"].pattern_index
    if current not in unlocked:
        current = unlocked[0]
    index = unlocked[(unlocked.index(current) + direction) % len(unlocked)]
    return select_pattern(state, index)


def make_window(fullscreen, resolution_index=1):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode(WINDOW_SIZES[resolution_index], pygame.RESIZABLE)


def mission_progress(state, mission):
    return state[mission["key"]]


def active_biome(profile, distance):
    """Kariyerde biyomu bölüme bağlar; finalde her kilometrede mevsim değişir."""
    stage = profile["story_stage"]
    if stage < len(MISSION_DEFS):
        biome = MISSION_DEFS[stage]["biome"]
        if biome != "FİNAL":
            return biome
        return ("İLKBAHAR", "YAZ", "SONBAHAR", "KIŞ", "ŞEHİR")[min(4, int(distance))]
    return ENVIRONMENTS[int(distance / 2.0) % len(ENVIRONMENTS)]


def check_missions(state, profile, sounds):
    """Kariyer hedefleri sırayla tamamlanır; her yarış hikâyeyi bir adım ilerletir."""
    if state["mission_completed_this_run"]:
        return False
    stage = profile["story_stage"]
    if stage >= len(MISSION_DEFS):
        return False
    mission = MISSION_DEFS[stage]
    if mission_progress(state, mission) < mission["target"]:
        return False

    profile["mission_mask"] |= 1 << stage
    profile["story_stage"] += 1
    profile["rewards"] += mission["reward"]
    profile["jokers"] += mission.get("jokers", 0)
    state["rewards"] = profile["rewards"]
    state["message"] = f"{mission['name']} TAMAM! +{mission['reward']} ÖDÜL"
    state["message_time"] = 4.0
    state["event_banner"] = "KARİYER İLERLEDİ"
    state["event_banner_time"] = 4.0
    state["mission_completed_this_run"] = True
    state["chapter_complete"] = True
    sounds.play("mission")
    save_progress(profile)
    return True


def use_joker(profile, state, sounds, message="JOKER SENİ KURTARDI!"):
    """Ölümcül bir hatada kalıcı jokeri otomatik tüketir ve sürüşü güvenli biçimde sürdürür."""
    if profile["jokers"] <= 0:
        return False
    profile["jokers"] -= 1
    state["shield_time"] = max(state["shield_time"], 2.5)
    state["message"] = f"{message} • {profile['jokers']} KALDI"
    state["message_time"] = 2.8
    sounds.play("shield")
    save_progress(profile)
    return True


def trigger_traffic_event(state, sounds):
    event = random.choice(("convoy", "roadblock", "reward_line", "oil_zone"))
    if event == "convoy":
        state["event_banner"] = "YOĞUN TRAFİK KONVOYU"
        for i in range(4):
            enemy = create_enemy()
            enemy.y = -180.0 - i * 235
            enemy.update_rect()
            state["enemies"].append(enemy)
    elif event == "roadblock":
        state["event_banner"] = "YOL ÇALIŞMASI: ŞERİT KAPALI"
        safe_lane = random.randrange(3)
        lane_x = [ROAD_LEFT + 45, ROAD_LEFT + ROAD_WIDTH // 3 + 35, ROAD_LEFT + ROAD_WIDTH * 2 // 3 + 25]
        for lane in range(3):
            if lane != safe_lane:
                barrier = RoadHazard("roadwork")
                barrier.x, barrier.y = float(lane_x[lane]), -120.0
                barrier.update_rect()
                state["hazards"].append(barrier)
    elif event == "reward_line":
        state["event_banner"] = "ALTIN ÖDÜL HATTI"
        for i in range(4):
            item = Pickup("reward")
            item.x = ROAD_LEFT + 125 + (i % 2) * 360
            item.y = -90.0 - i * 155
            item.update_rect()
            state["pickups"].append(item)
    else:
        state["event_banner"] = "YOLA YAĞ DÖKÜLDÜ"
        for i in range(3):
            oil = RoadHazard("oil")
            oil.y = -100.0 - i * 260
            oil.update_rect()
            state["hazards"].append(oil)
    state["event_banner_time"] = 3.2
    sounds.play("event")


def update_weather(state, dt, visual_speed):
    biome = state["environment"]
    if biome == "KIŞ":
        state["raining"] = False
        for drop in state["rain_drops"]:
            drop[0] -= 20 * dt
            drop[1] += (110 + visual_speed * 0.15) * dt
            if drop[1] > GAME_HEIGHT or drop[0] < -20:
                drop[0] = random.randint(0, GAME_WIDTH)
                drop[1] = random.randint(-250, -10)
        return
    if biome not in ("İLKBAHAR", "GECE"):
        state["raining"] = False
        return
    state["weather_timer"] -= dt
    if state["weather_timer"] <= 0:
        state["raining"] = not state["raining"]
        state["weather_timer"] = random.uniform(10.0, 16.0) if state["raining"] else random.uniform(18.0, 28.0)
        state["event_banner"] = "YAĞMUR BAŞLADI" if state["raining"] else "HAVA AÇILIYOR"
        state["event_banner_time"] = 2.4
    if state["raining"]:
        for drop in state["rain_drops"]:
            drop[0] -= 115 * dt
            drop[1] += (drop[2] + visual_speed * 0.35) * dt
            if drop[1] > GAME_HEIGHT or drop[0] < -30:
                drop[0] = random.randint(0, GAME_WIDTH + 120)
                drop[1] = random.randint(-300, -20)


def draw_atmosphere(surface, state):
    player = state["player"]
    biome = state["environment"]
    if state["night"] or biome == "GECE":
        darkness = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        darkness.fill((3, 8, 28, 168))
        # Farların önünde iki aydınlık görüş konisi bırakılır.
        left_light = [(player.rect.left + 13, player.rect.top + 8),
                      (max(ROAD_LEFT, player.rect.left - 125), 0), (player.rect.centerx, 0)]
        right_light = [(player.rect.right - 13, player.rect.top + 8),
                       (player.rect.centerx, 0), (min(ROAD_RIGHT, player.rect.right + 125), 0)]
        pygame.draw.polygon(darkness, (12, 15, 28, 42), left_light)
        pygame.draw.polygon(darkness, (12, 15, 28, 42), right_light)
        surface.blit(darkness, (0, 0))

    if state["raining"]:
        rain_layer = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        for x, y, _, length in state["rain_drops"]:
            pygame.draw.line(rain_layer, (170, 210, 235, 150), (int(x), int(y)),
                             (int(x - 7), int(y + length)), 2)
        surface.blit(rain_layer, (0, 0))

    if biome == "KIŞ":
        snow = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        for x, y, _, length in state["rain_drops"]:
            pygame.draw.circle(snow, (250, 253, 255, 205), (int(x), int(y)), max(2, length // 9))
        surface.blit(snow, (0, 0))
    elif biome == "SONBAHAR":
        fog = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        fog.fill((188, 194, 190, 72))
        for y, alpha in ((190, 48), (390, 38), (610, 28)):
            pygame.draw.ellipse(fog, (225, 229, 225, alpha), (-100, y, 1000, 220))
        surface.blit(fog, (0, 0))
    elif biome in ("YAZ", "ÇÖL"):
        heat = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(heat, (255, 174, 55, 28), (0, 0, GAME_WIDTH, GAME_HEIGHT))
        for y in range(170, GAME_HEIGHT, 190):
            pygame.draw.arc(heat, (255, 224, 155, 55), (ROAD_LEFT + 40, y, ROAD_WIDTH - 80, 65), 0, math.pi, 3)
        surface.blit(heat, (0, 0))


def present_scaled(window, canvas):
    ww, wh = window.get_size()
    scale = min(ww / GAME_WIDTH, wh / GAME_HEIGHT)
    dw, dh = max(1, int(GAME_WIDTH * scale)), max(1, int(GAME_HEIGHT * scale))
    scaled = pygame.transform.smoothscale(canvas, (dw, dh))
    window.fill(BLACK)
    window.blit(scaled, ((ww - dw) // 2, (wh - dh) // 2))
    pygame.display.flip()


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.display.set_caption("Araba Yarışı")
    profile = load_progress()
    fullscreen = bool(profile["fullscreen"])
    window = make_window(fullscreen, profile["resolution_index"])
    canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    load_player_sprites()
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("arial", 72, bold=True)
    font_score = pygame.font.SysFont("arial", 39, bold=True)
    font_info = pygame.font.SysFont("arial", 29, bold=True)
    font_small = pygame.font.SysFont("arial", 23, bold=True)
    font_item = pygame.font.SysFont("arial", 28, bold=True)

    sounds = SoundManager(profile)
    total_rewards = profile["rewards"]
    state = reset_game(total_rewards, profile["model_index"], profile["color_index"],
                       profile["pattern_index"], start_in_garage=False)
    ui_screen = "menu"
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        canvas_mouse = mouse_to_canvas(window, pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    profile["fullscreen"] = int(fullscreen)
                    window = make_window(fullscreen, profile["resolution_index"])
                    save_progress(profile)
                elif ui_screen != "play":
                    if event.key == pygame.K_ESCAPE:
                        if ui_screen == "menu":
                            running = False
                        else:
                            ui_screen = "menu"
                            sounds.play("click")
                    elif ui_screen == "menu" and event.key == pygame.K_RETURN:
                        ui_screen = "briefing"
                        sounds.play("click")
                    elif ui_screen == "briefing" and event.key == pygame.K_RETURN:
                        player = state["player"]
                        state = reset_game(total_rewards, player.model_index, player.color_index, player.pattern_index)
                        ui_screen = "play"
                        sounds.play("click")
                elif state["chapter_complete"]:
                    if event.key == pygame.K_RETURN:
                        ui_screen = "briefing"
                        sounds.play("click")
                    elif event.key == pygame.K_ESCAPE:
                        ui_screen = "menu"
                elif event.key == pygame.K_ESCAPE:
                    if state["paused"]:
                        state["paused"] = False
                    elif state["garage"]:
                        sync_profile(profile, state)
                        save_progress(profile)
                        state["garage"] = False
                        ui_screen = "menu"
                    elif state["game_over"]:
                        ui_screen = "menu"
                    else:
                        state["paused"] = True
                elif event.key == pygame.K_p and not state["game_over"] and not state["garage"]:
                    state["paused"] = not state["paused"]
                elif state["game_over"] and event.key == pygame.K_r:
                    player = state["player"]
                    state = reset_game(total_rewards, player.model_index, player.color_index, player.pattern_index)
                    sounds.play("click")
                elif not state["game_over"] and not state["paused"]:
                    player = state["player"]
                    if event.key == pygame.K_g:
                        state["garage"] = not state["garage"]
                    elif state["garage"]:
                        if event.key == pygame.K_RETURN:
                            state["garage"] = False
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            player.color_index = (player.color_index - 1) % len(CAR_COLORS)
                            sync_profile(profile, state)
                            save_progress(profile)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            player.color_index = (player.color_index + 1) % len(CAR_COLORS)
                            sync_profile(profile, state)
                            save_progress(profile)
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            if cycle_pattern(state, -1):
                                sync_profile(profile, state)
                                save_progress(profile)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if cycle_pattern(state, 1):
                                sync_profile(profile, state)
                                save_progress(profile)
                        elif event.key in (pygame.K_1, pygame.K_KP1):
                            if select_model(state, 0):
                                sync_profile(profile, state)
                                save_progress(profile)
                        elif event.key in (pygame.K_2, pygame.K_KP2):
                            if select_model(state, 1):
                                sync_profile(profile, state)
                                save_progress(profile)
                        elif event.key in (pygame.K_3, pygame.K_KP3):
                            if select_model(state, 2):
                                sync_profile(profile, state)
                                save_progress(profile)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = mouse_to_canvas(window, event.pos)
                if click is None:
                    continue
                if ui_screen == "menu":
                    if MENU_PLAY_RECT.collidepoint(click):
                        ui_screen = "briefing"
                    elif MENU_GARAGE_RECT.collidepoint(click):
                        player = state["player"]
                        state = reset_game(total_rewards, player.model_index, player.color_index,
                                           player.pattern_index, start_in_garage=True)
                        ui_screen = "play"
                    elif MENU_MISSIONS_RECT.collidepoint(click):
                        ui_screen = "missions"
                    elif MENU_SETTINGS_RECT.collidepoint(click):
                        ui_screen = "settings"
                    elif MENU_EXIT_RECT.collidepoint(click):
                        running = False
                    else:
                        continue
                    sounds.play("click")
                    continue
                if ui_screen == "briefing":
                    if BRIEFING_START_RECT.collidepoint(click):
                        player = state["player"]
                        state = reset_game(total_rewards, player.model_index, player.color_index, player.pattern_index)
                        ui_screen = "play"
                        sounds.play("click")
                    elif BRIEFING_BACK_RECT.collidepoint(click):
                        ui_screen = "menu"
                        sounds.play("click")
                    continue
                if ui_screen == "missions":
                    if BACK_RECT.collidepoint(click):
                        ui_screen = "menu"
                        sounds.play("click")
                    continue
                if ui_screen == "settings":
                    changed = True
                    if BACK_RECT.collidepoint(click):
                        ui_screen = "menu"
                    elif SETTINGS_MUSIC_MINUS.collidepoint(click):
                        profile["music_volume"] = max(0, profile["music_volume"] - 10)
                    elif SETTINGS_MUSIC_PLUS.collidepoint(click):
                        profile["music_volume"] = min(100, profile["music_volume"] + 10)
                    elif SETTINGS_SFX_MINUS.collidepoint(click):
                        profile["sfx_volume"] = max(0, profile["sfx_volume"] - 10)
                    elif SETTINGS_SFX_PLUS.collidepoint(click):
                        profile["sfx_volume"] = min(100, profile["sfx_volume"] + 10)
                    elif SETTINGS_MUSIC_TOGGLE.collidepoint(click):
                        profile["music_enabled"] = 1 - profile["music_enabled"]
                    elif SETTINGS_SFX_TOGGLE.collidepoint(click):
                        profile["sfx_enabled"] = 1 - profile["sfx_enabled"]
                    elif SETTINGS_FULLSCREEN.collidepoint(click):
                        fullscreen = not fullscreen
                        profile["fullscreen"] = int(fullscreen)
                        window = make_window(fullscreen, profile["resolution_index"])
                    else:
                        changed = False
                        for i, rect in enumerate(RESOLUTION_RECTS):
                            if rect.collidepoint(click):
                                profile["resolution_index"] = i
                                if not fullscreen:
                                    window = make_window(False, i)
                                changed = True
                                break
                    if changed:
                        sounds.apply_settings()
                        sounds.play("click")
                        save_progress(profile)
                    continue

                player = state["player"]
                if state["chapter_complete"]:
                    if CHAPTER_CONTINUE_RECT.collidepoint(click):
                        ui_screen = "briefing"
                        sounds.play("click")
                elif state["paused"]:
                    if PAUSE_CONTINUE_RECT.collidepoint(click):
                        state["paused"] = False
                    elif PAUSE_GARAGE_RECT.collidepoint(click):
                        state["paused"] = False
                        state["garage"] = True
                    elif PAUSE_EXIT_RECT.collidepoint(click):
                        sync_profile(profile, state)
                        save_progress(profile)
                        state["paused"] = False
                        ui_screen = "menu"
                elif state["game_over"] and RESTART_RECT.collidepoint(click):
                    state = reset_game(total_rewards, player.model_index, player.color_index, player.pattern_index)
                elif state["garage"] and not state["game_over"]:
                    if GARAGE_START_RECT.collidepoint(click):
                        state["garage"] = False
                    elif GARAGE_BACK_RECT.collidepoint(click):
                        sync_profile(profile, state)
                        save_progress(profile)
                        state["garage"] = False
                        ui_screen = "menu"
                    else:
                        for i, rect in enumerate(GARAGE_COLOR_RECTS):
                            if rect.collidepoint(click):
                                player.color_index = i
                                sync_profile(profile, state)
                                save_progress(profile)
                                break
                        for i, rect in enumerate(GARAGE_PATTERN_RECTS):
                            if rect.collidepoint(click):
                                if select_pattern(state, i):
                                    sync_profile(profile, state)
                                    save_progress(profile)
                                break
                        for i, rect in enumerate(GARAGE_MODEL_RECTS):
                            if rect.collidepoint(click):
                                if select_model(state, i):
                                    sync_profile(profile, state)
                                    save_progress(profile)
                                break
                elif not state["game_over"]:
                    if HUD_GARAGE_RECT.collidepoint(click):
                        state["garage"] = True
                    elif HUD_PAUSE_RECT.collidepoint(click):
                        state["paused"] = True
                sounds.play("click")

        if (ui_screen == "play" and not state["game_over"] and not state["garage"]
                and not state["paused"] and not state["chapter_complete"]):
            state["shield_time"] = max(0.0, state["shield_time"] - dt)
            state["turbo_time"] = max(0.0, state["turbo_time"] - dt)
            state["slow_time"] = max(0.0, state["slow_time"] - dt)
            state["message_time"] = max(0.0, state["message_time"] - dt)
            state["event_banner_time"] = max(0.0, state["event_banner_time"] - dt)

            # Kariyer ilk dört bölümde öğretir, ardından zorluk bölüm bölüm yumuşakça artar.
            career_stage = min(profile["story_stage"], len(MISSION_DEFS) - 1)
            road_speed = min(290.0 + career_stage * 4.5 + state["score"] * 0.075, 455.0)
            enemy_speed = road_speed + 34.0 + career_stage * 0.8
            spawn_interval = max(0.78, 1.68 - career_stage * 0.026 - state["score"] * 0.00035)
            if state["turbo_time"] > 0:
                road_speed *= 1.12

            player = state["player"]
            player_speed = PLAYER_MODELS[player.model_index]["speed"]
            if state["turbo_time"] > 0:
                player_speed *= 1.25
            if state["slow_time"] > 0:
                player_speed *= 0.58
            if state["raining"]:
                player_speed *= 0.90

            keys = pygame.key.get_pressed()
            dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(keys[pygame.K_w] or keys[pygame.K_UP])
            if dx and dy:
                dx *= math.sqrt(0.5)
                dy *= math.sqrt(0.5)
            if state["environment"] == "KIŞ":
                state["ice_drift"] += dx * 520.0 * dt
                state["ice_drift"] *= max(0.0, 1.0 - 1.15 * dt)
                player.x += (dx * player_speed * 0.32 + state["ice_drift"]) * dt
            else:
                state["ice_drift"] *= max(0.0, 1.0 - 5.0 * dt)
                player.x += dx * player_speed * dt
            player.y += dy * player_speed * dt
            player.x = max(ROAD_LEFT + 22, min(player.x, ROAD_RIGHT - player.width - 22))
            # Araç ekranın alt bölümünde kalır; ön tarafta daima geniş görüş alanı bulunur.
            player.y = max(PLAYER_MIN_Y, min(player.y, GAME_HEIGHT - player.height))
            player.update_rect()

            state["distance"] += road_speed * dt / 24000.0
            # Bir depo yaklaşık 25-35 saniye dayanır; bidon kovalamak artık önemlidir.
            fuel_burn = 2.15 + road_speed / 950.0
            if career_stage == 0:
                fuel_burn *= 0.55
            elif career_stage < 4:
                fuel_burn *= 0.78
            if state["environment"] in ("YAZ", "ÇÖL"):
                fuel_burn *= 1.32
            if state["turbo_time"] > 0:
                fuel_burn *= 1.22
            state["fuel"] = max(0.0, state["fuel"] - dt * fuel_burn)
            if state["fuel"] <= 0:
                if use_joker(profile, state, sounds, "JOKER ACİL YAKIT VERDİ!"):
                    state["fuel"] = 35.0
                else:
                    state["game_over"] = True
                    state["game_over_reason"] = "BENZİN BİTTİ!"

            visual_speed = road_speed * 0.62
            state["stripe_offset"] = (state["stripe_offset"] + visual_speed * dt) % 230
            state["environment"] = active_biome(profile, state["distance"])
            state["night"] = state["environment"] == "GECE"
            if career_stage == 0:
                state["raining"] = False
            else:
                update_weather(state, dt, visual_speed)

            state["event_timer"] += dt
            if career_stage >= 3 and state["event_timer"] >= state["next_event"]:
                state["event_timer"] = 0.0
                state["next_event"] = random.uniform(20.0, 31.0)
                trigger_traffic_event(state, sounds)

            for speck in state["specks"]:
                speck[1] += visual_speed * dt
                if speck[1] > GAME_HEIGHT:
                    speck[0] = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
                    speck[1] = 0

            state["enemy_timer"] += dt
            state["pickup_timer"] += dt
            state["hazard_timer"] += dt
            state["animal_timer"] += dt
            if state["enemy_timer"] >= spawn_interval:
                state["enemy_timer"] = 0.0
                state["enemies"].append(create_enemy())
            if state["pickup_timer"] >= state["next_pickup"]:
                state["pickup_timer"] = 0.0
                state["next_pickup"] = random.uniform(2.6, 3.8) if career_stage < 4 else random.uniform(3.2, 4.8)
                weights = [58, 20, 14, 8] if career_stage < 4 else [48, 18, 19, 15]
                kind = random.choices(["reward", "fuel", "shield", "turbo"], weights=weights)[0]
                state["pickups"].append(Pickup(kind))
            if career_stage >= 2 and state["hazard_timer"] >= state["next_hazard"]:
                state["hazard_timer"] = 0.0
                state["next_hazard"] = random.uniform(5.2, 8.2)
                state["hazards"].append(RoadHazard(random.choice(["pothole", "pothole", "roadwork"])))
            if (career_stage >= 2 and state["environment"] == "İLKBAHAR"
                    and state["animal_timer"] >= state["next_animal"]):
                state["animal_timer"] = 0.0
                state["next_animal"] = random.uniform(6.0, 10.0)
                sheep = RoadHazard("sheep")
                sheep.y = random.uniform(-80.0, 220.0)
                sheep.update_rect()
                state["hazards"].append(sheep)
                state["event_banner"] = "DİKKAT: YOLA KOYUN ÇIKTI!"
                state["event_banner_time"] = 2.0

            player_hitbox = player.rect.inflate(-20, -20)
            for enemy in state["enemies"][:]:
                if state["game_over"]:
                    break
                enemy.y += enemy_speed * dt
                enemy.update_rect()
                if enemy.rect.top > GAME_HEIGHT:
                    state["enemies"].remove(enemy)
                    state["score"] += 10
                    state["passed"] += 1
                elif player_hitbox.colliderect(enemy.rect.inflate(-16, -16)):
                    if state["shield_time"] > 0:
                        state["shield_time"] = 0.0
                        state["enemies"].remove(enemy)
                        state["message"], state["message_time"] = "KALKAN KURTARDI!", 1.5
                    elif use_joker(profile, state, sounds):
                        state["enemies"].remove(enemy)
                    else:
                        state["game_over"] = True
                        state["game_over_reason"] = "OYUN BİTTİ!"
                        sounds.play("crash")
                        break

            for hazard in state["hazards"][:]:
                if state["game_over"]:
                    break
                hazard.y += visual_speed * dt
                hazard.x += hazard.vx * dt
                hazard.update_rect()
                if (hazard.rect.top > GAME_HEIGHT or
                        (hazard.kind == "sheep" and (hazard.rect.right < ROAD_LEFT - 90 or hazard.rect.left > ROAD_RIGHT + 90))):
                    state["hazards"].remove(hazard)
                elif player_hitbox.colliderect(hazard.rect):
                    state["hazards"].remove(hazard)
                    if hazard.kind == "sheep":
                        state["slow_time"] = 2.5
                        state["score"] = max(0, state["score"] - 25)
                        state["message"] = "KOYUN! SERT FREN: -25 PUAN"
                        state["message_time"] = 2.2
                    elif hazard.kind == "pothole":
                        state["slow_time"] = 1.7
                        state["fuel"] = max(0.0, state["fuel"] - 6.0)
                        state["message"] = "ÇUKUR! ARAÇ YAVAŞLADI"
                        state["message_time"] = 1.7
                    elif hazard.kind == "oil":
                        state["slow_time"] = 2.2
                        player.x += random.choice((-1, 1)) * 85
                        player.x = max(ROAD_LEFT + 22, min(player.x, ROAD_RIGHT - player.width - 22))
                        player.update_rect()
                        state["message"] = "YAĞ LEKESİ! KONTROL ZORLAŞTI"
                        state["message_time"] = 2.0
                    elif state["shield_time"] > 0:
                        state["shield_time"] = 0.0
                        state["message"], state["message_time"] = "KALKAN BARİYERİ KIRDI!", 1.7
                    elif use_joker(profile, state, sounds):
                        pass
                    else:
                        state["game_over"] = True
                        state["game_over_reason"] = "YOL ÇALIŞMASINA ÇARPTIN!"
                        sounds.play("crash")

            for item in state["pickups"][:]:
                if state["game_over"]:
                    break
                item.y += visual_speed * 0.9 * dt
                item.update_rect()
                if item.rect.top > GAME_HEIGHT:
                    state["pickups"].remove(item)
                elif player_hitbox.colliderect(item.rect):
                    state["pickups"].remove(item)
                    if item.kind == "reward":
                        total_rewards += 1
                        state["rewards"] = total_rewards
                        state["collected"] += 1
                        state["score"] += 25
                        state["message"] = "+25 PUAN / ÖDÜL!"
                        sounds.play("reward")
                        sync_profile(profile, state)
                        save_progress(profile)
                    elif item.kind == "fuel":
                        state["fuel"] = 100.0
                        state["fuel_pickups"] += 1
                        state["message"] = "DEPO DOLDU!"
                        sounds.play("fuel")
                    elif item.kind == "shield":
                        state["shield_time"] = 7.0
                        state["message"] = "7 SANİYE KALKAN!"
                        sounds.play("shield")
                    else:
                        state["turbo_time"] = 5.0
                        state["message"] = "5 SANİYE TURBO!"
                        sounds.play("turbo")
                    state["message_time"] = 1.6

            if check_missions(state, profile, sounds):
                total_rewards = profile["rewards"]

        if state["game_over"] and not state["result_saved"]:
            sync_profile(profile, state)
            save_progress(profile)
            state["result_saved"] = True

        draw_background(canvas, state["stripe_offset"], state["specks"],
                        state["environment"], state["raining"])
        for hazard in state["hazards"]:
            hazard.draw(canvas)
        for item in state["pickups"]:
            item.draw(canvas, font_item)
        for enemy in state["enemies"]:
            enemy.draw(canvas)
        state["player"].draw(canvas, state["shield_time"] > 0)
        draw_atmosphere(canvas, state)

        draw_panel(canvas, pygame.Rect(14, 14, 282, 125))
        canvas.blit(font_score.render(f"SKOR {state['score']}", True, WHITE), (28, 19))
        current_record = max(profile["high_score"], state["score"])
        canvas.blit(font_small.render(f"REKOR {current_record}", True, CYAN), (28, 62))
        canvas.blit(font_small.render(f"ALTIN {state['rewards']} • J {profile['jokers']}", True, YELLOW), (135, 62))
        canvas.blit(font_small.render(f"MESAFE {state['distance']:.2f} km", True, WHITE), (28, 94))

        draw_button(canvas, HUD_PAUSE_RECT, "II", font_small, canvas_mouse,
                    selected=state["paused"])

        draw_panel(canvas, pygame.Rect(470, 14, 315, 125))
        canvas.blit(font_info.render("BENZİN", True, WHITE), (486, 20))
        if state["fuel"] < 25 and (pygame.time.get_ticks() // 350) % 2 == 0:
            canvas.blit(font_small.render("AZ!", True, (255, 80, 70)), (720, 27))
        bar = pygame.Rect(486, 54, 279, 25)
        pygame.draw.rect(canvas, (38, 39, 42), bar, border_radius=7)
        fuel_color = (65, 210, 90) if state["fuel"] > 35 else ((245, 175, 35) if state["fuel"] > 15 else RED)
        fill = bar.copy()
        fill.width = int(bar.width * state["fuel"] / 100)
        pygame.draw.rect(canvas, fuel_color, fill, border_radius=7)
        pygame.draw.rect(canvas, WHITE, bar, 3, border_radius=7)
        canvas.blit(font_small.render(f"%{state['fuel']:.0f}", True, WHITE), (486, 95))
        draw_button(canvas, HUD_GARAGE_RECT, "GARAJ", font_small, canvas_mouse,
                    selected=state["garage"])

        if ui_screen == "play" and not state["garage"]:
            if state["environment"] == "KIŞ":
                weather_name = "KAR / BUZ"
            elif state["environment"] == "SONBAHAR":
                weather_name = "SİS"
            elif state["environment"] in ("YAZ", "ÇÖL"):
                weather_name = "SICAK"
            else:
                weather_name = "YAĞMUR" if state["raining"] else "AÇIK"
            time_name = "GECE" if state["night"] else "GÜNDÜZ"
            badge = pygame.Rect(16, 1122, 390, 54)
            draw_panel(canvas, badge, 165)
            canvas.blit(font_small.render(f"{state['environment']} • {time_name} • {weather_name}", True, WHITE),
                        (29, 1138))
            stage = profile["story_stage"]
            if stage < len(MISSION_DEFS) and not state["chapter_complete"]:
                mission = MISSION_DEFS[stage]
                progress = min(mission_progress(state, mission), mission["target"])
                ratio = progress / mission["target"]
                goal_panel = pygame.Rect(170, 152, 460, 64)
                draw_panel(canvas, goal_panel, 165)
                goal_bar = pygame.Rect(190, 188, 420, 13)
                pygame.draw.rect(canvas, (35, 39, 45), goal_bar, border_radius=6)
                filled = goal_bar.copy()
                filled.width = int(goal_bar.width * ratio)
                pygame.draw.rect(canvas, CYAN, filled, border_radius=6)
                goal_text = font_small.render(f"{mission['chapter']} • {mission['description']}", True, WHITE)
                canvas.blit(goal_text, goal_text.get_rect(center=(400, 172)))

        if ui_screen == "play" and state["message_time"] > 0 and not state["garage"] and not state["paused"]:
            label = font_info.render(state["message"], True, YELLOW)
            draw_panel(canvas, pygame.Rect(145, 220, 510, 64), 170)
            canvas.blit(label, label.get_rect(center=(GAME_WIDTH // 2, 252)))

        if ui_screen == "play" and state["event_banner_time"] > 0 and not state["garage"] and not state["paused"]:
            label = font_info.render(state["event_banner"], True, (255, 165, 55))
            draw_panel(canvas, pygame.Rect(130, 305, 540, 68), 190)
            canvas.blit(label, label.get_rect(center=(GAME_WIDTH // 2, 339)))

        if ui_screen == "menu":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 8, 15, 226))
            canvas.blit(overlay, (0, 0))
            pygame.draw.circle(canvas, (12, 72, 91), (400, 205), 155)
            pygame.draw.circle(canvas, (40, 205, 225), (400, 205), 155, 4)
            pygame.draw.circle(canvas, (245, 198, 45), (400, 205), 125, 2)
            title = font_big.render("CAR RALLING", True, WHITE)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 178)))
            subtitle = font_info.render("SONSUZ YOL", True, CYAN)
            canvas.blit(subtitle, subtitle.get_rect(center=(GAME_WIDTH // 2, 250)))
            stats = font_small.render(
                f"REKOR {profile['high_score']}  •  ALTIN {profile['rewards']}  •  JOKER {profile['jokers']}  •  KARİYER {profile['story_stage']}/{len(MISSION_DEFS)}",
                True, (205, 214, 222))
            canvas.blit(stats, stats.get_rect(center=(GAME_WIDTH // 2, 355)))
            play_text = "SERBEST SÜRÜŞ" if profile["story_stage"] >= len(MISSION_DEFS) else "KARİYERE DEVAM"
            draw_button(canvas, MENU_PLAY_RECT, play_text, font_info, canvas_mouse, selected=True)
            draw_button(canvas, MENU_GARAGE_RECT, "GARAJ", font_info, canvas_mouse)
            draw_button(canvas, MENU_MISSIONS_RECT, "HİKÂYE VE KARİYER", font_info, canvas_mouse)
            draw_button(canvas, MENU_SETTINGS_RECT, "AYARLAR", font_info, canvas_mouse)
            draw_button(canvas, MENU_EXIT_RECT, "OYUNDAN ÇIK", font_info, canvas_mouse)
            footer = font_small.render("WASD / Ok tuşları  •  P: Duraklat  •  F11: Tam ekran", True, (155, 166, 177))
            canvas.blit(footer, footer.get_rect(center=(GAME_WIDTH // 2, 1100)))

        elif ui_screen == "briefing":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((4, 8, 14, 240))
            canvas.blit(overlay, (0, 0))
            stage = profile["story_stage"]
            if stage < len(MISSION_DEFS):
                mission = MISSION_DEFS[stage]
                chapter = font_info.render(mission["chapter"], True, CYAN)
                canvas.blit(chapter, chapter.get_rect(center=(GAME_WIDTH // 2, 105)))
                title = font_big.render(mission["name"], True, YELLOW)
                canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 180)))
                draw_panel(canvas, pygame.Rect(80, 280, 640, 390), 220)
                speaker = font_info.render(mission["speaker"], True, CYAN)
                canvas.blit(speaker, (115, 320))
                draw_wrapped_text(canvas, mission["dialogue"], font_info, WHITE,
                                  pygame.Rect(115, 385, 570, 150), line_spacing=12)
                pygame.draw.line(canvas, (80, 105, 125), (115, 545), (685, 545), 2)
                objective_title = font_small.render("YARIŞ HEDEFİ", True, (165, 175, 185))
                canvas.blit(objective_title, (115, 575))
                objective = font_info.render(mission["description"], True, YELLOW)
                canvas.blit(objective, (115, 610))
                biome = font_small.render(f"BİYOM: {mission['biome']}  •  {mission['effect']}", True, WHITE)
                canvas.blit(biome, biome.get_rect(center=(GAME_WIDTH // 2, 690)))
                reward = font_small.render(f"+{mission['reward']} ALTIN  •  {mission['special']}  •  {stage + 1}/{len(MISSION_DEFS)}",
                                           True, (90, 225, 135))
                canvas.blit(reward, reward.get_rect(center=(GAME_WIDTH // 2, 755)))
                start_text = "HİKÂYE YARIŞINI BAŞLAT"
            else:
                title = font_big.render("ŞAMPİYON", True, YELLOW)
                canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 175)))
                draw_panel(canvas, pygame.Rect(80, 300, 640, 350), 220)
                ending = ("Garaj kurtarıldı, Kuzgun yenildi ve şehrin gece rotası artık senin. "
                          "Kariyer tamamlandı; rekor kırmak ve bütün araçları açmak için serbest sürebilirsin.")
                draw_wrapped_text(canvas, ending, font_info, WHITE,
                                  pygame.Rect(120, 370, 560, 200), line_spacing=14, center=True)
                start_text = "SERBEST SÜRÜŞE BAŞLA"
            draw_button(canvas, BRIEFING_START_RECT, start_text, font_info, canvas_mouse, selected=True)
            draw_button(canvas, BRIEFING_BACK_RECT, "← ANA MENÜ", font_small, canvas_mouse)

        elif ui_screen == "settings":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((4, 8, 14, 238))
            canvas.blit(overlay, (0, 0))
            title = font_big.render("AYARLAR", True, CYAN)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 120)))
            subtitle = font_small.render("Değişiklikler otomatik kaydedilir", True, (170, 182, 193))
            canvas.blit(subtitle, subtitle.get_rect(center=(GAME_WIDTH // 2, 185)))

            canvas.blit(font_info.render("MÜZİK SESİ", True, WHITE), (300, 335))
            draw_button(canvas, SETTINGS_MUSIC_MINUS, "−", font_score, canvas_mouse)
            draw_button(canvas, SETTINGS_MUSIC_PLUS, "+", font_score, canvas_mouse)
            music_value = font_score.render(f"%{profile['music_volume']}", True, YELLOW)
            canvas.blit(music_value, music_value.get_rect(center=(GAME_WIDTH // 2, 430)))

            canvas.blit(font_info.render("EFEKT SESİ", True, WHITE), (300, 465))
            draw_button(canvas, SETTINGS_SFX_MINUS, "−", font_score, canvas_mouse)
            draw_button(canvas, SETTINGS_SFX_PLUS, "+", font_score, canvas_mouse)
            sfx_value = font_score.render(f"%{profile['sfx_volume']}", True, YELLOW)
            canvas.blit(sfx_value, sfx_value.get_rect(center=(GAME_WIDTH // 2, 530)))

            music_status = "MÜZİK: AÇIK" if profile["music_enabled"] else "MÜZİK: KAPALI"
            sfx_status = "EFEKTLER: AÇIK" if profile["sfx_enabled"] else "EFEKTLER: KAPALI"
            screen_status = "TAM EKRAN: AÇIK" if fullscreen else "TAM EKRAN: KAPALI"
            draw_button(canvas, SETTINGS_MUSIC_TOGGLE, music_status, font_info, canvas_mouse,
                        selected=bool(profile["music_enabled"]))
            draw_button(canvas, SETTINGS_SFX_TOGGLE, sfx_status, font_info, canvas_mouse,
                        selected=bool(profile["sfx_enabled"]))
            draw_button(canvas, SETTINGS_FULLSCREEN, screen_status, font_info, canvas_mouse,
                        selected=fullscreen)

            canvas.blit(font_small.render("PENCERE ÇÖZÜNÜRLÜĞÜ", True, WHITE), (265, 842))
            for i, rect in enumerate(RESOLUTION_RECTS):
                size = WINDOW_SIZES[i]
                draw_button(canvas, rect, f"{size[0]}×{size[1]}", font_small, canvas_mouse,
                            selected=i == profile["resolution_index"])
            draw_button(canvas, BACK_RECT, "← GERİ", font_small, canvas_mouse)

        elif ui_screen == "missions":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((4, 8, 14, 238))
            canvas.blit(overlay, (0, 0))
            title = font_big.render("KARİYER", True, YELLOW)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 120)))
            intro = font_small.render("Aile garajını kurtar • Kuzgun'u yen • Şehrin şampiyonu ol", True, (180, 190, 200))
            canvas.blit(intro, intro.get_rect(center=(GAME_WIDTH // 2, 190)))
            stage = profile["story_stage"]
            draw_panel(canvas, pygame.Rect(75, 235, 650, 250), 220)
            if stage < len(MISSION_DEFS):
                active = MISSION_DEFS[stage]
                canvas.blit(font_small.render(f"AKTİF • {active['chapter']}", True, CYAN), (105, 265))
                canvas.blit(font_info.render(active["name"], True, YELLOW), (105, 305))
                draw_wrapped_text(canvas, active["dialogue"], font_small, WHITE,
                                  pygame.Rect(105, 350, 590, 70), line_spacing=6)
                canvas.blit(font_small.render(f"HEDEF: {active['description']}   •   +{active['reward']} ALTIN",
                                              True, (90, 225, 135)), (105, 425))
                canvas.blit(font_small.render(f"ÖZEL: {active['special']}", True, YELLOW), (105, 455))
            else:
                canvas.blit(font_info.render("KARİYER TAMAMLANDI", True, (80, 230, 130)), (105, 285))
                draw_wrapped_text(canvas, "Garaj kurtarıldı ve şehrin gece şampiyonu oldun.", font_small, WHITE,
                                  pygame.Rect(105, 345, 590, 80), center=True)

            canvas.blit(font_small.render("HİKÂYE YOLU", True, (165, 175, 185)), (95, 525))
            visible_start = max(0, min(stage - 4, len(MISSION_DEFS) - 10))
            visible_end = min(len(MISSION_DEFS), visible_start + 10)
            for row, i in enumerate(range(visible_start, visible_end)):
                mission = MISSION_DEFS[i]
                y = 565 + row * 45
                completed = i < stage
                active_now = i == stage
                color = (75, 225, 125) if completed else (YELLOW if active_now else (100, 108, 118))
                marker = "✓" if completed else ("▶" if active_now else "•")
                canvas.blit(font_small.render(f"{marker}  {i + 1}. {mission['name']}", True, color), (110, y))
                reward = font_small.render(f"+{mission['reward']}", True, color)
                canvas.blit(reward, (650, y))
            draw_button(canvas, BACK_RECT, "← GERİ", font_small, canvas_mouse)

        if state["garage"] and ui_screen == "play":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((4, 7, 12, 232))
            canvas.blit(overlay, (0, 0))
            # Üst bölümde dekoratif çizgiler ve başlık.
            pygame.draw.line(canvas, (25, 115, 145), (85, 185), (715, 185), 3)
            pygame.draw.line(canvas, CYAN, (255, 185), (545, 185), 3)
            title = font_big.render("GARAJ", True, YELLOW)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 110)))

            preview = state["player"]
            old_pos = preview.rect.topleft
            # Araç sergileme platformu.
            pygame.draw.ellipse(canvas, (10, 12, 16), (245, 230, 310, 245))
            pygame.draw.ellipse(canvas, (54, 65, 73), (245, 230, 310, 245), 4)
            pygame.draw.ellipse(canvas, (35, 170, 195), (275, 270, 250, 165), 2)
            preview.rect.center = (GAME_WIDTH // 2, 345)
            preview.draw(canvas, False)
            preview.rect.topleft = old_pos

            model = PLAYER_MODELS[preview.model_index]
            model_label = font_score.render(model["name"], True, WHITE)
            canvas.blit(model_label, model_label.get_rect(center=(GAME_WIDTH // 2, 485)))

            section = font_small.render("RENK SEÇ", True, (180, 190, 200))
            canvas.blit(section, (120, 525))
            for i, rect in enumerate(GARAGE_COLOR_RECTS):
                draw_button(canvas, rect, "✓" if i == preview.color_index else "", font_info,
                            canvas_mouse, selected=i == preview.color_index, color=CAR_COLORS[i])

            section = font_small.render("DESEN SEÇ", True, (180, 190, 200))
            current_level = player_level(state["rewards"])
            level_label = font_small.render(f"SEVİYE {current_level}", True, YELLOW)
            canvas.blit(section, (82, 618))
            canvas.blit(level_label, (575, 618))
            for i, rect in enumerate(GARAGE_PATTERN_RECTS):
                unlocked = pattern_is_unlocked(i, state["rewards"])
                text = PATTERNS[i] if unlocked else f"{PATTERNS[i]} L{PATTERN_DEFS[i]['level']}"
                draw_button(canvas, rect, text, font_small, canvas_mouse,
                            selected=i == preview.pattern_index, disabled=not unlocked)

            for i, item in enumerate(PLAYER_MODELS):
                unlocked = state["rewards"] >= item["unlock"]
                status = "AÇIK" if unlocked else f"KİLİTLİ • {item['unlock']} ödül"
                draw_button(canvas, GARAGE_MODEL_RECTS[i], f"{i + 1}   {item['name']}   •   {status}",
                            font_info, canvas_mouse, selected=i == preview.model_index,
                            disabled=not unlocked)

            draw_button(canvas, GARAGE_START_RECT, "YARIŞA BAŞLA", font_info, canvas_mouse,
                        selected=True)
            draw_button(canvas, GARAGE_BACK_RECT, "← ANA MENÜ", font_small, canvas_mouse)
            help_text = font_small.render("Yeni renk ve desenler ödül/seviye ile açılır", True, (175, 185, 194))
            canvas.blit(help_text, help_text.get_rect(center=(GAME_WIDTH // 2, 1145)))

        if state["paused"] and ui_screen == "play":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 6, 10, 218))
            canvas.blit(overlay, (0, 0))
            title = font_big.render("DURAKLATILDI", True, CYAN)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 335)))
            record = font_small.render(f"Skor {state['score']}  •  Rekor {current_record}", True, WHITE)
            canvas.blit(record, record.get_rect(center=(GAME_WIDTH // 2, 410)))
            draw_button(canvas, PAUSE_CONTINUE_RECT, "DEVAM ET", font_info, canvas_mouse, selected=True)
            draw_button(canvas, PAUSE_GARAGE_RECT, "GARAJA GİT", font_info, canvas_mouse)
            draw_button(canvas, PAUSE_EXIT_RECT, "KAYDET VE ANA MENÜ", font_info, canvas_mouse)
            hint = font_small.render("ESC veya P ile devam edebilirsin", True, (178, 186, 194))
            canvas.blit(hint, hint.get_rect(center=(GAME_WIDTH // 2, 805)))

        if state["chapter_complete"] and ui_screen == "play":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((3, 10, 16, 225))
            canvas.blit(overlay, (0, 0))
            completed_index = max(0, profile["story_stage"] - 1)
            completed = MISSION_DEFS[completed_index]
            title = font_big.render("BÖLÜM TAMAMLANDI", True, YELLOW)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 360)))
            completed_label = font_score.render(completed["name"], True, CYAN)
            canvas.blit(completed_label, completed_label.get_rect(center=(GAME_WIDTH // 2, 455)))
            result = font_info.render(f"+{completed['reward']} ALTIN  •  TOPLAM {profile['rewards']}", True, WHITE)
            canvas.blit(result, result.get_rect(center=(GAME_WIDTH // 2, 535)))
            special = font_info.render(completed["special"], True, YELLOW)
            canvas.blit(special, special.get_rect(center=(GAME_WIDTH // 2, 590)))
            next_text = "FİNALİ GÖR" if profile["story_stage"] >= len(MISSION_DEFS) else "SONRAKİ BÖLÜM"
            draw_button(canvas, CHAPTER_CONTINUE_RECT, next_text, font_info, canvas_mouse, selected=True)
            hint = font_small.render("ENTER ile devam edebilirsin", True, (175, 185, 195))
            canvas.blit(hint, hint.get_rect(center=(GAME_WIDTH // 2, 830)))

        if state["game_over"] and ui_screen == "play":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 205))
            canvas.blit(overlay, (0, 0))
            title = font_big.render(state["game_over_reason"], True, (255, 76, 76))
            final = font_score.render(f"Skor {state['score']}  •  {state['distance']:.2f} km", True, WHITE)
            record = font_info.render(f"En yüksek skor: {profile['high_score']}", True, CYAN)
            canvas.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 470)))
            canvas.blit(final, final.get_rect(center=(GAME_WIDTH // 2, 575)))
            canvas.blit(record, record.get_rect(center=(GAME_WIDTH // 2, 620)))
            draw_button(canvas, RESTART_RECT, "YENİDEN BAŞLA", font_info, canvas_mouse, selected=True)
            hint = font_small.render("R tuşunu da kullanabilirsin", True, (180, 185, 190))
            canvas.blit(hint, hint.get_rect(center=(GAME_WIDTH // 2, 755)))

        present_scaled(window, canvas)

    sync_profile(profile, state)
    save_progress(profile)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
