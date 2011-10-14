# -*- coding: utf-8 -*-
import pygame, pygame.mixer
import pygame._view
import time 

init_continues = 5
continues = 5

def init_tanooki():
    pygame.mixer.quit()
    pygame.mixer.quit()    
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    buffer = 2048    # number of samples (experiment to get right sound)
    pygame.mixer.pre_init(freq, bitsize, 2, buffer)

def quit_tanooki():
    pygame.mixer.quit()


def play_tanooki_way(music_file, channels):
    global continues
    global init_continues
    # set up the mixer
    pygame.mixer.quit()
    pygame.mixer.quit()
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    buffer = 2048    # number of samples (experiment to get right sound)
    pygame.mixer.init(freq, bitsize, channels, buffer)

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(1.0)


    try:
        pygame.mixer.music.load(open(music_file, 'rb'))
        print "Music file loaded!"
    except pygame.error:
        print "File not found!"
        return
    pygame.mixer.music.play()

    time.sleep(0.1)
    if not pygame.mixer.music.get_busy():
        print 'hadouken'
        pygame.mixer.music.stop()
        if continues > 0:
            continues -= 1
            return play_tanooki_way(music_file, channels)
        else:
            continues = init_continues
            return False
    continues = init_continues
    return True
        

    #time.sleep(5)
    #pygame.mixer.music.stop()
    ##pygame.mixer.music.stop()
    #pygame.mixer.quit()
    #pygame.mixer.quit()
    #while pygame.mixer.music.get_busy():
    #    # check if playback has finished
    #    clock.tick(30)
    #pygame.mixer.music.stop()


## pick MP3 music file you have ...
## (if not in working folder, use full path)
#music_file = "panic.mp3"
#
#
#try:
#    play_5(music_file, 2)
#    print 'changing to mono'
#    time.sleep(0.5)
#    play_5(music_file, 1)
#except KeyboardInterrupt:
#    # if user hits Ctrl/C then exit
#    # (works only in console mode)
#    pygame.mixer.music.fadeout(1000)
#    pygame.mixer.music.stop()
#    raise SystemExit    #