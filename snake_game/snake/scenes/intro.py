import pygame
import sys
import os
import math
import pygame.display
from pygame.time import Clock
from snake.settings import TEXTS
try:
    from snake.app import Game
    import snake.settings as settings
except ImportError:
    print("Warning: snake.app or snake.settings not found. Using mock data.")
    class Game:
        def run(self, name): return 100
    class Settings: pass
    settings = Settings()
if not hasattr(settings, 'SOUND_ON'): settings.SOUND_ON = True
if not hasattr(settings, 'SOUND_VOLUME'): settings.SOUND_VOLUME = 0.5

SCREEN_W = 1280
SCREEN_H = 720
width_btn, height_btn = 260, int(80 * (26 / 23)) 
width_undo, height_undo = 100, 100
width_color, height_color = 150, 150
width_submit, height_submit = 170, 55

pos_star = (320, 420)
pos_option = (320, 530)
pos_exit = (320, 630)
pos_undo = (80, 80)
pos_player = (640, 270)
pos_bot = (640, 370)
pos_rule = (640, 470)
pos_color = (1180, 600)
pos_submit = (640, 440)
pos_inputBox = (390, 325)
pos_wrn = (375, 370)
pos_return = (470, 550)
pos_exit1 = (830, 550)
color_text = (64, 224, 208)
pos_idk=((850,390))
class Sound:
    def __init__(self, name):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init() # Ensure init is called
            base_path = f"snake/sound/sfx_{name}.mp3"
            if os.path.exists(base_path):
                self.sound = pygame.mixer.Sound(base_path)
            else:
                self.sound = None
                print(f"Warning: Sound file not found: {base_path}")
        except Exception as e:
            self.sound = None
            print(f"Sound Init Error: {e}")

    def run(self):
        if hasattr(settings, 'SOUND_ON') and settings.SOUND_ON:
            if self.sound:
                vol = getattr(settings, 'SOUND_VOLUME', 0.5)
                self.sound.set_volume(vol)
                self.sound.play()

class Button:
    def __init__(self, pos, button_name, width, height, rot=0.0):
        self.pos = pos
        self.width = width
        self.height = height
        self.rot = rot
        self.button_name = button_name
        
        self.assets_en = self.load_assets("")
        
        self.assets_vi = self.load_assets("_vi")

        self.sfx_hover = Sound("hover")
        self.sfx_clicked = Sound("clicked")
        self.was_clicked = False
        self.was_hover = False
        self.hover = False 

    def load_assets(self, suffix):
        base_path = f"snake/images/scenes_images/{self.button_name}{suffix}.png"
        
        if not os.path.exists(base_path):
            base_path = f"snake/images/scenes_images/{self.button_name}.png"

        if not os.path.exists(base_path):
            image_normal = pygame.Surface((self.width, self.height))
            image_normal.fill((255, 0, 0))
            image_big = pygame.Surface((self.width, self.height))
            image_big.fill((200, 0, 0))
        else:
            image_normal = pygame.image.load(base_path).convert_alpha()
            image_big = pygame.image.load(base_path).convert_alpha()

        if self.rot == 0:
            image_normal = pygame.transform.smoothscale(image_normal, (int(self.width), int(self.height)))
            image_big = pygame.transform.smoothscale(image_big, (int(self.width * 1.1), int(self.height * 1.1)))
            rect = image_normal.get_rect(center=self.pos)
            mask = None
        else:
            rad = math.radians(self.rot)
            height_btn = abs(math.sin(rad)) * self.width + abs(math.cos(rad)) * self.height
            width_btn = abs(math.sin(rad)) * self.height + abs(math.cos(rad)) * self.width

            image_normal = pygame.transform.rotate(image_normal, self.rot)
            image_normal = pygame.transform.smoothscale(image_normal, (int(width_btn), int(height_btn)))

            image_big = pygame.transform.rotate(image_big, self.rot)
            image_big = pygame.transform.smoothscale(image_big, (int(width_btn * 1.1), int(height_btn * 1.1)))

            rect = image_normal.get_rect(center=self.pos)
            mask = pygame.mask.from_surface(image_normal)
            
        return {"normal": image_normal, "big": image_big, "rect": rect, "mask": mask}

    @property
    def current_assets(self):
        if hasattr(settings, 'LANGUAGE') and settings.LANGUAGE == "VI":
            return self.assets_vi
        return self.assets_en

    @property
    def rect(self):
        return self.current_assets["rect"]

    def is_hover(self):
        assets = self.current_assets
        rect = assets["rect"]
        mask = assets["mask"]
        
        if self.rot == 0:
            self.hover = rect.collidepoint(pygame.mouse.get_pos())
        else:
            mx, my = pygame.mouse.get_pos()
            if (rect.left < mx < rect.right) and (rect.top < my < rect.bottom):
                try:
                    self.hover = (mask.get_at((mx - rect.left, my - rect.top)) == 1)
                except IndexError:
                    self.hover = False
            else:
                self.hover = False

    def draw(self, screen):
        assets = self.current_assets
        rect = assets["rect"]
        
        if self.hover:
            img = assets["big"]
            draw_rect = img.get_rect(center=rect.center)
            screen.blit(img, draw_rect)
        else:
            screen.blit(assets["normal"], rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.hover

    def sound_hover(self):
        if self.hover and not self.was_hover:
            self.sfx_hover.run()
        self.was_hover = self.hover
                    
class BackgroundLayer:
    def __init__(self, layer_name, use_alpha, scale_factor=1.0, rot_deg=0.0, period=10.0, pulse=0.0, pulse_period=6.0):
        self.layer_name = layer_name
        self.use_alpha = use_alpha
        self.scale_factor = scale_factor
        
        # Tải sẵn 2 phiên bản ảnh: Gốc (EN) và Việt (VI)
        self.base_en = self.load_processed_image("")
        self.base_vi = self.load_processed_image("_vi")

        self.rot_deg = float(rot_deg)
        self.period = max(float(period), 0.001)
        self.pulse = float(pulse)
        self.pulse_period = max(float(pulse_period), 0.001)

    def load_processed_image(self, suffix):
        """Hàm phụ trợ để tải và xử lý ảnh (scale)"""
        base_path = f"snake/images/scenes_images/{self.layer_name}{suffix}.png"
        
        # Nếu không có ảnh _vi, dùng lại ảnh gốc
        if not os.path.exists(base_path):
            base_path = f"snake/images/scenes_images/{self.layer_name}.png"
        
        # Fallback nếu ảnh gốc cũng không có
        if not os.path.exists(base_path):
            surf = pygame.Surface((SCREEN_W, SCREEN_H))
            surf.fill((50, 50, 50))
        else:
            surf = pygame.image.load(base_path)
            
        if self.use_alpha:
            surf = surf.convert_alpha()
        else:
            surf = surf.convert() # Không dùng convert_alpha cho ảnh nền đặc

        target_w = int(SCREEN_W * self.scale_factor)
        target_h = int(SCREEN_H * self.scale_factor)
        return pygame.transform.smoothscale(surf, (target_w, target_h))

    @property
    def current_base(self):
        """Chọn ảnh dựa trên ngôn ngữ hiện tại"""
        if hasattr(settings, 'LANGUAGE') and settings.LANGUAGE == "VI":
            return self.base_vi
        return self.base_en

    def draw(self, screen, t):
        # Lấy ảnh nền phù hợp với ngôn ngữ
        base = self.current_base
        
        angle = self.rot_deg * math.sin(2 * math.pi * t / self.period)
        scale = 1.0 + (self.pulse * math.sin(2 * math.pi * t / self.pulse_period)) if self.pulse > 0 else 1.0
        
        rotated = pygame.transform.rotozoom(base, angle, scale)

        rw, rh = rotated.get_size()
        x = (SCREEN_W - rw) // 2
        y = (SCREEN_H - rh) // 2
        screen.blit(rotated, (x, y))

class Snake_effect:
    def __init__(self, scale):
        base_path = f"snake/images/scenes_images/"
        try:
            p_open = pygame.image.load(base_path + "bg_1.on.png")
            p_closed = pygame.image.load(base_path + "bg_1.off.png")
            p_tongue = pygame.image.load(base_path + "bg_1.tongue.png")
            self.open = pygame.transform.smoothscale(p_open.convert_alpha(), (int(SCREEN_W * scale), int(SCREEN_H * scale)))
            self.closed = pygame.transform.smoothscale(p_closed.convert_alpha(), (int(SCREEN_W * scale), int(SCREEN_H * scale)))
            self.tongue = pygame.transform.smoothscale(p_tongue.convert_alpha(), (int(SCREEN_W * scale), int(SCREEN_H * scale)))
        except:
            # Placeholder if images missing
            self.open = pygame.Surface((100, 100))
            self.closed = pygame.Surface((100, 100))
            self.tongue = pygame.Surface((100, 100))
            
        self.pos = (SCREEN_W - self.open.get_width() + int(SCREEN_W * 0.02), SCREEN_H - self.open.get_height() + int(SCREEN_H * 0.02))
        self.BLINK_PERIOD = 5.0
        self.BLINK_LEN = 0.12
        self.TONGUE_PERIOD = 3.0
        self.TONGUE_LEN = 0.5

    def draw(self, screen, t):
        blink_phase = (t % self.BLINK_PERIOD)
        tongue_phase = (t % self.TONGUE_PERIOD)
        img = self.open
        if blink_phase < self.BLINK_LEN:
            img = self.closed
        if tongue_phase < self.TONGUE_LEN:
            img = self.tongue
        screen.blit(img, self.pos)

class Background_Main:
    def __init__(self):
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        self.title = BackgroundLayer("bg_1.title", use_alpha=True, scale_factor=1.00, rot_deg=3.0, period=6.0, pulse=0.04, pulse_period=10.0)
        self.snake = Snake_effect(scale=1.0)

    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.snake.draw(screen, t)
        self.title.draw(screen, t)

class Background_Select:
    def __init__(self):
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        self.board = BackgroundLayer("bg_2.board", use_alpha=True)

    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.board.draw(screen, t)

class Background_Rule:
    def __init__(self):
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        self.rule = BackgroundLayer("rule", use_alpha=True)

    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.rule.draw(screen, t)

class Background_Username:
    def __init__(self):
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        self.board = BackgroundLayer("bg_usn", use_alpha=True)

    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.board.draw(screen, t)

color_text = (64, 224, 208) 


class Background_Score:
    def __init__(self):
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        self.board = BackgroundLayer("bg_score", use_alpha=True)

        # Font
        try:
            self.font_name = pygame.font.Font("snake/images/font.ttf", 100)   # tên
        except:
            self.font_name = pygame.font.SysFont("Arial", 100)

        try:
            self.font_score = pygame.font.SysFont("Consolas", 100)            # điểm (monospace)
        except:
            self.font_score = self.font_name

    # Method trong class -> cần self
    def render_with_outline(self, text, font, fill=(46, 196, 182), outline=(20, 20, 20), offset=1):
        """
        Render chữ có viền (outline) 1–2 px để nổi bật hơn.
        """
        base = font.render(text, True, fill)
        out  = font.render(text, True, outline)
        surf = pygame.Surface((base.get_width()+2*offset, base.get_height()+2*offset), pygame.SRCALPHA)
        for dx, dy in [(-offset,0),(offset,0),(0,-offset),(0,offset)]:
            surf.blit(out, (dx+offset, dy+offset))
        surf.blit(base, (offset, offset))
        return surf

    def draw(self, screen, t, usn, point):
        # Vẽ nền
        self.base.draw(screen, t)
        self.board.draw(screen, t)

        # Hộp dòng & baseline
        line_rect   = pygame.Rect(330, 360, 580, 120)
        baseline_y  = 430
        pygame.draw.line(screen, (0, 0, 0), (line_rect.left, baseline_y), (line_rect.right, baseline_y), 1)

        # --- TẠO SURFACE CHỮ (có outline) ---
        usn_surf   = self.render_with_outline(f"{usn}:", self.font_name, fill=color_text)
        score_surf = self.render_with_outline(str(point), self.font_score, fill=color_text)

        # --- CĂN THEO BASELINE ---
        # Tên: căn trái + bám baseline
        usn_rect = usn_surf.get_rect()
        usn_rect.left = line_rect.left + 10
        usn_rect.top  = baseline_y - self.font_name.get_ascent() - 10

        # Điểm: căn phải + bám baseline (chừa 130 px cho icon)
        score_rect = score_surf.get_rect()
        score_rect.right = line_rect.right - 130
        score_rect.top   = baseline_y - self.font_score.get_ascent() -10

        # --- VẼ LÊN MÀN HÌNH ---
        screen.blit(usn_surf, usn_rect)
        screen.blit(score_surf, score_rect)


       


class Button_Main:
    def __init__(self):
        self.btn_start = Button(pos_star, "btn_start", width_btn, height_btn, rot=-3.0)
        self.btn_option = Button(pos_option, "btn_option", width_btn, height_btn, rot=6.9)
        self.btn_exit = Button(pos_exit, "btn_exit", width_btn, height_btn)

    def is_hover(self):
        self.btn_start.is_hover()
        self.btn_option.is_hover()
        self.btn_exit.is_hover()

    def draw(self, screen):
        self.btn_start.draw(screen)
        self.btn_option.draw(screen)
        self.btn_exit.draw(screen)

    def is_clicked(self, event):
        if self.btn_start.is_clicked(event): return "start"
        if self.btn_option.is_clicked(event): return "option"
        if self.btn_exit.is_clicked(event): return "exit"

    def sound_hover(self):
        self.btn_start.sound_hover()
        self.btn_option.sound_hover()
        self.btn_exit.sound_hover()

class Button_Select:
    def __init__(self):
        self.btn_color = Button(pos_color, "btn_color", width_color, height_color)
        self.btn_undo = Button(pos_undo, "btn_undo", width_undo, height_undo)
        self.btn_player = Button(pos_player, "btn_player", width_btn, height_btn)
        self.btn_bot = Button(pos_bot, "btn_bot", width_btn, height_btn)
        self.btn_rule = Button(pos_rule, "btn_rule", width_btn, height_btn)

    def is_hover(self):
        self.btn_color.is_hover()
        self.btn_bot.is_hover()
        self.btn_player.is_hover()
        self.btn_rule.is_hover()
        self.btn_undo.is_hover()

    def draw(self, screen):
        self.btn_color.draw(screen)
        self.btn_bot.draw(screen)
        self.btn_player.draw(screen)
        self.btn_rule.draw(screen)
        self.btn_undo.draw(screen)

    def is_clicked(self, event):
        if self.btn_color.is_clicked(event): return "color"
        if self.btn_bot.is_clicked(event): return "ai"
        if self.btn_player.is_clicked(event): return "player"
        if self.btn_rule.is_clicked(event): return "rule"
        if self.btn_undo.is_clicked(event): return "undo1"

    def sound_hover(self):
        self.btn_color.sound_hover()
        self.btn_bot.sound_hover()
        self.btn_player.sound_hover()
        self.btn_rule.sound_hover()
        self.btn_undo.sound_hover()

class Button_Rule:
    def __init__(self):
        self.btn_undo = Button(pos_undo, "btn_undo", width_undo, height_undo)

    def is_hover(self):
        self.btn_undo.is_hover()

    def draw(self, screen):
        self.btn_undo.draw(screen)

    def is_clicked(self, event):
        if self.btn_undo.is_clicked(event): return "undo2"

    def sound_hover(self):
        self.btn_undo.sound_hover()


class Button_Score:
    def __init__(self):
        self.btn_return = Button(pos_return, "btn_return", width_btn, height_btn)
        self.btn_exit = Button(pos_exit1, "btn_exit", width_btn, height_btn)
        self.btn_idk  = Button(pos_idk,"btn_idk",55,60)


    def is_hover(self):
        self.btn_return.is_hover()
        self.btn_exit.is_hover()
        self.btn_idk.is_hover()
    def draw(self, screen):
        self.btn_return.draw(screen)
        self.btn_exit.draw(screen)
        self.btn_idk.draw(screen)
    def is_clicked(self, event):
        if self.btn_return.is_clicked(event): return "return"
        if self.btn_exit.is_clicked(event): return "exit1"

    def sound_hover(self):
        self.btn_return.sound_hover()
        self.btn_exit.sound_hover()
        
class Input_Box:
    def __init__(self, x, y, w, h, font_size=30):
        self.rect = pygame.Rect(x, y, w, h)
        self.active = False
        self.star_game = False

        self.color = pygame.Color("green4")
        self.font = pygame.font.SysFont("Comic Sans MS", font_size)
        self.text = ""
        self.txt_surface = self.font.render(self.text, True, (255, 255, 255))

        self.cursor_visible = True
        self.cursor_time = 0
        self.cursor_status = 0.5

        try:
            self.wrn_img = pygame.image.load("snake/images/scenes_images/wrn_usn.png").convert_alpha()
        except:
            self.wrn_img = pygame.Surface((200, 50))

        self.show_wrn = False

    def handle_event(self, event):
       
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                
                self.font.render(self.text, True, (255, 255, 255))
                self.star_game = True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 10:
                    self.text += event.unicode
                    self.show_wrn = False
                else:
                    self.show_wrn = True
            self.txt_surface = self.font.render(self.text, True, (255, 255, 255))
    def enter_game (self):
        if self.star_game:
            self.star_game = False
            return True
        return False

    def update(self, dt):
        self.cursor_time += dt
        if self.cursor_time >= self.cursor_status:
            self.cursor_visible = not self.cursor_visible
            self.cursor_time = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=34)
        txt_rect = self.txt_surface.get_rect(center=(self.rect.centerx, self.rect.centery))
        screen.blit(self.txt_surface, txt_rect)

        if self.active and self.cursor_visible:
            self.cursor_x = txt_rect.right
            self.cursor_y = txt_rect.top + 6
            self.cursor_height = txt_rect.height * 0.7
            pygame.draw.line(screen, (255, 255, 255), (self.cursor_x, self.cursor_y), (self.cursor_x, self.cursor_y + self.cursor_height), 2)
        if self.show_wrn: screen.blit(self.wrn_img, pos_wrn)

class Username_Menu:
    def __init__(self, pos):
        self.input_box = Input_Box(pos[0], pos[1], 500, 40)

    def handle_event(self, event):
        self.input_box.handle_event(event)

    def update(self, dt):
        self.input_box.update(dt)

    def draw(self, screen, bg, t):
        bg.draw(screen, t)
        self.input_box.draw(screen)
    def enter_game(self):
        return self.input_box.enter_game()

class UI_Main:
    def __init__(self, clock, screen, t=0):
        self.screen = screen
        self.bg = Background_Main()
        self.btn = Button_Main()
        self.clicked = Sound("clicked")
        self.running = True
        self.clock = clock
        self.t = t

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.t += self.dt
            self.bg.draw(self.screen, self.t)
            self.btn.is_hover()
            self.btn.draw(self.screen)
            self.btn.sound_hover()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit", self.t
                if self.btn.is_clicked(event):
                    self.clicked.run()
                    return self.btn.is_clicked(event), self.t
            pygame.display.flip()

class UI_Select:
    def __init__(self, clock, screen, t):
        self.screen = screen
        self.bg = Background_Select()
        self.btn = Button_Select()
        self.clicked = Sound("clicked")
        self.running = True
        self.clock = clock
        self.t = t

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.t += self.dt
            self.bg.draw(self.screen, self.t)
            self.btn.is_hover()
            self.btn.draw(self.screen)
            self.btn.sound_hover()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit", self.t
                if self.btn.is_clicked(event):
                    self.clicked.run()
                    return self.btn.is_clicked(event), self.t
            pygame.display.flip()

class UI_Rule:
    def __init__(self, clock, screen, t):
        self.screen = screen
        self.bg = Background_Rule()
        self.btn = Button_Rule()
        self.clicked = Sound("clicked")
        self.clock = clock
        self.t = t
        self.running = True

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.t += self.dt
            self.bg.draw(self.screen, self.t)
            self.btn.is_hover()
            self.btn.draw(self.screen)
            self.btn.sound_hover()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit", self.t
                if self.btn.is_clicked(event):
                    self.clicked.run()
                    return self.btn.is_clicked(event), self.t
            pygame.display.flip()

class UI_Username:
    def __init__(self, clock, screen, t):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.t = t
        self.bg = Background_Username()
        self.usn_ui = Username_Menu(pos_inputBox)
        self.clicked = Sound("clicked")
        self.btn_undo = Button(pos_undo, "btn_undo", width_undo, height_undo)
        self.btn_submit = Button(pos_submit, "btn_submit", width_submit, height_submit)
       

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            self.t += self.dt
            self.usn_ui.draw(self.screen, self.bg, self.t)
            self.btn_submit.is_hover()
            self.btn_submit.draw(self.screen)
            self.btn_submit.sound_hover()
            self.btn_undo.is_hover()
            self.btn_undo.draw(self.screen)
            # Fix: Added () to execute method
            self.btn_undo.sound_hover() 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit", self.t
                self.usn_ui.handle_event(event)
                if self.usn_ui.enter_game() :
                    name = self.usn_ui.input_box.text 
                    if not bool(name.strip()): self.usn_ui.input_box.text = "PLAYER"
                    return "game", self.t, self.usn_ui.input_box.text
                if self.btn_undo.is_clicked(event):
                    self.clicked.run()
                    return "undo3", self.t, "..."
                if self.btn_submit.is_clicked(event):
                    self.clicked.run()
                    name = self.usn_ui.input_box.text 
                    if not bool(name.strip()): self.usn_ui.input_box.text = "PLAYER"
                    return "game", self.t, self.usn_ui.input_box.text
               
            self.usn_ui.update(self.dt)
            pygame.display.flip()

class UI_Score:
    def __init__(self, clock, screen, t, player_name, point):
        self.screen = screen
        self.bg = Background_Score()
        self.btn = Button_Score()
        self.clicked = Sound("clicked")
        self.running = True
        self.clock = clock
        self.t = t
        self.usn = player_name
        self.point = point

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.t += self.dt
            self.bg.draw(self.screen, self.t, self.usn, self.point)
            self.btn.is_hover()
            self.btn.draw(self.screen)
            self.btn.sound_hover()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit", self.t
                if self.btn.is_clicked(event):
                    self.clicked.run()
                    return self.btn.is_clicked(event), self.t
            pygame.display.flip()

class Slider:
    def __init__(self, pos, width, initial_val=0.5):
        self.pos = pos
        self.width = width
        self.height = 10
        self.value = initial_val
        self.rail_rect = pygame.Rect(pos[0], pos[1], width, self.height)
        self.knob_radius = 15
        self.knob_pos = [self.pos[0] + self.width * self.value, self.pos[1] + self.height // 2]
        self.dragging = False
        self.color_rail = (200, 200, 200)
        self.color_knob = (0, 255, 0)

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_rect = self.rail_rect.inflate(20, 20)
            if click_rect.collidepoint(mouse_pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        if self.dragging:
            rel_x = mouse_pos[0] - self.pos[0]
            val = rel_x / self.width
            val = max(0.0, min(1.0, val))
            self.value = val
            self.knob_pos[0] = self.pos[0] + self.width * self.value
            settings.SOUND_VOLUME = self.value
            if self.value > 0:
                settings.SOUND_ON = True

    def draw(self, screen):
        # Fix: Replaced dot with comma
        pygame.draw.rect(screen, self.color_rail, self.rail_rect, border_radius=5)
        fill_width = self.width * self.value
        fill_rect = pygame.Rect(self.pos[0], self.pos[1], fill_width, self.height)
        pygame.draw.rect(screen, self.color_knob, fill_rect, border_radius=5)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.knob_pos[0]), int(self.knob_pos[1])), self.knob_radius)
        pygame.draw.circle(screen, self.color_knob, (int(self.knob_pos[0]), int(self.knob_pos[1])), self.knob_radius - 3)

# --- Cập nhật Class Background_Option (Dùng khung trắng) ---
class Background_Option:
    def __init__(self):
        # 1. Ảnh nền tia sáng xoay (bg_1)
        self.base = BackgroundLayer("bg_1", use_alpha=False, scale_factor=1.2, rot_deg=4, period=10.0)
        
        # 2. Ảnh bảng Settings (bg_option - Khung trắng có tiêu đề)
        # Code tự động tìm bg_option_vi.png nếu ngôn ngữ là VI
        self.board = BackgroundLayer("bg_option", use_alpha=True, scale_factor=1.0) 

    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.board.draw(screen, t)

# --- Cập nhật Class UI_Option (Vẽ Icon và Nút thủ công) ---
class UI_Option:
    def __init__(self, clock, screen, t=0):
        self.screen = screen
        self.clock = clock
        self.t = t
        self.bg = Background_Option()
        self.clicked = Sound("clicked")
        self.running = True
        
        try:
            self.icon_vol = pygame.image.load("snake/images/scenes_images/btn_sound.png").convert_alpha()
            self.icon_music = pygame.image.load("snake/images/scenes_images/music.png").convert_alpha()
            self.icon_lang = pygame.image.load("snake/images/scenes_images/btn_language.png").convert_alpha()
            
            icon_size = (97, 97)
            self.icon_vol = pygame.transform.smoothscale(self.icon_vol, icon_size)
            self.icon_music = pygame.transform.smoothscale(self.icon_music, icon_size)
            self.icon_lang = pygame.transform.smoothscale(self.icon_lang, icon_size)
        except Exception as e:
            print(f"Icon warning: {e}")
            self.icon_vol = pygame.Surface((60, 60)); self.icon_vol.fill((0, 255, 0))
            self.icon_music = pygame.Surface((60, 60)); self.icon_music.fill((0, 255, 0))
            self.icon_lang = pygame.Surface((60, 60)); self.icon_lang.fill((0, 255, 0))

        center_x = SCREEN_W // 2
        center_y = SCREEN_H // 2
        
        x_icon = center_x - 250
        x_control = center_x - 150
        
        y_row1 = center_y - 120
        self.pos_icon_vol = self.icon_vol.get_rect(center=(x_icon, y_row1))
        current_vol = getattr(settings, 'SOUND_VOLUME', 0.5)
        self.slider = Slider((x_control, y_row1 - 5), 300, current_vol)
        
        y_row2 = center_y + 10
        self.pos_icon_music = self.icon_music.get_rect(center=(x_icon, y_row2))
        self.btn_sound = Button((x_control + 70, y_row2), "btn_audio", 140, 55) 
        
        y_row3 = center_y + 140
        self.pos_icon_lang = self.icon_lang.get_rect(center=(x_icon, y_row3))
        self.lang_rect = pygame.Rect(x_control, y_row3 - 25, 300, 50)
        
        self.btn_back = Button(pos_undo, "btn_undo", width_undo, height_undo)
    def get_font(self):
        if settings.LANGUAGE == "VI":
            if os.path.exists("snake/images/font_vi.ttf"):
                 return pygame.font.Font("snake/images/font_vi.ttf", 32)
            return pygame.font.SysFont("tahoma, segoeui, verdana, arial", 32, bold=True)
        if os.path.exists("snake/images/font.ttf"):
            return pygame.font.Font("snake/images/font.ttf", 32)
        return pygame.font.SysFont("arial", 32, bold=True)
    def run(self):
        while self.running:
            try:
                self.dt = self.clock.tick(60) / 1000.0
                self.t += self.dt
                
                self.bg.draw(self.screen, self.t)
                
                self.screen.blit(self.icon_vol, self.pos_icon_vol)
                self.screen.blit(self.icon_music, self.pos_icon_music)
                self.screen.blit(self.icon_lang, self.pos_icon_lang)
                
                font = pygame.font.SysFont("Arial", 32, bold=True)
                
                self.slider.draw(self.screen)
                vol_pct = int(self.slider.value * 100)
                vol_str = settings.TEXTS[settings.LANGUAGE]["volume"]
                vol_surf = font.render(f"{vol_pct}%", True, (80, 80, 80))
                self.screen.blit(vol_surf, (self.slider.pos[0] + self.slider.width + 15, self.slider.pos[1] - 15))

                self.btn_sound.is_hover() 
                self.btn_sound.draw(self.screen)
                
                status = "ON" if settings.SOUND_ON else "OFF"
                color = (0, 150, 0) if settings.SOUND_ON else (200, 0, 0)
                stat_surf = font.render(status, True, color)
                self.screen.blit(stat_surf, (self.btn_sound.rect.right + 15, self.btn_sound.rect.centery - 18))

                if self.lang_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (200, 200, 200), self.lang_rect, border_radius=10)
                    pygame.draw.rect(self.screen, (100, 100, 100), self.lang_rect, 2, border_radius=10)
                
                lang_name = settings.TEXTS[settings.LANGUAGE]["lang_label"]
                lang_surf = font.render(lang_name, True, (50, 50, 50))
                lang_rect_center = lang_surf.get_rect(center=self.lang_rect.center)
                self.screen.blit(lang_surf, lang_rect_center)

                self.btn_back.is_hover()
                self.btn_back.draw(self.screen)
                self.btn_back.sound_hover()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return "exit", self.t
                    
                    self.slider.update(event)
                    
                    if self.btn_back.is_clicked(event):
                        self.clicked.run()
                        return "menu", self.t
                    
                    if self.btn_sound.is_clicked(event):
                        self.clicked.run()
                        settings.SOUND_ON = not settings.SOUND_ON
                        if settings.SOUND_ON and self.slider.value == 0:
                            self.slider.value = 0.5
                            settings.SOUND_VOLUME = 0.5
                            self.slider.knob_pos[0] = self.slider.pos[0] + self.slider.width * 0.5
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.lang_rect.collidepoint(event.pos):
                            self.clicked.run()
                            if settings.LANGUAGE == "EN":
                                settings.LANGUAGE = "VI"
                            else:
                                settings.LANGUAGE = "EN"
                            
                pygame.display.flip()

            except Exception as e:
                print(f"CRITICAL UI ERROR: {e}")
                return "menu", self.t

class UI_Manager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.T = 0.0

        self.transitions = {
            "start": "select",
            "option": "option",
            "player": "user",
            "rule": "rule",
            "undo1": "main",
            "undo2": "select",
            "undo3": "select",
            "return": "user",
            "exit1": "main",
            "menu": "main"
        }
        self.Load_ui = {
            "main": UI_Main(self.clock, self.screen, t=self.T),
            "select": UI_Select(self.clock, self.screen, t=self.T),
            "rule": UI_Rule(self.clock, self.screen, t=self.T),
            "user": UI_Username(self.clock, self.screen, t=self.T),
            "option": UI_Option(self.clock, self.screen, t=self.T)
        }
        self.current = "main"

    def run(self):
        # Update current T into the scene before running
        self.Load_ui[self.current].t = self.T
        
        if self.current != "user":
            result, t = self.Load_ui[self.current].run()
            self.T = t
            if result == "exit":
                pygame.quit()
                sys.exit()
            elif result in self.transitions:
                self.current = self.transitions[result]
        else:
            result, t, usn = self.Load_ui[self.current].run()
            self.T = t
            if result == "exit":
                pygame.quit()
                sys.exit()
            if result == "undo3":
                self.current = self.transitions[result]
            elif result == "game":
                # Start actual game
                score = Game().run(usn)
                # Show score screen
                result, t = UI_Score(self.clock, self.screen, t=self.T, player_name=usn, point=score).run()
                self.T = t
                if result == "exit":
                    pygame.quit()
                    sys.exit()
                elif result in self.transitions:
                    self.current = self.transitions[result]

if __name__ == "__main__":
    manager = UI_Manager()
    while True:
        manager.run()