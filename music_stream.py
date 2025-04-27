import pygame
import os
import random
import threading
import time

pygame.mixer.init()

current_song_name = None
current_sentiment = None 
music_lock = threading.Lock()

def select_song(sentiment, current_song = None):
    folder_path = os.path.join("music", sentiment)
    song_options = os.listdir(folder_path)

    if current_song and current_song in song_options:
        song_options.remove(current_song)

    if not song_options:
        song_options = os.listdir(folder_path)

    song_name = random.choice(song_options)
    song_path = os.path.join(folder_path, song_name)
    print("song selected: " + song_path + song_name)
    return song_path, song_name

def start_music():
    song_path, song_name = select_song("neutral")

    pygame.mixer.music.load(song_path)

    volume = 0.5
    pygame.mixer.music.set_volume(volume)

    pygame.mixer.music.play()

    next_song_path, _ = select_song("neutral", os.path.basename(song_path))
    pygame.mixer.music.queue(next_song_path)
    print("music started")

def change(sentiment, intensity):
    global current_song_name, current_sentiment

    with music_lock:
        song_path, song_name = select_song(sentiment, intensity)

        song = pygame.mixer.Sound(song_path)
        song_length = song.get_length()
        start_time = random.uniform(0, song_length / 2)

        if pygame.mixer.music.get_busy():
            print("music playing")
            current_volume = pygame.mixer.music.get_volume()

            print("fading music")
            for i in range(10, 0, -1):
                pygame.mixer.music.set_volume(current_volume * (i / 10))
                pygame.time.delay(50)
            
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=start_time)
        volume = intensity / 10.0

        print("fade in new music")
        for i in range(0, 11):
            pygame.mixer.music.set_volume(current_volume * (i / 10))
            pygame.time.delay(50)

        current_song_name = song_name
        current_sentiment = sentiment

def queue():
    global current_sentiment, current_song_name

    while True:
        with music_lock:
            if pygame.mixer.music.get_busy():
                pos = pygame.mixer.music.get_pos() / 1000
                song = pygame.mixer.Sound(os.path.join("music", current_sentiment, current_song_name))
                song_length = song.get_length()
                time_rem = song_length - pos

                if time_rem < 3:
                    next_song_path, next_song_name = select_song(current_sentiment, current_song_name)
                    pygame.mixer.music.queue(next_song_path)
                    current_song_name = next_song_name
        
        time.sleep(1)