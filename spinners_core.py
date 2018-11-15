# -*- coding: utf-8 -*-
"""
Created on Fri Nov 02 20:51:36 2018

@author: Alexi
"""

import pygame
import random
import logging
from enum import Enum

DEBUG = False

class Visibility(Enum):
  locked = 0
  visible = 1
  hidden = 2

class GameException(Exception):
  pass

class Space:
  def __init__(self, visibility=Visibility.visible):
    self.visibility = visibility
    self.resource_type = 0 #no resource
    self.color = (random.randint(0,255),
                  random.randint(0,255),
                  random.randint(0,255))
    self.connections = (random.randint(0,1), #top
                        random.randint(0,1), #right
                        random.randint(0,1), #bottom
                        random.randint(0,1)) #left
    if self.connections == (0,0,0,0):
      self.connections = (1,1,1,1) #No void squares, more plus signs
      self.resource_type = 1

  def rotate_left(self):
    if self.visibility == Visibility.visible:
      self.connections = (self.connections[1],
                        self.connections[2],
                        self.connections[3],
                        self.connections[0])

  def rotate_right(self):
    if self.visibility == Visibility.visible:
      self.connections = (self.connections[3],
                        self.connections[0],
                        self.connections[1],
                        self.connections[2])

  def lock(self):
    self.visibility = Visibility.locked

  def reveal(self):
    if self.visibility != Visibility.locked:
      self.visibility = Visibility.visible

  def match_left(self,other):
    return self.connections[3]==1 and other.connections[1]==1

  def match_right(self,other):
    return self.connections[1]==1 and other.connections[3]==1

  def match_up(self,other):
    return self.connections[0]==1 and other.connections[2]==1

  def match_down(self,other):
    return self.connections[2]==1 and other.connections[0]==1

  def draw(self,screen,left,top,width,height):
    if self.visibility == Visibility.hidden:
      return #Don't draw hidden squares!
    pygame.draw.rect(screen, #surface
                       self.color, #color
                       pygame.Rect(left,top,width,height)) #shape
    #draw the connections in white
    if self.connections[0] == 1: #top
      pygame.draw.rect(screen,
                     (255,255,255),
                     pygame.Rect(left+width/2-1,
                                 top,2,height/2))
    if self.connections[1] == 1: #right
      pygame.draw.rect(screen,
                     (255,255,255),
                     pygame.Rect(left+width/2,top+height/2-1,width/2,2))
    if self.connections[2] == 1: #bottom
      pygame.draw.rect(screen,
                     (255,255,255),
                     pygame.Rect(left+width/2-1,
                                 top+height/2,2,height/2))
    if self.connections[3] == 1: #left
      pygame.draw.rect(screen,
                     (255,255,255),
                     pygame.Rect(left,
                                 top+height/2-1,width/2,2))
    if self.resource_type==0:
      return
    elif self.resource_type==1:
      #Fill circle
      pygame.draw.circle(screen,
                     (0,0,0),
                     (left+width/2,top+height/2), #center position
                     min(height,width)/4, #radius
                     0) #border width
      #Border circle
      pygame.draw.circle(screen,
                     (255,255,255),
                     (left+width/2,top+height/2), #center position
                     min(height,width)/4, #radius
                     2) #border width


class App:
  def __init__(self): #Setup the board game info
    self.screen_width = 800
    self.screen_height = 800
    self.size = 26 #size of a single square
    self.border = 2 #border around squares (double for border between)
    self.margin_left = 100
    self.margin_top = 100
    self.width = 20
    self.height = 20
    self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))

  def on_execute(self): #launch the game after setup (call constructor first!)
    try:
      pygame.init()

      self.my_font = pygame.font.SysFont('Average', 30)

      self.locked_count = 0
      self.board = [[Space(Visibility.hidden) for x in range(self.width)] for y in range(self.height)]

      start_x = random.randint(0,self.width-1)
      start_y = random.randint(0,self.height-1)
      #start_x = 0
      #start_y = 0
      self.home_color = self.board[start_y][start_x].color
      self.lock(self.board[start_y][start_x])
      self.cascade(start_x,start_y)

      text_surface = self.my_font.render("A: rotate anti-clockwise. S: rotate clockwise. Q: quit",
                                         False, (255,255,255))
      self.screen.blit(text_surface,(self.margin_left,
                                     self.screen_height-self.margin_top+20))

      done = False

      while not done:
        for event in pygame.event.get(): #empty the event queue. IMPORTANT SIDE-EFFECT
          if event.type == pygame.QUIT:
            done = True
          if event.type == pygame.KEYDOWN:
            self.register_action(event)
        pygame.display.flip() #pygame is double-buffered. this swaps for viz.
        for row in range(self.height):
          for col in range(self.width):
            self.board[row][col].draw(self.screen,
                                     self.margin_left+self.border+
                                     (self.border*2+self.size)*col,
                                     self.margin_top+self.border+
                                     (self.border*2+self.size)*row,
                                     self.size,self.size)
        if self.locked_count > self.width * self.height / 2:
          self.play_again_screen("You have added "+str(self.locked_count)+" squares to your empire. Victory!")
      pygame.quit()
    except AttributeError as aerr:
      print "AttributeError"
      print aerr
      logging.exception('Caught one.')
      print "An exception has occurred. Quitting now..."
      pygame.quit()

  def play_again_screen(self,message):
    done = False
    text_surface = self.my_font.render(message, False, (255,255,255))
    text_width, text_height = self.my_font.size(message)
    #print "Text width:",text_width
    #print "Text height:",text_height
    pygame.draw.rect(self.screen,(30,30,30),
                     pygame.Rect(80,80,text_width+40,50)) #470
    pygame.draw.rect(self.screen,(30,30,30),
                     pygame.Rect(80,130,200,50))
    self.screen.blit(text_surface,(100,100))
    text_surface_2 = self.my_font.render("Play again? (y/n)", False, (255,255,255))
    self.screen.blit(text_surface_2,(100,150))
    pygame.display.flip()
    while not done:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          done = True
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_y:
            pygame.draw.rect(self.screen,
                     (0,0,0),
                     pygame.Rect(0,0,self.screen_width,self.screen_height))
            self.on_execute() #play again!
            return
          else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    pygame.event.post(pygame.event.Event(pygame.QUIT))

  def lock(self,to_lock):
    self.locked_count += 1
    to_lock.color = self.home_color
    to_lock.lock()

  #Call this after rotating a square.
  #Executes a cascade of locking and revealing
  def cascade(self,x,y):
    curr = self.board[y][x]
    cv = curr.visibility
    if cv == Visibility.hidden:
      return #Never cascade from a hidden square!
    print "Cascading:",x,y,cv,
    print "\tConnex:",curr.connections

    left = right = up = down = None
    if x > 0:
      left = self.board[y][x-1]
    if x < self.width-1:
      right = self.board[y][x+1]
    if y > 0:
      up = self.board[y-1][x]
    if y < self.height-1:
      down = self.board[y+1][x]
    if DEBUG:
      print left, right, up, down

    if cv == Visibility.visible: #Find out if we should lock&cascade again
      if (left != None and left.visibility == Visibility.locked and curr.match_left(left)) or \
        (right != None and right.visibility == Visibility.locked and curr.match_right(right)) or \
        (up != None and up.visibility == Visibility.locked and curr.match_up(up)) or \
        (down != None and down.visibility == Visibility.locked and curr.match_down(down)):
        self.lock(curr)
        print "Locking:",x,y
        self.cascade(x,y)
        return
    else: #cv == Visibility.locked
      #For each adjacent square, do nothing if it's already locked
      #If it's visible, check for match and lock/cascade as needed
      #If it's hidden, reveal it and cascade it
      if left != None: #LEFT
        if left.visibility == Visibility.hidden:
          left.reveal()
          self.cascade(x-1,y)
        elif left.visibility == Visibility.visible and curr.match_left(left):
          self.lock(left)
          self.cascade(x-1,y)
      if right != None: #RIGHT
        if right.visibility == Visibility.hidden:
          right.reveal()
          self.cascade(x+1,y)
        elif right.visibility == Visibility.visible and curr.match_right(right):
          self.lock(right)
          self.cascade(x+1,y)
      if up != None: #UP
        if up.visibility == Visibility.hidden:
          up.reveal()
          self.cascade(x,y-1)
        elif up.visibility == Visibility.visible and curr.match_up(up):
          self.lock(up)
          self.cascade(x,y-1)
      if down != None: #DOWN
        if down.visibility == Visibility.hidden:
          down.reveal()
          self.cascade(x,y+1)
        elif down.visibility == Visibility.visible and curr.match_down(down):
          self.lock(down)
          self.cascade(x,y+1)

  def register_action(self, event):
    if event.key == pygame.K_q:
      print "Surrendering with",self.locked_count,"squares in your empire."
      self.play_again_screen("Surrendering with "+str(self.locked_count)+\
          " squares in your empire.")
      return
    #s for clockwise rotate
    #a for anti-clockwise rotate
    (x,y) = pygame.mouse.get_pos() #get the mouse position
    if DEBUG:
      print "Registered keypress at x,y:",x,y
    #If the mouse is over a square, rotate it. (and key is 'a' or 's')
    tmpx = x-self.margin_left #remove the left margin
    tmpx = tmpx/(self.border*2+self.size) #get the col index
    tmpy = y-self.margin_top
    tmpy = tmpy/(self.border*2+self.size) #get the row index
    #block events if mouse is actually over a border or generally out-of-board
    if x < self.margin_left + tmpx*(self.border*2+self.size) + self.border or \
      x > self.margin_left + tmpx*(self.border*2+self.size) + self.border + self.size or \
      y < self.margin_top + tmpy*(self.border*2+self.size) + self.border or \
      y > self.margin_top + tmpy*(self.border*2+self.size) + self.border + self.size or \
      tmpx < 0 or tmpx >= self.width or \
      tmpy < 0 or tmpy >= self.height:
      return
    if event.key == pygame.K_a:
      self.board[tmpy][tmpx].rotate_left()
      self.cascade(tmpx,tmpy)
    elif event.key == pygame.K_s:
      self.board[tmpy][tmpx].rotate_right()
      self.cascade(tmpx,tmpy)



if __name__=="__main__":
  theApp = App()
  theApp.on_execute()
