import pygame
import sys
import os
import math

import pygame.display
from pygame.time import Clock

SCREEN_W = 1280
SCREEN_H = 720
width_btn,height_btn = 260, 80*(26/23) # kích thước ảnh nút đỏ
width_undo,height_undo = 100,100
width_color,height_color = 150,150
width_submit,height_submit = 170,55
pos_star =((320,420))
pos_option =((320,530))
pos_exit = ((320,630))
pos_undo =((80,80))
pos_player =((640,270))
pos_bot = ((640,370))
pos_rule = ((640,470))
pos_color =((1180,600))
pos_submit = ((640, 440))
pos_inputBox = ((390, 325))
pos_wrn = ((375, 370))

class Button:
    def __init__(self, pos, button_name,width,height,rot = 0.0):
        base_path = f"snake/images/scenes_images/{button_name}.png"
        self.image_normal = pygame.image.load(base_path).convert_alpha() 
        self.image_big    = pygame.image.load(base_path).convert_alpha()
        self.rot          = rot
        if self.rot == 0:
            self.image_normal = pygame.transform.smoothscale(self.image_normal,(width,height))
            self.image_big    = pygame.transform.smoothscale(self.image_normal,(int(width*1.1),int(height*1.1)))
            self.rect         = self.image_normal.get_rect(center=pos)
            self.hover        = False
            
        else :
            rad               = math.radians(rot)
            self.height_btn   = abs(math.sin(rad))*width + abs(math.cos(rad))*height
            self.width_btn    = abs(math.sin(rad))*height + abs(math.cos(rad))*width
            self.image_normal = pygame.transform.rotate(self.image_normal,rot)
            self.image_normal = pygame.transform.smoothscale(self.image_normal,(self.width_btn,self.height_btn))
            self.rect         = self.image_normal.get_rect(center=pos)
            self.image_big    = pygame.transform.rotate(self.image_big,rot)
            self.image_big    = pygame.transform.smoothscale(self.image_normal,(int(self.width_btn*1.1),int(self.height_btn*1.1)))
            self.mask         = pygame.mask.from_surface(self.image_normal)


    def is_hover(self):# dùng để nhận biết vơ chuột
        if self.rot == 0:
                self.hover = self.rect.collidepoint(pygame.mouse.get_pos())
        else:
            mx,my = pygame.mouse.get_pos()
            if (self.rect.left<mx<self.rect.right) and (self.rect.top<my<self.rect.bottom):
                
                self.hover = (self.mask.get_at((mx-self.rect.left,my-self.rect.top)) == 1) 
            else : self.hover = False   

    def draw(self, screen):
        if self.rot == 0:
            if self.hover :
                   img = self.image_big
                   rect = img.get_rect(center=self.rect.center)
                   screen.blit(img,rect)
            else : screen.blit(self.image_normal, self.rect)
        else :
            if self.hover:
                img = self.image_big
                rect = img.get_rect(center=self.rect.center)
                screen.blit(img,rect)
            else :
                screen.blit(self.image_normal,self.rect)

    def is_clicked(self, event):## dùng để nhận biết click chuột
        if self.rot == 0: return event.type == pygame.MOUSEBUTTONDOWN and self.hover
        else : return event.type == pygame.MOUSEBUTTONDOWN and self.hover
        
    



class BackgroundLayer:
    def __init__(self, layer_name, use_alpha,scale_factor=1.0,rot_deg=0.0, period=10.0, pulse=0.0, pulse_period=6.0):

        #layer_name : tên background
        #use_alpha :  true(ảnh thường),false(ảnh đã xóa nền)
        #scale_factor : kích thước ảnh tăng n lần 
        #rotdeg : góc quay từ (-n độ đến n độ) do xài hàm sin 
        #period : thời gian quay 1 chu kỳ
        #pulse : điều chỉnh kích ảnh lên từ (-n% đến n%) do xài hàm sin
        #pulse_period : thời gian điều chỉnh 1 chu kỳ 

        base_path = f"snake/images/scenes_images/{layer_name}.png"
        surf = pygame.image.load(base_path)
        if use_alpha :surf = surf.convert_alpha()
        else :surf.convert()

        target_w = int(SCREEN_W * scale_factor)
        target_h = int(SCREEN_H * scale_factor)


        self.base = pygame.transform.smoothscale(surf, (target_w, target_h))
        self.rot_deg = float(rot_deg)
        self.period = max(float(period), 0.001)
        self.pulse = float(pulse)
        self.pulse_period = max(float(pulse_period), 0.001)

    def draw(self, screen, t):
        angle = self.rot_deg * math.sin(2 * math.pi * t / self.period)

        scale = 1.0 + (self.pulse * math.sin(2 * math.pi * t / self.pulse_period)) if self.pulse > 0 else 1.0
        rotated = pygame.transform.rotozoom(self.base, angle, scale)

        rw, rh = rotated.get_size()
        x = (SCREEN_W - rw) // 2
        y = (SCREEN_H - rh) // 2

        screen.blit(rotated, (x, y))


class Snake_effect:
    def __init__(self, scale):
        base_path = f"snake/images/scenes_images/"
        p_open   = pygame.image.load(base_path+"bg_1.on.png")
        p_closed = pygame.image.load(base_path+"bg_1.off.png")
        p_tongue = pygame.image.load(base_path+"bg_1.tongue.png")
        self.open   = pygame.transform.smoothscale(p_open.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        self.closed = pygame.transform.smoothscale(p_closed.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        self.tongue = pygame.transform.smoothscale(p_tongue.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        self.pos = (SCREEN_W - self.open.get_width() + int(SCREEN_W*0.02),SCREEN_H - self.open.get_height() + int(SCREEN_H*0.02))
        self.BLINK_PERIOD  = 5.0  # mỗi 5s
        self.BLINK_LEN     = 0.12 # nhắm 120ms
        self.TONGUE_PERIOD = 3.0  # mỗi 3s
        self.TONGUE_LEN    = 0.5  # lè lưỡi 300ms
    def draw(self, screen, t):
        blink_phase = (t % self.BLINK_PERIOD)
        tongue_phase = (t % self.TONGUE_PERIOD)
        img = self.open
        if blink_phase < self.BLINK_LEN :
            img = self.closed
        if tongue_phase < self.TONGUE_LEN:
            img =self.tongue
        screen.blit(img, self.pos)


class Background_Main:
    def __init__(self):
        self.base  = BackgroundLayer("bg_1", use_alpha=False ,scale_factor=1.1 ,rot_deg=3, period=15.0)
        self.title = BackgroundLayer("bg_1.title", use_alpha=True, scale_factor=1.00, rot_deg=3.0,period=6.0, pulse=0.04, pulse_period=10.0)
        self.snake = Snake_effect(scale=1.0)
    def draw(self, screen, t):
        self.base.draw(screen, t)
        self.snake.draw(screen, t)
        self.title.draw(screen, t)

class Background_Select:
    def __init__(self):
        self.base = BackgroundLayer("bg_1",use_alpha=False ,scale_factor=1.1 ,rot_deg=4, period=10.0)
        self.board = BackgroundLayer("bg_2.board",use_alpha=True)
    def draw(self,screen,t):
        self.base.draw(screen,t)
        self.board.draw(screen,t)

class Background_Rule:
    def __init__(self):
        self.base =  BackgroundLayer("bg_1", use_alpha=False ,scale_factor=1.1 ,rot_deg=4, period=10.0)
        self.rule =  BackgroundLayer("rule", use_alpha=True  )
    def draw(self,screen,t):
        self.base.draw(screen,t)
        self.rule.draw(screen,t)

class Background_Username:
    def __init__(self):
        self.base = BackgroundLayer("bg_1",use_alpha=False ,scale_factor=1.1 ,rot_deg=4, period=10.0)
        self.board = BackgroundLayer("bg_usn",use_alpha=True, scale_factor=1.0)
    def draw(self,screen,t):
        self.base.draw(screen,t)
        self.board.draw(screen,t)

class Button_Main:
    def __init__(self):
        self.btn_start   = Button(pos_star,"btn_start",width_btn,height_btn,rot = -3.0)
        self.btn_option = Button(pos_option,"btn_option",width_btn,height_btn,rot = 6.9)
        self.btn_exit   = Button(pos_exit,"btn_exit",width_btn,height_btn)
    def is_hover(self):
        self.btn_start.is_hover()
        self.btn_option.is_hover()
        self.btn_exit.is_hover()
    def draw(self,screen):
        self.btn_start.draw(screen)
        self.btn_option.draw(screen)
        self.btn_exit.draw(screen)
    def is_clicked(self,event):
        if self.btn_start.is_clicked(event):return "start"
        if self.btn_option.is_clicked(event):return "option"
        if self.btn_exit.is_clicked(event):return "exit"

class Button_Select:
    def __init__(self):
        self.btn_color=Button(pos_color,"btn_color",width_color,height_color)
        self.btn_undo=Button(pos_undo,"btn_undo",width_undo,height_undo)
        self.btn_player=Button(pos_player,"btn_player",width_btn,height_btn)
        self.btn_bot=Button(pos_bot,"btn_bot",width_btn,height_btn)
        self.btn_rule = Button(pos_rule,"btn_rule",width_btn,height_btn)
    def is_hover(self):
        self.btn_color.is_hover()
        self.btn_bot.is_hover()
        self.btn_player.is_hover()
        self.btn_rule.is_hover()
        self.btn_undo.is_hover()
    def draw(self,screen):
        self.btn_color.draw(screen)
        self.btn_bot.draw(screen)
        self.btn_player.draw(screen)
        self.btn_rule.draw(screen)
        self.btn_undo.draw(screen)
    def is_clicked(self,event):
        if self.btn_color.is_clicked(event):return "color"
        if self.btn_bot.is_clicked(event):return "ai"
        if self.btn_player.is_clicked(event):return "player"
        if self.btn_rule.is_clicked(event):return "rule"
        if self.btn_undo.is_clicked(event):return "undo1"

class Button_Rule:
    def __init__(self):
        self.btn_undo=Button(pos_undo,"btn_undo",width_undo,height_undo)
    def is_hover(self):
        self.btn_undo.is_hover()
    def draw(self,screen):
        self.btn_undo.draw(screen)
    def is_clicked(self,event):
        if self.btn_undo.is_clicked(event):return "undo2"

class Input_Box:
    def __init__(self, x, y, w, h, font_size=30):
        self.rect = pygame.Rect(x, y, w, h)
        self.active = False

        self.color = pygame.Color("green4")
        self.font = pygame.font.SysFont("Comic Sans MS", font_size)
        self.text = ""
        self.txt_surface = self.font.render(self.text, True, (255, 255, 255))

        self.cursor_visible = True
        self.cursor_time = 0
        self.cursor_status = 0.5

        self.wrn_img = pygame.image.load("snake/images/scenes_images/wrn_usn.png").convert_alpha()
        self.show_wrn = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                print("Username: ", self.text)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 10: 
                    self.text += event.unicode
                    self.show_wrn = False
                else:
                    self.show_wrn = True
            self.txt_surface = self.font.render(self.text, True, (255, 255, 255))
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

class UI_Main:#giao diện vào game
    def __init__(self,clock,screen):
        self.screen = screen
        self.bg = Background_Main()
        self.btn = Button_Main()
        self.running    = True
        self.clock      = clock  
        self.t          = 0.0
    def run(self):
            while self.running:
               self.dt = self.clock.tick(60)/1000.0
               self.t += self.dt
               self.bg.draw(self.screen,self.t)
               self.btn.is_hover()
               self.btn.draw(self.screen)
               for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                     self.running = False
                  if self.btn.is_clicked(event):
                     return self.btn.is_clicked(event)
  
               pygame.display.flip()
               
    
class UI_Select:#giao diện chọn chế độ chơi và skin
    def __init__(self,clock,screen):
        self.screen = screen
        self.bg = Background_Select()
        self.btn = Button_Select()
        self.running    = True
        self.clock      = clock  
        self.t          = 0.0

    def run(self):
            while self.running:
               self.dt = self.clock.tick(60)/1000.0
               self.t += self.dt
               self.bg.draw(self.screen,self.t)
               self.btn.is_hover()
               self.btn.draw(self.screen)
             
               for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                    self.running = False
                  if self.btn.is_clicked(event):
                    return self.btn.is_clicked(event)
                  
               pygame.display.flip()

class UI_Rule:
    def __init__(self,clock,screen):
        self.screen = screen
        self.bg = Background_Rule()
        self.btn = Button_Rule()
        self.clock = clock
        self.t =0.0
        self.running =True
    def run(self):
        while self.running:
            self.dt = self.clock.tick(60)/1000.0
            self.t +=self.dt
            self.bg.draw(self.screen,self.t)
            self.btn.is_hover()
            self.btn.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.btn.is_clicked(event):
                    return self.btn.is_clicked(event)
            pygame.display.flip()

class UI_Username:
    def __init__(self, clock, screen):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.t = 0
        self.bg = Background_Username()
        self.usn_ui = Username_Menu(pos_inputBox)
        self.btn_undo = Button(pos_undo, "btn_undo", width_undo, height_undo)
        self.btn_submit = Button(pos_submit, "btn_submit", width_submit, height_submit)
    def run(self):
        while self.running:
            self.dt = self.clock.tick(60)/1000
            self.t += self.dt
            self.usn_ui.draw(self.screen, self.bg, self.t)
            self.btn_submit.is_hover()
            self.btn_submit.draw(self.screen)
            self.btn_undo.is_hover()
            self.btn_undo.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.usn_ui.handle_event(event)
                if self.btn_undo.is_clicked(event):
                    return "undo2"
                if self.btn_submit.is_clicked(event):
                    print("SUBMIT: ", self.usn_ui.input_box.text)
                    return "submit"
            self.usn_ui.update(self.dt)
            pygame.display.flip()
        return "done"


class UI_Manager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
        self.clock  = pygame.time.Clock()
        self.current = UI_Main(self.clock,self.screen)
        
        self.transitions = {# giá trị trả về : menu #
            "start": UI_Select(self.clock,self.screen),
            "player": UI_Username(self.clock, self.screen),
            "rule" : UI_Rule(self.clock,self.screen),
            "undo1": UI_Main(self.clock,self.screen),
            "undo2": UI_Select(self.clock,self.screen),
            "submit": UI_Select(self.clock, self.screen),
        }

    def run(self):
        result = self.current.run()
        if result == "exit":
            pygame.quit()
            sys.exit()
        elif result in self.transitions:
            self.current = self.transitions[result]

       

if __name__ == "__main__":
   
 manager = UI_Manager()
 while True:
    manager.run()

           
       