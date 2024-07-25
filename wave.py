"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Author: Antony Kariuki, akk85
Date Completed: 12/03/2021
"""

from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _direction: the current direction of the wave [str; 'left','right', or 'down']
        _stepsToFire: the number of steps should take before any alien shoot a bolt [int]
        _aliensLeft: the number of aliens left [int]
        _waveSpeed: the number of seconds between alien steps [0 < float <= 1]
        _score: the current score of the player [int]
        _sound: states whether the sound is on or off [bool]
        _popSound: sound when an alien is killed [Sound object]
        _blastSound: sound when the ship is destroyed [Sound object]
        _pewShipSound: sound when the ship fires a bolt [Sound object]
        _pewAlienSound: sound when an alien fires a bolt [Sound object]
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLives(self):
        """
        Returns the number of the player's lives left.
        """
        return self._lives

    def getShip(self):
        """
        Returns the ship.
        """
        return self._ship

    def getAliensLeft(self):
        """
        Returns the number of aliens left.
        """
        return self._aliensLeft

    def getScore(self):
        """
        Returns the player's score.
        """
        return self._score

    def getSound(self):
        """
        Return whether the sound is on or off.
        """
        return self._sound

    def setShip(self):
        """
        Creates a new Ship object.
        """
        self._ship = Ship()

    def setSound(self, value):
        """
        Sets the sound to True/False.

        Parameter value: whether the sound is on or off
        Preconditions: value is a bool
        """
        self._sound = value

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializes a new Wave object.
        """
        self._blockAliens()
        self._ship = Ship()
        self._dline = GPath(points=[0, DEFENSE_LINE, GAME_WIDTH, DEFENSE_LINE],
        linewidth = 0.5, linecolor = 'gray')
        self._bolts = []
        self._time = 0
        self._direction = 'right'
        self._stepsToFire = random.randint(1,BOLT_RATE)
        self._lives = SHIP_LIVES
        self._aliensLeft = ALIEN_ROWS * ALIENS_IN_ROW
        self._score = 0
        self._popSound = Sound(POP_SOUND)
        self._blastSound = Sound(BLAST_SOUND)
        self._pewShipSound = Sound(SHIP_PEW)
        self._pewAlienSound = Sound(ALIEN_PEW)
        self._sound = True
        self._waveSpeed = ALIEN_SPEED

    #NON-HIDDEN METHODS

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, user_input, dt):
        """
        Animates the ship, aliens, and the laser bolts.

        Parameter user_input: states whether the user pressed a certain key
        Precondition: user_input is a list of bools

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._shipController(user_input)
        self._alienController(dt)
        self._boltsController()

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        This method draws all the models: aliens, ship, defensive line,
        and bolts.

        Parameter view: the game view, used in drawing
        Precondition: view is instance of GView; it is inherited from GameApp
        """
        #DRAW A BLOCK OF ALIENS
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_IN_ROW):
                alien = self._aliens[row][col]
                if alien!=None:
                    alien.draw(view)
        #DRAW THE DEFENSIVE LINE
        self._dline.draw(view)
        #DRAW THE SHIP
        if self._ship != None:
            self._ship.draw(view)
        #DRAW THE BOLTS
        for bolt in self._bolts:
            bolt.draw(view)

    def aliensPassedDefLine(self):
        """
        Returns True if any alien which is not destroyed has passed
        the defensive line; Otherwise, returns False.
        """
        for row in self._aliens:
            for alien in row:
                if alien!=None and (alien.getY()-ALIEN_HEIGHT/2)<= DEFENSE_LINE:
                    return True
        return False

    #HIDDEN METHODS

    #HELPER METHODS FOR INITIALIZER
    def _blockAliens(self):
        """
        Creates a block (a 2D list) of Alien objects.
        """
        # STARTING X COORDINATE OF THE BLOCK
        block_left = ALIEN_H_SEP + ALIEN_WIDTH/2
        # HEIGHT OF THE BLOCK OF ALIENS
        block_height = ALIEN_ROWS * ALIEN_HEIGHT + (ALIEN_ROWS-1)*ALIEN_H_SEP
        # STARTING Y COORDINATE OF THE BLOCK
        block_bottom = GAME_HEIGHT - block_height - ALIEN_CEILING

        self._aliens=[]
        for row in range(ALIEN_ROWS):
            list_row = []
            factor = row % 6
            if factor==0 or factor ==1:
                picture = ALIEN_IMAGES[0]
            elif factor==2 or factor ==3:
                picture = ALIEN_IMAGES[1]
            else:
                picture = ALIEN_IMAGES[2]
            for col in range(ALIENS_IN_ROW):
                list_row.append(Alien(block_left+(ALIEN_WIDTH+ALIEN_H_SEP)*col,
                block_bottom + (ALIEN_HEIGHT+ALIEN_V_SEP)*row,picture))
            self._aliens.append(list_row)

    #HELPER METHODS FOR UPDATE
    def _alienController(self,dt):
        """
        Moves the block of aliens and generates laser bolts from the aliens.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._time += dt
        if self._time >= self._waveSpeed:
            rightest = self._findRightestAlien()
            leftest = self._findLeftestAlien()

            if self._direction == 'right':
                if rightest.getX() + ALIEN_H_WALK <= (GAME_WIDTH -
                (ALIEN_WIDTH/2 + ALIEN_H_SEP)):
                    self._alienMove('right')
                else:
                    self._direction = 'left'
                    self._alienMove('down')
            elif self._direction == 'left':
                if leftest.getX() - ALIEN_H_WALK >= ALIEN_WIDTH/2 + ALIEN_H_SEP:
                    self._alienMove('left')
                else:
                    self._direction = 'right'
                    self._alienMove('down')
            self._stepsToFire -= 1
            if self._stepsToFire == 0:
                alienToShoot = random.choice(self._findBottomAliens())
                if self._sound:
                    self._pewAlienSound.play()
                self._bolts.append(Bolt(alienToShoot.getX(),
                alienToShoot.getY()-ALIEN_HEIGHT/2-BOLT_HEIGHT/2, -BOLT_SPEED))
                self._stepsToFire = random.randint(1,BOLT_RATE)
            self._time = 0

    def _shipController(self, user_input):
        """
        Moves the ship to the left and to the right and generates ship laser
         bolts, according to the user's input.

        Parameter user_input: states whether the user pressed a certain key
        Precondition: user_input is a list of bools
        """
        if user_input[0] == True:
            self._ship.setX(self._ship.getX() + min(SHIP_MOVEMENT,
            GAME_WIDTH - SHIP_WIDTH/2 - self._ship.getX()))
        if user_input[1] == True:
            self._ship.setX(self._ship.getX() - min(SHIP_MOVEMENT,
            self._ship.getX() - SHIP_WIDTH/2))
        if user_input[2]==True and self._existsPlayerBolt() == False:
            if self._sound:
                self._pewShipSound.play()
            self._bolts.append(Bolt(self._ship.getX(),
            SHIP_BOTTOM + SHIP_HEIGHT + BOLT_HEIGHT/2, BOLT_SPEED))

    def _boltsController(self):
        """
        This method animates the bolts and determines if any of them collides
        with an alien or with the ship. If it does, the method removes the
        corresponding bolt from the list of bolts, assignes None to the
        destroyed alien/ship, and if an alien is destroyed, the method increases
        the player's score and speeds up the rest of the aliens.
        """
        for bolt in self._bolts:
            bolt.setY(bolt.getY() + bolt.getVel())
            for row in range(ALIEN_ROWS):
                for col in range(ALIENS_IN_ROW):
                    if (self._aliens[row][col]!=None and bolt.isPlayerBolt() and
                    self._aliens[row][col].collides(bolt)):
                        if self._sound:
                            self._popSound.play()
                        self._aliens[row][col] = None
                        self._score += (row+1)*10
                        self._bolts.remove(bolt)
                        self._aliensLeft -= 1
                        #SPEED UP THE ALIENS
                        self._waveSpeed *= ALIEN_ACCELERATION
            if (self._ship != None and self._ship.collides(bolt)
            and not bolt.isPlayerBolt()):
                if self._sound:
                    self._blastSound.play()
                self._ship = None
                self._bolts.remove(bolt)
                self._lives -= 1
            if (bolt.getY() - BOLT_HEIGHT/2 >= GAME_HEIGHT or
            bolt.getY() + BOLT_HEIGHT/2 <= 0):
                self._bolts.remove(bolt)

    #HELPER METHODS FOR _alienController()
    def _findRightestAlien(self):
        """
        Returns the rightmost alien which is not None.
        """
        rightest = None
        for col in range(ALIENS_IN_ROW):
            for row in range(ALIEN_ROWS):
                if self._aliens[row][col] != None:
                    rightest = self._aliens[row][col]
        return rightest

    def _findLeftestAlien(self):
        """
        Returns the leftmost alien which is not None.
        """
        leftest = None
        for col in range(ALIENS_IN_ROW-1, -1, -1):
            for row in range(ALIEN_ROWS):
                if self._aliens[row][col] != None:
                    leftest = self._aliens[row][col]
        return leftest

    def _alienMove(self, direction):
        """
        Moves the block of aliens with one step.

        Parameter direction: the current direction of the wave
        Precondition: direction is a string ('right', 'left', or 'down')
        """
        for row in self._aliens:
            for alien in row:
                if alien!=None:
                    if direction=='right':
                        alien.setX(alien.getX() + ALIEN_H_WALK)
                    elif direction == 'left':
                        alien.setX(alien.getX() - ALIEN_H_WALK)
                    else:
                        alien.setY(alien.getY() - ALIEN_V_WALK)

    def _findBottomAliens(self):
        """
        Returns a list which includes the bottom alien from each column.
        """
        list = []
        for col in range(ALIENS_IN_ROW):
            bottom = None
            for row in range(ALIEN_ROWS-1,-1,-1):
                if self._aliens[row][col]!=None:
                    bottom = self._aliens[row][col]
            if bottom!=None:
                list.append(bottom)
        return list

    #HELPER METHOD FOR _boltsController()
    def _existsPlayerBolt(self):
        """
        Returns True if there is a player's bolt on the screen; Otherwise,
        returns False.
        """
        for bolt in self._bolts:
            if bolt.isPlayerBolt():
                return True
        return False
