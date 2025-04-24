import pygame
import os
import random

pygame.mixer.init()


def select_song(sentiment):
    folder_path = os.path.join("music", sentiment)
    song_options = os.listdir(folder_path)
    print(song_options)

    song_name = random.choice(song_options)
    song_path = os.path.join(folder_path, song_name)
    print(song_path)

    song = pygame.mixer.Sound(song_path)
    song_length = song.get_length()

    start_time = random.randint(0, int(song_length - 1))

    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play(start=start_time)

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)




if __name__ == "__main__":
    select_song("tense")