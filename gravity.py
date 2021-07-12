import turtle
from time import sleep

scr_height = 750 
ball_radius = 15 # Intended to allow reaching edge of canvas
g = -9.81  # Acceleration due to gravity m/s^2
m2p = 50   # Conversion of metres to pixels
T = 0.0    # Elapsed time
V = 0.0    # Current velocity
Vo = 0.0   # initial velocity
D = 0.0    # Distance travelled
Yinitial = (scr_height/2)-ball_radius # Initial Y position
dT = 0.01  # Time increment for the loop

ball = turtle.Turtle()
bg = ball.getscreen()
bg.screensize(canvwidth=200, canvheight=scr_height, bg="orange")
ball.hideturtle()
ball.shape("circle")
ball.penup()
ball.goto(0,Yinitial)
ball.showturtle()

while True:
  # Acceleration due to gravity is -9.81m/s^2, let's call it g
  # V = current velocity; T = elapsed time; D = distance traveled
  # V = Vo + gT, where Vo is initial velocity
  # Vdt (at time T+dT) = V + gdT, 
  #    where V = Vo + gT
  # D = Vo T + gT^2/2
  # DdT = Vc*dT + (g * dT^2)/2 

  # Check if at bottom edge, and if V < 0 i.e. not bounced yet (prevents oscillation)
    if ball.ycor() <= -Yinitial and V < 0:
        V = -V*0.9
    Tnew = T + dT
    Vincr = (g * dT)
    D = (Vo * Tnew) + (g*Tnew*Tnew)/2
    DdT = (V * dT) + (Vincr * dT)/2
    V = V + Vincr
    Ynew = ball.ycor() + (DdT*m2p)
    # print ("T,"+str(Tnew)+",V,"+str(V)+",D,"+str(D)+",Di,"+str(DdT)+",Yi,"+str(DdT*m2p)+",Y,"+str(Ynew))
    ball.goto(0,Ynew)
    T = Tnew
    sleep(dT)