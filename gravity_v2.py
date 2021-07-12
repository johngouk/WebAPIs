import turtle
from time import sleep
from typing import List

'''
    This Python script shows the movement of a ball repeatedly falling under the influence of
    gravity, hitting the bottom of the screen, and bouncing until it falls again. It does not
    include the effects of air resistance!
    Acceleration due to gravity (usually called "g") is 9.81 m/s/s i.e. every second, the
    speed towards the centre of the earth increases by 9.81 m/s.
    The script uses the Python Turtle implementation, where the centre of the screen is (0,0),
    up/right is +ive, down/left is -ive, width/2 > x > -width/2 and height/2 > y > -height/2.
    Thus in this model, g = -9.81, because downward speed (velocity) is in the -y direction -
    as the ball falls, y will go more negative, and after the bounce it will go less negative.
    The script converts metres into pixels using an adjustable conversion factor.
    
    The really hard problem is detecting when the ball has effectively stopped bouncing! At the
    moment the last 5 D_incr values are saved in a list, which is checked - observation of
    the output numbers indicates that if the movement is alternately up and down then things
    have pretty much stopped.
    
    The model is not continuous - it uses an adjustable time interval (T_incr) to examine the state
    of the ball after each (time interval) seconds have elapsed.

    I've experimented with different T_incr values; 0.1 is too big, the ball travels
    too far between intervals and often bounces below the line! 0.001 is too small, the ball
    moves incredibly slowly, I'm not sure why... maybe the meters_to_pixels conversion needs
    to be adjusted for different T_incr.
'''

scr_height = 750
scr_width = 200
ball_radius = 15 # Intended to allow reaching edge of canvas
Y_initial = float((scr_height/2)-ball_radius) # Initial Y position

m2p = 50   # Conversion of metres to pixels

g = -9.81  # Acceleration due to gravity m/s^2

T_elapsed = 0.0    # Elapsed time
V_current = 0.0    # Current velocity
V_initial = 0.0    # initial velocity, currently set to 0...
T_incr = 0.02  # Time increment for the loop
D_incr_list: List[float] = []

bounce_efficiency = 0.9 # = 90% efficient bounce i.e. 90% of kinetic energy retained
tick_count = 0         # Counter to print data every 10 ticks
print_interval = 100    # When to print - every N
printing = False       # Whether printing data or not

# Function to check if 5 alternate direction changes => no longer bouncing
def still_bouncing(Dl:List):
    if len(Dl) < 5:
        return True
    # Sledgehammer!!
    # Looking for 5 alternating +ive/-ive D_incr values
    if (Dl[0] < 0 and Dl[1] > 0 and Dl[2] < 0 and Dl[3] > 0 and Dl[4] < 0):
        return False
    elif (Dl[0] > 0 and Dl[1] < 0 and Dl[2] > 0 and Dl[3] < 0 and Dl[4] > 0):
        return False
    return True
        

ball = turtle.Turtle()
bg = ball.getscreen()
bg.setup(scr_width, scr_height+200, 0, 0)
bg.screensize(scr_width, scr_height, "orange")
ball.hideturtle()
ball.shape("circle")
ball.penup()

# Draw a measuring stick marked in meters
# Looks quite cool!
ball.goto(-scr_width/4,-scr_height/2)
meters = int(scr_height/m2p)
colours = ["white","black"]
ball.pensize(10)
ball.pendown()
# print("meters="+str(meters))
while meters > 0:
    i = meters%2
    # print("i="+str(i)+";col="+colours[i])
    ball.pencolor(colours[i])
    ball.goto(ball.xcor(),ball.ycor()+m2p)
    meters = meters-1
ball.penup()

# Draw a line to bounce on
ball.goto(-scr_width/2,-scr_height/2)
ball.pencolor("black")
ball.pendown()
ball.goto(scr_width/2,-scr_height/2)
ball.penup()

# Go to start position and show yourself!!
ball.goto(0,Y_initial)
ball.showturtle()

if printing:
    print ("ScrH=",scr_height,";ScrW=",scr_width,";T_incr=",T_incr,";bounce%=",bounce_efficiency*100)
V_current = V_initial
while still_bouncing(D_incr_list):
  # Check if at bottom edge, and if V < 0 i.e. not bounced yet (prevents oscillation)
    if ball.ycor() <= -Y_initial and V_current < 0:
        # Log data at finer resolution if required
        if abs(V_current) < 1.0:
            print_interval = 1
        # Change direction (V = -V) and take some off for a < 100% efficient bounce
        V_current = (-1 * V_current) * bounce_efficiency
    T_elapsed = T_elapsed + T_incr   # Calculate new current time 
    # Calculate velocity change, i.e. g * time or m/s^2 * s = m/s
    V_incr = (g * T_incr)
    # Calculate change in distance travelled; it has two components, which are added up:
    #   (V_at_start_of_T_incr * T_incr) - distance due to V at start of time interval
    #   ((V_at_end_of_T-incr / 2) * T_incr) - distance due to average increased speed at end
    # Note: D_travelled is a vector, and always negative, because it's always down from the
    #       start point (+ve Y at top of screen)
    D_incr = (V_current * T_incr) + ((V_incr/2) * T_incr)
    # SAve the last 5 D_incr values to check if still bouncing
    D_incr_list.append(D_incr)
    if len(D_incr_list) > 5: # If list more than 5...
        D_incr_list.pop(0)   # Throw away the oldest
    V_current = V_current + V_incr
    # Move ball to current Y + (distance this interval * meters_to_pixels)
    ball.goto(0,ball.ycor()+(D_incr*m2p))
    tick_count += 1
    if tick_count >= print_interval:
        if printing:
            print ("T="+str(T_elapsed)+";V="+str(V_current)+";D_incr="+str(D_incr))
        tick_count = 0
    sleep(T_incr)

print ("Ball effectively stopped bouncing")
        
