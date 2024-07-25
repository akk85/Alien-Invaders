"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY


    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializer for wave objects
        """

        self._ship = Ship()
        self._aliens = None
        self._bolts = []
        self._lives = 3
        self._time = 0
        self._right = True
        self._createAliens()


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Animates the ship, aliens and laser bolts
        Parameter dt: The time since the last animation frame
        Precondition: dt is a float
        Parameter input: The users Input
        Precondition:
        """

        self._updateShip(input)
        self._updateAliens(dt)
        self._ShipBolt(input)
        self._MoveBoltsUp()


    #DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Calls the functions that draw the aliens, ship,_dline, bolts and other features eg texts
        """

        self._drawShip(view)
        self._drawAliens(view)
        self._ship.draw(view)
        self._drawDline(view)
        self._drawBolts(view)
        self._updateBolts(view)


    #Helper function to help create the aliens
    def _createAliens(self):
        """
        Creates a list of aliens in their respective positions
        """
        self._aliens=[]
        centre_of_aliens = ALIEN_WIDTH*0.5
        pos_left = ALIEN_H_SEP + centre_of_aliens
        pos_top = GAME_HEIGHT-ALIEN_CEILING
        for column in range(ALIENS_IN_ROW):
            list = [] #List of aliens to append to aliens after creation.
            x = (ALIEN_WIDTH+ALIEN_H_SEP)*column
            for row in range(ALIEN_ROWS):
                y = (ALIEN_HEIGHT+ALIEN_V_SEP)*row
                index = (ALIEN_ROWS -1 - row)//2%len(ALIEN_IMAGES)
                source = ALIEN_IMAGES[index]
                list.append(Alien(pos_left+ x,pos_top -y , source))

            self._aliens.append(list)
        return self._aliens

    #function to DRAW THE ALIEN
    def _drawAliens(self, view):
        """
        Draws the Aliens
        """
        for column in range(len(self._aliens[0])):
            for row in range(len(self._aliens)):
               alien=self._aliens[row][column]
               if (alien is not None):
                    alien.draw(view)


    def _moveAliens(self):
        """
        Moves the aliens right first, and then left once they hit the wall, and so forth...
        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float.
        """
        self._moveAliensRight()



    def _updateAliens(self,dt):
        """
        Updates the Aliens by calling the function _moveAliens
        """
        if self._time < ALIEN_SPEED:
            self._time = self._time + dt
            return
        else:
            self._time = 0
            self._moveAliens()


    def _moveAliensRight(self):

        """
        Moves the aliens right and (down once they hit the wall by calling the function _moveAliensDown )
        """
        reached = False
        for row in self._aliens:
            for alien in row:
                if alien is not None:
                    if self._right ==  True:
                        alien.x = alien.x + ALIEN_H_WALK
                    else:
                        alien.x = alien.x - ALIEN_H_WALK
                    if alien.left < ALIEN_H_SEP or alien.right + ALIEN_H_SEP > GAME_WIDTH:
                        reached = True
        if reached == True:
            self._right = not self._right
            self._moveAliensDown()

    def _moveAliensDown(self):
        """
        Moves the aliens down after reaching edge of the screen
        """
        for row in self._aliens:
            for alien in row:
                if alien is not None:
                    alien.y = alien.y - ALIEN_V_WALK


    def _drawShip(self,view):
        """
        Draws the Ship
        """
        self._ship.draw(view)

    def _updateShip(self,input):
        """
        Method to update ship
        """
        if input.is_key_down('left') and self._ship.left > 0:
            self._ship.moveshipleft()
        if input.is_key_down('right') and self._ship.right < GAME_WIDTH:
            self._ship.moveshipright()



    def _drawDline(self,view):
        """
        Draws the defensive line
        """
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],linewidth=2, linecolor = 'black')
        self._dline.draw(view)



    def _drawBolts(self,view):
        """
        Draws the Bolts
        """
        for bolt in range(len(self._bolts)):
            self._bolts[bolt].draw(view)



    def _ShipBolt(self, input):
        """
        Creates a list and appends player bolts to that list
        Parameter input: the user input, used to control the ship and change state
        [instance of GInput; it is inherited from GameApp]
        Precondition: Must be an instance of GInput
        """
        bolts_list=[]
        for bolt in self._bolts:
            if bolt.isPlayerBolt() == True:
                bolts_list.append(1)
        if len(bolts_list)==0:
            if input.is_key_down('up'):
                self._bolts.append(Bolt(self._ship.x, SHIP_HEIGHT + BOLT_HEIGHT*2, BOLT_UP, BOLT_SPEED, 'red'))
                pewSound = Sound('pew2.wav')
                pewSound.play()

    def _MoveBoltsUp(self):
        """
        Moves the players bolts up one at a time.
        """
        for bolt in self._bolts:
            centre_of_bolt = BOLT_HEIGHT*0.5
            if bolt.isPlayerBolt() == True:
                bolt.y = bolt.y + bolt.getVelocity()
                if bolt.y > GAME_HEIGHT + centre_of_bolt:
                    self._bolts.remove(bolt)


    def _updateBolts(self,view):
        """
        Updates the position of the bolts during combat
        """
        for bolt in self._bolts:
            bolt.y = bolt.y + BOLT_SPEED



    def _AliensBolts():
        """
        Creates and appends alien Bolts to thhe list of bolts
        """



    def _pressbolt(self, input):
        """
        Determines if there was a key press

        This method checks for a key press, and if there is
        one, creates a player bolt . A key
        press is when a key is pressed for the FIRST TIME.
        We do not want the state to continue to change as
        we hold down the key. The user must release the
        key and press it again to change the state.

        ##Credits and acknowledgement: I used code inspired by Walker White's state.py sample code.
        """

        # Determine the current number of keys pressed
        curr_keys = self.input.is_key_down('up')


        # Only change if we have just pressed the keys this animation frame
        change = curr_keys and self.lastkeys == 0

        if self._state == STATE_INACTIVE:
            if change:
            # Click happened.  Change the state
                self._state = STATE_NEWWAVE


        # Update last_keys
        self.lastkeys= self.input.key_count


    # HELPER METHODS FOR COLLISION DETECTION
