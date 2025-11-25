import pygame
import sys
import os
import math

SCREEN_W = 1280
SCREEN_H = 720
width_btn_hcn = 230
height_btn_hcn= 80
pos_star =((320,450))
pos_option =((320,550))
pos_exit = ((320,650))
class Button:
    def __init__(self, pos, button_name,width,height):
        base_path = f"snake/images/scenes_images/{button_name}.png"
        self.image_normal = pygame.transform.smoothscale(pygame.image.load(base_path).convert_alpha(), (width ,height))
        self.image_big    = pygame.transform.smoothscale(pygame.image.load(base_path).convert_alpha(), (int(width*1.10) ,int(height*1.10)))
        self.rect         = self.image_normal.get_rect(center=pos)
        self.width        = width
        self.height       = height
        self.hover        = False
    
    def is_hover(self):## dùng để nhận biết vơ chuột
        self.hover = self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, screen):
        if self.hover :
            img = self.image_big
            rect = img.get_rect(center=self.rect.center)
            screen.blit(img,rect)
            
        else :
            screen.blit(self.image_normal, self.rect)
    def is_clicked(self, event):## dùng để nhận biết click chuột
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
    



class BackgroundLayer:
    def __init__(self, layer_name, use_alpha,xoay = False,scale_factor=1.0,rot_deg=0.0, period=10.0, pulse=0.0, pulse_period=6.0):

        #layer_name : ten background
        #use_alpha : kiem tra ảnh có xóa nền chưa
        #scale_factor : điều chỉnh phần scale ảnh 
        #rotdeg : góc quay
        #period : thời gian quay
        #pulse : độ lớn ảnh theo thời gian (ảnh thở)
        #pulse_period : khoảng thơi gian để 
        #xoay : kiểm tra xem hinh sẽ xoay hay chỉ lắc nhẹ 

        base_path = f"snake/images/scenes_images/{layer_name}.png"
        surf = pygame.image.load(base_path)
        if use_alpha :surf = surf.convert_alpha()
        else :surf.convert()

        target_w = int(SCREEN_W * scale_factor)
        target_h = int(SCREEN_H * scale_factor)

        if xoay : self.base = pygame.transform.smoothscale(surf, (target_h, target_h))
        else : self.base = pygame.transform.smoothscale(surf, (target_w, target_h))
        self.rot_deg = float(rot_deg)
        self.period = max(float(period), 0.001)
        self.pulse = float(pulse)
        self.pulse_period = max(float(pulse_period), 0.001)
        self.checkxoay =xoay

    def draw(self, screen, t):
        if self.checkxoay : angle = (t / self.period) * self.rot_deg
        else :angle = self.rot_deg * math.sin(2 * math.pi * t / self.period)

        scale = 1.0 + (self.pulse * math.sin(2 * math.pi * t / self.pulse_period)) if self.pulse > 0 else 1.0
        rotated = pygame.transform.rotozoom(self.base, angle, scale)

        rw, rh = rotated.get_size()
        x = (SCREEN_W - rw) // 2
        y = (SCREEN_H - rh) // 2

        screen.blit(rotated, (x, y))


class Snake_effect:
    def __init__(self, scale=0.90):
        base_path = f"snake/images/scenes_images/"
        p_open   = pygame.image.load(base_path+"bg_1.on.png")
        p_closed = pygame.image.load(base_path+"bg_1.off.png")
        p_tongue = pygame.image.load(base_path+"bg_1.tongue.png")
        self.open   = pygame.transform.smoothscale(p_open.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        self.closed = pygame.transform.smoothscale(p_closed.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        self.tongue = pygame.transform.smoothscale(p_tongue.convert_alpha(),(int(SCREEN_W*scale), int(SCREEN_H*scale)))
        # đặt mép phải, hơi lệch vào trong màn hình
        self.pos = (SCREEN_W - self.open.get_width() + int(SCREEN_W*0.02),SCREEN_H - self.open.get_height() + int(SCREEN_H*0.02))
        self.BLINK_PERIOD = 5.0  # mỗi 5s
        self.BLINK_LEN    = 0.12 # nhắm 120ms
        self.TONGUE_PERIOD = 3.0  # mỗi 3s
        self.TONGUE_LEN    = 0.3  # lè lưỡi 300ms
    def draw(self, screen, t):
        blink_phase = (t % self.BLINK_PERIOD)
        tongue_phase = (t % self.TONGUE_PERIOD)
        img = self.open
        if blink_phase < self.BLINK_LEN :
            img = self.closed
        if tongue_phase < self.TONGUE_LEN:
            img =self.tongue
        screen.blit(img, self.pos)


class Background_Menu:
    def __init__(self):
        
        self.base  = BackgroundLayer("bg_1", use_alpha=False ,scale_factor=1.1 ,rot_deg=4, period=10.0)
       
       
       
        self.title = BackgroundLayer("bg_1.title", use_alpha=True, scale_factor=1.00, rot_deg=3.0,period=6.0, pulse=0.04, pulse_period=10.0)
       
        self.snake = Snake_effect(scale=0.90)

    def draw(self, screen, t):
        # vẽ theo thứ tự: nền -> ánh sáng -> rắn -> tiêu đề
        self.base.draw(screen, t)
        
        self.snake.draw(screen, t)
        self.title.draw(screen, t)





class UI_Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
        self.bg = Background_Menu()
        self.btn_star   = Button(pos_star,"btn_start",width_btn_hcn,height_btn_hcn)
        self.btn_option = Button(pos_option,"btn_option",width_btn_hcn,height_btn_hcn)
        self.btn_exit   = Button((pos_exit),"btn_exit",width_btn_hcn,height_btn_hcn)
        self.running    = True
        self.clock      = pygame.time.Clock()  
        self.t          = 0.0
    def run(self):
            while self.running:
               self.dt = self.clock.tick(60)/1000.0
               self.t += self.dt
               self.bg.draw(self.screen,self.t)

               self.btn_star.is_hover()
               self.btn_option.is_hover()
               self.btn_exit.is_hover()



               self.btn_star.draw(self.screen)
               self.btn_option.draw(self.screen)
               self.btn_exit.draw(self.screen)



               for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                    self.running = False
                  if self.btn_star.is_clicked(event):
                    print ("Star")
                  if self.btn_option.is_clicked(event):
                    print ("option")
                  if self.btn_exit.is_clicked(event):
                    print ("Exit")
                    return 
                  
                   
                   
               pygame.display.flip()
               
    

    
if __name__ == "__main__":
    UI_Menu().run()
    pygame.quit()
    sys.exit()

