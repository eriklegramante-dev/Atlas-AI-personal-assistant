import pygame
from PIL import Image, ImageSequence 
import os
import logging as logger

class AtlasAvatar:
    def __init__(self, initial_gif, target_size=(400, 400)):
        self.target_size = target_size
        self.frames = []
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.is_talking = False
        self.last_update = pygame.time.get_ticks()
        self.load_gif(initial_gif)

    def load_gif(self, path):
        """Carrega, redimensiona e padroniza os frames do GIF."""
        if not path or not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return
            
        try:
            pil_gif = Image.open(path)
            orig_w, orig_h = pil_gif.size
            aspect_ratio = orig_w / orig_h
                
            target_h = 500 
            target_w = int(target_h * aspect_ratio)
            self.target_size = (target_w, target_h)

            new_frames = []
            for frame in ImageSequence.Iterator(pil_gif):
                frame = frame.convert("RGBA")
                frame = frame.resize(self.target_size, Image.Resampling.LANCZOS)
                    
                pygame_surface = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                ).convert_alpha()
                new_frames.append(pygame_surface)
                
                self.frames = new_frames
                self.frame_index = 0
                logger.info(f"--- [DEBUG] Loaded {len(self.frames)} frames at {self.target_size}")
                
        except Exception as e:
            logger.error(f"Resize error: {e}")

    def draw(self, screen, pos=(0, 0)):
        """Desenha o avatar centralizado na base da tela."""
        if not self.frames:
            print("--- [AVISO] Avatar.draw tentou desenhar, mas 'frames' está vazia.")
            return
        
        screen_w, screen_h = screen.get_size()
        gif_w, gif_h = self.target_size

        pos_x = (screen_w - gif_w) // 2
        pos_y = screen_h - gif_h

        self.current_pos = (pos_x, pos_y)
        
        now = pygame.time.get_ticks()
        if now - self.last_update > 80:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_update = now
            
        screen.blit(self.frames[self.frame_index], self.current_pos)