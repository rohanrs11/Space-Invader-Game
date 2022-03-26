from main import Player

import pygame

def test_scoreboard():
    """this will test the last number gets eliminated in the highscore"""
    s = scoreboard()
    assert s(1,2,3,4,5,6,7,8,9,10,11) == (2,3,4,5,6,7,8,9,10,11)
    assert s(1,1,2,3,4,5,6,7,8,9,10) == (1,2,3,4,5,6,7,8,9,10)
    assert s(1,2,3,4,5,6,6,7,8,9,10) == (2,3,4,5,6,6,7,8,9,10)
    assert s(2,3,4,4,5,5,6,7,8,9,10) == (3,4,4,5,5,6,7,8,9,10)

