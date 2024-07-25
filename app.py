"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There
is no need for any additional classes in this module.  If you need more classes, 99% of
the time they belong in either the wave module or the models module. If you are unsure
about where a new class should go, post a question on Piazza.

Author: Antony Kariuki, akk85
Date Completed: 12/03/2021
"""
from consts import *
from game2d import *
from wave1 import *


# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py


class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application

    This class extends GameApp and implements the various methods necessary for processing
    the player inputs and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Play object

        Method draw displays the Play object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is to manage the game state: which is when the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]

    STATE SPECIFIC INVARIANTS:
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.

    For a complete description of how the states work, see the specification for the
    method update.

    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be
    documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _sKeyPressed:   states whether the 's' key was pressed in the last frame
                        [bool]
        _score          text which shows the current score of the player
                        [GLabel or None]
        _message        currently active message
                        [GLabel or None]
        _instructions   text with instructions for player
                        [GLabel or None]
        _lives          text which shows the remaining lives of the player
                        [GLabel or None]
        _background     the background of the game
                        [GRectangle]
        _win            states whether the player won or not
                        [bool]
        _personalBest   text message which shows the player's best score so far
                        [GLabel or None]
        _recordMessage  text message which appears at the end of the game if
                        the player sets a new record
                        [GLabel or None]
    """

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message
        (in attribute _text) saying that the user should press to play a game.
        """
        self._state = STATE_INACTIVE
        self._wave = None
        self._sKeyPressed = False
        self._personalBest = 0
        self._background = GRectangle(x=400, y=350, width=800, height=700,
        fillcolor='black')
        #ALL THE MESSAGES BELOW
        self._message = None
        self._instructions = None
        self._score = None
        self._lives = None
        self._recordMessage = None

    def update(self,dt):
        """
        Animates a single frame in the game.

        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.

        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, and STATE_COMPLETE.  Each one of these
        does its own thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).

        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.

        STATE_CONTINUE: This state restores the ship after it was destroyed. The
        application switches to this state if the state was STATE_PAUSED in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_COMPLETE: The wave is over, and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._setText()
        if self._state == STATE_INACTIVE:
            self._wave = None
            self._win = False
            self._checkKeyPressed()
        if self._state == STATE_NEWWAVE:
            self._wave = Wave()
            self._state = STATE_ACTIVE
        if self._state == STATE_ACTIVE:
            playkeys_pressed = [self.input.is_key_down('right'),
            self.input.is_key_down('left'), self.input.is_key_down('spacebar')]
            self._checkKeyPressed()
            self._wave.update(playkeys_pressed, dt)
            if self._wave.getShip() == None and self._wave.getLives()>0:
                self._state = STATE_PAUSED
            if ((self._wave.getShip() == None and self._wave.getLives()==0) or
            self._wave.aliensPassedDefLine()):
                self._state = STATE_COMPLETE
                self._win = False
            if self._wave.getAliensLeft()==0:
                self._state = STATE_COMPLETE
                self._win = True
        if self._state == STATE_PAUSED:
            self._checkKeyPressed()
        if self._state == STATE_CONTINUE:
            self._wave.setShip()
            self._state = STATE_ACTIVE
        if self._state == STATE_COMPLETE:
            self._checkRecord()
            self._checkKeyPressed()

    def draw(self):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        self._background.draw(self.view)
        if (self._state == STATE_ACTIVE or self._state == STATE_NEWWAVE
        and self._wave != None):
            self._wave.draw(self.view)
        if self._message != None:
            self._message.draw(self.view)
        if self._score != None:
            self._score.draw(self.view)
        if self._instructions != None:
            self._instructions.draw(self.view)
        if self._lives != None:
            self._lives.draw(self.view)
        if self._recordMessage!=None:
            self._recordMessage.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE
    def _checkKeyPressed(self):
        """
        This method checks if the user has pressed the 'S' key. If the key is
        pressed, the method changes the state or turn on/off the sound,
        depending on the current state of the game.
        """
        is_key_pressed = self.input.is_key_down('s')
        if (is_key_pressed and self._sKeyPressed == False):
            if self._state == STATE_INACTIVE or self._state == STATE_COMPLETE:
                self._message = None
                self._state = STATE_NEWWAVE
            if self._state == STATE_PAUSED:
                self._instructions = None
                self._state = STATE_CONTINUE
            if self._state == STATE_ACTIVE:
                self._wave.setSound(not self._wave.getSound())
        self._sKeyPressed = is_key_pressed

    def _setText(self):
        """
        This method changes the text messages on the screen
        (_message, _score, _instructions, _lives) in respect to
        the current state of the game.
        """
        if self._state == STATE_INACTIVE:
            self._instructions = GLabel(text="Press 'S' To Start",font_size =50,
            x= 400, y = 400, linecolor = 'yellow', font_name = FONT)
        if self._state == STATE_NEWWAVE:
            self._instructions = None
        if self._state == STATE_ACTIVE:
            self._setTextActive()
        if self._state == STATE_PAUSED:
            self._instructions = GLabel(text="Press 'S' To Continue",
            font_size=50, x= 400, y =400, linecolor = 'yellow',font_name = FONT)
            self._lives = GLabel(text="Lives: "+ str(self._wave.getLives()),
            font_size =30,x=730, y =680, linecolor ='yellow', font_name =FONT)
        if self._state == STATE_COMPLETE:
            self._score =  GLabel(text="Score: "+ str(self._wave.getScore()),
            font_size = 30, x= 90, y =680, linecolor ='yellow', font_name =FONT)
            if self._win:
                self._message = GLabel(text="You Win", font_size = 50,
                x= 400, y = 400, linecolor = 'yellow', font_name = FONT)
            elif not self._win:
                self._message = GLabel(text="You Lose", font_size = 50,
                x= 400, y = 400, linecolor = 'yellow', font_name = FONT)
            self._lives = None
            self._instructions = GLabel(text="Press 'S' To Play Again",
            font_size =50, x =400, y =300, linecolor ='yellow', font_name =FONT)
        else:
            self._recordMessage = None #Record messages only at STATE_COMPLETE

    def _setTextActive(self):
        """
        This method changes the text messages on the screen (_message,
         _score, _instructions, _lives) when the game is in STATE_ACTIVE.
        """
        self._instructions = GLabel(text="Press 'S' To Turn Sound On/Off",
        font_size = 20, x=630, y =20, linecolor ='yellow', font_name = FONT)
        self._score =  GLabel(text="Score: "+ str(self._wave.getScore()),
        font_size = 30, x= 90, y =680, linecolor ='yellow', font_name =FONT)
        self._lives = GLabel(text="Lives: "+ str(self._wave.getLives()),
        font_size =30,x=730, y =680, linecolor ='yellow', font_name =FONT)
        self._message=GLabel(text="Personal Best: "+str(self._personalBest),
        font_size =30,x=400, y =680, linecolor ='yellow', font_name =FONT)

    def _checkRecord(self):
        """
        This method checks if the player set a new record. If yes, the method
        generates a creates a congratulation message and sets the _personalBest
        attribute to the new score.
        """
        if self._wave.getScore() > self._personalBest:
            self._personalBest = self._wave.getScore()
            self._recordMessage = GLabel(text = "New Record: " + \
            str(self._personalBest), font_size =50, x =400, y =500,
            linecolor ='red',font_name =FONT)
