import sys
import time

try:
    from PIL import Image
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

import cozmo
from random import randrange

class starfield:

    def __init__(self, num_stars, max_depth, my_coz):
    	self.coz = my_coz
    	self.clock = time.clock()
    	self.num_stars = num_stars
    	self.max_depth = max_depth
    	self.screen_width = 128
    	self.screen_height = 32
    	self.screen = []
    	
    	for i in range(0, self.screen_width):
    		temp_list = []
    		for j in range(0, self.screen_height):
    			temp_list.append(0x00)
    		self.screen.append(temp_list)
    	self.init_stars()
    	
    def blank_screen(self):
    	for i in range(0, self.screen_width):
    		temp_list = self.screen[i]
    		for j in range(0, self.screen_height):
    			temp_list[j] = 0x00

    def init_stars(self):
        """ Create the starfield """
        self.stars = []
        for i in range(self.num_stars):
            # A star is represented as a list with this format: [X,Y,Z]
            star = [randrange(-25,25), randrange(-25,25), randrange(1, self.max_depth)]
            self.stars.append(star)
            
    
    def move_and_draw_stars(self):
        """ Move and draw the stars """
        origin_x = self.screen_width / 2
        origin_y = self.screen_height / 2
        
        self.blank_screen()
        
        for star in self.stars:
            # The Z component is decreased on each frame.
            star[2] -= 0.2
 
            # If the star has past the screen (I mean Z<=0) then we
            # reposition it far away from the screen (Z=max_depth)
            # with random X and Y coordinates.
            if star[2] <= 0:
                star[0] = randrange(-25,25)
                star[1] = randrange(-25,25)
                star[2] = self.max_depth
 
            # Convert the 3D coordinates to 2D using perspective projection.
            k = 64.0 / star[2]
            x = int(star[0] * k + origin_x)
            y = int(star[1] * k + origin_y)
 
            # Draw the star (if it is visible in the screen).
            if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
            	row_target = self.screen[x]
            	row_target[y] = 0x01
		
		#transform the screen to a list to be converted into bytes
        newScreen = []
        for i in range(0,self.screen_height):
        	for j in range(0,self.screen_width):
        		newScreen.append((self.screen[j])[i])
		#convert the screen to bytes and send to OLED
        face_image = bytes(newScreen)
        image = cozmo.oled_face.convert_pixels_to_screen_data(face_image,self.screen_width,self.screen_height)
        self.coz.display_oled_face_image(image, 1.0)

    def run(self):
        """ Main Loop """
        while 1:
        	t0 = time.clock()
        	#throttle the speed of the animation by counting ticks
        	if t0 - self.clock > .01: 
        		self.move_and_draw_stars()
        		self.clock = time.clock()
           		
def run(sdk_conn):
    '''The run method runs once Cozmo is connected.'''
    robot = sdk_conn.wait_for_robot()
   	
	# move head and lift to make it easy to see Cozmo's face
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    starfield(300, 32, robot).run()
        
if __name__ == '__main__':
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
